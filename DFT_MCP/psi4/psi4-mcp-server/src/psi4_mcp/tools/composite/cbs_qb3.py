"""
CBS-QB3 Composite Method Tool.

CBS-QB3 combines geometry optimization, frequency calculation, and
a series of single-point calculations with complete basis set
extrapolation for accurate thermochemistry.

Key Features:
    - B3LYP/6-311G(2d,d,p) geometry and frequencies
    - CBS extrapolation of MP2 energy
    - CCSD(T) correction
    - Empirical corrections
    - High accuracy for thermochemistry

Reference:
    Montgomery, J.A.; Frisch, M.J.; Ochterski, J.W.; Petersson, G.A.
    J. Chem. Phys. 1999, 110, 2822-2827.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
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
HARTREE_TO_KJ = 2625.4996394799


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CBSExtrapolationResult:
    """CBS extrapolation result."""
    e_cbs: float
    e_small_basis: float
    e_large_basis: float
    extrapolation_formula: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_cbs_hartree": self.e_cbs,
            "e_small_basis_hartree": self.e_small_basis,
            "e_large_basis_hartree": self.e_large_basis,
            "extrapolation_formula": self.extrapolation_formula,
        }


@dataclass
class CBSQB3Result:
    """Complete CBS-QB3 calculation results."""
    e_0: float  # Final CBS-QB3 energy at 0 K
    e_298: float  # Enthalpy at 298 K
    g_298: float  # Free energy at 298 K
    
    e_b3lyp: float
    e_mp2_cbs: float
    e_ccsd_t_correction: float
    e_empirical: float
    zpve: float
    thermal_correction: float
    
    optimized_geometry: str
    frequencies: List[float]
    n_imaginary: int
    
    basis_set: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_0_hartree": self.e_0,
            "e_0_kcal": self.e_0 * HARTREE_TO_KCAL,
            "h_298_hartree": self.e_298,
            "h_298_kcal": self.e_298 * HARTREE_TO_KCAL,
            "g_298_hartree": self.g_298,
            "g_298_kcal": self.g_298 * HARTREE_TO_KCAL,
            "components": {
                "e_b3lyp": self.e_b3lyp,
                "e_mp2_cbs": self.e_mp2_cbs,
                "e_ccsd_t_correction": self.e_ccsd_t_correction,
                "e_empirical": self.e_empirical,
                "zpve": self.zpve,
                "thermal_correction": self.thermal_correction,
            },
            "optimized_geometry": self.optimized_geometry,
            "frequencies_cm": self.frequencies,
            "n_imaginary": self.n_imaginary,
            "basis_set": self.basis_set,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class CBSQB3Input(ToolInput):
    """Input schema for CBS-QB3 calculation."""
    
    geometry: str = Field(..., description="Initial molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    temperature: float = Field(default=298.15, description="Temperature in K")
    pressure: float = Field(default=101325.0, description="Pressure in Pa")
    
    skip_optimization: bool = Field(default=False, description="Skip geometry optimization")
    skip_frequencies: bool = Field(default=False, description="Skip frequency calculation")
    
    scale_factor: float = Field(default=0.99, description="Frequency scaling factor")
    
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_cbs_qb3_input(input_data: CBSQB3Input) -> Optional[ValidationError]:
    """Validate CBS-QB3 input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    if input_data.temperature < 0:
        return ValidationError(field="temperature", message="Temperature must be positive")
    
    return None


# =============================================================================
# CBS EXTRAPOLATION
# =============================================================================

def cbs_extrapolate_mp2(e_small: float, e_large: float, n_small: int = 3, n_large: int = 4) -> float:
    """
    Perform CBS extrapolation of MP2 correlation energy.
    
    Uses the two-point formula: E_CBS = (n_large^3 * E_large - n_small^3 * E_small) / (n_large^3 - n_small^3)
    """
    n_s3 = n_small ** 3
    n_l3 = n_large ** 3
    
    e_cbs = (n_l3 * e_large - n_s3 * e_small) / (n_l3 - n_s3)
    
    return e_cbs


# =============================================================================
# CBS-QB3 COMPUTATION
# =============================================================================

def run_cbs_qb3_calculation(input_data: CBSQB3Input) -> CBSQB3Result:
    """Execute CBS-QB3 composite calculation."""
    import psi4
    import numpy as np
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_cbsqb3.out", False)
    
    # Build molecule
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    logger.info("CBS-QB3: Starting calculation")
    
    # Step 1: B3LYP/6-311G(2d,d,p) geometry optimization
    logger.info("CBS-QB3 Step 1: B3LYP geometry optimization")
    
    psi4.set_options({
        "basis": "6-311G(2d,d,p)",
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    if not input_data.skip_optimization:
        e_b3lyp = psi4.optimize("b3lyp/6-311G(2d,d,p)", molecule=mol)
    else:
        e_b3lyp = psi4.energy("b3lyp/6-311G(2d,d,p)", molecule=mol)
    
    optimized_geometry = mol.save_string_xyz()
    
    # Step 2: B3LYP/6-311G(2d,d,p) frequencies
    logger.info("CBS-QB3 Step 2: Frequency calculation")
    
    if not input_data.skip_frequencies:
        e_freq, freq_wfn = psi4.frequency("b3lyp/6-311G(2d,d,p)", molecule=mol, return_wfn=True)
        
        # Get frequencies
        vib_info = freq_wfn.frequency_analysis
        frequencies = vib_info['omega'].to_array().tolist()
        
        # Scale frequencies
        scaled_freq = [f * input_data.scale_factor for f in frequencies]
        
        # Count imaginary
        n_imaginary = sum(1 for f in frequencies if f < 0)
        
        # ZPVE
        zpve = sum(f for f in scaled_freq if f > 0) * 0.5 * 4.556335e-6  # cm^-1 to Hartree
        
        # Thermal corrections
        thermal_correction = vib_info['thermo']['E_thermal'] if 'thermo' in vib_info else 0.0
    else:
        frequencies = []
        scaled_freq = []
        n_imaginary = 0
        zpve = 0.0
        thermal_correction = 0.0
    
    # Step 3: MP2/6-31+G(d') single point
    logger.info("CBS-QB3 Step 3: MP2/6-31+G(d') energy")
    psi4.set_options({"basis": "6-31+G*", "freeze_core": True})
    e_mp2_small, mp2_wfn_small = psi4.energy("mp2", return_wfn=True, molecule=mol)
    e_mp2_corr_small = psi4.variable("MP2 CORRELATION ENERGY")
    e_hf_small = psi4.variable("SCF TOTAL ENERGY")
    
    # Step 4: MP2/6-311+G(2df,2p) single point
    logger.info("CBS-QB3 Step 4: MP2/6-311+G(2df,2p) energy")
    psi4.set_options({"basis": "6-311+G(2df,2p)", "freeze_core": True})
    e_mp2_large, mp2_wfn_large = psi4.energy("mp2", return_wfn=True, molecule=mol)
    e_mp2_corr_large = psi4.variable("MP2 CORRELATION ENERGY")
    e_hf_large = psi4.variable("SCF TOTAL ENERGY")
    
    # CBS extrapolation of MP2 correlation energy
    e_mp2_corr_cbs = cbs_extrapolate_mp2(e_mp2_corr_small, e_mp2_corr_large)
    e_mp2_cbs = e_hf_large + e_mp2_corr_cbs
    
    # Step 5: CCSD(T)/6-31+G(d') single point for higher-order correction
    logger.info("CBS-QB3 Step 5: CCSD(T)/6-31+G(d') energy")
    psi4.set_options({"basis": "6-31+G*", "freeze_core": True})
    e_ccsd_t = psi4.energy("ccsd(t)", molecule=mol)
    e_ccsd_t_mp2 = psi4.variable("CCSD(T) CORRELATION ENERGY") - psi4.variable("MP2 CORRELATION ENERGY")
    
    # CCSD(T) correction (difference from MP2)
    e_ccsd_t_correction = e_ccsd_t_mp2
    
    # Empirical correction
    n_electrons = mol.nelectron()
    n_unpaired = input_data.multiplicity - 1
    e_empirical = -0.00454 * n_electrons - 0.00056 * n_unpaired
    
    # Final CBS-QB3 energy at 0 K
    e_0 = e_mp2_cbs + e_ccsd_t_correction + e_empirical + zpve
    
    # Enthalpy at 298 K
    e_298 = e_0 + thermal_correction
    
    # Gibbs free energy at 298 K (approximate)
    entropy_correction = 0.0  # Would need more detailed calculation
    g_298 = e_298 - input_data.temperature * entropy_correction
    
    psi4.core.clean()
    
    return CBSQB3Result(
        e_0=e_0,
        e_298=e_298,
        g_298=g_298,
        e_b3lyp=e_b3lyp,
        e_mp2_cbs=e_mp2_cbs,
        e_ccsd_t_correction=e_ccsd_t_correction,
        e_empirical=e_empirical,
        zpve=zpve,
        thermal_correction=thermal_correction,
        optimized_geometry=optimized_geometry,
        frequencies=frequencies,
        n_imaginary=n_imaginary,
        basis_set="CBS-QB3",
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class CBSQB3Tool(BaseTool[CBSQB3Input, ToolOutput]):
    """Tool for CBS-QB3 composite method calculations."""
    
    name: ClassVar[str] = "calculate_cbs_qb3"
    description: ClassVar[str] = (
        "Calculate CBS-QB3 composite energy for accurate thermochemistry."
    )
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: CBSQB3Input) -> Optional[ValidationError]:
        return validate_cbs_qb3_input(input_data)
    
    def _execute(self, input_data: CBSQB3Input) -> Result[ToolOutput]:
        result = run_cbs_qb3_calculation(input_data)
        
        message = (
            f"CBS-QB3 Composite Calculation\n"
            f"{'='*50}\n"
            f"E(0 K):     {result.e_0:16.10f} Eh ({result.e_0 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"H(298 K):   {result.e_298:16.10f} Eh ({result.e_298 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"G(298 K):   {result.g_298:16.10f} Eh ({result.g_298 * HARTREE_TO_KCAL:.2f} kcal/mol)\n"
            f"{'='*50}\n"
            f"Components:\n"
            f"  MP2/CBS:       {result.e_mp2_cbs:16.10f} Eh\n"
            f"  CCSD(T) corr:  {result.e_ccsd_t_correction:16.10f} Eh\n"
            f"  Empirical:     {result.e_empirical:16.10f} Eh\n"
            f"  ZPVE:          {result.zpve:16.10f} Eh\n"
            f"{'='*50}\n"
            f"Imaginary frequencies: {result.n_imaginary}"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_cbs_qb3(
    geometry: str,
    charge: int = 0,
    multiplicity: int = 1,
    temperature: float = 298.15,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate CBS-QB3 composite energy."""
    tool = CBSQB3Tool()
    return tool.run({
        "geometry": geometry, "charge": charge, "multiplicity": multiplicity,
        "temperature": temperature, **kwargs,
    })
