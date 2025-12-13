"""MP2.5 Tool - Average of MP2 and MP3."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class MP25ToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class MP25Tool(BaseTool[MP25ToolInput, ToolOutput]):
    """MP2.5 = (MP2 + MP3) / 2. Good error cancellation."""
    name: ClassVar[str] = "calculate_mp2_5"
    description: ClassVar[str] = "Calculate MP2.5 energy (average of MP2 and MP3)."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: MP25ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            energy = psi4.energy(f"mp2.5/{input_data.basis}", molecule=mol)
            mp2 = psi4.variable("MP2 TOTAL ENERGY")
            mp3 = psi4.variable("MP3 TOTAL ENERGY")
            data = {
                "mp2_5_energy": float(energy),
                "mp2_energy": float(mp2),
                "mp3_energy": float(mp3),
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"MP2.5: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="MP25_ERROR", message=str(e)))

def calculate_mp2_5(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return MP25Tool().run({"geometry": geometry, "basis": basis, **kwargs})
