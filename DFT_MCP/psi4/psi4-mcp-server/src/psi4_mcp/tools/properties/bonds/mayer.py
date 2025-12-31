"""
Mayer Bond Order Analysis Tool.

Computes Mayer bond indices, which are a generalization of the Wiberg
bond order to non-orthogonal basis sets and open-shell systems.

Key Features:
    - Mayer bond indices
    - Generalized bond order for open-shell
    - Total valence per atom
    - Shared and transferred electrons

Reference:
    Mayer, I. Chem. Phys. Lett. 1983, 97, 270-274.
    Mayer, I. Int. J. Quantum Chem. 1984, 26, 151-154.
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
# DATA CLASSES
# =============================================================================

@dataclass
class MayerBondOrder:
    """Mayer bond order between two atoms."""
    atom_i: int
    atom_j: int
    element_i: str
    element_j: str
    bond_order: float
    covalent_component: float
    ionic_component: float
    shared_electrons: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_i": self.atom_i,
            "atom_j": self.atom_j,
            "element_i": self.element_i,
            "element_j": self.element_j,
            "bond_order": self.bond_order,
            "covalent_component": self.covalent_component,
            "ionic_component": self.ionic_component,
            "shared_electrons": self.shared_electrons,
        }


@dataclass
class MayerAtomicValence:
    """Mayer valence indices for an atom."""
    atom_index: int
    element: str
    total_valence: float
    bonded_valence: float
    free_valence: float
    gross_population: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_index": self.atom_index,
            "element": self.element,
            "total_valence": self.total_valence,
            "bonded_valence": self.bonded_valence,
            "free_valence": self.free_valence,
            "gross_population": self.gross_population,
        }


@dataclass
class MayerAnalysisResult:
    """Complete Mayer bond order analysis results."""
    bond_orders: List[MayerBondOrder]
    atomic_valences: List[MayerAtomicValence]
    bond_order_matrix: List[List[float]]
    total_bond_order_sum: float
    is_open_shell: bool
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "bond_orders": [b.to_dict() for b in self.bond_orders],
            "atomic_valences": [v.to_dict() for v in self.atomic_valences],
            "bond_order_matrix": self.bond_order_matrix,
            "total_bond_order_sum": self.total_bond_order_sum,
            "is_open_shell": self.is_open_shell,
            "method": self.method,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class MayerBondOrderInput(ToolInput):
    """Input schema for Mayer bond order analysis."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ or Psi4 format")
    method: str = Field(default="hf", description="Electronic structure method")
    basis: str = Field(default="cc-pvdz", description="Basis set for calculation")
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    bond_threshold: float = Field(default=0.1, description="Minimum bond order to report")
    compute_components: bool = Field(default=True, description="Compute covalent/ionic components")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# VALIDATION AND PARSING
# =============================================================================

def validate_mayer_input(input_data: MayerBondOrderInput) -> Optional[ValidationError]:
    """Validate Mayer analysis input."""
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


# =============================================================================
# MAYER BOND ORDER COMPUTATION
# =============================================================================

def compute_mayer_bond_orders(
    wfn: Any,
    elements: List[str],
    bond_threshold: float = 0.1,
    compute_components: bool = True,
) -> MayerAnalysisResult:
    """
    Compute Mayer bond orders from Psi4 wavefunction.
    
    The Mayer bond index is defined as:
    B_AB = sum_{mu in A} sum_{nu in B} [(DS)_{mu,nu}(DS)_{nu,mu} + (DS')_{mu,nu}(DS')_{nu,mu}]
    """
    import psi4
    import numpy as np
    
    mol = wfn.molecule()
    natoms = mol.natom()
    basisset = wfn.basisset()
    nbf = basisset.nbf()
    
    # Get density matrices
    Da = np.asarray(wfn.Da())
    is_open_shell = not wfn.same_a_b_dens()
    Db = np.asarray(wfn.Db()) if is_open_shell else Da
    
    # Get overlap matrix
    mints = psi4.core.MintsHelper(basisset)
    S = np.asarray(mints.ao_overlap())
    
    # Compute DS products
    DSa = Da @ S
    DSb = Db @ S
    D_total = Da + Db
    DS_total = D_total @ S
    
    # Map basis functions to atoms
    bf_to_atom = []
    for shell_idx in range(basisset.nshell()):
        atom_idx = basisset.shell_to_center(shell_idx)
        n_func = basisset.shell(shell_idx).nfunction
        bf_to_atom.extend([atom_idx] * n_func)
    
    # Compute Mayer bond order matrix
    mayer_matrix = np.zeros((natoms, natoms))
    covalent_matrix = np.zeros((natoms, natoms))
    
    for mu in range(nbf):
        atom_mu = bf_to_atom[mu]
        for nu in range(nbf):
            atom_nu = bf_to_atom[nu]
            
            if atom_mu != atom_nu:
                mayer_contribution = DSa[mu, nu] * DSa[nu, mu] + DSb[mu, nu] * DSb[nu, mu]
                mayer_matrix[atom_mu, atom_nu] += mayer_contribution
                
                if compute_components:
                    covalent = 0.5 * (DSa[mu, nu] * DSa[nu, mu] + DSb[mu, nu] * DSb[nu, mu])
                    covalent_matrix[atom_mu, atom_nu] += covalent
    
    # Compute gross atomic populations
    gross_pop = np.zeros(natoms)
    for mu in range(nbf):
        atom_mu = bf_to_atom[mu]
        gross_pop[atom_mu] += DS_total[mu, mu]
    
    # Extract significant bonds
    bond_orders = []
    for i in range(natoms):
        for j in range(i + 1, natoms):
            bo = mayer_matrix[i, j]
            if bo > bond_threshold:
                covalent = covalent_matrix[i, j] if compute_components else 0.0
                ionic = bo - covalent if compute_components else 0.0
                
                bond_orders.append(MayerBondOrder(
                    atom_i=i,
                    atom_j=j,
                    element_i=elements[i] if i < len(elements) else mol.label(i),
                    element_j=elements[j] if j < len(elements) else mol.label(j),
                    bond_order=float(bo),
                    covalent_component=float(covalent),
                    ionic_component=float(ionic),
                    shared_electrons=float(bo),
                ))
    
    # Compute atomic valences
    atomic_valences = []
    for i in range(natoms):
        element = elements[i] if i < len(elements) else mol.label(i)
        bonded_valence = np.sum(mayer_matrix[i, :])
        
        diag_contribution = 0.0
        for mu in range(nbf):
            if bf_to_atom[mu] == i:
                for nu in range(nbf):
                    if bf_to_atom[nu] == i:
                        diag_contribution += DS_total[mu, nu] * DS_total[nu, mu]
        
        total_valence = 2 * gross_pop[i] - diag_contribution
        free_valence = max(0, total_valence - bonded_valence)
        
        atomic_valences.append(MayerAtomicValence(
            atom_index=i,
            element=element,
            total_valence=float(total_valence),
            bonded_valence=float(bonded_valence),
            free_valence=float(free_valence),
            gross_population=float(gross_pop[i]),
        ))
    
    total_bo_sum = np.sum(mayer_matrix) / 2.0
    
    return MayerAnalysisResult(
        bond_orders=bond_orders,
        atomic_valences=atomic_valences,
        bond_order_matrix=mayer_matrix.tolist(),
        total_bond_order_sum=float(total_bo_sum),
        is_open_shell=is_open_shell,
        method=wfn.name(),
        basis=basisset.name(),
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class MayerBondOrderTool(BaseTool[MayerBondOrderInput, ToolOutput]):
    """Tool for Mayer bond order analysis."""
    
    name: ClassVar[str] = "calculate_mayer_bond_orders"
    description: ClassVar[str] = "Calculate Mayer bond indices for covalent bonding analysis."
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: MayerBondOrderInput) -> Optional[ValidationError]:
        return validate_mayer_input(input_data)
    
    def _execute(self, input_data: MayerBondOrderInput) -> Result[ToolOutput]:
        import psi4
        
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_mayer.out", False)
        
        mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        elements = parse_geometry_elements(input_data.geometry)
        psi4.set_options({"basis": input_data.basis})
        
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for Mayer bond order analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        result = compute_mayer_bond_orders(
            wfn, elements, input_data.bond_threshold, input_data.compute_components,
        )
        
        psi4.core.clean()
        
        bond_strs = []
        for bo in sorted(result.bond_orders, key=lambda x: -x.bond_order)[:10]:
            bond_strs.append(f"{bo.element_i}{bo.atom_i}-{bo.element_j}{bo.atom_j}: {bo.bond_order:.3f}")
        
        shell_type = "open-shell" if result.is_open_shell else "closed-shell"
        message = (
            f"Mayer bond order analysis completed ({shell_type})\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Significant bonds ({len(result.bond_orders)}):\n"
            + "\n".join(f"  {s}" for s in bond_strs)
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_mayer_bond_orders(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    bond_threshold: float = 0.1,
    compute_components: bool = True,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Mayer bond orders.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        bond_threshold: Minimum bond order to report.
        compute_components: Compute covalent/ionic breakdown.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with Mayer bond order analysis results.
    """
    tool = MayerBondOrderTool()
    input_data = {
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "bond_threshold": bond_threshold, 
        "compute_components": compute_components, **kwargs,
    }
    return tool.run(input_data)
