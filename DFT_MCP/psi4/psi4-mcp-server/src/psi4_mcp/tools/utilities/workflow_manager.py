"""
Workflow Manager Tool.

Orchestrates multi-step computational workflows combining
different calculation types in sequence.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
import logging
import time

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


WORKFLOW_TEMPLATES = {
    "optimization": ["energy", "optimize", "energy"],
    "thermochemistry": ["optimize", "frequency"],
    "full_characterization": ["optimize", "frequency", "properties"],
    "reaction_energy": ["optimize", "energy"],
    "vertical_excitation": ["optimize", "tddft"],
}


@dataclass
class WorkflowStep:
    """Single step in a workflow."""
    step_number: int
    step_type: str
    method: str
    basis: str
    status: str
    energy: Optional[float]
    runtime_seconds: float
    output_data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number, "type": self.step_type,
            "method": self.method, "basis": self.basis,
            "status": self.status, "energy_hartree": self.energy,
            "runtime_seconds": self.runtime_seconds, "data": self.output_data,
        }


@dataclass
class WorkflowResult:
    """Workflow execution results."""
    workflow_name: str
    steps: List[WorkflowStep]
    final_geometry: Optional[str]
    final_energy: float
    total_runtime: float
    all_completed: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow": self.workflow_name,
            "steps": [s.to_dict() for s in self.steps],
            "final_geometry": self.final_geometry,
            "final_energy_hartree": self.final_energy,
            "total_runtime_seconds": self.total_runtime,
            "all_completed": self.all_completed,
        }


class WorkflowInput(ToolInput):
    """Input for workflow execution."""
    geometry: str = Field(..., description="Initial geometry")
    workflow: str = Field(default="thermochemistry",
        description="Workflow: optimization, thermochemistry, full_characterization, reaction_energy")
    
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    custom_steps: Optional[List[str]] = Field(default=None, description="Custom step sequence")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_workflow_input(input_data: WorkflowInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.workflow not in WORKFLOW_TEMPLATES and not input_data.custom_steps:
        return ValidationError(field="workflow",
                              message=f"Unknown workflow. Use: {', '.join(WORKFLOW_TEMPLATES.keys())}")
    return None


def run_workflow_step(mol, step_type: str, method: str, basis: str) -> tuple:
    """Run a single workflow step."""
    import psi4
    
    start = time.time()
    output_data = {}
    
    if step_type == "energy":
        energy = psi4.energy(f"{method}/{basis}", molecule=mol)
        output_data["energy"] = energy
        
    elif step_type == "optimize":
        energy = psi4.optimize(f"{method}/{basis}", molecule=mol)
        output_data["energy"] = energy
        output_data["geometry"] = mol.save_string_xyz()
        
    elif step_type == "frequency":
        energy, wfn = psi4.frequency(f"{method}/{basis}", return_wfn=True, molecule=mol)
        output_data["energy"] = energy
        output_data["zpe"] = psi4.variable("ZPVE")
        
    elif step_type == "properties":
        energy, wfn = psi4.energy(f"{method}/{basis}", return_wfn=True, molecule=mol)
        psi4.oeprop(wfn, "DIPOLE")
        output_data["energy"] = energy
        output_data["dipole"] = psi4.variable("SCF DIPOLE")
        
    elif step_type == "tddft":
        psi4.set_options({"roots_per_irrep": [5]})
        energy, wfn = psi4.energy(f"td-{method}/{basis}", return_wfn=True, molecule=mol)
        output_data["ground_energy"] = energy
    
    else:
        energy = psi4.energy(f"{method}/{basis}", molecule=mol)
        output_data["energy"] = energy
    
    runtime = time.time() - start
    return output_data.get("energy", 0), runtime, output_data


def run_workflow(input_data: WorkflowInput) -> WorkflowResult:
    """Execute workflow."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_workflow.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    steps_to_run = input_data.custom_steps or WORKFLOW_TEMPLATES[input_data.workflow]
    
    logger.info(f"Running workflow: {input_data.workflow}")
    
    steps = []
    total_runtime = 0.0
    final_energy = 0.0
    final_geometry = None
    all_completed = True
    
    for i, step_type in enumerate(steps_to_run):
        logger.info(f"  Step {i+1}/{len(steps_to_run)}: {step_type}")
        
        energy, runtime, output_data = run_workflow_step(
            mol, step_type, input_data.method, input_data.basis
        )
        
        total_runtime += runtime
        final_energy = energy
        
        if "geometry" in output_data:
            final_geometry = output_data["geometry"]
        
        steps.append(WorkflowStep(
            step_number=i+1, step_type=step_type,
            method=input_data.method, basis=input_data.basis,
            status="completed", energy=energy,
            runtime_seconds=runtime, output_data=output_data,
        ))
    
    psi4.core.clean()
    
    return WorkflowResult(
        workflow_name=input_data.workflow,
        steps=steps,
        final_geometry=final_geometry,
        final_energy=final_energy,
        total_runtime=total_runtime,
        all_completed=all_completed,
    )


@register_tool
class WorkflowManagerTool(BaseTool[WorkflowInput, ToolOutput]):
    """Tool for workflow management."""
    name: ClassVar[str] = "run_workflow"
    description: ClassVar[str] = "Execute multi-step computational workflow."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITY
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: WorkflowInput) -> Optional[ValidationError]:
        return validate_workflow_input(input_data)
    
    def _execute(self, input_data: WorkflowInput) -> Result[ToolOutput]:
        result = run_workflow(input_data)
        
        step_lines = [f"  {s.step_number}. {s.step_type}: {s.energy:.10f} Eh ({s.runtime_seconds:.1f}s)"
                      for s in result.steps]
        message = (
            f"Workflow: {result.workflow_name}\n{'='*40}\n"
            + "\n".join(step_lines) + "\n"
            f"Final Energy: {result.final_energy:.10f} Eh\n"
            f"Total Runtime: {result.total_runtime:.2f}s"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def run_workflow_calc(geometry: str, workflow: str = "thermochemistry", **kwargs: Any) -> ToolOutput:
    """Execute workflow."""
    return WorkflowManagerTool().run({"geometry": geometry, "workflow": workflow, **kwargs})
