"""
Mulliken Population Analysis Tool.

Provides Mulliken charge analysis for molecular systems, computing atomic
charges based on partitioning of the electron density using basis function
contributions.

Key Features:
    - Atomic charges from Mulliken population analysis
    - Orbital populations
    - Bond population analysis
    - Spin population (for open-shell systems)

Reference:
    Mulliken, R. S. J. Chem. Phys. 1955, 23, 1833-1840.
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
class MullikenAtomicCharge:
    """Mulliken charge for a single atom."""
    atom_index: int
    element: str
    charge: float
    alpha_population: float
    beta_population: float
    total_population: float
    spin_population: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "atom_index": self.atom_index,
            "element": self.element,
            "charge": self.charge,
            "alpha_population": self.alpha_population,
            "beta_population": self.beta_population,
            "total_population": self.total_population,
            "spin_population": self.spin_population,
        }


@dataclass
class MullikenOrbitalPopulation:
    """Mulliken population for a molecular orbital."""
    orbital_index: int
    orbital_energy: float
    occupation: float
    atom_contributions: Dict[int, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "orbital_index": self.orbital_index,
            "orbital_energy": self.orbital_energy,
            "occupation": self.occupation,
            "atom_contributions": self.atom_contributions,
        }


@dataclass 
class MullikenBondPopulation:
    """Mulliken bond population between two atoms."""
    atom_i: int
    atom_j: int
    population: float
    alpha_contribution: float
    beta_contribution: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "atom_i": self.atom_i,
            "atom_j": self.atom_j,
            "population": self.population,
            "alpha_contribution": self.alpha_contribution,
            "beta_contribution": self.beta_contribution,
        }


@dataclass
class MullikenAnalysisResult:
    """Complete Mulliken population analysis results."""
    atomic_charges: List[MullikenAtomicCharge]
    total_charge: float
    total_spin: float
    orbital_populations: Optional[List[MullikenOrbitalPopulation]]
    bond_populations: Optional[List[MullikenBondPopulation]]
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "atomic_charges": [c.to_dict() for c in self.atomic_charges],
            "total_charge": self.total_charge,
            "total_spin": self.total_spin,
            "method": self.method,
            "basis": self.basis,
        }
        if self.orbital_populations:
            result["orbital_populations"] = [
                o.to_dict() for o in self.orbital_populations
            ]
        if self.bond_populations:
            result["bond_populations"] = [
                b.to_dict() for b in self.bond_populations
            ]
        return result


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class MullikenChargesInput(ToolInput):
    """Input schema for Mulliken population analysis."""
    
    geometry: str = Field(
        ...,
        description="Molecular geometry in XYZ or Psi4 format",
    )
    
    method: str = Field(
        default="hf",
        description="Electronic structure method",
    )
    
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set for calculation",
    )
    
    charge: int = Field(
        default=0,
        description="Molecular charge",
        ge=-10,
        le=10,
    )
    
    multiplicity: int = Field(
        default=1,
        description="Spin multiplicity",
        ge=1,
        le=10,
    )
    
    compute_orbital_populations: bool = Field(
        default=False,
        description="Whether to compute orbital-resolved populations",
    )
    
    compute_bond_populations: bool = Field(
        default=False,
        description="Whether to compute bond populations",
    )
    
    memory: int = Field(
        default=2000,
        description="Memory limit in MB",
    )
    
    n_threads: int = Field(
        default=1,
        description="Number of threads",
    )


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_mulliken_input(input_data: MullikenChargesInput) -> Optional[ValidationError]:
    """Validate Mulliken analysis input."""
    # Check geometry is not empty
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(
            field="geometry",
            message="Geometry cannot be empty",
        )
    
    # Check method is valid
    valid_methods = {
        "hf", "rhf", "uhf", "rohf",
        "b3lyp", "pbe", "pbe0", "bp86", "blyp",
        "wb97x", "wb97x-d", "m06-2x", "cam-b3lyp",
        "mp2", "mp3",
    }
    if input_data.method.lower() not in valid_methods:
        logger.warning(f"Method '{input_data.method}' may not support Mulliken analysis")
    
    return None


def parse_geometry_elements(geometry: str) -> List[str]:
    """Extract element symbols from geometry string."""
    elements = []
    lines = geometry.strip().split("\n")
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            element = parts[0]
            # Handle element symbols with numbers (like H1, C2)
            element_clean = ''.join(c for c in element if c.isalpha())
            if element_clean:
                elements.append(element_clean)
    
    return elements


# =============================================================================
# MULLIKEN ANALYSIS FUNCTIONS
# =============================================================================

def compute_mulliken_charges_from_wfn(
    wfn: Any,
    elements: List[str],
    compute_orbital_pops: bool = False,
    compute_bond_pops: bool = False,
) -> MullikenAnalysisResult:
    """
    Compute Mulliken charges from Psi4 wavefunction.
    
    Args:
        wfn: Psi4 wavefunction object
        elements: List of element symbols
        compute_orbital_pops: Whether to compute orbital populations
        compute_bond_pops: Whether to compute bond populations
        
    Returns:
        MullikenAnalysisResult with all computed data
    """
    import psi4
    import numpy as np
    
    # Get molecular data
    mol = wfn.molecule()
    natoms = mol.natom()
    
    # Get basis set info
    basisset = wfn.basisset()
    
    # Get density matrices
    Da = np.asarray(wfn.Da())  # Alpha density
    
    # Check for beta density (unrestricted)
    is_unrestricted = wfn.same_a_b_dens() is False
    if is_unrestricted:
        Db = np.asarray(wfn.Db())
    else:
        Db = Da.copy()
    
    # Get overlap matrix
    mints = psi4.core.MintsHelper(basisset)
    S = np.asarray(mints.ao_overlap())
    
    # Compute PS matrices
    PS_alpha = np.dot(Da, S)
    PS_beta = np.dot(Db, S)
    
    # Map basis functions to atoms
    shell_to_atom = []
    for shell_idx in range(basisset.nshell()):
        atom_idx = basisset.shell_to_center(shell_idx)
        n_functions = basisset.shell(shell_idx).nfunction
        shell_to_atom.extend([atom_idx] * n_functions)
    
    # Compute atomic populations
    alpha_pops = np.zeros(natoms)
    beta_pops = np.zeros(natoms)
    
    nbf = basisset.nbf()
    for mu in range(nbf):
        atom = shell_to_atom[mu]
        alpha_pops[atom] += PS_alpha[mu, mu]
        beta_pops[atom] += PS_beta[mu, mu]
    
    # Get nuclear charges
    nuclear_charges = []
    for i in range(natoms):
        nuclear_charges.append(mol.Z(i))
    
    # Compute Mulliken charges
    atomic_charges = []
    for i in range(natoms):
        total_pop = alpha_pops[i] + beta_pops[i]
        spin_pop = alpha_pops[i] - beta_pops[i]
        charge = nuclear_charges[i] - total_pop
        
        atomic_charges.append(MullikenAtomicCharge(
            atom_index=i,
            element=elements[i] if i < len(elements) else mol.label(i),
            charge=float(charge),
            alpha_population=float(alpha_pops[i]),
            beta_population=float(beta_pops[i]),
            total_population=float(total_pop),
            spin_population=float(spin_pop),
        ))
    
    total_charge = sum(c.charge for c in atomic_charges)
    total_spin = sum(c.spin_population for c in atomic_charges)
    
    # Compute orbital populations if requested
    orbital_populations = None
    if compute_orbital_pops:
        orbital_populations = _compute_orbital_populations(
            wfn, basisset, S, shell_to_atom, natoms
        )
    
    # Compute bond populations if requested
    bond_populations = None
    if compute_bond_pops:
        bond_populations = _compute_bond_populations(
            Da, Db, S, shell_to_atom, natoms
        )
    
    return MullikenAnalysisResult(
        atomic_charges=atomic_charges,
        total_charge=total_charge,
        total_spin=total_spin,
        orbital_populations=orbital_populations,
        bond_populations=bond_populations,
        method=wfn.name(),
        basis=basisset.name(),
    )


def _compute_orbital_populations(
    wfn: Any,
    basisset: Any,
    S: Any,
    shell_to_atom: List[int],
    natoms: int,
) -> List[MullikenOrbitalPopulation]:
    """Compute Mulliken populations for each molecular orbital."""
    import numpy as np
    
    orbital_pops = []
    
    # Get orbital coefficients and energies
    Ca = np.asarray(wfn.Ca())
    epsilon_a = np.asarray(wfn.epsilon_a())
    
    # Get occupation numbers
    nalpha = wfn.nalpha()
    nbf = basisset.nbf()
    
    for orb_idx in range(min(nalpha + 5, nbf)):  # Include some virtuals
        occupation = 2.0 if orb_idx < nalpha else 0.0
        
        # Compute atom contributions for this orbital
        atom_contributions = {}
        for atom in range(natoms):
            atom_contributions[atom] = 0.0
        
        # C_mu,i * S_mu,nu * C_nu,i
        for mu in range(nbf):
            atom = shell_to_atom[mu]
            for nu in range(nbf):
                contribution = Ca[mu, orb_idx] * S[mu, nu] * Ca[nu, orb_idx]
                atom_contributions[atom] += contribution
        
        orbital_pops.append(MullikenOrbitalPopulation(
            orbital_index=orb_idx,
            orbital_energy=float(epsilon_a[orb_idx]),
            occupation=occupation,
            atom_contributions=atom_contributions,
        ))
    
    return orbital_pops


def _compute_bond_populations(
    Da: Any,
    Db: Any,
    S: Any,
    shell_to_atom: List[int],
    natoms: int,
) -> List[MullikenBondPopulation]:
    """Compute Mulliken bond populations between atom pairs."""
    import numpy as np
    
    nbf = len(shell_to_atom)
    
    # Compute off-diagonal PS populations
    bond_alpha = np.zeros((natoms, natoms))
    bond_beta = np.zeros((natoms, natoms))
    
    PS_alpha = np.dot(Da, S)
    PS_beta = np.dot(Db, S)
    
    for mu in range(nbf):
        atom_mu = shell_to_atom[mu]
        for nu in range(nbf):
            atom_nu = shell_to_atom[nu]
            if atom_mu != atom_nu:
                bond_alpha[atom_mu, atom_nu] += PS_alpha[mu, nu]
                bond_beta[atom_mu, atom_nu] += PS_beta[mu, nu]
    
    # Collect unique atom pairs
    bond_populations = []
    for i in range(natoms):
        for j in range(i + 1, natoms):
            alpha_pop = bond_alpha[i, j] + bond_alpha[j, i]
            beta_pop = bond_beta[i, j] + bond_beta[j, i]
            total_pop = alpha_pop + beta_pop
            
            if abs(total_pop) > 0.01:  # Only significant bonds
                bond_populations.append(MullikenBondPopulation(
                    atom_i=i,
                    atom_j=j,
                    population=float(total_pop),
                    alpha_contribution=float(alpha_pop),
                    beta_contribution=float(beta_pop),
                ))
    
    return bond_populations


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class MullikenChargesTool(BaseTool[MullikenChargesInput, ToolOutput]):
    """
    Tool for Mulliken population analysis.
    
    Computes Mulliken atomic charges by partitioning the electron density
    among atoms based on basis function contributions.
    """
    
    name: ClassVar[str] = "calculate_mulliken_charges"
    description: ClassVar[str] = (
        "Perform Mulliken population analysis to compute atomic charges, "
        "orbital populations, and bond populations."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: MullikenChargesInput) -> Optional[ValidationError]:
        """Validate input parameters."""
        return validate_mulliken_input(input_data)
    
    def _execute(self, input_data: MullikenChargesInput) -> Result[ToolOutput]:
        """Execute Mulliken population analysis."""
        import psi4
        
        # Configure Psi4
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_mulliken.out", False)
        
        # Build molecule
        mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        # Extract elements
        elements = parse_geometry_elements(input_data.geometry)
        
        # Set options
        psi4.set_options({
            "basis": input_data.basis,
        })
        
        # Determine reference
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        # Run SCF calculation
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for Mulliken analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        # Compute Mulliken charges
        result = compute_mulliken_charges_from_wfn(
            wfn=wfn,
            elements=elements,
            compute_orbital_pops=input_data.compute_orbital_populations,
            compute_bond_pops=input_data.compute_bond_populations,
        )
        
        # Clean up
        psi4.core.clean()
        
        # Format output
        charges_str = ", ".join(
            f"{c.element}({c.atom_index}): {c.charge:+.4f}"
            for c in result.atomic_charges
        )
        
        message = (
            f"Mulliken population analysis completed\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Charges: {charges_str}\n"
            f"Total charge: {result.total_charge:.4f}\n"
            f"Total spin: {result.total_spin:.4f}"
        )
        
        output = ToolOutput(
            success=True,
            message=message,
            data=result.to_dict(),
        )
        
        return Result.success(output)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_mulliken_charges(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    compute_orbital_populations: bool = False,
    compute_bond_populations: bool = False,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Mulliken atomic charges.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        compute_orbital_populations: Whether to compute orbital populations.
        compute_bond_populations: Whether to compute bond populations.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with Mulliken analysis results.
        
    Examples:
        >>> result = calculate_mulliken_charges(
        ...     geometry="O 0 0 0\\nH 0 0 0.96\\nH 0 0.96 0",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        >>> charges = result.data["atomic_charges"]
    """
    tool = MullikenChargesTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "compute_orbital_populations": compute_orbital_populations,
        "compute_bond_populations": compute_bond_populations,
        **kwargs,
    }
    
    return tool.run(input_data)
