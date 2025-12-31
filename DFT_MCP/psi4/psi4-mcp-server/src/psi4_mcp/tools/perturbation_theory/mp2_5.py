"""
MP2.5 Perturbation Theory Tool.

MP2.5 is the average of MP2 and MP3, providing improved accuracy
for many systems at moderate additional cost.

Reference:
    Pitonak, M.; Neogrady, P.; Cerny, J.; Grimme, S.; Hobza, P.
    ChemPhysChem 2009, 10, 282-289.
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
class MP25Result:
    """MP2.5 calculation results."""
    total_energy: float
    correlation_energy: float
    mp2_energy: float
    mp3_energy: float
    mp2_correlation: float
    mp3_correlation: float
    hf_energy: float
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "mp2_total_hartree": self.mp2_energy,
            "mp3_total_hartree": self.mp3_energy,
            "mp2_correlation_hartree": self.mp2_correlation,
            "mp3_correlation_hartree": self.mp3_correlation,
            "hf_energy_hartree": self.hf_energy,
            "basis": self.basis,
        }


class MP25Input(ToolInput):
    """Input for MP2.5 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_mp25_input(input_data: MP25Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_mp25_calculation(input_data: MP25Input) -> MP25Result:
    """Execute MP2.5 calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_mp25.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running MP2.5/{input_data.basis}")
    
    # Run MP3 (includes MP2)
    e_mp3, wfn = psi4.energy("mp3", return_wfn=True, molecule=mol)
    
    hf_energy = psi4.variable("SCF TOTAL ENERGY")
    mp2_correlation = psi4.variable("MP2 CORRELATION ENERGY")
    mp3_correlation = psi4.variable("MP3 CORRELATION ENERGY")
    
    mp2_energy = hf_energy + mp2_correlation
    mp3_energy = hf_energy + mp3_correlation
    
    # MP2.5 = average of MP2 and MP3
    mp25_correlation = (mp2_correlation + mp3_correlation) / 2
    mp25_energy = hf_energy + mp25_correlation
    
    psi4.core.clean()
    
    return MP25Result(
        total_energy=mp25_energy, correlation_energy=mp25_correlation,
        mp2_energy=mp2_energy, mp3_energy=mp3_energy,
        mp2_correlation=mp2_correlation, mp3_correlation=mp3_correlation,
        hf_energy=hf_energy, basis=input_data.basis,
    )


@register_tool
class MP25Tool(BaseTool[MP25Input, ToolOutput]):
    """Tool for MP2.5 calculations."""
    name: ClassVar[str] = "calculate_mp2_5"
    description: ClassVar[str] = "Calculate MP2.5 (average of MP2 and MP3) energy."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: MP25Input) -> Optional[ValidationError]:
        return validate_mp25_input(input_data)
    
    def _execute(self, input_data: MP25Input) -> Result[ToolOutput]:
        result = run_mp25_calculation(input_data)
        message = (
            f"MP2.5/{input_data.basis}\n"
            f"{'='*40}\n"
            f"MP2.5 Energy: {result.total_energy:.10f} Eh\n"
            f"MP2 Energy:   {result.mp2_energy:.10f} Eh\n"
            f"MP3 Energy:   {result.mp3_energy:.10f} Eh\n"
            f"HF Energy:    {result.hf_energy:.10f} Eh\n"
            f"MP2.5 Corr:   {result.correlation_energy:.10f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_mp2_5(geometry: str, basis: str = "cc-pvdz", charge: int = 0,
                    multiplicity: int = 1, **kwargs: Any) -> ToolOutput:
    """Calculate MP2.5 energy."""
    return MP25Tool().run({"geometry": geometry, "basis": basis, "charge": charge,
                           "multiplicity": multiplicity, **kwargs})
