"""FCI Tool - Full Configuration Interaction."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class FCIToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="sto-3g", description="Small basis recommended for FCI")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    num_roots: int = Field(default=1)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)

@register_tool
class FCITool(BaseTool[FCIToolInput, ToolOutput]):
    """FCI - Full CI, exact within basis set. Exponential scaling."""
    name: ClassVar[str] = "calculate_fci"
    description: ClassVar[str] = "Calculate FCI energy. Exact but scales exponentially."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: FCIToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis, "num_roots": input_data.num_roots})
            energy = psi4.energy(f"fci/{input_data.basis}", molecule=mol)
            data = {"fci_energy": float(energy), "basis": input_data.basis, "method": "FCI", 
                    "note": "Exact correlation within basis set"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"FCI: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="FCI_ERROR", message=str(e)))

def calculate_fci(geometry: str, basis: str = "sto-3g", **kwargs) -> ToolOutput:
    return FCITool().run({"geometry": geometry, "basis": basis, **kwargs})
