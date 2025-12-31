"""
Löwdin Population Analysis Tool.

Provides Löwdin charge analysis for molecular systems using symmetric
orthogonalization of the basis functions. This method addresses some
of the basis set dependence issues of Mulliken analysis.

Key Features:
    - Atomic charges from Löwdin population analysis
    - Symmetric orthogonalization
    - Reduced basis set dependence compared to Mulliken
    - Orbital populations

Reference:
    Löwdin, P.-O. J. Chem. Phys. 1950, 18, 365-375.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
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
class LowdinAtomicCharge:
    """Löwdin charge for a single atom."""
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
class LowdinOrbitalPopulation:
    """Löwdin population for a molecular orbital."""
    orbital_index: int
    orbital_energy: float
    occupation: float
    atom_contributions: Dict[int, float]
    angular_momentum_contributions: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "orbital_index": self.orbital_index,
            "orbital_energy": self.orbital_energy,
            "occupation": self.occupation,
            "atom_contributions": self.atom_contributions,
            "angular_momentum_contributions": self.angular_momentum_contributions,
        }


@dataclass
class LowdinAnalysisResult:
    """Complete Löwdin population analysis results."""
    atomic_charges: List[LowdinAtomicCharge]
    total_charge: float
    total_spin: float
    orbital_populations: Optional[List[LowdinOrbitalPopulation]]
    s_half_matrix_condition: float
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "atomic_charges": [c.to_dict() for c in self.atomic_charges],
            "total_charge": self.total_charge,
            "total_spin": self.total_spin,
            "s_half_matrix_condition": self.s_half_matrix_condition,
            "method": self.method,
            "basis": self.basis,
        }
        if self.orbital_populations:
            result["orbital_populations"] = [
                o.to_dict() for o in self.orbital_populations
            ]
        return result


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class LowdinChargesInput(ToolInput):
    """Input schema for Löwdin population analysis."""
    
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
    
    eigenvalue_threshold: float = Field(
        default=1e-8,
        description="Threshold for S^(-1/2) eigenvalues",
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

def validate_lowdin_input(input_data: LowdinChargesInput) -> Optional[ValidationError]:
    """Validate Löwdin analysis input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(
            field="geometry",
            message="Geometry cannot be empty",
        )
    
    if input_data.eigenvalue_threshold <= 0:
        return ValidationError(
            field="eigenvalue_threshold",
            message="Eigenvalue threshold must be positive",
        )
    
    return None


def parse_geometry_elements(geometry: str) -> List[str]:
    """Extract element symbols from geometry string."""
    elements = []
    lines = geometry.strip().split("\n")
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            element = parts[0]
            element_clean = ''.join(c for c in element if c.isalpha())
            if element_clean:
                elements.append(element_clean)
    
    return elements


# =============================================================================
# LÖWDIN ANALYSIS FUNCTIONS
# =============================================================================

def compute_s_half_inverse(S: Any, threshold: float = 1e-8) -> Any:
    """
    Compute S^(-1/2) using symmetric orthogonalization.
    
    Args:
        S: Overlap matrix
        threshold: Eigenvalue threshold for numerical stability
        
    Returns:
        S^(-1/2) matrix
    """
    import numpy as np
    
    # Diagonalize S
    eigenvalues, eigenvectors = np.linalg.eigh(S)
    
    # Check condition number
    condition = eigenvalues[-1] / max(eigenvalues[0], threshold)
    
    # Apply threshold and compute S^(-1/2)
    s_half_inv_diag = np.zeros_like(eigenvalues)
    for i, eigval in enumerate(eigenvalues):
        if eigval > threshold:
            s_half_inv_diag[i] = 1.0 / np.sqrt(eigval)
    
    # Reconstruct S^(-1/2)
    S_half_inv = eigenvectors @ np.diag(s_half_inv_diag) @ eigenvectors.T
    
    return S_half_inv, condition


def compute_lowdin_charges_from_wfn(
    wfn: Any,
    elements: List[str],
    compute_orbital_pops: bool = False,
    eigenvalue_threshold: float = 1e-8,
) -> LowdinAnalysisResult:
    """
    Compute Löwdin charges from Psi4 wavefunction.
    
    Args:
        wfn: Psi4 wavefunction object
        elements: List of element symbols
        compute_orbital_pops: Whether to compute orbital populations
        eigenvalue_threshold: Threshold for S^(-1/2) eigenvalues
        
    Returns:
        LowdinAnalysisResult with all computed data
    """
    import psi4
    import numpy as np
    
    # Get molecular data
    mol = wfn.molecule()
    natoms = mol.natom()
    
    # Get basis set info
    basisset = wfn.basisset()
    nbf = basisset.nbf()
    
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
    
    # Compute S^(-1/2)
    S_half_inv, condition = compute_s_half_inverse(S, eigenvalue_threshold)
    
    # Transform density to Löwdin basis: D' = S^(1/2) D S^(1/2)
    # For populations: P' = S^(-1/2) D S^(1/2)
    S_half = np.linalg.inv(S_half_inv)
    
    # Löwdin density matrix
    D_lowdin_alpha = S_half @ Da @ S_half
    D_lowdin_beta = S_half @ Db @ S_half
    
    # Map basis functions to atoms
    shell_to_atom = []
    shell_to_am = []  # Angular momentum
    for shell_idx in range(basisset.nshell()):
        atom_idx = basisset.shell_to_center(shell_idx)
        am = basisset.shell(shell_idx).am
        n_functions = basisset.shell(shell_idx).nfunction
        shell_to_atom.extend([atom_idx] * n_functions)
        shell_to_am.extend([am] * n_functions)
    
    # Compute atomic populations from diagonal of Löwdin density
    alpha_pops = np.zeros(natoms)
    beta_pops = np.zeros(natoms)
    
    for mu in range(nbf):
        atom = shell_to_atom[mu]
        alpha_pops[atom] += D_lowdin_alpha[mu, mu]
        beta_pops[atom] += D_lowdin_beta[mu, mu]
    
    # Get nuclear charges
    nuclear_charges = []
    for i in range(natoms):
        nuclear_charges.append(mol.Z(i))
    
    # Compute Löwdin charges
    atomic_charges = []
    for i in range(natoms):
        total_pop = alpha_pops[i] + beta_pops[i]
        spin_pop = alpha_pops[i] - beta_pops[i]
        charge = nuclear_charges[i] - total_pop
        
        atomic_charges.append(LowdinAtomicCharge(
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
        orbital_populations = _compute_lowdin_orbital_populations(
            wfn, basisset, S_half, shell_to_atom, shell_to_am, natoms
        )
    
    return LowdinAnalysisResult(
        atomic_charges=atomic_charges,
        total_charge=total_charge,
        total_spin=total_spin,
        orbital_populations=orbital_populations,
        s_half_matrix_condition=float(condition),
        method=wfn.name(),
        basis=basisset.name(),
    )


def _compute_lowdin_orbital_populations(
    wfn: Any,
    basisset: Any,
    S_half: Any,
    shell_to_atom: List[int],
    shell_to_am: List[int],
    natoms: int,
) -> List[LowdinOrbitalPopulation]:
    """Compute Löwdin populations for each molecular orbital."""
    import numpy as np
    
    orbital_pops = []
    
    # Get orbital coefficients and energies
    Ca = np.asarray(wfn.Ca())
    epsilon_a = np.asarray(wfn.epsilon_a())
    
    # Transform to Löwdin basis
    Ca_lowdin = S_half @ Ca
    
    nalpha = wfn.nalpha()
    nbf = basisset.nbf()
    
    # Angular momentum labels
    am_labels = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g"}
    
    for orb_idx in range(min(nalpha + 5, nbf)):
        occupation = 2.0 if orb_idx < nalpha else 0.0
        
        # Compute atom contributions
        atom_contributions = {}
        for atom in range(natoms):
            atom_contributions[atom] = 0.0
        
        # Angular momentum contributions
        am_contributions = {label: 0.0 for label in am_labels.values()}
        
        # Sum of |C'_mu,i|^2
        for mu in range(nbf):
            atom = shell_to_atom[mu]
            am = shell_to_am[mu]
            coeff_sq = Ca_lowdin[mu, orb_idx] ** 2
            
            atom_contributions[atom] += coeff_sq
            
            am_label = am_labels.get(am, f"l={am}")
            if am_label in am_contributions:
                am_contributions[am_label] += coeff_sq
        
        orbital_pops.append(LowdinOrbitalPopulation(
            orbital_index=orb_idx,
            orbital_energy=float(epsilon_a[orb_idx]),
            occupation=occupation,
            atom_contributions=atom_contributions,
            angular_momentum_contributions=am_contributions,
        ))
    
    return orbital_pops


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class LowdinChargesTool(BaseTool[LowdinChargesInput, ToolOutput]):
    """
    Tool for Löwdin population analysis.
    
    Uses symmetric orthogonalization to compute atomic charges with
    reduced basis set dependence compared to Mulliken analysis.
    """
    
    name: ClassVar[str] = "calculate_lowdin_charges"
    description: ClassVar[str] = (
        "Perform Löwdin population analysis to compute atomic charges "
        "using symmetric orthogonalization."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: LowdinChargesInput) -> Optional[ValidationError]:
        """Validate input parameters."""
        return validate_lowdin_input(input_data)
    
    def _execute(self, input_data: LowdinChargesInput) -> Result[ToolOutput]:
        """Execute Löwdin population analysis."""
        import psi4
        
        # Configure Psi4
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_lowdin.out", False)
        
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
        
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        # Run SCF calculation
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for Löwdin analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        # Compute Löwdin charges
        result = compute_lowdin_charges_from_wfn(
            wfn=wfn,
            elements=elements,
            compute_orbital_pops=input_data.compute_orbital_populations,
            eigenvalue_threshold=input_data.eigenvalue_threshold,
        )
        
        # Clean up
        psi4.core.clean()
        
        # Format output
        charges_str = ", ".join(
            f"{c.element}({c.atom_index}): {c.charge:+.4f}"
            for c in result.atomic_charges
        )
        
        message = (
            f"Löwdin population analysis completed\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Charges: {charges_str}\n"
            f"Total charge: {result.total_charge:.4f}\n"
            f"S^(-1/2) condition: {result.s_half_matrix_condition:.2e}"
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

def calculate_lowdin_charges(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    compute_orbital_populations: bool = False,
    eigenvalue_threshold: float = 1e-8,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Löwdin atomic charges.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        compute_orbital_populations: Whether to compute orbital populations.
        eigenvalue_threshold: Threshold for S^(-1/2) eigenvalues.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with Löwdin analysis results.
        
    Examples:
        >>> result = calculate_lowdin_charges(
        ...     geometry="O 0 0 0\\nH 0 0 0.96\\nH 0 0.96 0",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        >>> charges = result.data["atomic_charges"]
    """
    tool = LowdinChargesTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "compute_orbital_populations": compute_orbital_populations,
        "eigenvalue_threshold": eigenvalue_threshold,
        **kwargs,
    }
    
    return tool.run(input_data)
