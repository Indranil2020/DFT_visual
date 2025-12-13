"""SAPT2+ Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SAPT2PlusToolInput(ToolInput):
    dimer_geometry: str = Field(...)
    basis: str = Field(default="aug-cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)

@register_tool
class SAPT2PlusTool(BaseTool[SAPT2PlusToolInput, ToolOutput]):
    """SAPT2+ - SAPT2 with improved dispersion."""
    name: ClassVar[str] = "calculate_sapt2_plus"
    description: ClassVar[str] = "Calculate SAPT2+ with improved dispersion."
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SAPT2PlusToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.dimer_geometry}")
            psi4.set_options({"basis": input_data.basis})
            energy = psi4.energy(f"sapt2+/{input_data.basis}", molecule=mol)
            
            HARTREE_TO_KCAL = 627.509
            total = psi4.variable("SAPT TOTAL ENERGY")
            data = {
                "sapt2_plus_total": float(total) * HARTREE_TO_KCAL,
                "electrostatics": float(psi4.variable("SAPT ELST ENERGY")) * HARTREE_TO_KCAL,
                "exchange": float(psi4.variable("SAPT EXCH ENERGY")) * HARTREE_TO_KCAL,
                "induction": float(psi4.variable("SAPT IND ENERGY")) * HARTREE_TO_KCAL,
                "dispersion": float(psi4.variable("SAPT DISP ENERGY")) * HARTREE_TO_KCAL,
                "units": "kcal/mol",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"SAPT2+: {float(total)*HARTREE_TO_KCAL:.2f} kcal/mol", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SAPT2PLUS_ERROR", message=str(e)))

def calculate_sapt2_plus(dimer_geometry: str, basis: str = "aug-cc-pvdz", **kwargs) -> ToolOutput:
    return SAPT2PlusTool().run({"dimer_geometry": dimer_geometry, "basis": basis, **kwargs})
