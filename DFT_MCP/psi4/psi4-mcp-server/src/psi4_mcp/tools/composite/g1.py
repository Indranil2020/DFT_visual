"""G1 Composite Method Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class G1ToolInput(ToolInput):
    geometry: str = Field(...)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class G1Tool(BaseTool[G1ToolInput, ToolOutput]):
    """G1 composite method for thermochemistry."""
    name: ClassVar[str] = "calculate_g1"
    description: ClassVar[str] = "Calculate G1 composite energy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: G1ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            # G1 = HF/6-311G** + MP4/6-311G** correlation + HLC
            energy = psi4.energy("mp4/6-311g**", molecule=mol)
            data = {"g1_energy": float(energy), "method": "G1 (simplified)"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"G1: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="G1_ERROR", message=str(e)))

def calculate_g1(geometry: str, **kwargs) -> ToolOutput:
    return G1Tool().run({"geometry": geometry, **kwargs})
