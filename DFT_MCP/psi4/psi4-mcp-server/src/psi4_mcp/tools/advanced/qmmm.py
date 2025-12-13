"""QM/MM Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class QMMMToolInput(ToolInput):
    qm_geometry: str = Field(...)
    mm_charges: list[tuple[float, float, float, float]] = Field(default=[], description="(x, y, z, charge) for MM atoms")
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class QMMMTool(BaseTool[QMMMToolInput, ToolOutput]):
    """QM/MM with external point charges."""
    name: ClassVar[str] = "calculate_qmmm"
    description: ClassVar[str] = "Calculate QM energy with MM point charges."
    category: ClassVar[ToolCategory] = ToolCategory.MULTISCALE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: QMMMToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.qm_geometry}")
            
            # Add external charges
            if input_data.mm_charges:
                charges = [[c[3], c[0], c[1], c[2]] for c in input_data.mm_charges]
                psi4.QMMM().addChargeAngstrom(charges)
            
            psi4.set_options({"basis": input_data.basis})
            energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
            
            data = {
                "qm_mm_energy": float(energy),
                "n_mm_charges": len(input_data.mm_charges),
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"QM/MM: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="QMMM_ERROR", message=str(e)))

def calculate_qmmm(qm_geometry: str, mm_charges: list = [], **kwargs) -> ToolOutput:
    return QMMMTool().run({"qm_geometry": qm_geometry, "mm_charges": mm_charges, **kwargs})
