"""
W1 (Weizmann-1) Composite Method Tool.

W1 theory provides sub-kcal/mol accuracy through explicit basis set
extrapolation and inclusion of higher-order correlation effects.

Reference:
    Martin, J.M.L.; de Oliveira, G.
    J. Chem. Phys. 1999, 111, 1843-1856.
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
class W1Result:
    """W1 calculation results."""
    e_total: float
    e_scf_cbs: float
    e_ccsd_cbs: float
    e_t_cbs: float
    e_core_valence: float
    e_relativistic: float
    zpve: float
    optimized_geometry: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_total_hartree": self.e_total,
            "e_total_kcal": self.e_total * HARTREE_TO_KCAL,
            "components": {
                "e_scf_cbs": self.e_scf_cbs,
                "e_ccsd_cbs": self.e_ccsd_cbs,
                "e_t_cbs": self.e_t_cbs,
                "e_core_valence": self.e_core_valence,
                "e_relativistic": self.e_relativistic,
                "zpve": self.zpve,
            },
            "optimized_geometry": self.optimized_geometry,
        }


class W1Input(ToolInput):
    """Input for W1 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    scale_factor: float = Field(default=0.985, description="CCSD(T) frequency scaling")
    memory: int = Field(default=16000, description="Memory (W1 needs more)")
    n_threads: int = Field(default=1)


def validate_w1_input(input_data: W1Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def extrapolate_scf(e_tz: float, e_qz: float) -> float:
    """Extrapolate SCF energy to CBS limit."""
    # Two-point exponential extrapolation
    alpha = 5.34
    e_cbs = (e_qz * 4**alpha - e_tz * 3**alpha) / (4**alpha - 3**alpha)
    return e_cbs


def extrapolate_correlation(corr_tz: float, corr_qz: float, n_small: int = 3, n_large: int = 4) -> float:
    """Extrapolate correlation energy to CBS limit."""
    alpha = 3.0
    e_cbs = (corr_qz * n_large**alpha - corr_tz * n_small**alpha) / (n_large**alpha - n_small**alpha)
    return e_cbs


def run_w1_calculation(input_data: W1Input) -> W1Result:
    """Execute W1 composite calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_w1.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    ref = "rhf" if input_data.multiplicity == 1 else "uhf"
    
    # CCSD(T)/cc-pVTZ geometry optimization
    logger.info("W1: CCSD(T)/cc-pVTZ geometry optimization")
    psi4.set_options({"basis": "cc-pVTZ", "freeze_core": True, "reference": ref})
    psi4.optimize("ccsd(t)/cc-pVTZ", molecule=mol)
    optimized_geometry = mol.save_string_xyz()
    
    # CCSD(T)/cc-pVTZ frequencies
    logger.info("W1: CCSD(T)/cc-pVTZ frequencies")
    e_freq, freq_wfn = psi4.frequency("ccsd(t)/cc-pVTZ", molecule=mol, return_wfn=True)
    frequencies = freq_wfn.frequency_analysis['omega'].to_array().tolist()
    zpve = sum(f for f in frequencies if f > 0) * 0.5 * input_data.scale_factor * 4.556335e-6
    
    # SCF extrapolation (aug-cc-pVTZ -> aug-cc-pVQZ)
    logger.info("W1: SCF CBS extrapolation")
    psi4.set_options({"basis": "aug-cc-pVTZ"})
    e_scf_tz = psi4.energy("hf/aug-cc-pVTZ", molecule=mol)
    psi4.set_options({"basis": "aug-cc-pVQZ"})
    e_scf_qz = psi4.energy("hf/aug-cc-pVQZ", molecule=mol)
    e_scf_cbs = extrapolate_scf(e_scf_tz, e_scf_qz)
    
    # CCSD correlation extrapolation
    logger.info("W1: CCSD CBS extrapolation")
    psi4.set_options({"basis": "aug-cc-pVTZ", "freeze_core": True})
    e_ccsd_tz = psi4.energy("ccsd/aug-cc-pVTZ", molecule=mol)
    ccsd_corr_tz = e_ccsd_tz - e_scf_tz
    
    psi4.set_options({"basis": "aug-cc-pVQZ"})
    e_ccsd_qz = psi4.energy("ccsd/aug-cc-pVQZ", molecule=mol)
    ccsd_corr_qz = e_ccsd_qz - e_scf_qz
    
    e_ccsd_cbs = extrapolate_correlation(ccsd_corr_tz, ccsd_corr_qz)
    
    # (T) correction extrapolation
    logger.info("W1: (T) CBS extrapolation")
    psi4.set_options({"basis": "aug-cc-pVDZ"})
    e_ccsd_t_dz = psi4.energy("ccsd(t)/aug-cc-pVDZ", molecule=mol)
    e_ccsd_dz = psi4.energy("ccsd/aug-cc-pVDZ", molecule=mol)
    t_corr_dz = e_ccsd_t_dz - e_ccsd_dz
    
    psi4.set_options({"basis": "aug-cc-pVTZ"})
    e_ccsd_t_tz = psi4.energy("ccsd(t)/aug-cc-pVTZ", molecule=mol)
    t_corr_tz = e_ccsd_t_tz - e_ccsd_tz
    
    e_t_cbs = extrapolate_correlation(t_corr_dz, t_corr_tz, n_small=2, n_large=3)
    
    # Core-valence correlation
    logger.info("W1: Core-valence correlation")
    psi4.set_options({"basis": "cc-pCVTZ", "freeze_core": False})
    e_cv_full = psi4.energy("mp2/cc-pCVTZ", molecule=mol)
    psi4.set_options({"freeze_core": True})
    e_cv_frozen = psi4.energy("mp2/cc-pCVTZ", molecule=mol)
    e_core_valence = e_cv_full - e_cv_frozen
    
    # Relativistic correction (scalar relativity, approximate)
    e_relativistic = 0.0  # Would need DKH/X2C calculation
    
    # Total W1 energy
    e_total = e_scf_cbs + e_ccsd_cbs + e_t_cbs + e_core_valence + e_relativistic + zpve
    
    psi4.core.clean()
    
    return W1Result(
        e_total=e_total, e_scf_cbs=e_scf_cbs, e_ccsd_cbs=e_ccsd_cbs,
        e_t_cbs=e_t_cbs, e_core_valence=e_core_valence,
        e_relativistic=e_relativistic, zpve=zpve,
        optimized_geometry=optimized_geometry,
    )


@register_tool
class W1Tool(BaseTool[W1Input, ToolOutput]):
    """Tool for W1 composite calculations."""
    name: ClassVar[str] = "calculate_w1"
    description: ClassVar[str] = "Calculate W1 composite energy for sub-kcal/mol accuracy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: W1Input) -> Optional[ValidationError]:
        return validate_w1_input(input_data)
    
    def _execute(self, input_data: W1Input) -> Result[ToolOutput]:
        result = run_w1_calculation(input_data)
        message = (
            f"W1 Composite Calculation\n"
            f"{'='*50}\n"
            f"Total Energy: {result.e_total:16.10f} Eh ({result.e_total * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"{'='*50}\n"
            f"Components:\n"
            f"  SCF CBS:        {result.e_scf_cbs:16.10f} Eh\n"
            f"  CCSD CBS:       {result.e_ccsd_cbs:16.10f} Eh\n"
            f"  (T) CBS:        {result.e_t_cbs:16.10f} Eh\n"
            f"  Core-Valence:   {result.e_core_valence:16.10f} Eh\n"
            f"  ZPVE:           {result.zpve:16.10f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_w1(geometry: str, charge: int = 0, multiplicity: int = 1, **kwargs: Any) -> ToolOutput:
    """Calculate W1 composite energy."""
    return W1Tool().run({"geometry": geometry, "charge": charge, "multiplicity": multiplicity, **kwargs})
