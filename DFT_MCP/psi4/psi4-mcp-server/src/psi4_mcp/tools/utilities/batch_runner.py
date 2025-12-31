"""
Batch Calculation Runner Tool.

Executes multiple calculations in sequence with configurable
parameters for high-throughput computational chemistry.
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


@dataclass
class BatchJob:
    """Single job in a batch."""
    job_id: str
    geometry: str
    method: str
    basis: str
    status: str
    energy: Optional[float]
    runtime_seconds: float
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id, "method": self.method, "basis": self.basis,
            "status": self.status, "energy_hartree": self.energy,
            "runtime_seconds": self.runtime_seconds, "error": self.error_message,
        }


@dataclass
class BatchResult:
    """Batch calculation results."""
    jobs: List[BatchJob]
    n_completed: int
    n_failed: int
    total_runtime: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jobs": [j.to_dict() for j in self.jobs],
            "n_completed": self.n_completed,
            "n_failed": self.n_failed,
            "total_runtime_seconds": self.total_runtime,
            "average_runtime": self.total_runtime / len(self.jobs) if self.jobs else 0,
        }


class BatchRunnerInput(ToolInput):
    """Input for batch calculations."""
    geometries: List[str] = Field(..., description="List of geometries")
    job_ids: Optional[List[str]] = Field(default=None, description="Optional job identifiers")
    
    method: str = Field(default="hf", description="Method for all jobs")
    basis: str = Field(default="cc-pvdz", description="Basis for all jobs")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    calculation_type: str = Field(default="energy", description="energy, optimize, or frequency")
    
    stop_on_error: bool = Field(default=False)
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_batch_input(input_data: BatchRunnerInput) -> Optional[ValidationError]:
    if not input_data.geometries:
        return ValidationError(field="geometries", message="At least one geometry required")
    for i, geom in enumerate(input_data.geometries):
        if not geom or not geom.strip():
            return ValidationError(field="geometries", message=f"Geometry {i} is empty")
    return None


def run_single_job(geometry: str, method: str, basis: str, charge: int, 
                   multiplicity: int, calc_type: str, memory: int, n_threads: int) -> tuple:
    """Run a single calculation job."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{memory} MB")
    psi4.set_num_threads(n_threads)
    psi4.core.set_output_file("psi4_batch.out", False)
    
    mol_string = f"{charge} {multiplicity}\n{geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": basis,
        "reference": "rhf" if multiplicity == 1 else "uhf",
    })
    
    start = time.time()
    
    if calc_type == "energy":
        energy = psi4.energy(f"{method}/{basis}", molecule=mol)
    elif calc_type == "optimize":
        energy = psi4.optimize(f"{method}/{basis}", molecule=mol)
    else:  # frequency
        energy, wfn = psi4.frequency(f"{method}/{basis}", return_wfn=True, molecule=mol)
    
    runtime = time.time() - start
    psi4.core.clean()
    
    return energy, runtime, None


def run_batch_calculations(input_data: BatchRunnerInput) -> BatchResult:
    """Execute batch calculations."""
    jobs = []
    n_completed = 0
    n_failed = 0
    total_runtime = 0.0
    
    job_ids = input_data.job_ids or [f"job_{i}" for i in range(len(input_data.geometries))]
    
    for i, geometry in enumerate(input_data.geometries):
        job_id = job_ids[i] if i < len(job_ids) else f"job_{i}"
        
        logger.info(f"Running job {job_id} ({i+1}/{len(input_data.geometries)})")
        
        energy, runtime, error = run_single_job(
            geometry, input_data.method, input_data.basis,
            input_data.charge, input_data.multiplicity,
            input_data.calculation_type, input_data.memory, input_data.n_threads
        )
        
        if error:
            status = "failed"
            n_failed += 1
            if input_data.stop_on_error:
                jobs.append(BatchJob(job_id, geometry, input_data.method, input_data.basis,
                                    status, None, runtime, error))
                break
        else:
            status = "completed"
            n_completed += 1
        
        total_runtime += runtime
        
        jobs.append(BatchJob(
            job_id=job_id, geometry=geometry, method=input_data.method,
            basis=input_data.basis, status=status, energy=energy,
            runtime_seconds=runtime, error_message=error,
        ))
    
    return BatchResult(
        jobs=jobs, n_completed=n_completed,
        n_failed=n_failed, total_runtime=total_runtime,
    )


@register_tool
class BatchRunnerTool(BaseTool[BatchRunnerInput, ToolOutput]):
    """Tool for batch calculations."""
    name: ClassVar[str] = "run_batch"
    description: ClassVar[str] = "Run multiple calculations in batch mode."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITY
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: BatchRunnerInput) -> Optional[ValidationError]:
        return validate_batch_input(input_data)
    
    def _execute(self, input_data: BatchRunnerInput) -> Result[ToolOutput]:
        result = run_batch_calculations(input_data)
        
        energies = [f"  {j.job_id}: {j.energy:.10f} Eh" for j in result.jobs if j.energy]
        message = (
            f"Batch Calculation Complete\n{'='*40}\n"
            f"Completed: {result.n_completed}/{len(result.jobs)}\n"
            f"Failed: {result.n_failed}\n"
            f"Total Runtime: {result.total_runtime:.2f}s\n"
            f"Energies:\n" + "\n".join(energies[:10])
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def run_batch(geometries: List[str], method: str = "hf", **kwargs: Any) -> ToolOutput:
    """Run batch calculations."""
    return BatchRunnerTool().run({"geometries": geometries, "method": method, **kwargs})
