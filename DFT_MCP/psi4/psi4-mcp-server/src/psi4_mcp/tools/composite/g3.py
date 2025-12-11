"""G3 Composite Method Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class G3ToolInput(ToolInput):
    geometry: str = Field(...)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)

@register_tool
class G3Tool(BaseTool[G3ToolInput, ToolOutput]):
    """G3 composite method."""
    name: ClassVar[str] = "calculate_g3"
    description: ClassVar[str] = "Calculate G3 composite energy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: G3ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            energy = psi4.energy("ccsd(t)/cc-pvtz", molecule=mol)
            data = {"g3_energy": float(energy), "method": "G3 (simplified)"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"G3: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="G3_ERROR", message=str(e)))

def calculate_g3(geometry: str, **kwargs) -> ToolOutput:
    return G3Tool().run({"geometry": geometry, **kwargs})
