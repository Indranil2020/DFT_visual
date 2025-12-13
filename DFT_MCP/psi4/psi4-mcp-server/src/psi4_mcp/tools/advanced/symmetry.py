"""Symmetry Analysis Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SymmetryToolInput(ToolInput):
    geometry: str = Field(...)
    tolerance: float = Field(default=0.01, description="Symmetry detection tolerance")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)

@register_tool
class SymmetryTool(BaseTool[SymmetryToolInput, ToolOutput]):
    """Analyze molecular point group symmetry."""
    name: ClassVar[str] = "analyze_symmetry"
    description: ClassVar[str] = "Determine molecular point group."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SymmetryToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            point_group = mol.point_group().symbol()
            
            data = {
                "point_group": point_group,
                "n_atoms": mol.natom(),
                "tolerance": input_data.tolerance,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Point group: {point_group}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SYMMETRY_ERROR", message=str(e)))

def analyze_symmetry(geometry: str, **kwargs) -> ToolOutput:
    return SymmetryTool().run({"geometry": geometry, **kwargs})
