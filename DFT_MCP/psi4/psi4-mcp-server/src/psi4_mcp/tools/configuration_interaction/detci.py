"""DETCI Tool - Determinant CI."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class DETCIToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    ci_type: str = Field(default="cisd", description="CI type: cis, cisd, cisdt, etc.")
    num_roots: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class DETCITool(BaseTool[DETCIToolInput, ToolOutput]):
    """DETCI - General determinant-based CI."""
    name: ClassVar[str] = "calculate_detci"
    description: ClassVar[str] = "Calculate general determinant CI."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: DETCIToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({
                "basis": input_data.basis,
                "freeze_core": input_data.freeze_core,
                "num_roots": input_data.num_roots,
            })
            energy = psi4.energy(f"detci/{input_data.basis}", molecule=mol)
            data = {"detci_energy": float(energy), "ci_type": input_data.ci_type, "basis": input_data.basis}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"DETCI: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="DETCI_ERROR", message=str(e)))

def calculate_detci(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return DETCITool().run({"geometry": geometry, "basis": basis, **kwargs})
