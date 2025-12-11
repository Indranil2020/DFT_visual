"""CISD Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class CISDToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class CISDTool(BaseTool[CISDToolInput, ToolOutput]):
    """CISD - Configuration Interaction Singles and Doubles."""
    name: ClassVar[str] = "calculate_cisd"
    description: ClassVar[str] = "Calculate CISD energy."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CISDToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            energy = psi4.energy(f"cisd/{input_data.basis}", molecule=mol)
            data = {"cisd_energy": float(energy), "basis": input_data.basis, "method": "CISD"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CISD: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CISD_ERROR", message=str(e)))

def calculate_cisd(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return CISDTool().run({"geometry": geometry, "basis": basis, **kwargs})
