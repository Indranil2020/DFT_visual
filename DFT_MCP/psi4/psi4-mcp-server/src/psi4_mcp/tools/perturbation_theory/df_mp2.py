"""DF-MP2 (Density-Fitted MP2) Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class DFMP2ToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    aux_basis: str = Field(default="cc-pvdz-ri", description="Auxiliary basis for DF")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class DFMP2Tool(BaseTool[DFMP2ToolInput, ToolOutput]):
    """DF-MP2 uses density fitting for efficient integral evaluation. Much faster than conventional MP2."""
    name: ClassVar[str] = "calculate_df_mp2"
    description: ClassVar[str] = "Calculate DF-MP2 energy. Faster than conventional MP2."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: DFMP2ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({
                "basis": input_data.basis,
                "freeze_core": input_data.freeze_core,
                "df_basis_mp2": input_data.aux_basis,
            })
            energy = psi4.energy(f"df-mp2/{input_data.basis}", molecule=mol)
            mp2_corr = psi4.variable("MP2 CORRELATION ENERGY")
            data = {
                "df_mp2_energy": float(energy),
                "correlation_energy": float(mp2_corr),
                "basis": input_data.basis,
                "aux_basis": input_data.aux_basis,
                "method": "DF-MP2",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"DF-MP2: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="DFMP2_ERROR", message=str(e)))

def calculate_df_mp2(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return DFMP2Tool().run({"geometry": geometry, "basis": basis, **kwargs})
