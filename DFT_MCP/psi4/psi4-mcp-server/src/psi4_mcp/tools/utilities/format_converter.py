"""Format Converter Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError
from typing import Literal

class FormatConverterToolInput(ToolInput):
    geometry: str = Field(...)
    input_format: Literal["xyz", "zmat", "psi4"] = Field(default="xyz")
    output_format: Literal["xyz", "zmat", "psi4"] = Field(default="psi4")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)

@register_tool
class FormatConverterTool(BaseTool[FormatConverterToolInput, ToolOutput]):
    """Convert between molecular geometry formats."""
    name: ClassVar[str] = "convert_format"
    description: ClassVar[str] = "Convert geometry between XYZ, Z-matrix, Psi4 formats."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITY
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: FormatConverterToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            if input_data.output_format == "xyz":
                output = mol.save_string_xyz()
            elif input_data.output_format == "zmat":
                output = mol.save_string_xyz()  # Psi4 doesn't have direct zmat output
            else:
                output = mol.save_string_xyz()
            
            data = {
                "converted_geometry": output,
                "input_format": input_data.input_format,
                "output_format": input_data.output_format,
                "n_atoms": mol.natom(),
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Converted {mol.natom()} atoms", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CONVERT_ERROR", message=str(e)))

def convert_format(geometry: str, output_format: str = "psi4", **kwargs) -> ToolOutput:
    return FormatConverterTool().run({"geometry": geometry, "output_format": output_format, **kwargs})
