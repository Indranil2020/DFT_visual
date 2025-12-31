"""
SAPT0 Interaction Energy Decomposition Tool.

SAPT0 is the lowest level of Symmetry-Adapted Perturbation Theory,
providing fast interaction energy decomposition using HF-level monomer
wavefunctions.

Key Features:
    - Electrostatic, exchange, induction, and dispersion components
    - Fast for large systems
    - HF-level accuracy for monomers
    - Suitable for screening studies

Reference:
    Jeziorski, B.; Moszynski, R.; Szalewicz, K. Chem. Rev. 1994, 94, 1887.
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


# =============================================================================
# CONSTANTS
# =============================================================================

HARTREE_TO_KCAL = 627.5094740631
HARTREE_TO_KJ = 2625.4996394799


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SAPT0EnergyComponents:
    """SAPT0 energy decomposition components."""
    electrostatics: float
    exchange: float
    induction: float
    exchange_induction: float
    dispersion: float
    exchange_dispersion: float
    total: float
    
    # Grouped terms
    total_electrostatics: float
    total_exchange: float
    total_induction: float
    total_dispersion: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "electrostatics": self.electrostatics,
            "exchange": self.exchange,
            "induction": self.induction,
            "exchange_induction": self.exchange_induction,
            "dispersion": self.dispersion,
            "exchange_dispersion": self.exchange_dispersion,
            "total": self.total,
            "total_electrostatics": self.total_electrostatics,
            "total_exchange": self.total_exchange,
            "total_induction": self.total_induction,
            "total_dispersion": self.total_dispersion,
        }


@dataclass
class SAPT0Result:
    """Complete SAPT0 analysis results."""
    components_hartree: SAPT0EnergyComponents
    components_kcal: SAPT0EnergyComponents
    components_kj: SAPT0EnergyComponents
    monomer_a_energy: float
    monomer_b_energy: float
    dimer_energy: float
    basis: str
    n_basis_functions: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "components_hartree": self.components_hartree.to_dict(),
            "components_kcal_mol": self.components_kcal.to_dict(),
            "components_kj_mol": self.components_kj.to_dict(),
            "monomer_a_energy": self.monomer_a_energy,
            "monomer_b_energy": self.monomer_b_energy,
            "dimer_energy": self.dimer_energy,
            "basis": self.basis,
            "n_basis_functions": self.n_basis_functions,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class SAPT0Input(ToolInput):
    """Input schema for SAPT0 calculation."""
    
    dimer_geometry: str = Field(
        ...,
        description="Dimer geometry with monomers separated by '--' line",
    )
    
    basis: str = Field(
        default="jun-cc-pvdz",
        description="Basis set (jun-cc-pvdz recommended for SAPT0)",
    )
    
    charge_a: int = Field(default=0, description="Charge of monomer A")
    charge_b: int = Field(default=0, description="Charge of monomer B")
    multiplicity_a: int = Field(default=1, description="Multiplicity of monomer A")
    multiplicity_b: int = Field(default=1, description="Multiplicity of monomer B")
    
    freeze_core: bool = Field(
        default=True,
        description="Freeze core electrons",
    )
    
    density_fitting: bool = Field(
        default=True,
        description="Use density fitting for efficiency",
    )
    
    memory: int = Field(default=4000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# VALIDATION
# =============================================================================

def validate_sapt0_input(input_data: SAPT0Input) -> Optional[ValidationError]:
    """Validate SAPT0 input."""
    if not input_data.dimer_geometry or not input_data.dimer_geometry.strip():
        return ValidationError(field="dimer_geometry", message="Dimer geometry cannot be empty")
    
    if "--" not in input_data.dimer_geometry:
        return ValidationError(
            field="dimer_geometry",
            message="Dimer geometry must contain '--' separator between monomers",
        )
    
    return None


def parse_dimer_geometry(geometry: str) -> Tuple[str, str]:
    """Parse dimer geometry into two monomers."""
    parts = geometry.split("--")
    if len(parts) != 2:
        return geometry, ""
    return parts[0].strip(), parts[1].strip()


# =============================================================================
# SAPT0 COMPUTATION
# =============================================================================

def extract_sapt0_components(variables: Dict[str, float]) -> SAPT0EnergyComponents:
    """Extract SAPT0 energy components from Psi4 variables."""
    
    # Core components
    elst = variables.get("SAPT ELST10,R ENERGY", 0.0)
    exch = variables.get("SAPT EXCH10 ENERGY", 0.0)
    ind = variables.get("SAPT IND20,R ENERGY", 0.0)
    exch_ind = variables.get("SAPT EXCH-IND20,R ENERGY", 0.0)
    disp = variables.get("SAPT DISP20 ENERGY", 0.0)
    exch_disp = variables.get("SAPT EXCH-DISP20 ENERGY", 0.0)
    
    # Total
    total = variables.get("SAPT0 TOTAL ENERGY", 0.0)
    if total == 0.0:
        total = elst + exch + ind + exch_ind + disp + exch_disp
    
    # Grouped terms
    total_elst = elst
    total_exch = exch
    total_ind = ind + exch_ind
    total_disp = disp + exch_disp
    
    return SAPT0EnergyComponents(
        electrostatics=elst,
        exchange=exch,
        induction=ind,
        exchange_induction=exch_ind,
        dispersion=disp,
        exchange_dispersion=exch_disp,
        total=total,
        total_electrostatics=total_elst,
        total_exchange=total_exch,
        total_induction=total_ind,
        total_dispersion=total_disp,
    )


def convert_components(components: SAPT0EnergyComponents, factor: float) -> SAPT0EnergyComponents:
    """Convert energy components by a factor."""
    return SAPT0EnergyComponents(
        electrostatics=components.electrostatics * factor,
        exchange=components.exchange * factor,
        induction=components.induction * factor,
        exchange_induction=components.exchange_induction * factor,
        dispersion=components.dispersion * factor,
        exchange_dispersion=components.exchange_dispersion * factor,
        total=components.total * factor,
        total_electrostatics=components.total_electrostatics * factor,
        total_exchange=components.total_exchange * factor,
        total_induction=components.total_induction * factor,
        total_dispersion=components.total_dispersion * factor,
    )


def run_sapt0_calculation(
    dimer_geometry: str,
    basis: str,
    charge_a: int,
    charge_b: int,
    mult_a: int,
    mult_b: int,
    freeze_core: bool,
    density_fitting: bool,
    memory: int,
    n_threads: int,
) -> SAPT0Result:
    """Execute SAPT0 calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{memory} MB")
    psi4.set_num_threads(n_threads)
    psi4.core.set_output_file("psi4_sapt0.out", False)
    
    # Parse monomers
    monomer_a, monomer_b = parse_dimer_geometry(dimer_geometry)
    
    # Build dimer molecule with fragment specification
    total_charge = charge_a + charge_b
    # For dimer, multiplicity is complex - use singlet for closed-shell
    dimer_mult = 1 if (mult_a == 1 and mult_b == 1) else mult_a
    
    mol_string = f"""
    {charge_a} {mult_a}
    {monomer_a}
    --
    {charge_b} {mult_b}
    {monomer_b}
    units angstrom
    symmetry c1
    no_reorient
    no_com
    """
    
    dimer = psi4.geometry(mol_string)
    dimer.update_geometry()
    
    # Set options
    psi4.set_options({
        "basis": basis,
        "freeze_core": freeze_core,
        "guess": "sad",
        "scf_type": "df" if density_fitting else "pk",
    })
    
    # Run SAPT0
    logger.info(f"Running SAPT0/{basis}")
    energy = psi4.energy("sapt0", molecule=dimer)
    
    # Extract all SAPT variables
    all_vars = {}
    for var_name in psi4.core.variables():
        if "SAPT" in var_name:
            all_vars[var_name] = psi4.variable(var_name)
    
    # Get monomer energies
    monomer_a_energy = psi4.variable("SAPT HF(A) TOTAL ENERGY")
    monomer_b_energy = psi4.variable("SAPT HF(B) TOTAL ENERGY")
    dimer_energy = energy
    
    # Extract components
    components_hartree = extract_sapt0_components(all_vars)
    components_kcal = convert_components(components_hartree, HARTREE_TO_KCAL)
    components_kj = convert_components(components_hartree, HARTREE_TO_KJ)
    
    # Get basis info
    n_bf = dimer.nbf() if hasattr(dimer, 'nbf') else 0
    
    psi4.core.clean()
    
    return SAPT0Result(
        components_hartree=components_hartree,
        components_kcal=components_kcal,
        components_kj=components_kj,
        monomer_a_energy=float(monomer_a_energy),
        monomer_b_energy=float(monomer_b_energy),
        dimer_energy=float(dimer_energy),
        basis=basis,
        n_basis_functions=n_bf,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class SAPT0Tool(BaseTool[SAPT0Input, ToolOutput]):
    """
    Tool for SAPT0 interaction energy decomposition.
    
    SAPT0 provides the fastest SAPT calculation, suitable for
    initial screening of intermolecular interactions.
    """
    
    name: ClassVar[str] = "calculate_sapt0"
    description: ClassVar[str] = (
        "Calculate SAPT0 interaction energy decomposition into "
        "electrostatic, exchange, induction, and dispersion components."
    )
    category: ClassVar[ToolCategory] = ToolCategory.INTERMOLECULAR
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: SAPT0Input) -> Optional[ValidationError]:
        return validate_sapt0_input(input_data)
    
    def _execute(self, input_data: SAPT0Input) -> Result[ToolOutput]:
        result = run_sapt0_calculation(
            dimer_geometry=input_data.dimer_geometry,
            basis=input_data.basis,
            charge_a=input_data.charge_a,
            charge_b=input_data.charge_b,
            mult_a=input_data.multiplicity_a,
            mult_b=input_data.multiplicity_b,
            freeze_core=input_data.freeze_core,
            density_fitting=input_data.density_fitting,
            memory=input_data.memory,
            n_threads=input_data.n_threads,
        )
        
        c = result.components_kcal
        message = (
            f"SAPT0/{input_data.basis} Interaction Energy Decomposition\n"
            f"{'='*50}\n"
            f"Electrostatics:     {c.electrostatics:10.4f} kcal/mol\n"
            f"Exchange:           {c.exchange:10.4f} kcal/mol\n"
            f"Induction:          {c.total_induction:10.4f} kcal/mol\n"
            f"Dispersion:         {c.total_dispersion:10.4f} kcal/mol\n"
            f"{'='*50}\n"
            f"Total SAPT0:        {c.total:10.4f} kcal/mol"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_sapt0(
    dimer_geometry: str,
    basis: str = "jun-cc-pvdz",
    charge_a: int = 0,
    charge_b: int = 0,
    multiplicity_a: int = 1,
    multiplicity_b: int = 1,
    freeze_core: bool = True,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate SAPT0 interaction energy decomposition.
    
    Args:
        dimer_geometry: Dimer geometry with '--' separator.
        basis: Basis set (jun-cc-pvdz recommended).
        charge_a: Charge of monomer A.
        charge_b: Charge of monomer B.
        multiplicity_a: Multiplicity of monomer A.
        multiplicity_b: Multiplicity of monomer B.
        freeze_core: Freeze core electrons.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with SAPT0 energy decomposition.
        
    Example:
        >>> result = calculate_sapt0(
        ...     dimer_geometry=\"\"\"
        ...     O  0.000  0.000  0.117
        ...     H -0.756  0.000 -0.468
        ...     H  0.756  0.000 -0.468
        ...     --
        ...     O  3.000  0.000  0.117
        ...     H  2.244  0.000 -0.468
        ...     H  3.756  0.000 -0.468
        ...     \"\"\",
        ...     basis="jun-cc-pvdz"
        ... )
    """
    tool = SAPT0Tool()
    input_data = {
        "dimer_geometry": dimer_geometry, "basis": basis,
        "charge_a": charge_a, "charge_b": charge_b,
        "multiplicity_a": multiplicity_a, "multiplicity_b": multiplicity_b,
        "freeze_core": freeze_core, **kwargs,
    }
    return tool.run(input_data)
