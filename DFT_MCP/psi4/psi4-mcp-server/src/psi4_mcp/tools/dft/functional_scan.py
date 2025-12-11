"""Functional Scan Tool - Compare DFT functionals."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

COMMON_FUNCTIONALS = ["svwn", "blyp", "pbe", "b3lyp", "pbe0", "m06-2x", "wb97x-d"]

class FunctionalScanToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    functionals: list[str] = Field(default=COMMON_FUNCTIONALS)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class FunctionalScanTool(BaseTool[FunctionalScanToolInput, ToolOutput]):
    """Compare energies across multiple DFT functionals."""
    name: ClassVar[str] = "scan_functionals"
    description: ClassVar[str] = "Compare energies from multiple DFT functionals."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: FunctionalScanToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            results = {}
            for func in input_data.functionals:
                try:
                    energy = psi4.energy(f"{func}/{input_data.basis}", molecule=mol)
                    results[func] = float(energy)
                except Exception as e:
                    results[func] = f"ERROR: {str(e)}"
                psi4.core.clean_variables()
            
            # Find min/max
            valid = {k: v for k, v in results.items() if isinstance(v, float)}
            spread = max(valid.values()) - min(valid.values()) if valid else 0
            
            data = {
                "energies": results,
                "basis": input_data.basis,
                "energy_spread_hartree": spread,
                "energy_spread_kcal": spread * 627.509,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Scanned {len(results)} functionals", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="FUNC_SCAN_ERROR", message=str(e)))

def scan_functionals(geometry: str, **kwargs) -> ToolOutput:
    return FunctionalScanTool().run({"geometry": geometry, **kwargs})
