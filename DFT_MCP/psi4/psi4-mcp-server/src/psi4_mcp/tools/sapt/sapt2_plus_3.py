"""
SAPT2+(3) Interaction Energy Decomposition Tool.

SAPT2+(3) adds third-order dispersion and induction corrections to SAPT2+,
providing benchmark-quality interaction energies.

Key Features:
    - Third-order perturbation corrections
    - High-accuracy dispersion
    - Suitable for benchmark studies
    - Near-CCSD(T) accuracy for many systems

Reference:
    Hohenstein, E.G.; Sherrill, C.D. J. Chem. Phys. 2010, 133, 014101.
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
class SAPT2Plus3EnergyComponents:
    """SAPT2+(3) energy decomposition components."""
    electrostatics: float
    exchange: float
    induction: float
    dispersion: float
    total: float
    
    # Third-order terms
    elst13: float
    ind30: float
    exch_ind30: float
    disp30: float
    
    # Delta HF correction
    delta_hf: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "electrostatics": self.electrostatics,
            "exchange": self.exchange,
            "induction": self.induction,
            "dispersion": self.dispersion,
            "total": self.total,
            "elst13": self.elst13,
            "ind30": self.ind30,
            "exch_ind30": self.exch_ind30,
            "disp30": self.disp30,
            "delta_hf": self.delta_hf,
        }


@dataclass
class SAPT2Plus3Result:
    """Complete SAPT2+(3) analysis results."""
    components_hartree: SAPT2Plus3EnergyComponents
    components_kcal: Dict[str, float]
    sapt2_plus_total: float
    sapt2_plus_3_total: float
    third_order_correction: float
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components_hartree": self.components_hartree.to_dict(),
            "components_kcal_mol": self.components_kcal,
            "sapt2_plus_total_kcal": self.sapt2_plus_total * HARTREE_TO_KCAL,
            "sapt2_plus_3_total_kcal": self.sapt2_plus_3_total * HARTREE_TO_KCAL,
            "third_order_correction_kcal": self.third_order_correction * HARTREE_TO_KCAL,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class SAPT2Plus3Input(ToolInput):
    """Input schema for SAPT2+(3) calculation."""
    
    dimer_geometry: str = Field(..., description="Dimer geometry with '--' separator")
    basis: str = Field(default="aug-cc-pvdz", description="Basis set")
    charge_a: int = Field(default=0)
    charge_b: int = Field(default=0)
    multiplicity_a: int = Field(default=1)
    multiplicity_b: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    include_delta_hf: bool = Field(default=True, description="Include delta HF correction")
    memory: int = Field(default=8000, description="Memory (more needed for 3rd order)")
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sapt2_plus_3_input(input_data: SAPT2Plus3Input) -> Optional[ValidationError]:
    """Validate SAPT2+(3) input."""
    if not input_data.dimer_geometry or "--" not in input_data.dimer_geometry:
        return ValidationError(
            field="dimer_geometry",
            message="Dimer geometry must contain '--' separator",
        )
    return None


# =============================================================================
# SAPT2+(3) COMPUTATION
# =============================================================================

def run_sapt2_plus_3_calculation(input_data: SAPT2Plus3Input) -> SAPT2Plus3Result:
    """Execute SAPT2+(3) calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_sapt2plus3.out", False)
    
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
    
    psi4.set_options({
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "scf_type": "df",
    })
    
    # Run SAPT2+(3)
    logger.info(f"Running SAPT2+(3)/{input_data.basis}")
    energy = psi4.energy("sapt2+(3)", molecule=dimer)
    
    # Extract variables
    vars_dict = {name: psi4.variable(name) for name in psi4.core.variables() if "SAPT" in name}
    
    # Second-order terms (from SAPT2+)
    elst10 = vars_dict.get("SAPT ELST10,R ENERGY", 0.0)
    elst12 = vars_dict.get("SAPT ELST12,R ENERGY", 0.0)
    exch10 = vars_dict.get("SAPT EXCH10 ENERGY", 0.0)
    exch11 = vars_dict.get("SAPT EXCH11(S^2) ENERGY", 0.0)
    exch12 = vars_dict.get("SAPT EXCH12(S^2) ENERGY", 0.0)
    ind20 = vars_dict.get("SAPT IND20,R ENERGY", 0.0)
    exch_ind20 = vars_dict.get("SAPT EXCH-IND20,R ENERGY", 0.0)
    ind22 = vars_dict.get("SAPT IND22 ENERGY", 0.0)
    disp20 = vars_dict.get("SAPT DISP20 ENERGY", 0.0)
    exch_disp20 = vars_dict.get("SAPT EXCH-DISP20 ENERGY", 0.0)
    disp22_sdq = vars_dict.get("SAPT DISP2(SDQ) ENERGY", 0.0)
    disp22_t = vars_dict.get("SAPT DISP22(T) ENERGY", 0.0)
    
    # Third-order terms
    elst13 = vars_dict.get("SAPT ELST13,R ENERGY", 0.0)
    ind30 = vars_dict.get("SAPT IND30,R ENERGY", 0.0)
    exch_ind30 = vars_dict.get("SAPT EXCH-IND30,R ENERGY", 0.0)
    disp30 = vars_dict.get("SAPT DISP30 ENERGY", 0.0)
    
    # Delta HF
    delta_hf = vars_dict.get("SAPT HF(2) ENERGY", 0.0) if input_data.include_delta_hf else 0.0
    
    # Compute totals
    electrostatics = elst10 + elst12 + elst13
    exchange = exch10 + exch11 + exch12
    induction = ind20 + exch_ind20 + ind22 + ind30 + exch_ind30 + delta_hf
    dispersion = disp20 + exch_disp20 + disp22_sdq + disp22_t + disp30
    total = electrostatics + exchange + induction + dispersion
    
    sapt2_plus_total = vars_dict.get("SAPT2+ TOTAL ENERGY", 0.0)
    sapt2_plus_3_total = vars_dict.get("SAPT2+(3) TOTAL ENERGY", total)
    
    components = SAPT2Plus3EnergyComponents(
        electrostatics=electrostatics,
        exchange=exchange,
        induction=induction,
        dispersion=dispersion,
        total=total,
        elst13=elst13,
        ind30=ind30,
        exch_ind30=exch_ind30,
        disp30=disp30,
        delta_hf=delta_hf,
    )
    
    components_kcal = {
        "electrostatics": electrostatics * HARTREE_TO_KCAL,
        "exchange": exchange * HARTREE_TO_KCAL,
        "induction": induction * HARTREE_TO_KCAL,
        "dispersion": dispersion * HARTREE_TO_KCAL,
        "total": total * HARTREE_TO_KCAL,
    }
    
    psi4.core.clean()
    
    return SAPT2Plus3Result(
        components_hartree=components,
        components_kcal=components_kcal,
        sapt2_plus_total=sapt2_plus_total,
        sapt2_plus_3_total=sapt2_plus_3_total,
        third_order_correction=sapt2_plus_3_total - sapt2_plus_total,
        basis=input_data.basis,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class SAPT2Plus3Tool(BaseTool[SAPT2Plus3Input, ToolOutput]):
    """Tool for SAPT2+(3) interaction energy decomposition."""
    
    name: ClassVar[str] = "calculate_sapt2_plus_3"
    description: ClassVar[str] = "Calculate SAPT2+(3) with third-order perturbation corrections."
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: SAPT2Plus3Input) -> Optional[ValidationError]:
        return validate_sapt2_plus_3_input(input_data)
    
    def _execute(self, input_data: SAPT2Plus3Input) -> Result[ToolOutput]:
        result = run_sapt2_plus_3_calculation(input_data)
        
        c = result.components_kcal
        message = (
            f"SAPT2+(3)/{input_data.basis} Interaction Energy Decomposition\n"
            f"{'='*50}\n"
            f"Electrostatics:     {c['electrostatics']:10.4f} kcal/mol\n"
            f"Exchange:           {c['exchange']:10.4f} kcal/mol\n"
            f"Induction:          {c['induction']:10.4f} kcal/mol\n"
            f"Dispersion:         {c['dispersion']:10.4f} kcal/mol\n"
            f"{'='*50}\n"
            f"Total SAPT2+(3):    {c['total']:10.4f} kcal/mol"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_sapt2_plus_3(
    dimer_geometry: str,
    basis: str = "aug-cc-pvdz",
    charge_a: int = 0,
    charge_b: int = 0,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate SAPT2+(3) interaction energy decomposition."""
    tool = SAPT2Plus3Tool()
    input_data = {
        "dimer_geometry": dimer_geometry, "basis": basis,
        "charge_a": charge_a, "charge_b": charge_b, **kwargs,
    }
    return tool.run(input_data)
