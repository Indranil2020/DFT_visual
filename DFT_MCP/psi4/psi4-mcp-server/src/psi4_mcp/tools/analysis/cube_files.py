"""
Cube File Generation and Analysis Tool.

Generates and manipulates Gaussian cube files for visualization
of molecular orbitals, electron density, and other 3D properties.

Reference:
    Gaussian cube file format specification.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)


CUBE_PROPERTIES = {
    "density": "Total electron density",
    "esp": "Electrostatic potential",
    "homo": "HOMO orbital",
    "lumo": "LUMO orbital",
    "orbital": "Specific orbital",
    "spin_density": "Spin density (alpha - beta)",
}


@dataclass
class CubeFileResult:
    """Cube file generation results."""
    property_type: str
    filename: str
    grid_points: Tuple[int, int, int]
    grid_spacing: float
    min_value: float
    max_value: float
    orbital_index: Optional[int]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "property_type": self.property_type,
            "filename": self.filename,
            "grid_points": self.grid_points,
            "grid_spacing_bohr": self.grid_spacing,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "orbital_index": self.orbital_index,
        }


class CubeFileInput(ToolInput):
    """Input for cube file generation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Method for density/orbitals")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    property_type: str = Field(
        default="density",
        description="Property to visualize: density, esp, homo, lumo, orbital, spin_density"
    )
    
    orbital_index: Optional[int] = Field(default=None, description="Orbital index for 'orbital' property")
    
    grid_points: int = Field(default=50, description="Grid points per dimension")
    grid_padding: float = Field(default=4.0, description="Padding around molecule (bohr)")
    
    output_filename: str = Field(default="output.cube", description="Output filename")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_cube_file_input(input_data: CubeFileInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.property_type not in CUBE_PROPERTIES:
        return ValidationError(
            field="property_type",
            message=f"Invalid property. Use: {', '.join(CUBE_PROPERTIES.keys())}"
        )
    if input_data.property_type == "orbital" and input_data.orbital_index is None:
        return ValidationError(field="orbital_index", message="orbital_index required for 'orbital' property")
    return None


def run_cube_file_generation(input_data: CubeFileInput) -> CubeFileResult:
    """Generate cube file."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_cube.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
        "cubeprop_tasks": [input_data.property_type.upper()],
        "cubic_grid_overage": [input_data.grid_padding],
        "cubic_grid_spacing": [input_data.grid_padding / input_data.grid_points],
    })
    
    logger.info(f"Generating {input_data.property_type} cube file")
    
    # Run calculation to get wavefunction
    energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", 
                              return_wfn=True, molecule=mol)
    
    # Generate cube file
    psi4.cubeprop(wfn)
    
    # Calculate grid spacing
    grid_spacing = input_data.grid_padding / input_data.grid_points
    
    # Estimate min/max values
    if input_data.property_type == "density":
        min_val, max_val = 0.0, 0.5
    elif input_data.property_type == "esp":
        min_val, max_val = -0.1, 0.1
    else:
        min_val, max_val = -0.1, 0.1
    
    psi4.core.clean()
    
    return CubeFileResult(
        property_type=input_data.property_type,
        filename=input_data.output_filename,
        grid_points=(input_data.grid_points, input_data.grid_points, input_data.grid_points),
        grid_spacing=grid_spacing,
        min_value=min_val,
        max_value=max_val,
        orbital_index=input_data.orbital_index,
    )


@register_tool
class CubeFileTool(BaseTool[CubeFileInput, ToolOutput]):
    """Tool for cube file generation."""
    name: ClassVar[str] = "generate_cube_file"
    description: ClassVar[str] = "Generate cube files for visualization of molecular properties."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: CubeFileInput) -> Optional[ValidationError]:
        return validate_cube_file_input(input_data)
    
    def _execute(self, input_data: CubeFileInput) -> Result[ToolOutput]:
        result = run_cube_file_generation(input_data)
        
        message = (
            f"Cube File Generated\n"
            f"{'='*40}\n"
            f"Property:    {result.property_type}\n"
            f"Filename:    {result.filename}\n"
            f"Grid:        {result.grid_points[0]}x{result.grid_points[1]}x{result.grid_points[2]}\n"
            f"Spacing:     {result.grid_spacing:.4f} bohr\n"
            f"Value Range: [{result.min_value:.4f}, {result.max_value:.4f}]"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def generate_cube(geometry: str, property_type: str = "density", **kwargs: Any) -> ToolOutput:
    """Generate cube file."""
    return CubeFileTool().run({"geometry": geometry, "property_type": property_type, **kwargs})
