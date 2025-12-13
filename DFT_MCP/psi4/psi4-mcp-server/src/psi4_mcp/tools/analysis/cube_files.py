"""Cube File Generation Tool."""
from typing import Any, ClassVar, Literal
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class CubeFileToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    property_type: Literal["density", "esp", "mo"] = Field(default="density")
    orbital_indices: list[int] = Field(default=[], description="MO indices for mo type")
    grid_spacing: float = Field(default=0.2, description="Grid spacing in Bohr")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class CubeFileTool(BaseTool[CubeFileToolInput, ToolOutput]):
    """Generate cube files for visualization."""
    name: ClassVar[str] = "generate_cube"
    description: ClassVar[str] = "Generate cube file for density/ESP/orbital visualization."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CubeFileToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis, "cubeprop_tasks": [input_data.property_type]})
            
            energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", return_wfn=True, molecule=mol)
            psi4.cubeprop(wfn)
            
            data = {
                "energy": float(energy),
                "property": input_data.property_type,
                "grid_spacing": input_data.grid_spacing,
                "files_generated": f"{input_data.property_type}.cube",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Cube file generated for {input_data.property_type}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CUBE_ERROR", message=str(e)))

def generate_cube(geometry: str, property_type: str = "density", **kwargs) -> ToolOutput:
    return CubeFileTool().run({"geometry": geometry, "property_type": property_type, **kwargs})
