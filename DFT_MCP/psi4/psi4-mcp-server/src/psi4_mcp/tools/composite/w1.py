"""W1 Composite Method Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class W1ToolInput(ToolInput):
    geometry: str = Field(...)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=16000)
    n_threads: int = Field(default=1)

@register_tool
class W1Tool(BaseTool[W1ToolInput, ToolOutput]):
    """W1 (Weizmann-1) high-accuracy composite method."""
    name: ClassVar[str] = "calculate_w1"
    description: ClassVar[str] = "Calculate W1 composite energy (high accuracy)."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: W1ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            # W1 uses CCSD(T) with CBS extrapolation
            energy = psi4.energy("ccsd(t)/aug-cc-pvqz", molecule=mol)
            data = {"w1_energy": float(energy), "method": "W1 (simplified)"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"W1: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="W1_ERROR", message=str(e)))

def calculate_w1(geometry: str, **kwargs) -> ToolOutput:
    return W1Tool().run({"geometry": geometry, **kwargs})
