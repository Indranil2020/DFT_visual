"""Population Analysis Tool."""
from typing import Any, ClassVar, Literal
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class PopulationToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    analysis_type: Literal["mulliken", "lowdin", "all"] = Field(default="all")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class PopulationTool(BaseTool[PopulationToolInput, ToolOutput]):
    """Perform population analysis (Mulliken, Löwdin)."""
    name: ClassVar[str] = "analyze_population"
    description: ClassVar[str] = "Compute atomic populations and charges."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: PopulationToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            import numpy as np
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", return_wfn=True, molecule=mol)
            
            data = {"energy": float(energy)}
            
            if input_data.analysis_type in ["mulliken", "all"]:
                psi4.oeprop(wfn, "MULLIKEN_CHARGES")
                data["mulliken_charges"] = np.array(wfn.atomic_point_charges()).tolist()
            
            if input_data.analysis_type in ["lowdin", "all"]:
                psi4.oeprop(wfn, "LOWDIN_CHARGES")
                try:
                    data["lowdin_charges"] = np.array(wfn.atomic_point_charges()).tolist()
                except:
                    pass
            
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message="Population analysis complete", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="POP_ERROR", message=str(e)))

def analyze_population(geometry: str, **kwargs) -> ToolOutput:
    return PopulationTool().run({"geometry": geometry, **kwargs})
