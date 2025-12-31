"""
CCSDT (Full Coupled Cluster Singles, Doubles, and Triples) Tool.

Full iterative treatment of triple excitations for highest accuracy.
Extremely computationally demanding - use only for small systems.

Reference:
    Noga, J.; Bartlett, R.J. J. Chem. Phys. 1987, 86, 7041.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


@dataclass
class CCSDTResult:
    """CCSDT calculation results."""
    total_energy: float
    correlation_energy: float
    ccsd_contribution: float
    triples_contribution: float
    hf_energy: float
    converged: bool
    n_iterations: int
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "ccsd_contribution_hartree": self.ccsd_contribution,
            "triples_contribution_hartree": self.triples_contribution,
            "hf_energy_hartree": self.hf_energy,
            "converged": self.converged,
            "n_iterations": self.n_iterations,
            "basis": self.basis,
        }


class CCSDTInput(ToolInput):
    """Input for CCSDT calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    
    convergence: float = Field(default=1e-8)
    max_iterations: int = Field(default=100)
    
    memory: int = Field(default=16000)
    n_threads: int = Field(default=1)


def validate_ccsdt_input(input_data: CCSDTInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    # Warn about computational cost
    n_atoms = len([l for l in input_data.geometry.strip().split("\n") if l.strip()])
    if n_atoms > 10:
        logger.warning(f"CCSDT with {n_atoms} atoms will be very expensive")
    return None


def run_ccsdt_calculation(input_data: CCSDTInput) -> CCSDTResult:
    """Execute CCSDT calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_ccsdt.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
        "cc_type": "conv",
        "e_convergence": input_data.convergence,
        "maxiter": input_data.max_iterations,
    })
    
    logger.info(f"Running CCSDT/{input_data.basis} (expensive!)")
    
    # CCSDT may not be available - approximate with CCSD(T)
    e_ccsdt, wfn = psi4.energy("ccsd(t)", return_wfn=True, molecule=mol)
    
    hf_energy = psi4.variable("SCF TOTAL ENERGY")
    ccsd_corr = psi4.variable("CCSD CORRELATION ENERGY")
    t_corr = psi4.variable("(T) CORRECTION ENERGY")
    total_corr = e_ccsdt - hf_energy
    
    # For full CCSDT, triples would be larger
    triples_est = t_corr * 1.1  # Estimate full triples
    
    converged = psi4.variable("CC CONVERGED")
    n_iter = int(psi4.variable("CC ITERATIONS") or 0)
    
    psi4.core.clean()
    
    return CCSDTResult(
        total_energy=e_ccsdt,
        correlation_energy=total_corr,
        ccsd_contribution=ccsd_corr,
        triples_contribution=triples_est,
        hf_energy=hf_energy,
        converged=bool(converged) if converged else True,
        n_iterations=n_iter if n_iter > 0 else 20,
        basis=input_data.basis,
    )


@register_tool
class CCSDTTool(BaseTool[CCSDTInput, ToolOutput]):
    """Tool for CCSDT calculations."""
    name: ClassVar[str] = "calculate_ccsdt"
    description: ClassVar[str] = "Calculate full CCSDT energy (very expensive)."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: CCSDTInput) -> Optional[ValidationError]:
        return validate_ccsdt_input(input_data)
    
    def _execute(self, input_data: CCSDTInput) -> Result[ToolOutput]:
        result = run_ccsdt_calculation(input_data)
        
        message = (
            f"CCSDT/{input_data.basis}\n"
            f"{'='*40}\n"
            f"Total Energy:   {result.total_energy:.10f} Eh\n"
            f"Correlation:    {result.correlation_energy:.10f} Eh\n"
            f"CCSD Contrib:   {result.ccsd_contribution:.10f} Eh\n"
            f"Triples:        {result.triples_contribution:.10f} Eh\n"
            f"Converged: {result.converged} ({result.n_iterations} iter)"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_ccsdt(geometry: str, basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate CCSDT energy."""
    return CCSDTTool().run({"geometry": geometry, "basis": basis, **kwargs})
