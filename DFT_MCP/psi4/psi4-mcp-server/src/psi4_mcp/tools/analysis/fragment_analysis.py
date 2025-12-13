"""Fragment Analysis Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class FragmentToolInput(ToolInput):
    dimer_geometry: str = Field(..., description="Geometry with -- separator")
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class FragmentTool(BaseTool[FragmentToolInput, ToolOutput]):
    """Analyze system by fragments (BSSE, interaction energy)."""
    name: ClassVar[str] = "analyze_fragments"
    description: ClassVar[str] = "Fragment-based analysis with BSSE correction."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: FragmentToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.dimer_geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            # Counterpoise correction
            e_cp = psi4.energy(f"{input_data.method}/{input_data.basis}", bsse_type="cp", molecule=mol)
            e_nocp = psi4.energy(f"{input_data.method}/{input_data.basis}", bsse_type="nocp", molecule=mol)
            
            bsse = float(e_nocp) - float(e_cp)
            
            HARTREE_TO_KCAL = 627.509
            data = {
                "interaction_cp": float(e_cp) * HARTREE_TO_KCAL,
                "interaction_nocp": float(e_nocp) * HARTREE_TO_KCAL,
                "bsse": bsse * HARTREE_TO_KCAL,
                "units": "kcal/mol",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"BSSE: {bsse*HARTREE_TO_KCAL:.2f} kcal/mol", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="FRAGMENT_ERROR", message=str(e)))

def analyze_fragments(dimer_geometry: str, **kwargs) -> ToolOutput:
    return FragmentTool().run({"dimer_geometry": dimer_geometry, **kwargs})
