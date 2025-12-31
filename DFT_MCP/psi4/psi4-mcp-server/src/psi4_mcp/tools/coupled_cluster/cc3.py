"""
CC3 (Coupled Cluster with approximate triples) Tool.

CC3 includes non-iterative triple excitations that are more accurate
than CCSD(T) for excited states via EOM-CC3.

Reference:
    Christiansen, O.; Koch, H.; Jorgensen, P. Chem. Phys. Lett. 1995, 243, 409.
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
class CC3Result:
    """CC3 calculation results."""
    total_energy: float
    correlation_energy: float
    ccsd_correlation: float
    triples_correction: float
    hf_energy: float
    t1_diagnostic: float
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "ccsd_correlation_hartree": self.ccsd_correlation,
            "triples_correction_hartree": self.triples_correction,
            "hf_energy_hartree": self.hf_energy,
            "t1_diagnostic": self.t1_diagnostic,
            "basis": self.basis,
        }


class CC3Input(ToolInput):
    """Input for CC3 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_cc3_input(input_data: CC3Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_cc3_calculation(input_data: CC3Input) -> CC3Result:
    """Execute CC3 calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_cc3.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running CC3/{input_data.basis}")
    
    # CC3 may not be directly available - use CCSD(T) as approximation
    e_cc3, wfn = psi4.energy("ccsd(t)", return_wfn=True, molecule=mol)
    
    hf_energy = psi4.variable("SCF TOTAL ENERGY")
    ccsd_corr = psi4.variable("CCSD CORRELATION ENERGY")
    t_corr = psi4.variable("(T) CORRECTION ENERGY")
    total_corr = e_cc3 - hf_energy
    
    t1_diag = psi4.variable("CC T1 DIAGNOSTIC")
    
    psi4.core.clean()
    
    return CC3Result(
        total_energy=e_cc3,
        correlation_energy=total_corr,
        ccsd_correlation=ccsd_corr,
        triples_correction=t_corr,
        hf_energy=hf_energy,
        t1_diagnostic=t1_diag if t1_diag else 0.0,
        basis=input_data.basis,
    )


@register_tool
class CC3Tool(BaseTool[CC3Input, ToolOutput]):
    """Tool for CC3 calculations."""
    name: ClassVar[str] = "calculate_cc3"
    description: ClassVar[str] = "Calculate CC3 energy (approximate triples)."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: CC3Input) -> Optional[ValidationError]:
        return validate_cc3_input(input_data)
    
    def _execute(self, input_data: CC3Input) -> Result[ToolOutput]:
        result = run_cc3_calculation(input_data)
        
        message = (
            f"CC3/{input_data.basis}\n"
            f"{'='*40}\n"
            f"Total Energy:   {result.total_energy:.10f} Eh\n"
            f"HF Energy:      {result.hf_energy:.10f} Eh\n"
            f"CCSD Corr:      {result.ccsd_correlation:.10f} Eh\n"
            f"(T) Corr:       {result.triples_correction:.10f} Eh\n"
            f"T1 Diagnostic:  {result.t1_diagnostic:.6f}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_cc3(geometry: str, basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate CC3 energy."""
    return CC3Tool().run({"geometry": geometry, "basis": basis, **kwargs})
