"""
Wiberg Bond Order Analysis Tool.

Computes Wiberg bond indices from the density matrix, providing a
measure of covalent bond strength between atom pairs.

Key Features:
    - Wiberg bond indices
    - Total valence per atom
    - Bond multiplicity analysis
    - Detection of multiple bonds

Reference:
    Wiberg, K.B. Tetrahedron 1968, 24, 1083-1096.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolCategory,
    register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError, ValidationError


logger = logging.getLogger(__name__)


# =============================================================================
# BOND TYPE CLASSIFICATION
# =============================================================================

BOND_THRESHOLDS = {
    "single": (0.5, 1.5),
    "double": (1.5, 2.5),
    "triple": (2.5, 3.5),
    "aromatic": (1.2, 1.8),
}


def classify_bond(bond_order: float) -> str:
    """Classify bond type based on bond order."""
    if bond_order < 0.3:
        return "none"
    elif bond_order < 0.8:
        return "weak"
    elif bond_order < 1.5:
        return "single"
    elif bond_order < 2.3:
        return "double"
    elif bond_order < 3.3:
        return "triple"
    else:
        return "multiple"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WibergBondOrder:
    """Wiberg bond order between two atoms."""
    atom_i: int
    atom_j: int
    element_i: str
    element_j: str
    bond_order: float
    bond_type: str
    alpha_contribution: float
    beta_contribution: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_i": self.atom_i,
            "atom_j": self.atom_j,
            "element_i": self.element_i,
            "element_j": self.element_j,
            "bond_order": self.bond_order,
            "bond_type": self.bond_type,
            "alpha_contribution": self.alpha_contribution,
            "beta_contribution": self.beta_contribution,
        }


@dataclass
class AtomicValence:
    """Total Wiberg valence for an atom."""
    atom_index: int
    element: str
    total_valence: float
    free_valence: float
    n_bonds: int
    bonded_atoms: List[int]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_index": self.atom_index,
            "element": self.element,
            "total_valence": self.total_valence,
            "free_valence": self.free_valence,
            "n_bonds": self.n_bonds,
            "bonded_atoms": self.bonded_atoms,
        }


@dataclass
class WibergAnalysisResult:
    """Complete Wiberg bond order analysis results."""
    bond_orders: List[WibergBondOrder]
    atomic_valences: List[AtomicValence]
    bond_order_matrix: List[List[float]]
    total_bond_order_sum: float
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bond_orders": [b.to_dict() for b in self.bond_orders],
            "atomic_valences": [v.to_dict() for v in self.atomic_valences],
            "bond_order_matrix": self.bond_order_matrix,
            "total_bond_order_sum": self.total_bond_order_sum,
            "method": self.method,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class WibergBondOrderInput(ToolInput):
    """Input schema for Wiberg bond order analysis."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ or Psi4 format")
    method: str = Field(default="hf", description="Electronic structure method")
    basis: str = Field(default="cc-pvdz", description="Basis set for calculation")
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    bond_threshold: float = Field(default=0.1, description="Minimum bond order to report")
    expected_valences: Optional[Dict[str, float]] = Field(default=None, description="Expected valences for free valence calculation")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# VALIDATION AND PARSING
# =============================================================================

def validate_wiberg_input(input_data: WibergBondOrderInput) -> Optional[ValidationError]:
    """Validate Wiberg analysis input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    if input_data.bond_threshold < 0 or input_data.bond_threshold > 1:
        return ValidationError(field="bond_threshold", message="Bond threshold must be 0-1")
    
    return None


def parse_geometry_elements(geometry: str) -> List[str]:
    """Extract element symbols from geometry string."""
    elements = []
    for line in geometry.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 4:
            element = ''.join(c for c in parts[0] if c.isalpha())
            elements.append(element)
    return elements


# Expected valences for free valence calculation
DEFAULT_EXPECTED_VALENCES = {
    "H": 1.0, "C": 4.0, "N": 3.0, "O": 2.0, "F": 1.0,
    "Si": 4.0, "P": 3.0, "S": 2.0, "Cl": 1.0, "Br": 1.0, "I": 1.0,
}


# =============================================================================
# WIBERG BOND ORDER COMPUTATION
# =============================================================================

def compute_wiberg_bond_orders(
    wfn: Any,
    elements: List[str],
    bond_threshold: float = 0.1,
    expected_valences: Optional[Dict[str, float]] = None,
) -> WibergAnalysisResult:
    """
    Compute Wiberg bond orders from Psi4 wavefunction.
    
    The Wiberg bond index between atoms A and B is:
    W_AB = sum_{mu in A} sum_{nu in B} (DS)_{mu,nu}^2
    
    where D is the density matrix and S is the overlap matrix.
    """
    import psi4
    import numpy as np
    
    mol = wfn.molecule()
    natoms = mol.natom()
    basisset = wfn.basisset()
    nbf = basisset.nbf()
    
    if expected_valences is None:
        expected_valences = DEFAULT_EXPECTED_VALENCES
    
    # Get density matrices
    Da = np.asarray(wfn.Da())
    Db = np.asarray(wfn.Db()) if not wfn.same_a_b_dens() else Da
    
    # Get overlap matrix
    mints = psi4.core.MintsHelper(basisset)
    S = np.asarray(mints.ao_overlap())
    
    # Compute DS products
    DSa = Da @ S
    DSb = Db @ S
    
    # Map basis functions to atoms
    bf_to_atom = []
    for shell_idx in range(basisset.nshell()):
        atom_idx = basisset.shell_to_center(shell_idx)
        n_func = basisset.shell(shell_idx).nfunction
        bf_to_atom.extend([atom_idx] * n_func)
    
    # Compute Wiberg bond order matrix
    wiberg_matrix = np.zeros((natoms, natoms))
    wiberg_alpha = np.zeros((natoms, natoms))
    wiberg_beta = np.zeros((natoms, natoms))
    
    for mu in range(nbf):
        atom_mu = bf_to_atom[mu]
        for nu in range(nbf):
            atom_nu = bf_to_atom[nu]
            
            if atom_mu != atom_nu:
                wiberg_alpha[atom_mu, atom_nu] += DSa[mu, nu] * DSa[nu, mu]
                wiberg_beta[atom_mu, atom_nu] += DSb[mu, nu] * DSb[nu, mu]
    
    wiberg_matrix = wiberg_alpha + wiberg_beta
    
    # Extract significant bonds
    bond_orders = []
    for i in range(natoms):
        for j in range(i + 1, natoms):
            bo = wiberg_matrix[i, j]
            if bo > bond_threshold:
                bond_orders.append(WibergBondOrder(
                    atom_i=i,
                    atom_j=j,
                    element_i=elements[i] if i < len(elements) else mol.label(i),
                    element_j=elements[j] if j < len(elements) else mol.label(j),
                    bond_order=float(bo),
                    bond_type=classify_bond(bo),
                    alpha_contribution=float(wiberg_alpha[i, j]),
                    beta_contribution=float(wiberg_beta[i, j]),
                ))
    
    # Compute atomic valences
    atomic_valences = []
    for i in range(natoms):
        element = elements[i] if i < len(elements) else mol.label(i)
        total_valence = np.sum(wiberg_matrix[i, :])
        
        # Find bonded atoms
        bonded = [j for j in range(natoms) if j != i and wiberg_matrix[i, j] > bond_threshold]
        n_bonds = len(bonded)
        
        # Calculate free valence
        expected = expected_valences.get(element, 4.0)
        free_valence = max(0, expected - total_valence)
        
        atomic_valences.append(AtomicValence(
            atom_index=i,
            element=element,
            total_valence=float(total_valence),
            free_valence=float(free_valence),
            n_bonds=n_bonds,
            bonded_atoms=bonded,
        ))
    
    # Total bond order sum
    total_bo_sum = np.sum(wiberg_matrix) / 2.0  # Each bond counted twice
    
    return WibergAnalysisResult(
        bond_orders=bond_orders,
        atomic_valences=atomic_valences,
        bond_order_matrix=wiberg_matrix.tolist(),
        total_bond_order_sum=float(total_bo_sum),
        method=wfn.name(),
        basis=basisset.name(),
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class WibergBondOrderTool(BaseTool[WibergBondOrderInput, ToolOutput]):
    """Tool for Wiberg bond order analysis."""
    
    name: ClassVar[str] = "calculate_wiberg_bond_orders"
    description: ClassVar[str] = "Calculate Wiberg bond indices to analyze covalent bonding."
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: WibergBondOrderInput) -> Optional[ValidationError]:
        return validate_wiberg_input(input_data)
    
    def _execute(self, input_data: WibergBondOrderInput) -> Result[ToolOutput]:
        import psi4
        
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_wiberg.out", False)
        
        mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        elements = parse_geometry_elements(input_data.geometry)
        psi4.set_options({"basis": input_data.basis})
        
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for Wiberg bond order analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        result = compute_wiberg_bond_orders(
            wfn, elements, input_data.bond_threshold, input_data.expected_valences,
        )
        
        psi4.core.clean()
        
        # Format bond summary
        bond_strs = []
        for bo in sorted(result.bond_orders, key=lambda x: -x.bond_order)[:10]:
            bond_strs.append(f"{bo.element_i}{bo.atom_i}-{bo.element_j}{bo.atom_j}: {bo.bond_order:.3f} ({bo.bond_type})")
        
        message = (
            f"Wiberg bond order analysis completed\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Significant bonds ({len(result.bond_orders)}):\n"
            + "\n".join(f"  {s}" for s in bond_strs)
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_wiberg_bond_orders(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    bond_threshold: float = 0.1,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Wiberg bond orders.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        bond_threshold: Minimum bond order to report.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with Wiberg bond order analysis results.
    """
    tool = WibergBondOrderTool()
    input_data = {
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "bond_threshold": bond_threshold, **kwargs,
    }
    return tool.run(input_data)
