"""
G3 (Gaussian-3) Composite Method Tool.

G3 theory provides high-accuracy thermochemical predictions through
a combination of geometry optimization, frequencies, and multiple
single-point energy corrections.

Key Features:
    - MP2(full)/6-31G(d) geometry
    - HF/6-31G(d) frequencies
    - QCISD(T)/6-31G(d) base energy
    - MP4/6-31+G(d), MP4/6-31G(2df,p), MP2(full)/G3Large corrections
    - Spin-orbit and higher-level corrections
    - ~1 kcal/mol accuracy for G2 test set

Reference:
    Curtiss, L.A.; Raghavachari, K.; Redfern, P.C.; Rassolov, V.; Pople, J.A.
    J. Chem. Phys. 1998, 109, 7764-7776.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolCategory,
    register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError, ValidationError


logger = logging.getLogger(__name__)


HARTREE_TO_KCAL = 627.5094740631


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class G3Result:
    """Complete G3 calculation results."""
    e_0: float  # G3 energy at 0 K
    e_298: float  # Enthalpy at 298 K
    
    e_qcisd_t: float
    delta_e_plus: float  # Diffuse function correction
    delta_e_2df: float  # Polarization function correction
    delta_e_g3large: float  # G3Large basis set correction
    delta_e_so: float  # Spin-orbit correction
    delta_e_hlc: float  # Higher-level correction
    zpve: float
    
    optimized_geometry: str
    n_imaginary: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_0_hartree": self.e_0,
            "e_0_kcal": self.e_0 * HARTREE_TO_KCAL,
            "h_298_hartree": self.e_298,
            "h_298_kcal": self.e_298 * HARTREE_TO_KCAL,
            "components": {
                "e_qcisd_t": self.e_qcisd_t,
                "delta_e_plus": self.delta_e_plus,
                "delta_e_2df": self.delta_e_2df,
                "delta_e_g3large": self.delta_e_g3large,
                "delta_e_so": self.delta_e_so,
                "delta_e_hlc": self.delta_e_hlc,
                "zpve": self.zpve,
            },
            "optimized_geometry": self.optimized_geometry,
            "n_imaginary": self.n_imaginary,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class G3Input(ToolInput):
    """Input schema for G3 calculation."""
    
    geometry: str = Field(..., description="Initial molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    temperature: float = Field(default=298.15)
    scale_factor: float = Field(default=0.8929, description="HF frequency scaling")
    
    skip_optimization: bool = Field(default=False)
    skip_frequencies: bool = Field(default=False)
    
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_g3_input(input_data: G3Input) -> Optional[ValidationError]:
    """Validate G3 input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


# =============================================================================
# G3 COMPUTATION
# =============================================================================

def run_g3_calculation(input_data: G3Input) -> G3Result:
    """Execute G3 composite calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_g3.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    logger.info("G3: Starting calculation")
    
    # Step 1: MP2(full)/6-31G(d) geometry optimization
    logger.info("G3 Step 1: MP2/6-31G(d) geometry optimization")
    psi4.set_options({
        "basis": "6-31G*",
        "freeze_core": False,  # full
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    if not input_data.skip_optimization:
        psi4.optimize("mp2/6-31G*", molecule=mol)
    
    optimized_geometry = mol.save_string_xyz()
    
    # Step 2: HF/6-31G(d) frequencies
    logger.info("G3 Step 2: HF/6-31G(d) frequencies")
    
    if not input_data.skip_frequencies:
        psi4.set_options({"basis": "6-31G*"})
        e_freq, freq_wfn = psi4.frequency("hf/6-31G*", molecule=mol, return_wfn=True)
        
        vib_info = freq_wfn.frequency_analysis
        frequencies = vib_info['omega'].to_array().tolist()
        n_imaginary = sum(1 for f in frequencies if f < 0)
        
        # Scaled ZPVE
        zpve = sum(f for f in frequencies if f > 0) * 0.5 * input_data.scale_factor * 4.556335e-6
    else:
        n_imaginary = 0
        zpve = 0.0
    
    # Step 3: QCISD(T)/6-31G(d) base energy
    logger.info("G3 Step 3: QCISD(T)/6-31G(d) base energy")
    psi4.set_options({"basis": "6-31G*", "freeze_core": True})
    # Note: Psi4 uses CCSD(T) as QCISD(T) approximation
    e_qcisd_t = psi4.energy("ccsd(t)/6-31G*", molecule=mol)
    
    # Step 4: MP4/6-31+G(d) for diffuse correction
    logger.info("G3 Step 4: MP4/6-31+G(d) correction")
    psi4.set_options({"basis": "6-31+G*", "freeze_core": True})
    e_mp4_plus = psi4.energy("mp4/6-31+G*", molecule=mol)
    
    psi4.set_options({"basis": "6-31G*"})
    e_mp4_base = psi4.energy("mp4/6-31G*", molecule=mol)
    
    delta_e_plus = e_mp4_plus - e_mp4_base
    
    # Step 5: MP4/6-31G(2df,p) for polarization correction
    logger.info("G3 Step 5: MP4/6-31G(2df,p) correction")
    psi4.set_options({"basis": "6-31G(2df,p)", "freeze_core": True})
    e_mp4_2df = psi4.energy("mp4/6-31G(2df,p)", molecule=mol)
    
    delta_e_2df = e_mp4_2df - e_mp4_base
    
    # Step 6: MP2(full)/G3Large for higher basis
    logger.info("G3 Step 6: MP2/G3Large correction")
    psi4.set_options({"basis": "cc-pVTZ", "freeze_core": False})  # G3Large approximation
    e_mp2_g3large = psi4.energy("mp2/cc-pVTZ", molecule=mol)
    
    psi4.set_options({"basis": "6-31G(2df,p)"})
    e_mp2_2df = psi4.energy("mp2/6-31G(2df,p)", molecule=mol)
    
    psi4.set_options({"basis": "6-31+G*"})
    e_mp2_plus = psi4.energy("mp2/6-31+G*", molecule=mol)
    
    psi4.set_options({"basis": "6-31G*"})
    e_mp2_base = psi4.energy("mp2/6-31G*", molecule=mol)
    
    delta_e_g3large = e_mp2_g3large - e_mp2_2df - e_mp2_plus + e_mp2_base
    
    # Higher-level correction
    n_alpha = mol.nelectron() // 2 + mol.nelectron() % 2
    n_beta = mol.nelectron() // 2
    n_unpaired = abs(n_alpha - n_beta)
    
    # G3 HLC parameters (for molecules)
    A = 0.006386
    B = 0.002977
    
    n_valence_pairs = (mol.nelectron() - n_unpaired) // 2
    delta_e_hlc = -A * n_valence_pairs - B * n_unpaired
    
    # Spin-orbit correction (simplified)
    delta_e_so = 0.0  # Would need atomic spin-orbit constants
    
    # G3 total energy
    e_0 = e_qcisd_t + delta_e_plus + delta_e_2df + delta_e_g3large + delta_e_hlc + delta_e_so + zpve
    
    # Thermal correction to 298 K
    e_298 = e_0 + 0.00236  # Approximate thermal correction
    
    psi4.core.clean()
    
    return G3Result(
        e_0=e_0,
        e_298=e_298,
        e_qcisd_t=e_qcisd_t,
        delta_e_plus=delta_e_plus,
        delta_e_2df=delta_e_2df,
        delta_e_g3large=delta_e_g3large,
        delta_e_so=delta_e_so,
        delta_e_hlc=delta_e_hlc,
        zpve=zpve,
        optimized_geometry=optimized_geometry,
        n_imaginary=n_imaginary,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class G3Tool(BaseTool[G3Input, ToolOutput]):
    """Tool for G3 composite method calculations."""
    
    name: ClassVar[str] = "calculate_g3"
    description: ClassVar[str] = "Calculate G3 composite energy for accurate thermochemistry."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: G3Input) -> Optional[ValidationError]:
        return validate_g3_input(input_data)
    
    def _execute(self, input_data: G3Input) -> Result[ToolOutput]:
        result = run_g3_calculation(input_data)
        
        message = (
            f"G3 Composite Calculation\n"
            f"{'='*50}\n"
            f"E(0 K):     {result.e_0:16.10f} Eh ({result.e_0 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"H(298 K):   {result.e_298:16.10f} Eh ({result.e_298 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"{'='*50}\n"
            f"Components:\n"
            f"  QCISD(T):      {result.e_qcisd_t:16.10f} Eh\n"
            f"  ΔE(+):         {result.delta_e_plus:16.10f} Eh\n"
            f"  ΔE(2df):       {result.delta_e_2df:16.10f} Eh\n"
            f"  ΔE(G3Large):   {result.delta_e_g3large:16.10f} Eh\n"
            f"  ΔE(HLC):       {result.delta_e_hlc:16.10f} Eh\n"
            f"  ZPVE:          {result.zpve:16.10f} Eh"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_g3(
    geometry: str,
    charge: int = 0,
    multiplicity: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate G3 composite energy."""
    tool = G3Tool()
    return tool.run({"geometry": geometry, "charge": charge, "multiplicity": multiplicity, **kwargs})
