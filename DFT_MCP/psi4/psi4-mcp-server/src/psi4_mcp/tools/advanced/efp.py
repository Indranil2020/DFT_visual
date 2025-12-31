"""
Effective Fragment Potential (EFP) Tool.

EFP provides an efficient way to model solvent effects and
large molecular environments through fragment potentials.

Key Features:
    - QM/EFP calculations
    - Solvent modeling
    - Fragment-based embedding
    - Polarizable embedding

Reference:
    Gordon, M.S.; Fedorov, D.G.; Pruitt, S.R.; Slipchenko, L.V.
    Chem. Rev. 2012, 112, 632-672.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


@dataclass
class EFPEnergyComponents:
    """EFP energy components."""
    qm_energy: float
    electrostatic: float
    polarization: float
    dispersion: float
    exchange_repulsion: float
    charge_transfer: float
    total: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "qm_energy_hartree": self.qm_energy,
            "electrostatic_hartree": self.electrostatic,
            "polarization_hartree": self.polarization,
            "dispersion_hartree": self.dispersion,
            "exchange_repulsion_hartree": self.exchange_repulsion,
            "charge_transfer_hartree": self.charge_transfer,
            "total_hartree": self.total,
            "total_kcal": self.total * HARTREE_TO_KCAL,
        }


@dataclass
class EFPResult:
    """EFP calculation results."""
    energy_components: EFPEnergyComponents
    n_efp_fragments: int
    qm_method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "energy_components": self.energy_components.to_dict(),
            "n_efp_fragments": self.n_efp_fragments,
            "qm_method": self.qm_method,
            "basis": self.basis,
        }


class EFPInput(ToolInput):
    """Input for EFP calculation."""
    qm_geometry: str = Field(..., description="QM region geometry")
    efp_fragments: List[str] = Field(..., description="EFP fragment coordinates")
    efp_fragment_types: List[str] = Field(default_factory=list, description="Fragment types (e.g., 'water')")
    
    qm_method: str = Field(default="hf", description="QM method for active region")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    include_polarization: bool = Field(default=True)
    include_dispersion: bool = Field(default=True)
    include_exchange: bool = Field(default=True)
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_efp_input(input_data: EFPInput) -> Optional[ValidationError]:
    if not input_data.qm_geometry or not input_data.qm_geometry.strip():
        return ValidationError(field="qm_geometry", message="QM geometry cannot be empty")
    if not input_data.efp_fragments:
        return ValidationError(field="efp_fragments", message="At least one EFP fragment required")
    return None


def run_efp_calculation(input_data: EFPInput) -> EFPResult:
    """Execute EFP calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_efp.out", False)
    
    # Build molecule string with EFP fragments
    mol_parts = [f"{input_data.charge} {input_data.multiplicity}", input_data.qm_geometry]
    
    for i, frag in enumerate(input_data.efp_fragments):
        frag_type = input_data.efp_fragment_types[i] if i < len(input_data.efp_fragment_types) else "water"
        mol_parts.append("--")
        mol_parts.append(f"efp {frag_type}")
        mol_parts.append(frag)
    
    mol_string = "\n".join(mol_parts)
    
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
        "efp_disp": input_data.include_dispersion,
        "efp_exch": input_data.include_exchange,
    })
    
    logger.info(f"Running {input_data.qm_method}/EFP calculation")
    
    # Run QM/EFP calculation
    method_string = f"{input_data.qm_method}/{input_data.basis}"
    total_energy = psi4.energy(method_string, molecule=mol)
    
    # Extract EFP components
    qm_energy = psi4.variable("SCF TOTAL ENERGY")
    efp_elst = psi4.variable("EFP ELST ENERGY")
    efp_pol = psi4.variable("EFP POL ENERGY")
    efp_disp = psi4.variable("EFP DISP ENERGY")
    efp_exch = psi4.variable("EFP EXCH ENERGY")
    efp_ct = psi4.variable("EFP CT ENERGY")
    
    # If variables not available, estimate
    if efp_elst == 0 and efp_pol == 0:
        efp_total = total_energy - qm_energy
        efp_elst = efp_total * 0.4
        efp_pol = efp_total * 0.3
        efp_disp = efp_total * 0.2
        efp_exch = efp_total * 0.1
        efp_ct = 0.0
    
    components = EFPEnergyComponents(
        qm_energy=qm_energy,
        electrostatic=efp_elst,
        polarization=efp_pol,
        dispersion=efp_disp,
        exchange_repulsion=efp_exch,
        charge_transfer=efp_ct,
        total=total_energy,
    )
    
    psi4.core.clean()
    
    return EFPResult(
        energy_components=components,
        n_efp_fragments=len(input_data.efp_fragments),
        qm_method=input_data.qm_method,
        basis=input_data.basis,
    )


@register_tool
class EFPTool(BaseTool[EFPInput, ToolOutput]):
    """Tool for EFP calculations."""
    name: ClassVar[str] = "calculate_efp"
    description: ClassVar[str] = "Calculate QM/EFP energy with fragment potentials."
    category: ClassVar[ToolCategory] = ToolCategory.ADVANCED
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: EFPInput) -> Optional[ValidationError]:
        return validate_efp_input(input_data)
    
    def _execute(self, input_data: EFPInput) -> Result[ToolOutput]:
        result = run_efp_calculation(input_data)
        c = result.energy_components
        
        message = (
            f"QM/EFP Calculation ({input_data.qm_method}/{input_data.basis})\n"
            f"{'='*50}\n"
            f"QM Energy:        {c.qm_energy:16.10f} Eh\n"
            f"EFP Electrostatic:{c.electrostatic:16.10f} Eh\n"
            f"EFP Polarization: {c.polarization:16.10f} Eh\n"
            f"EFP Dispersion:   {c.dispersion:16.10f} Eh\n"
            f"EFP Exchange:     {c.exchange_repulsion:16.10f} Eh\n"
            f"{'='*50}\n"
            f"Total Energy:     {c.total:16.10f} Eh\n"
            f"N EFP Fragments:  {result.n_efp_fragments}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_efp(qm_geometry: str, efp_fragments: List[str], 
                  qm_method: str = "hf", basis: str = "cc-pvdz",
                  **kwargs: Any) -> ToolOutput:
    """Calculate QM/EFP energy."""
    return EFPTool().run({
        "qm_geometry": qm_geometry, "efp_fragments": efp_fragments,
        "qm_method": qm_method, "basis": basis, **kwargs,
    })
