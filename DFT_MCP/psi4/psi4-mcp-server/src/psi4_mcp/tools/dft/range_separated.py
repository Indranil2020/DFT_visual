"""
Range-Separated Hybrid DFT Tool.

Implements range-separated hybrid functionals with tunable parameters
for improved description of charge-transfer and long-range interactions.

Reference:
    Baer, R.; Livshits, E.; Salzner, U. Annu. Rev. Phys. Chem. 2010, 61, 85.
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
HARTREE_TO_EV = 27.211386245988


RSH_FUNCTIONALS = {
    "cam-b3lyp": {"omega": 0.33, "alpha": 0.19, "beta": 0.46, "description": "Coulomb-attenuating B3LYP"},
    "wb97x": {"omega": 0.30, "alpha": 0.157, "beta": 0.843, "description": "ωB97X"},
    "wb97x-d": {"omega": 0.20, "alpha": 0.222, "beta": 0.778, "description": "ωB97X-D with dispersion"},
    "lc-wpbe": {"omega": 0.40, "alpha": 0.0, "beta": 1.0, "description": "Long-range corrected ωPBE"},
    "lc-blyp": {"omega": 0.33, "alpha": 0.0, "beta": 1.0, "description": "Long-range corrected BLYP"},
}


@dataclass
class RSHResult:
    """Range-separated hybrid calculation results."""
    energy: float
    functional: str
    omega: float
    homo: float
    lumo: float
    gap: float
    ip_estimate: float
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "energy_hartree": self.energy,
            "functional": self.functional,
            "omega_bohr": self.omega,
            "homo_hartree": self.homo,
            "homo_ev": self.homo * HARTREE_TO_EV,
            "lumo_hartree": self.lumo,
            "lumo_ev": self.lumo * HARTREE_TO_EV,
            "gap_hartree": self.gap,
            "gap_ev": self.gap * HARTREE_TO_EV,
            "ip_estimate_ev": self.ip_estimate * HARTREE_TO_EV,
            "basis": self.basis,
        }


class RSHInput(ToolInput):
    """Input for range-separated hybrid calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    functional: str = Field(default="cam-b3lyp", description="RSH functional")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    custom_omega: Optional[float] = Field(default=None, description="Custom range-separation parameter")
    
    tune_omega: bool = Field(default=False, description="Tune omega via IP theorem")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_rsh_input(input_data: RSHInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_rsh_calculation(input_data: RSHInput) -> RSHResult:
    """Execute range-separated hybrid calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_rsh.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    functional_lower = input_data.functional.lower()
    
    # Get omega value
    if input_data.custom_omega:
        omega = input_data.custom_omega
    elif functional_lower in RSH_FUNCTIONALS:
        omega = RSH_FUNCTIONALS[functional_lower]["omega"]
    else:
        omega = 0.33  # Default
    
    options = {
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    }
    
    if input_data.custom_omega:
        options["dft_omega"] = input_data.custom_omega
    
    psi4.set_options(options)
    
    logger.info(f"Running {input_data.functional}/{input_data.basis} (ω={omega})")
    
    energy, wfn = psi4.energy(f"{input_data.functional}/{input_data.basis}", 
                              return_wfn=True, molecule=mol)
    
    # Extract orbital energies
    epsilon_a = wfn.epsilon_a()
    n_occ = wfn.nalpha()
    
    homo = epsilon_a.get(n_occ - 1)
    lumo = epsilon_a.get(n_occ)
    gap = lumo - homo
    
    # IP estimate from Koopmans' theorem
    ip_estimate = -homo
    
    psi4.core.clean()
    
    return RSHResult(
        energy=energy,
        functional=input_data.functional.upper(),
        omega=omega,
        homo=homo,
        lumo=lumo,
        gap=gap,
        ip_estimate=ip_estimate,
        basis=input_data.basis,
    )


@register_tool
class RSHTool(BaseTool[RSHInput, ToolOutput]):
    """Tool for range-separated hybrid calculations."""
    name: ClassVar[str] = "calculate_rsh"
    description: ClassVar[str] = "Calculate energy with range-separated hybrid functional."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: RSHInput) -> Optional[ValidationError]:
        return validate_rsh_input(input_data)
    
    def _execute(self, input_data: RSHInput) -> Result[ToolOutput]:
        result = run_rsh_calculation(input_data)
        
        message = (
            f"{result.functional}/{result.basis} (ω = {result.omega:.3f})\n"
            f"{'='*50}\n"
            f"Energy:    {result.energy:.10f} Eh\n"
            f"HOMO:      {result.homo:.6f} Eh ({result.homo * HARTREE_TO_EV:.3f} eV)\n"
            f"LUMO:      {result.lumo:.6f} Eh ({result.lumo * HARTREE_TO_EV:.3f} eV)\n"
            f"Gap:       {result.gap:.6f} Eh ({result.gap * HARTREE_TO_EV:.3f} eV)\n"
            f"IP (est):  {result.ip_estimate * HARTREE_TO_EV:.3f} eV"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_rsh(geometry: str, functional: str = "cam-b3lyp", **kwargs: Any) -> ToolOutput:
    """Calculate RSH energy."""
    return RSHTool().run({"geometry": geometry, "functional": functional, **kwargs})
