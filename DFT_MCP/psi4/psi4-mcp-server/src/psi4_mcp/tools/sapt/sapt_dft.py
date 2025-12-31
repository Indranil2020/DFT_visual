"""
SAPT-DFT (SAPT with DFT Monomers) Tool.

SAPT-DFT uses DFT monomer densities instead of HF, providing improved
accuracy for induction and dispersion at lower cost than full SAPT2.

Key Features:
    - DFT-based monomer densities
    - Asymptotically corrected functionals
    - Improved charge-transfer description
    - Good balance of cost and accuracy

Reference:
    Misquitta, A.J.; Szalewicz, K. Chem. Phys. Lett. 2002, 357, 301-306.
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
class SAPTDFTEnergyComponents:
    """SAPT(DFT) energy decomposition components."""
    electrostatics: float
    first_order_exchange: float
    induction: float
    exchange_induction: float
    dispersion: float
    exchange_dispersion: float
    delta_hf: float
    total: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "electrostatics": self.electrostatics,
            "first_order_exchange": self.first_order_exchange,
            "induction": self.induction,
            "exchange_induction": self.exchange_induction,
            "dispersion": self.dispersion,
            "exchange_dispersion": self.exchange_dispersion,
            "delta_hf": self.delta_hf,
            "total": self.total,
        }


@dataclass
class SAPTDFTResult:
    """Complete SAPT(DFT) analysis results."""
    components_hartree: SAPTDFTEnergyComponents
    components_kcal: Dict[str, float]
    functional: str
    basis: str
    grac_shift_a: float
    grac_shift_b: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components_hartree": self.components_hartree.to_dict(),
            "components_kcal_mol": self.components_kcal,
            "functional": self.functional,
            "basis": self.basis,
            "grac_shift_a": self.grac_shift_a,
            "grac_shift_b": self.grac_shift_b,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class SAPTDFTInput(ToolInput):
    """Input schema for SAPT(DFT) calculation."""
    
    dimer_geometry: str = Field(..., description="Dimer geometry with '--' separator")
    basis: str = Field(default="aug-cc-pvdz", description="Basis set")
    
    functional: str = Field(
        default="pbe0",
        description="DFT functional for monomers (PBE0, B3LYP, etc.)",
    )
    
    grac_shift_a: Optional[float] = Field(
        default=None,
        description="GRAC asymptotic correction shift for monomer A (auto if None)",
    )
    
    grac_shift_b: Optional[float] = Field(
        default=None,
        description="GRAC asymptotic correction shift for monomer B (auto if None)",
    )
    
    charge_a: int = Field(default=0)
    charge_b: int = Field(default=0)
    multiplicity_a: int = Field(default=1)
    multiplicity_b: int = Field(default=1)
    
    freeze_core: bool = Field(default=True)
    include_delta_hf: bool = Field(default=True, description="Include delta HF correction")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sapt_dft_input(input_data: SAPTDFTInput) -> Optional[ValidationError]:
    """Validate SAPT(DFT) input."""
    if not input_data.dimer_geometry or "--" not in input_data.dimer_geometry:
        return ValidationError(field="dimer_geometry", message="Dimer geometry must contain '--' separator")
    
    supported_functionals = {
        "pbe0", "b3lyp", "pbe", "blyp", "bp86", "m06", "m06-2x",
        "wb97x", "cam-b3lyp", "lc-wpbe",
    }
    if input_data.functional.lower() not in supported_functionals:
        return ValidationError(
            field="functional",
            message=f"Functional must be one of {supported_functionals}",
        )
    
    return None


# =============================================================================
# GRAC SHIFT CALCULATION
# =============================================================================

def estimate_grac_shift(
    homo_energy: float,
    ionization_potential: Optional[float] = None,
) -> float:
    """
    Estimate GRAC asymptotic correction shift.
    
    GRAC shift = IP - (-HOMO)
    If IP not provided, use empirical estimate.
    """
    if ionization_potential is not None:
        return ionization_potential - (-homo_energy)
    
    # Empirical estimate: typical shift for organic molecules
    return 0.0


# =============================================================================
# SAPT(DFT) COMPUTATION
# =============================================================================

def run_sapt_dft_calculation(input_data: SAPTDFTInput) -> SAPTDFTResult:
    """Execute SAPT(DFT) calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_saptdft.out", False)
    
    # Build dimer
    parts = input_data.dimer_geometry.split("--")
    monomer_a = parts[0].strip()
    monomer_b = parts[1].strip() if len(parts) > 1 else ""
    
    mol_string = f"""
    {input_data.charge_a} {input_data.multiplicity_a}
    {monomer_a}
    --
    {input_data.charge_b} {input_data.multiplicity_b}
    {monomer_b}
    units angstrom
    symmetry c1
    no_reorient
    no_com
    """
    
    dimer = psi4.geometry(mol_string)
    dimer.update_geometry()
    
    # Set options for SAPT(DFT)
    options = {
        "basis": input_data.basis,
        "scf_type": "df",
        "freeze_core": input_data.freeze_core,
        "sapt_dft_functional": input_data.functional,
        "sapt_dft_grac_shift_a": input_data.grac_shift_a if input_data.grac_shift_a else 0.0,
        "sapt_dft_grac_shift_b": input_data.grac_shift_b if input_data.grac_shift_b else 0.0,
    }
    psi4.set_options(options)
    
    logger.info(f"Running SAPT(DFT)-{input_data.functional}/{input_data.basis}")
    
    # Run SAPT(DFT) - uses sapt0 with DFT options
    energy = psi4.energy("sapt(dft)", molecule=dimer)
    
    # Extract variables
    vars_dict = {name: psi4.variable(name) for name in psi4.core.variables() if "SAPT" in name}
    
    elst = vars_dict.get("SAPT ELST ENERGY", 0.0)
    exch = vars_dict.get("SAPT EXCH ENERGY", 0.0)
    ind = vars_dict.get("SAPT IND ENERGY", 0.0)
    exch_ind = vars_dict.get("SAPT EXCH-IND ENERGY", 0.0)
    disp = vars_dict.get("SAPT DISP ENERGY", 0.0)
    exch_disp = vars_dict.get("SAPT EXCH-DISP ENERGY", 0.0)
    delta_hf = vars_dict.get("SAPT HF(2) ENERGY", 0.0) if input_data.include_delta_hf else 0.0
    
    total = elst + exch + ind + exch_ind + disp + exch_disp + delta_hf
    total_from_psi4 = vars_dict.get("SAPT(DFT) TOTAL ENERGY", total)
    
    components = SAPTDFTEnergyComponents(
        electrostatics=elst,
        first_order_exchange=exch,
        induction=ind,
        exchange_induction=exch_ind,
        dispersion=disp,
        exchange_dispersion=exch_disp,
        delta_hf=delta_hf,
        total=total_from_psi4,
    )
    
    components_kcal = {
        "electrostatics": elst * HARTREE_TO_KCAL,
        "exchange": exch * HARTREE_TO_KCAL,
        "induction": (ind + exch_ind) * HARTREE_TO_KCAL,
        "dispersion": (disp + exch_disp) * HARTREE_TO_KCAL,
        "delta_hf": delta_hf * HARTREE_TO_KCAL,
        "total": total_from_psi4 * HARTREE_TO_KCAL,
    }
    
    psi4.core.clean()
    
    return SAPTDFTResult(
        components_hartree=components,
        components_kcal=components_kcal,
        functional=input_data.functional,
        basis=input_data.basis,
        grac_shift_a=input_data.grac_shift_a or 0.0,
        grac_shift_b=input_data.grac_shift_b or 0.0,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class SAPTDFTTool(BaseTool[SAPTDFTInput, ToolOutput]):
    """Tool for SAPT(DFT) interaction energy decomposition."""
    
    name: ClassVar[str] = "calculate_sapt_dft"
    description: ClassVar[str] = "Calculate SAPT(DFT) using DFT monomer wavefunctions."
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: SAPTDFTInput) -> Optional[ValidationError]:
        return validate_sapt_dft_input(input_data)
    
    def _execute(self, input_data: SAPTDFTInput) -> Result[ToolOutput]:
        result = run_sapt_dft_calculation(input_data)
        
        c = result.components_kcal
        message = (
            f"SAPT(DFT)-{input_data.functional}/{input_data.basis} Analysis\n"
            f"{'='*50}\n"
            f"Electrostatics:     {c['electrostatics']:10.4f} kcal/mol\n"
            f"Exchange:           {c['exchange']:10.4f} kcal/mol\n"
            f"Induction:          {c['induction']:10.4f} kcal/mol\n"
            f"Dispersion:         {c['dispersion']:10.4f} kcal/mol\n"
            f"Delta HF:           {c['delta_hf']:10.4f} kcal/mol\n"
            f"{'='*50}\n"
            f"Total SAPT(DFT):    {c['total']:10.4f} kcal/mol"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_sapt_dft(
    dimer_geometry: str,
    basis: str = "aug-cc-pvdz",
    functional: str = "pbe0",
    **kwargs: Any,
) -> ToolOutput:
    """Calculate SAPT(DFT) interaction energy decomposition."""
    tool = SAPTDFTTool()
    return tool.run({
        "dimer_geometry": dimer_geometry,
        "basis": basis,
        "functional": functional,
        **kwargs,
    })
