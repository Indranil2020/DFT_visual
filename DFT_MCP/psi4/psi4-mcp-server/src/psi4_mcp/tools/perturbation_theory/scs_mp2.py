"""SCS-MP2 (Spin-Component Scaled MP2) Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SCSMP2ToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    scale_os: float = Field(default=1.2, description="Opposite-spin scaling factor")
    scale_ss: float = Field(default=0.33, description="Same-spin scaling factor")
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class SCSMP2Tool(BaseTool[SCSMP2ToolInput, ToolOutput]):
    """SCS-MP2 improves MP2 accuracy with empirical spin-component scaling."""
    name: ClassVar[str] = "calculate_scs_mp2"
    description: ClassVar[str] = "Calculate SCS-MP2 energy with spin-component scaling."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SCSMP2ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({
                "basis": input_data.basis,
                "freeze_core": input_data.freeze_core,
                "mp2_os_scale": input_data.scale_os,
                "mp2_ss_scale": input_data.scale_ss,
            })
            # Run MP2 to get components
            psi4.energy(f"mp2/{input_data.basis}", molecule=mol)
            
            hf = psi4.variable("HF TOTAL ENERGY")
            ss = psi4.variable("MP2 SAME-SPIN CORRELATION ENERGY")
            os = psi4.variable("MP2 OPPOSITE-SPIN CORRELATION ENERGY")
            
            # Apply SCS scaling
            scs_corr = input_data.scale_os * float(os) + input_data.scale_ss * float(ss)
            scs_total = float(hf) + scs_corr
            
            data = {
                "scs_mp2_energy": scs_total,
                "hf_energy": float(hf),
                "scs_correlation": scs_corr,
                "scale_os": input_data.scale_os,
                "scale_ss": input_data.scale_ss,
                "same_spin_raw": float(ss),
                "opposite_spin_raw": float(os),
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"SCS-MP2: E = {scs_total:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SCSMP2_ERROR", message=str(e)))

def calculate_scs_mp2(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return SCSMP2Tool().run({"geometry": geometry, "basis": basis, **kwargs})
