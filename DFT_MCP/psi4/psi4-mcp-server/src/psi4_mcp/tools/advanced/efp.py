"""EFP (Effective Fragment Potential) Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class EFPToolInput(ToolInput):
    qm_geometry: str = Field(..., description="QM region geometry")
    efp_fragments: list[str] = Field(default=[], description="EFP fragment specifications")
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class EFPTool(BaseTool[EFPToolInput, ToolOutput]):
    """EFP for explicit solvation with fragment potentials."""
    name: ClassVar[str] = "calculate_efp"
    description: ClassVar[str] = "Calculate with EFP fragment potentials."
    category: ClassVar[ToolCategory] = ToolCategory.SOLVATION
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: EFPToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            
            # Build geometry with EFP fragments
            geom_str = f"{input_data.charge} {input_data.multiplicity}\n{input_data.qm_geometry}"
            for frag in input_data.efp_fragments:
                geom_str += f"\n--\nefp {frag}"
            
            mol = psi4.geometry(geom_str)
            psi4.set_options({"basis": input_data.basis})
            
            energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
            
            data = {"total_energy": float(energy), "n_efp_fragments": len(input_data.efp_fragments)}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"EFP: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="EFP_ERROR", message=str(e)))

def calculate_efp(qm_geometry: str, efp_fragments: list = [], **kwargs) -> ToolOutput:
    return EFPTool().run({"qm_geometry": qm_geometry, "efp_fragments": efp_fragments, **kwargs})
