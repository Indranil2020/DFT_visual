"""
G4 (Gaussian-4) Composite Method Tool.

G4 theory is the most recent Gn method, with improved accuracy and
efficiency over G3 through optimized basis sets and corrections.

Reference:
    Curtiss, L.A.; Redfern, P.C.; Raghavachari, K.
    J. Chem. Phys. 2007, 126, 084108.
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
class G4Result:
    """G4 calculation results."""
    e_0: float
    e_298: float
    e_ccsd_t: float
    delta_e_hf: float
    delta_e_mp2: float
    delta_e_cc: float
    delta_e_hlc: float
    zpve: float
    optimized_geometry: str
    n_imaginary: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_0_hartree": self.e_0, "e_0_kcal": self.e_0 * HARTREE_TO_KCAL,
            "h_298_hartree": self.e_298, "h_298_kcal": self.e_298 * HARTREE_TO_KCAL,
            "components": {
                "e_ccsd_t": self.e_ccsd_t, "delta_e_hf": self.delta_e_hf,
                "delta_e_mp2": self.delta_e_mp2, "delta_e_cc": self.delta_e_cc,
                "delta_e_hlc": self.delta_e_hlc, "zpve": self.zpve,
            },
            "optimized_geometry": self.optimized_geometry,
            "n_imaginary": self.n_imaginary,
        }


class G4Input(ToolInput):
    """Input for G4 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    temperature: float = Field(default=298.15)
    scale_factor: float = Field(default=0.9854, description="B3LYP frequency scaling")
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_g4_input(input_data: G4Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_g4_calculation(input_data: G4Input) -> G4Result:
    """Execute G4 composite calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_g4.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    ref = "rhf" if input_data.multiplicity == 1 else "uhf"
    
    # B3LYP/6-31G(2df,p) geometry optimization
    logger.info("G4: B3LYP geometry optimization")
    psi4.set_options({"basis": "6-31G(2df,p)", "reference": ref})
    psi4.optimize("b3lyp/6-31G(2df,p)", molecule=mol)
    optimized_geometry = mol.save_string_xyz()
    
    # B3LYP/6-31G(2df,p) frequencies
    logger.info("G4: B3LYP frequencies")
    e_freq, freq_wfn = psi4.frequency("b3lyp/6-31G(2df,p)", molecule=mol, return_wfn=True)
    frequencies = freq_wfn.frequency_analysis['omega'].to_array().tolist()
    n_imaginary = sum(1 for f in frequencies if f < 0)
    zpve = sum(f for f in frequencies if f > 0) * 0.5 * input_data.scale_factor * 4.556335e-6
    
    # CCSD(T)/6-31G(d) base energy
    logger.info("G4: CCSD(T)/6-31G(d)")
    psi4.set_options({"basis": "6-31G*", "freeze_core": True})
    e_ccsd_t = psi4.energy("ccsd(t)/6-31G*", molecule=mol)
    
    # HF limit extrapolation
    logger.info("G4: HF extrapolation")
    psi4.set_options({"basis": "aug-cc-pVTZ"})
    e_hf_tz = psi4.energy("hf/aug-cc-pVTZ", molecule=mol)
    psi4.set_options({"basis": "aug-cc-pVQZ"})
    e_hf_qz = psi4.energy("hf/aug-cc-pVQZ", molecule=mol)
    
    # CBS extrapolation for HF
    e_hf_cbs = (e_hf_qz * 4**5 - e_hf_tz * 3**5) / (4**5 - 3**5)
    psi4.set_options({"basis": "6-31G*"})
    e_hf_base = psi4.energy("hf/6-31G*", molecule=mol)
    delta_e_hf = e_hf_cbs - e_hf_base
    
    # MP2 extrapolation
    logger.info("G4: MP2 extrapolation")
    psi4.set_options({"basis": "aug-cc-pVTZ", "freeze_core": True})
    e_mp2_tz = psi4.energy("mp2/aug-cc-pVTZ", molecule=mol)
    psi4.set_options({"basis": "aug-cc-pVQZ"})
    e_mp2_qz = psi4.energy("mp2/aug-cc-pVQZ", molecule=mol)
    
    corr_tz = e_mp2_tz - psi4.variable("SCF TOTAL ENERGY")
    corr_qz = e_mp2_qz - psi4.variable("SCF TOTAL ENERGY")
    
    # CBS extrapolation for MP2 correlation
    corr_cbs = (corr_qz * 4**3 - corr_tz * 3**3) / (4**3 - 3**3)
    psi4.set_options({"basis": "6-31G*"})
    e_mp2_base = psi4.energy("mp2/6-31G*", molecule=mol)
    corr_base = e_mp2_base - psi4.variable("SCF TOTAL ENERGY")
    delta_e_mp2 = corr_cbs - corr_base
    
    # CCSD(T) correction
    delta_e_cc = 0.0  # Included in base already
    
    # Higher-level correction (G4)
    n_electrons = mol.nelectron()
    n_unpaired = input_data.multiplicity - 1
    n_pairs = (n_electrons - n_unpaired) // 2
    
    A = 0.009472
    B = 0.003179
    delta_e_hlc = -A * n_pairs - B * n_unpaired
    
    e_0 = e_ccsd_t + delta_e_hf + delta_e_mp2 + delta_e_cc + delta_e_hlc + zpve
    e_298 = e_0 + 0.00236  # Approximate thermal correction
    
    psi4.core.clean()
    
    return G4Result(
        e_0=e_0, e_298=e_298, e_ccsd_t=e_ccsd_t,
        delta_e_hf=delta_e_hf, delta_e_mp2=delta_e_mp2,
        delta_e_cc=delta_e_cc, delta_e_hlc=delta_e_hlc,
        zpve=zpve, optimized_geometry=optimized_geometry,
        n_imaginary=n_imaginary,
    )


@register_tool
class G4Tool(BaseTool[G4Input, ToolOutput]):
    """Tool for G4 composite calculations."""
    name: ClassVar[str] = "calculate_g4"
    description: ClassVar[str] = "Calculate G4 composite energy for high-accuracy thermochemistry."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: G4Input) -> Optional[ValidationError]:
        return validate_g4_input(input_data)
    
    def _execute(self, input_data: G4Input) -> Result[ToolOutput]:
        result = run_g4_calculation(input_data)
        message = (
            f"G4 Composite Calculation\n"
            f"{'='*50}\n"
            f"E(0 K):   {result.e_0:16.10f} Eh ({result.e_0 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"H(298 K): {result.e_298:16.10f} Eh ({result.e_298 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"Imaginary frequencies: {result.n_imaginary}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_g4(geometry: str, charge: int = 0, multiplicity: int = 1, **kwargs: Any) -> ToolOutput:
    """Calculate G4 composite energy."""
    return G4Tool().run({"geometry": geometry, "charge": charge, "multiplicity": multiplicity, **kwargs})
