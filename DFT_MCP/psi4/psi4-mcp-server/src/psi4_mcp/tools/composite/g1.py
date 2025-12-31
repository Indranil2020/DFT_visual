"""
G1 (Gaussian-1) Composite Method Tool.

G1 theory was the first in the Gn series, providing accurate
atomization energies through HF-based corrections.

Reference:
    Pople, J.A.; Head-Gordon, M.; Fox, D.J.; Raghavachari, K.; Curtiss, L.A.
    J. Chem. Phys. 1989, 90, 5622-5629.
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
class G1Result:
    """G1 calculation results."""
    e_0: float
    e_mp4: float
    e_qci_correction: float
    delta_e_basis: float
    delta_e_hlc: float
    zpve: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_0_hartree": self.e_0, "e_0_kcal": self.e_0 * HARTREE_TO_KCAL,
            "components": {
                "e_mp4": self.e_mp4, "e_qci_correction": self.e_qci_correction,
                "delta_e_basis": self.delta_e_basis, "delta_e_hlc": self.delta_e_hlc,
                "zpve": self.zpve,
            },
        }


class G1Input(ToolInput):
    """Input for G1 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    scale_factor: float = Field(default=0.8929)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_g1_input(input_data: G1Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_g1_calculation(input_data: G1Input) -> G1Result:
    """Execute G1 composite calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_g1.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    # HF/6-31G* geometry optimization
    psi4.set_options({"basis": "6-31G*", "reference": "rhf" if input_data.multiplicity == 1 else "uhf"})
    psi4.optimize("hf/6-31G*", molecule=mol)
    
    # HF/6-31G* frequencies
    e_freq, freq_wfn = psi4.frequency("hf/6-31G*", molecule=mol, return_wfn=True)
    vib_info = freq_wfn.frequency_analysis
    frequencies = vib_info['omega'].to_array().tolist()
    zpve = sum(f for f in frequencies if f > 0) * 0.5 * input_data.scale_factor * 4.556335e-6
    
    # MP4/6-311G** base energy
    psi4.set_options({"basis": "6-311G**", "freeze_core": True})
    e_mp4 = psi4.energy("mp4/6-311G**", molecule=mol)
    
    # QCI correction
    psi4.set_options({"basis": "6-311G**"})
    e_qcisd_t = psi4.energy("ccsd(t)/6-311G**", molecule=mol)
    e_qci_correction = e_qcisd_t - e_mp4
    
    # Basis set extension correction
    psi4.set_options({"basis": "6-311+G**"})
    e_mp4_plus = psi4.energy("mp4/6-311+G**", molecule=mol)
    psi4.set_options({"basis": "6-311G(2df,p)"})
    e_mp2_2df = psi4.energy("mp2/6-311G(2df,p)", molecule=mol)
    psi4.set_options({"basis": "6-311G**"})
    e_mp2_base = psi4.energy("mp2/6-311G**", molecule=mol)
    
    delta_e_basis = (e_mp4_plus - e_mp4) + (e_mp2_2df - e_mp2_base)
    
    # Higher-level correction
    n_electrons = mol.nelectron()
    n_unpaired = input_data.multiplicity - 1
    delta_e_hlc = -0.00481 * ((n_electrons - n_unpaired) // 2) - 0.00019 * n_unpaired
    
    e_0 = e_mp4 + e_qci_correction + delta_e_basis + delta_e_hlc + zpve
    
    psi4.core.clean()
    
    return G1Result(e_0=e_0, e_mp4=e_mp4, e_qci_correction=e_qci_correction,
                   delta_e_basis=delta_e_basis, delta_e_hlc=delta_e_hlc, zpve=zpve)


@register_tool
class G1Tool(BaseTool[G1Input, ToolOutput]):
    """Tool for G1 composite calculations."""
    name: ClassVar[str] = "calculate_g1"
    description: ClassVar[str] = "Calculate G1 composite energy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: G1Input) -> Optional[ValidationError]:
        return validate_g1_input(input_data)
    
    def _execute(self, input_data: G1Input) -> Result[ToolOutput]:
        result = run_g1_calculation(input_data)
        message = f"G1 Energy: {result.e_0:.10f} Eh ({result.e_0 * HARTREE_TO_KCAL:.2f} kcal/mol)"
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_g1(geometry: str, charge: int = 0, multiplicity: int = 1, **kwargs: Any) -> ToolOutput:
    """Calculate G1 composite energy."""
    return G1Tool().run({"geometry": geometry, "charge": charge, "multiplicity": multiplicity, **kwargs})
