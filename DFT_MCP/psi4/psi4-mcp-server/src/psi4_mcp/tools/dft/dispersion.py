"""Dispersion Correction Tool."""
from typing import Any, ClassVar, Literal
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class DispersionToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    dispersion: Literal["d3", "d3bj", "d4"] = Field(default="d3bj")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class DispersionTool(BaseTool[DispersionToolInput, ToolOutput]):
    """DFT with empirical dispersion corrections (D3, D3BJ, D4)."""
    name: ClassVar[str] = "calculate_dispersion"
    description: ClassVar[str] = "Calculate DFT energy with dispersion correction."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: DispersionToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            method = f"{input_data.method}-{input_data.dispersion}"
            energy = psi4.energy(f"{method}/{input_data.basis}", molecule=mol)
            
            disp_corr = psi4.variable("DISPERSION CORRECTION ENERGY")
            dft_only = energy - float(disp_corr)
            
            data = {
                "total_energy": float(energy),
                "dft_energy": dft_only,
                "dispersion_correction": float(disp_corr),
                "method": method,
                "dispersion_type": input_data.dispersion,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"{method}: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="DISPERSION_ERROR", message=str(e)))

def calculate_dispersion(geometry: str, dispersion: str = "d3bj", **kwargs) -> ToolOutput:
    return DispersionTool().run({"geometry": geometry, "dispersion": dispersion, **kwargs})
