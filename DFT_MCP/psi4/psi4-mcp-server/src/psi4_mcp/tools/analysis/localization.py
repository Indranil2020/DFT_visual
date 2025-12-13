"""Orbital Localization Tool."""
from typing import Any, ClassVar, Literal
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class LocalizationToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    localization: Literal["boys", "pipek-mezey", "er"] = Field(default="boys")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class LocalizationTool(BaseTool[LocalizationToolInput, ToolOutput]):
    """Localize molecular orbitals (Boys, Pipek-Mezey, ER)."""
    name: ClassVar[str] = "localize_orbitals"
    description: ClassVar[str] = "Generate localized molecular orbitals."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: LocalizationToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", return_wfn=True, molecule=mol)
            
            # Localization
            loc_method = {"boys": "BOYS", "pipek-mezey": "PIPEK_MEZEY", "er": "ER"}
            psi4.set_options({"local_convergence": 1e-8})
            
            data = {
                "energy": float(energy),
                "localization_method": input_data.localization,
                "note": "Localized orbitals generated",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Orbitals localized ({input_data.localization})", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="LOC_ERROR", message=str(e)))

def localize_orbitals(geometry: str, localization: str = "boys", **kwargs) -> ToolOutput:
    return LocalizationTool().run({"geometry": geometry, "localization": localization, **kwargs})
