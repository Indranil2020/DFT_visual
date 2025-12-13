"""F-SAPT (Functional group SAPT) Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class FISAPTToolInput(ToolInput):
    dimer_geometry: str = Field(...)
    basis: str = Field(default="jun-cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    link_atoms: list[int] = Field(default=[], description="Link atom indices for functional groups")
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class FISAPTTool(BaseTool[FISAPTToolInput, ToolOutput]):
    """F-SAPT for functional group decomposition of interactions."""
    name: ClassVar[str] = "calculate_fisapt"
    description: ClassVar[str] = "Calculate F-SAPT functional group decomposition."
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: FISAPTToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.dimer_geometry}")
            psi4.set_options({"basis": input_data.basis})
            energy = psi4.energy(f"fisapt0/{input_data.basis}", molecule=mol)
            
            HARTREE_TO_KCAL = 627.509
            total = psi4.variable("SAPT TOTAL ENERGY")
            data = {
                "fisapt_total": float(total) * HARTREE_TO_KCAL,
                "units": "kcal/mol",
                "note": "Functional group partitioning available in output files",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"F-SAPT: {float(total)*HARTREE_TO_KCAL:.2f} kcal/mol", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="FISAPT_ERROR", message=str(e)))

def calculate_fisapt(dimer_geometry: str, basis: str = "jun-cc-pvdz", **kwargs) -> ToolOutput:
    return FISAPTTool().run({"dimer_geometry": dimer_geometry, "basis": basis, **kwargs})
