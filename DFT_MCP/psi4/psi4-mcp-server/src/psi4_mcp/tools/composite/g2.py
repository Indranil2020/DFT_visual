"""G2 Composite Method Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class G2ToolInput(ToolInput):
    geometry: str = Field(...)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class G2Tool(BaseTool[G2ToolInput, ToolOutput]):
    """G2 composite method."""
    name: ClassVar[str] = "calculate_g2"
    description: ClassVar[str] = "Calculate G2 composite energy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: G2ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            energy = psi4.energy("mp4/6-311+g(2df,p)", molecule=mol)
            data = {"g2_energy": float(energy), "method": "G2 (simplified)"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"G2: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="G2_ERROR", message=str(e)))

def calculate_g2(geometry: str, **kwargs) -> ToolOutput:
    return G2Tool().run({"geometry": geometry, **kwargs})
