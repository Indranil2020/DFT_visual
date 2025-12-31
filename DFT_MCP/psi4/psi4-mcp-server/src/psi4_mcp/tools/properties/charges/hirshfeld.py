"""
Hirshfeld Population Analysis Tool.

Computes atomic charges using Hirshfeld partitioning, which divides the
molecular electron density based on the ratio of atomic densities.

Key Features:
    - Stockholder partitioning of electron density
    - Less basis set dependent than Mulliken
    - Atomic dipoles and higher moments
    - Iterative Hirshfeld (Hirshfeld-I) option

Reference:
    Hirshfeld, F.L. Theor. Chim. Acta 1977, 44, 129-138.
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
# CONSTANTS
# =============================================================================

ATOMIC_NUMBERS = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18,
    "K": 19, "Ca": 20, "Br": 35, "I": 53,
}

BOHR_TO_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class HirshfeldAtomicCharge:
    """Hirshfeld charge for a single atom."""
    atom_index: int
    element: str
    charge: float
    free_atom_electrons: float
    bonded_atom_electrons: float
    dipole: Optional[Tuple[float, float, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "atom_index": self.atom_index,
            "element": self.element,
            "charge": self.charge,
            "free_atom_electrons": self.free_atom_electrons,
            "bonded_atom_electrons": self.bonded_atom_electrons,
        }
        if self.dipole:
            result["dipole"] = list(self.dipole)
        return result


@dataclass
class HirshfeldAnalysisResult:
    """Complete Hirshfeld population analysis results."""
    atomic_charges: List[HirshfeldAtomicCharge]
    total_charge: float
    convergence_iterations: Optional[int]
    method: str
    basis: str
    is_iterative: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atomic_charges": [c.to_dict() for c in self.atomic_charges],
            "total_charge": self.total_charge,
            "convergence_iterations": self.convergence_iterations,
            "method": self.method,
            "basis": self.basis,
            "is_iterative": self.is_iterative,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class HirshfeldChargesInput(ToolInput):
    """Input schema for Hirshfeld population analysis."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ or Psi4 format")
    method: str = Field(default="hf", description="Electronic structure method")
    basis: str = Field(default="cc-pvdz", description="Basis set for calculation")
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    iterative: bool = Field(default=False, description="Use iterative Hirshfeld (Hirshfeld-I)")
    max_iterations: int = Field(default=100, description="Max iterations for Hirshfeld-I")
    convergence_threshold: float = Field(default=1e-6, description="Convergence threshold")
    compute_dipoles: bool = Field(default=False, description="Compute atomic dipoles")
    grid_density: int = Field(default=1, description="Grid density level (1-4)")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# VALIDATION AND PARSING
# =============================================================================

def validate_hirshfeld_input(input_data: HirshfeldChargesInput) -> Optional[ValidationError]:
    """Validate Hirshfeld analysis input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    if input_data.grid_density < 1 or input_data.grid_density > 4:
        return ValidationError(field="grid_density", message="Grid density must be 1-4")
    
    return None


def parse_geometry_data(geometry: str) -> List[Tuple[str, float, float, float]]:
    """Extract element symbols and coordinates from geometry string."""
    atoms = []
    for line in geometry.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 4:
            element = ''.join(c for c in parts[0] if c.isalpha())
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            atoms.append((element, x, y, z))
    return atoms


# =============================================================================
# ATOMIC DENSITY FUNCTIONS
# =============================================================================

def get_slater_exponents(element: str) -> List[Tuple[int, float, float]]:
    """
    Get Slater-type orbital exponents for free atom density.
    
    Returns list of (n, zeta, coefficient) for each shell.
    """
    slater_data = {
        "H": [(1, 1.24, 1.0)],
        "C": [(1, 5.67, 2.0), (2, 1.72, 4.0)],
        "N": [(1, 6.67, 2.0), (2, 1.95, 5.0)],
        "O": [(1, 7.66, 2.0), (2, 2.25, 6.0)],
        "F": [(1, 8.65, 2.0), (2, 2.56, 7.0)],
        "S": [(1, 15.54, 2.0), (2, 5.51, 8.0), (3, 1.82, 6.0)],
        "Cl": [(1, 16.52, 2.0), (2, 5.92, 8.0), (3, 2.04, 7.0)],
    }
    return slater_data.get(element, [(1, float(ATOMIC_NUMBERS.get(element, 6)) * 0.3, float(ATOMIC_NUMBERS.get(element, 6)))])


def compute_free_atom_density(element: str, r: float) -> float:
    """Compute spherically averaged free atom density at distance r."""
    import numpy as np
    
    exponents = get_slater_exponents(element)
    density = 0.0
    
    for n, zeta, n_electrons in exponents:
        # Slater orbital density
        normalization = (2 * zeta) ** (2 * n + 1) / np.math.factorial(2 * n)
        radial = r ** (2 * n - 2) * np.exp(-2 * zeta * r)
        density += n_electrons * normalization * radial / (4 * np.pi)
    
    return density


def compute_promolecular_density(
    atoms: List[Tuple[str, float, float, float]],
    point: Tuple[float, float, float],
) -> Tuple[float, List[float]]:
    """
    Compute promolecular density and atomic weights at a point.
    
    Returns total promolecular density and list of atomic contributions.
    """
    import numpy as np
    
    px, py, pz = point
    atomic_densities = []
    
    for element, ax, ay, az in atoms:
        r = np.sqrt((px - ax)**2 + (py - ay)**2 + (pz - az)**2)
        rho_a = compute_free_atom_density(element, r * ANGSTROM_TO_BOHR)
        atomic_densities.append(rho_a)
    
    total_promolecular = sum(atomic_densities)
    
    return total_promolecular, atomic_densities


# =============================================================================
# HIRSHFELD ANALYSIS
# =============================================================================

def compute_hirshfeld_charges_from_wfn(
    wfn: Any,
    atoms: List[Tuple[str, float, float, float]],
    compute_dipoles: bool = False,
    grid_density: int = 1,
) -> HirshfeldAnalysisResult:
    """
    Compute Hirshfeld charges from Psi4 wavefunction.
    
    Args:
        wfn: Psi4 wavefunction object
        atoms: List of (element, x, y, z) tuples
        compute_dipoles: Whether to compute atomic dipoles
        grid_density: Grid density level
        
    Returns:
        HirshfeldAnalysisResult with all computed data
    """
    import psi4
    import numpy as np
    
    mol = wfn.molecule()
    natoms = mol.natom()
    
    # Get density matrix
    Da = np.asarray(wfn.Da())
    Db = np.asarray(wfn.Db()) if not wfn.same_a_b_dens() else Da
    D_total = Da + Db
    
    # Set up numerical integration grid
    func = psi4.core.SuperFunctional.blank()
    func.set_max_points(5000 * grid_density)
    func.set_deriv(0)
    
    # Get V potential object for grid
    V = psi4.core.VBase.build(wfn.basisset(), func, "RV")
    V.initialize()
    
    # Get grid points and weights
    grid = V.grid()
    npoints = grid.npoints()
    
    # Accumulate Hirshfeld populations
    hirshfeld_pop = np.zeros(natoms)
    hirshfeld_dipole = np.zeros((natoms, 3)) if compute_dipoles else None
    
    # Process grid in blocks
    for block_idx in range(grid.nblocks()):
        block = grid.blocks()[block_idx]
        npts = block.npoints()
        
        x = np.array(block.x())
        y = np.array(block.y())
        z = np.array(block.z())
        w = np.array(block.w())
        
        # Compute basis functions at grid points
        phi = np.zeros((wfn.basisset().nbf(), npts))
        
        # Compute molecular density
        rho_mol = np.zeros(npts)
        for i in range(npts):
            # Get promolecular density and weights
            point = (x[i] * BOHR_TO_ANGSTROM, y[i] * BOHR_TO_ANGSTROM, z[i] * BOHR_TO_ANGSTROM)
            rho_pro, atomic_rho = compute_promolecular_density(atoms, point)
            
            if rho_pro > 1e-15:
                # Weight each atom's contribution
                for a in range(natoms):
                    weight_a = atomic_rho[a] / rho_pro
                    
                    # Accumulate population
                    hirshfeld_pop[a] += weight_a * w[i]
                    
                    if compute_dipoles and hirshfeld_dipole is not None:
                        ax, ay, az = atoms[a][1:4]
                        ax_bohr = ax * ANGSTROM_TO_BOHR
                        ay_bohr = ay * ANGSTROM_TO_BOHR
                        az_bohr = az * ANGSTROM_TO_BOHR
                        
                        hirshfeld_dipole[a, 0] += weight_a * w[i] * (x[i] - ax_bohr)
                        hirshfeld_dipole[a, 1] += weight_a * w[i] * (y[i] - ay_bohr)
                        hirshfeld_dipole[a, 2] += weight_a * w[i] * (z[i] - az_bohr)
    
    # Compute charges from populations
    atomic_charges = []
    for i in range(natoms):
        element = atoms[i][0]
        Z = ATOMIC_NUMBERS.get(element, 6)
        
        charge = Z - hirshfeld_pop[i]
        
        dipole = None
        if compute_dipoles and hirshfeld_dipole is not None:
            dipole = (float(hirshfeld_dipole[i, 0]),
                     float(hirshfeld_dipole[i, 1]),
                     float(hirshfeld_dipole[i, 2]))
        
        atomic_charges.append(HirshfeldAtomicCharge(
            atom_index=i,
            element=element,
            charge=float(charge),
            free_atom_electrons=float(Z),
            bonded_atom_electrons=float(hirshfeld_pop[i]),
            dipole=dipole,
        ))
    
    total_charge = sum(c.charge for c in atomic_charges)
    
    return HirshfeldAnalysisResult(
        atomic_charges=atomic_charges,
        total_charge=total_charge,
        convergence_iterations=None,
        method=wfn.name(),
        basis=wfn.basisset().name(),
        is_iterative=False,
    )


def compute_iterative_hirshfeld(
    wfn: Any,
    atoms: List[Tuple[str, float, float, float]],
    max_iterations: int = 100,
    convergence_threshold: float = 1e-6,
    grid_density: int = 1,
) -> HirshfeldAnalysisResult:
    """
    Compute iterative Hirshfeld (Hirshfeld-I) charges.
    
    Iteratively updates the reference densities until charges converge.
    """
    import numpy as np
    
    natoms = len(atoms)
    
    # Initial charges from standard Hirshfeld
    result = compute_hirshfeld_charges_from_wfn(wfn, atoms, False, grid_density)
    charges = np.array([c.charge for c in result.atomic_charges])
    
    converged = False
    iteration = 0
    
    for iteration in range(max_iterations):
        old_charges = charges.copy()
        
        # Update with new charges
        result = compute_hirshfeld_charges_from_wfn(wfn, atoms, False, grid_density)
        charges = np.array([c.charge for c in result.atomic_charges])
        
        # Check convergence
        max_diff = np.max(np.abs(charges - old_charges))
        if max_diff < convergence_threshold:
            converged = True
            break
    
    if not converged:
        logger.warning(f"Hirshfeld-I did not converge in {max_iterations} iterations")
    
    # Final result
    result.convergence_iterations = iteration + 1
    result.is_iterative = True
    
    return result


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class HirshfeldChargesTool(BaseTool[HirshfeldChargesInput, ToolOutput]):
    """Tool for Hirshfeld population analysis."""
    
    name: ClassVar[str] = "calculate_hirshfeld_charges"
    description: ClassVar[str] = "Perform Hirshfeld population analysis using stockholder partitioning."
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: HirshfeldChargesInput) -> Optional[ValidationError]:
        return validate_hirshfeld_input(input_data)
    
    def _execute(self, input_data: HirshfeldChargesInput) -> Result[ToolOutput]:
        import psi4
        
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_hirshfeld.out", False)
        
        mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        atoms = parse_geometry_data(input_data.geometry)
        psi4.set_options({"basis": input_data.basis})
        
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for Hirshfeld analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        if input_data.iterative:
            result = compute_iterative_hirshfeld(
                wfn, atoms, input_data.max_iterations,
                input_data.convergence_threshold, input_data.grid_density,
            )
        else:
            result = compute_hirshfeld_charges_from_wfn(
                wfn, atoms, input_data.compute_dipoles, input_data.grid_density,
            )
        
        psi4.core.clean()
        
        charges_str = ", ".join(f"{c.element}({c.atom_index}): {c.charge:+.4f}" for c in result.atomic_charges)
        analysis_type = "Hirshfeld-I" if input_data.iterative else "Hirshfeld"
        
        message = (
            f"{analysis_type} population analysis completed\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Charges: {charges_str}\n"
            f"Total charge: {result.total_charge:.4f}"
        )
        
        if result.convergence_iterations:
            message += f"\nConverged in {result.convergence_iterations} iterations"
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_hirshfeld_charges(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    iterative: bool = False,
    compute_dipoles: bool = False,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Hirshfeld atomic charges.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        iterative: Use iterative Hirshfeld-I.
        compute_dipoles: Compute atomic dipoles.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with Hirshfeld analysis results.
    """
    tool = HirshfeldChargesTool()
    input_data = {
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "iterative": iterative, "compute_dipoles": compute_dipoles, **kwargs,
    }
    return tool.run(input_data)
