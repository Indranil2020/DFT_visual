"""Range-Separated Hybrid Functional Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

RANGE_SEPARATED = {
    "cam-b3lyp": {"omega": 0.33, "alpha": 0.19, "beta": 0.46},
    "lc-wpbe": {"omega": 0.40, "alpha": 0.0, "beta": 1.0},
    "wb97x": {"omega": 0.30, "alpha": 0.157706, "beta": 0.842294},
    "wb97x-d": {"omega": 0.20, "alpha": 0.222036, "beta": 0.777964},
}

class RangeSeparatedToolInput(ToolInput):
    geometry: str = Field(...)
    functional: str = Field(default="cam-b3lyp")
    basis: str = Field(default="cc-pvdz")
    omega: float = Field(default=None, description="Override range-separation parameter")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class RangeSeparatedTool(BaseTool[RangeSeparatedToolInput, ToolOutput]):
    """Range-separated hybrid DFT for charge-transfer and Rydberg states."""
    name: ClassVar[str] = "calculate_range_separated"
    description: ClassVar[str] = "Calculate with range-separated hybrid functional."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: RangeSeparatedToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            options = {"basis": input_data.basis}
            if input_data.omega is not None:
                options["omega"] = input_data.omega
            psi4.set_options(options)
            
            energy = psi4.energy(f"{input_data.functional}/{input_data.basis}", molecule=mol)
            
            params = RANGE_SEPARATED.get(input_data.functional.lower(), {})
            data = {
                "total_energy": float(energy),
                "functional": input_data.functional,
                "parameters": params,
                "custom_omega": input_data.omega,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"{input_data.functional}: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="RSH_ERROR", message=str(e)))

def calculate_range_separated(geometry: str, functional: str = "cam-b3lyp", **kwargs) -> ToolOutput:
    return RangeSeparatedTool().run({"geometry": geometry, "functional": functional, **kwargs})
