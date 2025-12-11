"""CISDT Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class CISDTToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class CISDTTool(BaseTool[CISDTToolInput, ToolOutput]):
    """CISDT - CI with Singles, Doubles, and Triples."""
    name: ClassVar[str] = "calculate_cisdt"
    description: ClassVar[str] = "Calculate CISDT energy."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CISDTToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            energy = psi4.energy(f"cisdt/{input_data.basis}", molecule=mol)
            data = {"cisdt_energy": float(energy), "basis": input_data.basis, "method": "CISDT"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CISDT: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CISDT_ERROR", message=str(e)))

def calculate_cisdt(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return CISDTTool().run({"geometry": geometry, "basis": basis, **kwargs})
