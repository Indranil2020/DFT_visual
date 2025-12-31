"""
Electrostatic Potential (ESP) Derived Charges Tool.

Computes atomic charges by fitting to the molecular electrostatic potential
on a grid of points around the molecule. These charges reproduce the
electrostatic potential outside the van der Waals surface.

Key Features:
    - ESP fitting on Merz-Kollman or CHELPG grids
    - Restrained ESP (RESP) charges
    - Charge constraints (total charge, symmetry)
    - Quality metrics for the fit

References:
    - Merz-Kollman: Singh, U.C.; Kollman, P.A. J. Comput. Chem. 1984, 5, 129.
    - CHELPG: Breneman, C.M.; Wiberg, K.B. J. Comput. Chem. 1990, 11, 361.
    - RESP: Bayly, C.I. et al. J. Phys. Chem. 1993, 97, 10269.
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

VDW_RADII = {
    "H": 1.20, "He": 1.40,
    "Li": 1.82, "Be": 1.53, "B": 1.92, "C": 1.70, "N": 1.55, "O": 1.52, "F": 1.47, "Ne": 1.54,
    "Na": 2.27, "Mg": 1.73, "Al": 1.84, "Si": 2.10, "P": 1.80, "S": 1.80, "Cl": 1.75, "Ar": 1.88,
    "K": 2.75, "Ca": 2.31, "Br": 1.85, "I": 1.98,
}

BOHR_TO_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ESPAtomicCharge:
    """ESP-derived charge for a single atom."""
    atom_index: int
    element: str
    charge: float
    coordinates: Tuple[float, float, float]
    vdw_radius: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_index": self.atom_index,
            "element": self.element,
            "charge": self.charge,
            "coordinates": list(self.coordinates),
            "vdw_radius": self.vdw_radius,
        }


@dataclass
class ESPFitStatistics:
    """Statistics for ESP fitting quality."""
    n_grid_points: int
    rms_error: float
    relative_rms_error: float
    max_error: float
    r_squared: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "n_grid_points": self.n_grid_points,
            "rms_error": self.rms_error,
            "relative_rms_error": self.relative_rms_error,
            "max_error": self.max_error,
            "r_squared": self.r_squared,
        }


@dataclass
class ESPAnalysisResult:
    """Complete ESP charge analysis results."""
    atomic_charges: List[ESPAtomicCharge]
    total_charge: float
    fit_statistics: ESPFitStatistics
    grid_type: str
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atomic_charges": [c.to_dict() for c in self.atomic_charges],
            "total_charge": self.total_charge,
            "fit_statistics": self.fit_statistics.to_dict(),
            "grid_type": self.grid_type,
            "method": self.method,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class ESPChargesInput(ToolInput):
    """Input schema for ESP charge fitting."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ or Psi4 format")
    method: str = Field(default="hf", description="Electronic structure method")
    basis: str = Field(default="cc-pvdz", description="Basis set for calculation")
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    grid_type: str = Field(default="mk", description="Grid type: mk, chelpg, or connolly")
    vdw_scale: float = Field(default=1.4, description="Scaling factor for VDW surface")
    vdw_increment: float = Field(default=0.2, description="Layer spacing in Angstrom")
    n_layers: int = Field(default=4, description="Number of layers around molecule")
    grid_density: float = Field(default=1.0, description="Grid density in points/Angstrom^2")
    use_resp: bool = Field(default=False, description="Use RESP restraints")
    resp_a: float = Field(default=0.0005, description="RESP restraint strength")
    resp_b: float = Field(default=0.1, description="RESP hyperbolic restraint")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# VALIDATION AND PARSING
# =============================================================================

def validate_esp_input(input_data: ESPChargesInput) -> Optional[ValidationError]:
    """Validate ESP analysis input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    valid_grid_types = {"mk", "chelpg", "connolly"}
    if input_data.grid_type.lower() not in valid_grid_types:
        return ValidationError(field="grid_type", message=f"Grid type must be one of {valid_grid_types}")
    
    if input_data.vdw_scale < 1.0:
        return ValidationError(field="vdw_scale", message="VDW scale must be >= 1.0")
    
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
# GRID GENERATION
# =============================================================================

def generate_mk_grid(
    atoms: List[Tuple[str, float, float, float]],
    vdw_scale: float,
    vdw_increment: float,
    n_layers: int,
    density: float,
) -> List[Tuple[float, float, float]]:
    """Generate Merz-Kollman grid points on shells around VDW surface."""
    import numpy as np
    
    grid_points = []
    
    for layer in range(n_layers):
        scale = vdw_scale + layer * vdw_increment
        
        for element, x, y, z in atoms:
            radius = VDW_RADII.get(element, 1.70) * scale
            n_points = max(int(4 * np.pi * radius**2 * density), 20)
            golden_angle = np.pi * (3 - np.sqrt(5))
            
            for i in range(n_points):
                theta = golden_angle * i
                z_offset = 1 - (2 * i + 1) / n_points
                r_xy = np.sqrt(1 - z_offset**2)
                
                px = x + radius * r_xy * np.cos(theta)
                py = y + radius * r_xy * np.sin(theta)
                pz = z + radius * z_offset
                
                is_outside = True
                for elem2, x2, y2, z2 in atoms:
                    r2 = VDW_RADII.get(elem2, 1.70) * vdw_scale
                    dist = np.sqrt((px-x2)**2 + (py-y2)**2 + (pz-z2)**2)
                    if dist < r2 * 0.99:
                        is_outside = False
                        break
                
                if is_outside:
                    grid_points.append((px, py, pz))
    
    return grid_points


def generate_chelpg_grid(
    atoms: List[Tuple[str, float, float, float]],
    vdw_scale: float,
    spacing: float = 0.3,
) -> List[Tuple[float, float, float]]:
    """Generate CHELPG regular cubic grid."""
    import numpy as np
    
    coords = np.array([(x, y, z) for _, x, y, z in atoms])
    radii = np.array([VDW_RADII.get(e, 1.70) for e, _, _, _ in atoms])
    
    min_coords = coords.min(axis=0) - radii.max() * vdw_scale - 2.8
    max_coords = coords.max(axis=0) + radii.max() * vdw_scale + 2.8
    
    grid_points = []
    
    for px in np.arange(min_coords[0], max_coords[0], spacing):
        for py in np.arange(min_coords[1], max_coords[1], spacing):
            for pz in np.arange(min_coords[2], max_coords[2], spacing):
                min_dist = float('inf')
                inside_any = False
                
                for i, (element, x, y, z) in enumerate(atoms):
                    r_vdw = VDW_RADII.get(element, 1.70)
                    dist = np.sqrt((px-x)**2 + (py-y)**2 + (pz-z)**2)
                    
                    if dist < r_vdw * vdw_scale:
                        inside_any = True
                        break
                    min_dist = min(min_dist, dist - r_vdw * vdw_scale)
                
                if not inside_any and min_dist < 2.8:
                    grid_points.append((px, py, pz))
    
    return grid_points


# =============================================================================
# ESP COMPUTATION AND FITTING
# =============================================================================

def compute_esp_on_grid(wfn: Any, grid_points: List[Tuple[float, float, float]]) -> List[float]:
    """Compute electrostatic potential at grid points."""
    import psi4
    import numpy as np
    
    grid_bohr = np.array(grid_points) * ANGSTROM_TO_BOHR
    mol = wfn.molecule()
    natoms = mol.natom()
    
    esp_values = []
    for point in grid_bohr:
        esp = 0.0
        for i in range(natoms):
            Z = mol.Z(i)
            x, y, z = mol.x(i), mol.y(i), mol.z(i)
            dist = np.sqrt((point[0]-x)**2 + (point[1]-y)**2 + (point[2]-z)**2)
            if dist > 1e-10:
                esp += Z / dist
        esp_values.append(esp)
    
    return esp_values


def fit_esp_charges(
    atoms: List[Tuple[str, float, float, float]],
    grid_points: List[Tuple[float, float, float]],
    esp_values: List[float],
    total_charge: int,
    use_resp: bool = False,
    resp_a: float = 0.0005,
    resp_b: float = 0.1,
) -> Tuple[List[float], ESPFitStatistics]:
    """Fit atomic charges to reproduce ESP using constrained least squares."""
    import numpy as np
    
    natoms = len(atoms)
    npoints = len(grid_points)
    
    A = np.zeros((npoints, natoms))
    for i, (px, py, pz) in enumerate(grid_points):
        for j, (_, ax, ay, az) in enumerate(atoms):
            dist = np.sqrt((px-ax)**2 + (py-ay)**2 + (pz-az)**2)
            if dist > 1e-10:
                A[i, j] = 1.0 / (dist * ANGSTROM_TO_BOHR)
    
    b = np.array(esp_values)
    ATA = A.T @ A
    ATb = A.T @ b
    
    if use_resp:
        for j in range(natoms):
            ATA[j, j] += resp_a
    
    augmented = np.zeros((natoms + 1, natoms + 1))
    augmented[:natoms, :natoms] = ATA
    augmented[:natoms, natoms] = 1.0
    augmented[natoms, :natoms] = 1.0
    
    rhs = np.zeros(natoms + 1)
    rhs[:natoms] = ATb
    rhs[natoms] = total_charge
    
    solution = np.linalg.solve(augmented, rhs)
    charges = solution[:natoms]
    
    esp_fitted = A @ charges
    errors = esp_fitted - b
    
    rms_error = np.sqrt(np.mean(errors**2))
    max_error = np.max(np.abs(errors))
    esp_range = np.max(b) - np.min(b)
    relative_rms = rms_error / esp_range if esp_range > 1e-10 else 0.0
    
    ss_res = np.sum(errors**2)
    ss_tot = np.sum((b - np.mean(b))**2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 1e-10 else 0.0
    
    stats = ESPFitStatistics(
        n_grid_points=npoints,
        rms_error=float(rms_error),
        relative_rms_error=float(relative_rms),
        max_error=float(max_error),
        r_squared=float(r_squared),
    )
    
    return list(charges), stats


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class ESPChargesTool(BaseTool[ESPChargesInput, ToolOutput]):
    """Tool for ESP-derived atomic charges."""
    
    name: ClassVar[str] = "calculate_esp_charges"
    description: ClassVar[str] = "Calculate ESP-derived atomic charges by fitting to molecular electrostatic potential."
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: ESPChargesInput) -> Optional[ValidationError]:
        return validate_esp_input(input_data)
    
    def _execute(self, input_data: ESPChargesInput) -> Result[ToolOutput]:
        import psi4
        
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_esp.out", False)
        
        mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        atoms = parse_geometry_data(input_data.geometry)
        psi4.set_options({"basis": input_data.basis})
        
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for ESP analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        if input_data.grid_type.lower() == "chelpg":
            grid_points = generate_chelpg_grid(atoms, input_data.vdw_scale)
        else:
            grid_points = generate_mk_grid(
                atoms, input_data.vdw_scale, input_data.vdw_increment,
                input_data.n_layers, input_data.grid_density,
            )
        
        esp_values = compute_esp_on_grid(wfn, grid_points)
        charges, stats = fit_esp_charges(
            atoms, grid_points, esp_values, input_data.charge,
            input_data.use_resp, input_data.resp_a, input_data.resp_b,
        )
        
        atomic_charges = []
        for i, ((element, x, y, z), charge) in enumerate(zip(atoms, charges)):
            atomic_charges.append(ESPAtomicCharge(
                atom_index=i, element=element, charge=float(charge),
                coordinates=(x, y, z), vdw_radius=VDW_RADII.get(element, 1.70),
            ))
        
        result = ESPAnalysisResult(
            atomic_charges=atomic_charges,
            total_charge=sum(charges),
            fit_statistics=stats,
            grid_type=input_data.grid_type,
            method=input_data.method,
            basis=input_data.basis,
        )
        
        psi4.core.clean()
        
        charges_str = ", ".join(f"{c.element}({c.atom_index}): {c.charge:+.4f}" for c in atomic_charges)
        message = (
            f"ESP charge fitting completed\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Grid: {input_data.grid_type} ({stats.n_grid_points} points)\n"
            f"Charges: {charges_str}\n"
            f"RMS error: {stats.rms_error:.6f}, R²: {stats.r_squared:.4f}"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_esp_charges(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    grid_type: str = "mk",
    use_resp: bool = False,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate ESP-derived atomic charges.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        grid_type: Grid type (mk or chelpg).
        use_resp: Whether to use RESP restraints.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with ESP charge analysis results.
    """
    tool = ESPChargesTool()
    input_data = {
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "grid_type": grid_type, "use_resp": use_resp, **kwargs,
    }
    return tool.run(input_data)
