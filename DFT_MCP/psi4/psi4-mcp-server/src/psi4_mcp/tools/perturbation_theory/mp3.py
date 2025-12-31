"""
Third-order Møller-Plesset Perturbation Theory (MP3) Tool.

MP3 extends MP2 with third-order correlation corrections.

Reference:
    Pople, J.A.; Binkley, J.S.; Seeger, R.
    Int. J. Quantum Chem. 1976, 10, 1-19.
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
class MP3Result:
    """MP3 calculation results."""
    total_energy: float
    correlation_energy: float
    mp2_correlation: float
    mp3_correction: float
    hf_energy: float
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "mp2_correlation_hartree": self.mp2_correlation,
            "mp3_correction_hartree": self.mp3_correction,
            "hf_energy_hartree": self.hf_energy,
            "basis": self.basis,
        }


class MP3Input(ToolInput):
    """Input for MP3 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_mp3_input(input_data: MP3Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_mp3_calculation(input_data: MP3Input) -> MP3Result:
    """Execute MP3 calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_mp3.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running MP3/{input_data.basis}")
    
    e_mp3, wfn = psi4.energy("mp3", return_wfn=True, molecule=mol)
    
    hf_energy = psi4.variable("SCF TOTAL ENERGY")
    mp2_correlation = psi4.variable("MP2 CORRELATION ENERGY")
    mp3_correlation = psi4.variable("MP3 CORRELATION ENERGY")
    mp3_correction = mp3_correlation - mp2_correlation
    
    psi4.core.clean()
    
    return MP3Result(
        total_energy=e_mp3, correlation_energy=mp3_correlation,
        mp2_correlation=mp2_correlation, mp3_correction=mp3_correction,
        hf_energy=hf_energy, basis=input_data.basis,
    )


@register_tool
class MP3Tool(BaseTool[MP3Input, ToolOutput]):
    """Tool for MP3 calculations."""
    name: ClassVar[str] = "calculate_mp3"
    description: ClassVar[str] = "Calculate MP3 perturbation theory energy."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: MP3Input) -> Optional[ValidationError]:
        return validate_mp3_input(input_data)
    
    def _execute(self, input_data: MP3Input) -> Result[ToolOutput]:
        result = run_mp3_calculation(input_data)
        message = (
            f"MP3/{input_data.basis}\n"
            f"Total: {result.total_energy:.10f} Eh\n"
            f"MP2 Corr: {result.mp2_correlation:.10f} Eh\n"
            f"MP3 Corr: {result.mp3_correction:.10f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_mp3(geometry: str, basis: str = "cc-pvdz", charge: int = 0, 
                  multiplicity: int = 1, **kwargs: Any) -> ToolOutput:
    """Calculate MP3 energy."""
    return MP3Tool().run({"geometry": geometry, "basis": basis, "charge": charge, 
                          "multiplicity": multiplicity, **kwargs})
