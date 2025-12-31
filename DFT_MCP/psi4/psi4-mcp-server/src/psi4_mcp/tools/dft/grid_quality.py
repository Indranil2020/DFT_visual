"""
DFT Grid Quality Tool.

Controls and analyzes DFT integration grid settings for accuracy
and computational efficiency.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)


GRID_PRESETS = {
    "coarse": {"dft_spherical_points": 302, "dft_radial_points": 50, "description": "Fast, lower accuracy"},
    "medium": {"dft_spherical_points": 434, "dft_radial_points": 75, "description": "Standard accuracy"},
    "fine": {"dft_spherical_points": 590, "dft_radial_points": 99, "description": "High accuracy"},
    "ultrafine": {"dft_spherical_points": 974, "dft_radial_points": 175, "description": "Very high accuracy"},
    "superfine": {"dft_spherical_points": 1454, "dft_radial_points": 250, "description": "Maximum accuracy"},
}


@dataclass
class GridQualityResult:
    """Grid quality analysis results."""
    preset: str
    spherical_points: int
    radial_points: int
    estimated_points_per_atom: int
    energy: float
    functional: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "preset": self.preset,
            "spherical_points": self.spherical_points,
            "radial_points": self.radial_points,
            "total_points_per_atom": self.estimated_points_per_atom,
            "energy_hartree": self.energy,
            "functional": self.functional,
            "basis": self.basis,
        }


class GridQualityInput(ToolInput):
    """Input for grid quality analysis."""
    geometry: str = Field(..., description="Molecular geometry")
    functional: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    grid_preset: str = Field(default="fine", description="coarse, medium, fine, ultrafine, superfine")
    
    custom_spherical: Optional[int] = Field(default=None, description="Custom spherical grid points")
    custom_radial: Optional[int] = Field(default=None, description="Custom radial grid points")
    
    compare_grids: bool = Field(default=False, description="Compare multiple grid settings")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_grid_quality_input(input_data: GridQualityInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.grid_preset not in GRID_PRESETS and not input_data.custom_spherical:
        return ValidationError(field="grid_preset", message=f"Use: {', '.join(GRID_PRESETS.keys())}")
    return None


def run_grid_calculation(input_data: GridQualityInput) -> GridQualityResult:
    """Execute DFT calculation with specified grid."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_grid.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    # Get grid settings
    if input_data.custom_spherical and input_data.custom_radial:
        spherical = input_data.custom_spherical
        radial = input_data.custom_radial
        preset = "custom"
    else:
        grid_settings = GRID_PRESETS[input_data.grid_preset]
        spherical = grid_settings["dft_spherical_points"]
        radial = grid_settings["dft_radial_points"]
        preset = input_data.grid_preset
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
        "dft_spherical_points": spherical,
        "dft_radial_points": radial,
    })
    
    logger.info(f"Running {input_data.functional}/{input_data.basis} with {preset} grid")
    
    energy = psi4.energy(f"{input_data.functional}/{input_data.basis}", molecule=mol)
    
    estimated_points = spherical * radial
    
    psi4.core.clean()
    
    return GridQualityResult(
        preset=preset,
        spherical_points=spherical,
        radial_points=radial,
        estimated_points_per_atom=estimated_points,
        energy=energy,
        functional=input_data.functional.upper(),
        basis=input_data.basis,
    )


@register_tool  
class GridQualityTool(BaseTool[GridQualityInput, ToolOutput]):
    """Tool for DFT grid quality control."""
    name: ClassVar[str] = "analyze_grid_quality"
    description: ClassVar[str] = "Analyze DFT integration grid settings."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: GridQualityInput) -> Optional[ValidationError]:
        return validate_grid_quality_input(input_data)
    
    def _execute(self, input_data: GridQualityInput) -> Result[ToolOutput]:
        result = run_grid_calculation(input_data)
        
        message = (
            f"DFT Grid Analysis ({result.functional}/{result.basis})\n"
            f"{'='*50}\n"
            f"Grid Preset:     {result.preset}\n"
            f"Spherical Pts:   {result.spherical_points}\n"
            f"Radial Pts:      {result.radial_points}\n"
            f"Pts/Atom:        ~{result.estimated_points_per_atom:,}\n"
            f"Energy:          {result.energy:.10f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def analyze_grid(geometry: str, grid_preset: str = "fine", **kwargs: Any) -> ToolOutput:
    """Analyze DFT grid quality."""
    return GridQualityTool().run({"geometry": geometry, "grid_preset": grid_preset, **kwargs})
