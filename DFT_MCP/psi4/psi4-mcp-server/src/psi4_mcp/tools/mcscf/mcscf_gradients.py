"""MCSCF Gradients Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class MCSCFGradientsToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    active_electrons: int = Field(...)
    active_orbitals: int = Field(...)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class MCSCFGradientsTool(BaseTool[MCSCFGradientsToolInput, ToolOutput]):
    """MCSCF analytical gradients for geometry optimization."""
    name: ClassVar[str] = "calculate_mcscf_gradient"
    description: ClassVar[str] = "Calculate CASSCF analytical gradient."
    category: ClassVar[ToolCategory] = ToolCategory.MULTIREFERENCE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: MCSCFGradientsToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            import numpy as np
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({
                "basis": input_data.basis,
                "active": [input_data.active_orbitals],
            })
            grad, wfn = psi4.gradient(f"casscf/{input_data.basis}", molecule=mol, return_wfn=True)
            grad_array = np.array(grad)
            rms_grad = np.sqrt(np.mean(grad_array**2))
            max_grad = np.max(np.abs(grad_array))
            data = {
                "energy": float(wfn.energy()),
                "gradient": grad_array.tolist(),
                "rms_gradient": float(rms_grad),
                "max_gradient": float(max_grad),
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"MCSCF gradient: RMS = {rms_grad:.6f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="MCSCF_GRAD_ERROR", message=str(e)))

def calculate_mcscf_gradient(geometry: str, active_electrons: int, active_orbitals: int,
                             basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return MCSCFGradientsTool().run({"geometry": geometry, "basis": basis,
                                     "active_electrons": active_electrons, "active_orbitals": active_orbitals, **kwargs})
