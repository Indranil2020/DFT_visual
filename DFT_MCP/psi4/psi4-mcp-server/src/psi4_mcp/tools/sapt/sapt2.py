"""
SAPT2 Interaction Energy Decomposition Tool.

SAPT2 includes second-order correlation effects in the monomer
wavefunctions, providing improved accuracy over SAPT0.

Key Features:
    - MP2-level correlation for monomers
    - Improved induction and dispersion
    - Second-order exchange corrections
    - Charge-transfer analysis

Reference:
    Hohenstein, E.G.; Sherrill, C.D. WIREs Comput. Mol. Sci. 2012, 2, 304-326.
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
class SAPT2EnergyComponents:
    """SAPT2 energy decomposition components."""
    # First-order
    elst10: float
    exch10: float
    
    # Second-order induction
    ind20: float
    exch_ind20: float
    
    # Second-order dispersion
    disp20: float
    exch_disp20: float
    
    # SAPT2 corrections
    elst12: float
    exch11: float
    exch12: float
    ind22: float
    disp21: float
    
    # Totals
    total_electrostatics: float
    total_exchange: float
    total_induction: float
    total_dispersion: float
    total: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "elst10": self.elst10,
            "exch10": self.exch10,
            "ind20": self.ind20,
            "exch_ind20": self.exch_ind20,
            "disp20": self.disp20,
            "exch_disp20": self.exch_disp20,
            "elst12": self.elst12,
            "exch11": self.exch11,
            "exch12": self.exch12,
            "ind22": self.ind22,
            "disp21": self.disp21,
            "total_electrostatics": self.total_electrostatics,
            "total_exchange": self.total_exchange,
            "total_induction": self.total_induction,
            "total_dispersion": self.total_dispersion,
            "total": self.total,
        }


@dataclass
class SAPT2Result:
    """Complete SAPT2 analysis results."""
    components_hartree: SAPT2EnergyComponents
    components_kcal: Dict[str, float]
    sapt0_total: float
    sapt2_total: float
    correlation_correction: float
    basis: str
    method: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components_hartree": self.components_hartree.to_dict(),
            "components_kcal_mol": self.components_kcal,
            "sapt0_total_kcal": self.sapt0_total * HARTREE_TO_KCAL,
            "sapt2_total_kcal": self.sapt2_total * HARTREE_TO_KCAL,
            "correlation_correction_kcal": self.correlation_correction * HARTREE_TO_KCAL,
            "basis": self.basis,
            "method": self.method,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class SAPT2Input(ToolInput):
    """Input schema for SAPT2 calculation."""
    
    dimer_geometry: str = Field(
        ...,
        description="Dimer geometry with monomers separated by '--' line",
    )
    
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set (augmented basis recommended)",
    )
    
    charge_a: int = Field(default=0)
    charge_b: int = Field(default=0)
    multiplicity_a: int = Field(default=1)
    multiplicity_b: int = Field(default=1)
    
    freeze_core: bool = Field(default=True)
    
    nat_orbs: bool = Field(
        default=False,
        description="Use natural orbitals for correlation",
    )
    
    nat_orbs_cutoff: float = Field(
        default=1e-6,
        description="Cutoff for natural orbital truncation",
    )
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sapt2_input(input_data: SAPT2Input) -> Optional[ValidationError]:
    """Validate SAPT2 input."""
    if not input_data.dimer_geometry or "--" not in input_data.dimer_geometry:
        return ValidationError(
            field="dimer_geometry",
            message="Dimer geometry must contain '--' separator between monomers",
        )
    return None


# =============================================================================
# SAPT2 COMPUTATION
# =============================================================================

def extract_sapt2_components(variables: Dict[str, float]) -> SAPT2EnergyComponents:
    """Extract SAPT2 energy components from Psi4 variables."""
    
    # First-order terms
    elst10 = variables.get("SAPT ELST10,R ENERGY", 0.0)
    exch10 = variables.get("SAPT EXCH10 ENERGY", 0.0)
    
    # Second-order induction
    ind20 = variables.get("SAPT IND20,R ENERGY", 0.0)
    exch_ind20 = variables.get("SAPT EXCH-IND20,R ENERGY", 0.0)
    
    # Second-order dispersion
    disp20 = variables.get("SAPT DISP20 ENERGY", 0.0)
    exch_disp20 = variables.get("SAPT EXCH-DISP20 ENERGY", 0.0)
    
    # SAPT2 corrections
    elst12 = variables.get("SAPT ELST12,R ENERGY", 0.0)
    exch11 = variables.get("SAPT EXCH11(S^2) ENERGY", 0.0)
    exch12 = variables.get("SAPT EXCH12(S^2) ENERGY", 0.0)
    ind22 = variables.get("SAPT IND22 ENERGY", 0.0)
    disp21 = variables.get("SAPT DISP21 ENERGY", 0.0)
    
    # Compute totals
    total_elst = elst10 + elst12
    total_exch = exch10 + exch11 + exch12
    total_ind = ind20 + exch_ind20 + ind22
    total_disp = disp20 + exch_disp20 + disp21
    
    total = total_elst + total_exch + total_ind + total_disp
    
    return SAPT2EnergyComponents(
        elst10=elst10, exch10=exch10,
        ind20=ind20, exch_ind20=exch_ind20,
        disp20=disp20, exch_disp20=exch_disp20,
        elst12=elst12, exch11=exch11, exch12=exch12,
        ind22=ind22, disp21=disp21,
        total_electrostatics=total_elst,
        total_exchange=total_exch,
        total_induction=total_ind,
        total_dispersion=total_disp,
        total=total,
    )


def run_sapt2_calculation(input_data: SAPT2Input) -> SAPT2Result:
    """Execute SAPT2 calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_sapt2.out", False)
    
    # Build dimer molecule
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
    
    # Set options
    options = {
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "scf_type": "df",
    }
    
    if input_data.nat_orbs:
        options["nat_orbs_t2"] = True
        options["occ_tolerance"] = input_data.nat_orbs_cutoff
    
    psi4.set_options(options)
    
    # Run SAPT2
    logger.info(f"Running SAPT2/{input_data.basis}")
    energy = psi4.energy("sapt2", molecule=dimer)
    
    # Extract variables
    all_vars = {name: psi4.variable(name) for name in psi4.core.variables() if "SAPT" in name}
    
    components = extract_sapt2_components(all_vars)
    
    # SAPT0 total for comparison
    sapt0_total = all_vars.get("SAPT0 TOTAL ENERGY", 0.0)
    sapt2_total = all_vars.get("SAPT2 TOTAL ENERGY", components.total)
    
    # Convert to kcal/mol
    components_kcal = {
        "electrostatics": components.total_electrostatics * HARTREE_TO_KCAL,
        "exchange": components.total_exchange * HARTREE_TO_KCAL,
        "induction": components.total_induction * HARTREE_TO_KCAL,
        "dispersion": components.total_dispersion * HARTREE_TO_KCAL,
        "total": components.total * HARTREE_TO_KCAL,
    }
    
    psi4.core.clean()
    
    return SAPT2Result(
        components_hartree=components,
        components_kcal=components_kcal,
        sapt0_total=sapt0_total,
        sapt2_total=sapt2_total,
        correlation_correction=sapt2_total - sapt0_total,
        basis=input_data.basis,
        method="SAPT2",
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class SAPT2Tool(BaseTool[SAPT2Input, ToolOutput]):
    """Tool for SAPT2 interaction energy decomposition."""
    
    name: ClassVar[str] = "calculate_sapt2"
    description: ClassVar[str] = (
        "Calculate SAPT2 interaction energy decomposition with "
        "MP2-level correlation in monomers."
    )
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: SAPT2Input) -> Optional[ValidationError]:
        return validate_sapt2_input(input_data)
    
    def _execute(self, input_data: SAPT2Input) -> Result[ToolOutput]:
        result = run_sapt2_calculation(input_data)
        
        c = result.components_kcal
        message = (
            f"SAPT2/{input_data.basis} Interaction Energy Decomposition\n"
            f"{'='*50}\n"
            f"Electrostatics:     {c['electrostatics']:10.4f} kcal/mol\n"
            f"Exchange:           {c['exchange']:10.4f} kcal/mol\n"
            f"Induction:          {c['induction']:10.4f} kcal/mol\n"
            f"Dispersion:         {c['dispersion']:10.4f} kcal/mol\n"
            f"{'='*50}\n"
            f"Total SAPT2:        {c['total']:10.4f} kcal/mol\n"
            f"Correlation corr.:  {result.correlation_correction * HARTREE_TO_KCAL:10.4f} kcal/mol"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_sapt2(
    dimer_geometry: str,
    basis: str = "aug-cc-pvdz",
    charge_a: int = 0,
    charge_b: int = 0,
    multiplicity_a: int = 1,
    multiplicity_b: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate SAPT2 interaction energy decomposition.
    
    Args:
        dimer_geometry: Dimer geometry with '--' separator.
        basis: Basis set (augmented basis recommended).
        charge_a: Charge of monomer A.
        charge_b: Charge of monomer B.
        multiplicity_a: Multiplicity of monomer A.
        multiplicity_b: Multiplicity of monomer B.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with SAPT2 energy decomposition.
    """
    tool = SAPT2Tool()
    input_data = {
        "dimer_geometry": dimer_geometry, "basis": basis,
        "charge_a": charge_a, "charge_b": charge_b,
        "multiplicity_a": multiplicity_a, "multiplicity_b": multiplicity_b,
        **kwargs,
    }
    return tool.run(input_data)
