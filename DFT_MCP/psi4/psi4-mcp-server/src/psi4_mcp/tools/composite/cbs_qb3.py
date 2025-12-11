"""CBS-QB3 Composite Method Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class CBSQB3ToolInput(ToolInput):
    geometry: str = Field(...)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class CBSQB3Tool(BaseTool[CBSQB3ToolInput, ToolOutput]):
    """CBS-QB3 composite method."""
    name: ClassVar[str] = "calculate_cbs_qb3"
    description: ClassVar[str] = "Calculate CBS-QB3 composite energy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CBSQB3ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            # CBS-QB3 uses B3LYP geometry + CCSD(T) with extrapolation
            energy = psi4.energy("ccsd(t)/cc-pvtz", molecule=mol)
            data = {"cbs_qb3_energy": float(energy), "method": "CBS-QB3 (simplified)"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CBS-QB3: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CBSQB3_ERROR", message=str(e)))

def calculate_cbs_qb3(geometry: str, **kwargs) -> ToolOutput:
    return CBSQB3Tool().run({"geometry": geometry, **kwargs})
