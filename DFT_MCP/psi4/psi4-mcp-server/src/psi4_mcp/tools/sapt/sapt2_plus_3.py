"""SAPT2+(3) Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SAPT2Plus3ToolInput(ToolInput):
    dimer_geometry: str = Field(...)
    basis: str = Field(default="aug-cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)

@register_tool
class SAPT2Plus3Tool(BaseTool[SAPT2Plus3ToolInput, ToolOutput]):
    """SAPT2+(3) - Highest accuracy SAPT with third-order terms."""
    name: ClassVar[str] = "calculate_sapt2_plus_3"
    description: ClassVar[str] = "Calculate SAPT2+(3) with third-order corrections."
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SAPT2Plus3ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.dimer_geometry}")
            psi4.set_options({"basis": input_data.basis})
            energy = psi4.energy(f"sapt2+(3)/{input_data.basis}", molecule=mol)
            
            HARTREE_TO_KCAL = 627.509
            total = psi4.variable("SAPT TOTAL ENERGY")
            data = {
                "sapt2_plus_3_total": float(total) * HARTREE_TO_KCAL,
                "units": "kcal/mol",
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"SAPT2+(3): {float(total)*HARTREE_TO_KCAL:.2f} kcal/mol", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SAPT2PLUS3_ERROR", message=str(e)))

def calculate_sapt2_plus_3(dimer_geometry: str, basis: str = "aug-cc-pvdz", **kwargs) -> ToolOutput:
    return SAPT2Plus3Tool().run({"dimer_geometry": dimer_geometry, "basis": basis, **kwargs})
