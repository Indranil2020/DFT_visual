"""SAPT Analysis Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SAPTAnalysisToolInput(ToolInput):
    electrostatics: float = Field(...)
    exchange: float = Field(...)
    induction: float = Field(...)
    dispersion: float = Field(...)

@register_tool
class SAPTAnalysisTool(BaseTool[SAPTAnalysisToolInput, ToolOutput]):
    """Analyze SAPT components to characterize interaction type."""
    name: ClassVar[str] = "analyze_sapt"
    description: ClassVar[str] = "Analyze SAPT energy components."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SAPTAnalysisToolInput) -> Result[ToolOutput]:
        total = input_data.electrostatics + input_data.exchange + input_data.induction + input_data.dispersion
        attractive = input_data.electrostatics + input_data.induction + input_data.dispersion
        
        # Determine interaction type
        if abs(input_data.electrostatics) > abs(input_data.dispersion) * 2:
            interaction_type = "electrostatic-dominated"
        elif abs(input_data.dispersion) > abs(input_data.electrostatics) * 2:
            interaction_type = "dispersion-dominated"
        else:
            interaction_type = "mixed"
        
        # Calculate percentages
        total_attr = abs(input_data.electrostatics) + abs(input_data.induction) + abs(input_data.dispersion)
        data = {
            "total_interaction": total,
            "interaction_type": interaction_type,
            "binding": "favorable" if total < 0 else "unfavorable",
            "percent_electrostatic": abs(input_data.electrostatics) / total_attr * 100 if total_attr else 0,
            "percent_induction": abs(input_data.induction) / total_attr * 100 if total_attr else 0,
            "percent_dispersion": abs(input_data.dispersion) / total_attr * 100 if total_attr else 0,
        }
        return Result.success(ToolOutput(success=True, message=f"Interaction: {interaction_type}", data=data))

def analyze_sapt(electrostatics: float, exchange: float, induction: float, dispersion: float) -> ToolOutput:
    return SAPTAnalysisTool().run({
        "electrostatics": electrostatics, "exchange": exchange,
        "induction": induction, "dispersion": dispersion
    })
