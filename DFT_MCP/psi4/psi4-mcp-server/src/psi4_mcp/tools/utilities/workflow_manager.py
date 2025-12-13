"""Workflow Manager Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError
from typing import Literal

class WorkflowToolInput(ToolInput):
    geometry: str = Field(...)
    workflow: Literal["opt_freq", "opt_prop", "full_analysis"] = Field(default="opt_freq")
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class WorkflowTool(BaseTool[WorkflowToolInput, ToolOutput]):
    """Run predefined calculation workflows."""
    name: ClassVar[str] = "run_workflow"
    description: ClassVar[str] = "Run workflow: opt_freq, opt_prop, or full_analysis."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITY
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: WorkflowToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_options({"basis": input_data.basis})
            
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            results = {}
            
            # Always optimize
            opt_energy = psi4.optimize(f"{input_data.method}/{input_data.basis}", molecule=mol)
            results["optimization"] = {"final_energy": float(opt_energy), "geometry": mol.save_string_xyz()}
            
            if input_data.workflow in ["opt_freq", "full_analysis"]:
                freq_energy, wfn = psi4.frequency(f"{input_data.method}/{input_data.basis}", return_wfn=True, molecule=mol)
                vibinfo = wfn.frequency_analysis
                results["frequencies"] = {"freqs": list(vibinfo['omega'].to_array())}
            
            if input_data.workflow in ["opt_prop", "full_analysis"]:
                psi4.oeprop(wfn if 'wfn' in dir() else None, "DIPOLE", "MULLIKEN_CHARGES")
                results["properties"] = {"computed": True}
            
            data = {"workflow": input_data.workflow, "results": results}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Workflow {input_data.workflow} complete", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="WORKFLOW_ERROR", message=str(e)))

def run_workflow(geometry: str, workflow: str = "opt_freq", **kwargs) -> ToolOutput:
    return WorkflowTool().run({"geometry": geometry, "workflow": workflow, **kwargs})
