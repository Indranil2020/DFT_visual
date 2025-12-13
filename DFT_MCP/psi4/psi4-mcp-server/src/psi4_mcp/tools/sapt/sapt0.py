"""SAPT0 Tool - Fastest SAPT level."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SAPT0ToolInput(ToolInput):
    dimer_geometry: str = Field(..., description="Dimer geometry with -- separator between monomers")
    basis: str = Field(default="jun-cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class SAPT0Tool(BaseTool[SAPT0ToolInput, ToolOutput]):
    """SAPT0 - Fastest SAPT, HF-level monomers."""
    name: ClassVar[str] = "calculate_sapt0"
    description: ClassVar[str] = "Calculate SAPT0 interaction energy decomposition."
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SAPT0ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.dimer_geometry}")
            psi4.set_options({"basis": input_data.basis})
            energy = psi4.energy(f"sapt0/{input_data.basis}", molecule=mol)
            
            # Extract components
            elst = psi4.variable("SAPT ELST ENERGY")
            exch = psi4.variable("SAPT EXCH ENERGY")
            ind = psi4.variable("SAPT IND ENERGY")
            disp = psi4.variable("SAPT DISP ENERGY")
            total = psi4.variable("SAPT TOTAL ENERGY")
            
            HARTREE_TO_KCAL = 627.509
            data = {
                "sapt0_total": float(total) * HARTREE_TO_KCAL,
                "electrostatics": float(elst) * HARTREE_TO_KCAL,
                "exchange": float(exch) * HARTREE_TO_KCAL,
                "induction": float(ind) * HARTREE_TO_KCAL,
                "dispersion": float(disp) * HARTREE_TO_KCAL,
                "units": "kcal/mol",
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"SAPT0: {float(total)*HARTREE_TO_KCAL:.2f} kcal/mol", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SAPT0_ERROR", message=str(e)))

def calculate_sapt0(dimer_geometry: str, basis: str = "jun-cc-pvdz", **kwargs) -> ToolOutput:
    return SAPT0Tool().run({"dimer_geometry": dimer_geometry, "basis": basis, **kwargs})
