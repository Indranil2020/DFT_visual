"""
ddCOSMO (Domain-Decomposition COSMO) Solvation Tool.

Efficient domain-decomposition implementation of the COSMO solvation model
for large molecular systems.

Reference:
    Lipparini, F. et al. J. Chem. Theory Comput. 2013, 9, 3637.
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


DDCOSMO_SOLVENTS = {
    "water": 78.355,
    "acetonitrile": 35.688,
    "methanol": 32.613,
    "ethanol": 24.852,
    "dmso": 46.826,
    "chloroform": 4.7113,
    "dichloromethane": 8.93,
    "thf": 7.4257,
    "toluene": 2.3741,
    "hexane": 1.8819,
    "benzene": 2.2706,
    "acetone": 20.493,
}


@dataclass
class ddCOSMOResult:
    """ddCOSMO calculation results."""
    gas_energy: float
    solution_energy: float
    solvation_energy: float
    dielectric_constant: float
    surface_area: float
    solvent: str
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gas_energy_hartree": self.gas_energy,
            "solution_energy_hartree": self.solution_energy,
            "solvation_energy_hartree": self.solvation_energy,
            "solvation_energy_kcal": self.solvation_energy * HARTREE_TO_KCAL,
            "dielectric_constant": self.dielectric_constant,
            "surface_area_angstrom2": self.surface_area,
            "solvent": self.solvent,
            "method": self.method, "basis": self.basis,
        }


class ddCOSMOInput(ToolInput):
    """Input for ddCOSMO calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    solvent: str = Field(default="water")
    custom_epsilon: Optional[float] = Field(default=None)
    
    lmax: int = Field(default=6, description="Max angular momentum for cavity")
    eta: float = Field(default=0.5, description="Regularization parameter")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_ddcosmo_input(input_data: ddCOSMOInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.solvent.lower() not in DDCOSMO_SOLVENTS and not input_data.custom_epsilon:
        return ValidationError(field="solvent",
                              message=f"Unknown solvent. Use: {', '.join(DDCOSMO_SOLVENTS.keys())}")
    return None


def run_ddcosmo_calculation(input_data: ddCOSMOInput) -> ddCOSMOResult:
    """Execute ddCOSMO calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_ddcosmo.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running ddCOSMO in {input_data.solvent}")
    
    # Gas phase
    e_gas = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
    
    # Get dielectric constant
    solvent_lower = input_data.solvent.lower()
    epsilon = input_data.custom_epsilon if input_data.custom_epsilon else DDCOSMO_SOLVENTS[solvent_lower]
    
    # ddCOSMO setup
    psi4.set_options({
        "ddx": True,
        "ddx_model": "cosmo",
        "ddx_solvent_epsilon": epsilon,
        "ddx_lmax": input_data.lmax,
        "ddx_eta": input_data.eta,
    })
    
    e_sol = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
    
    solvation_energy = e_sol - e_gas
    
    # Estimate surface area (simplified)
    n_atoms = mol.natom()
    surface_area = n_atoms * 15.0  # Rough estimate
    
    psi4.core.clean()
    
    return ddCOSMOResult(
        gas_energy=e_gas,
        solution_energy=e_sol,
        solvation_energy=solvation_energy,
        dielectric_constant=epsilon,
        surface_area=surface_area,
        solvent=input_data.solvent,
        method=input_data.method.upper(),
        basis=input_data.basis,
    )


@register_tool
class ddCOSMOTool(BaseTool[ddCOSMOInput, ToolOutput]):
    """Tool for ddCOSMO calculations."""
    name: ClassVar[str] = "calculate_ddcosmo"
    description: ClassVar[str] = "Calculate solvation energy using ddCOSMO."
    category: ClassVar[ToolCategory] = ToolCategory.SOLVATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: ddCOSMOInput) -> Optional[ValidationError]:
        return validate_ddcosmo_input(input_data)
    
    def _execute(self, input_data: ddCOSMOInput) -> Result[ToolOutput]:
        result = run_ddcosmo_calculation(input_data)
        message = (
            f"ddCOSMO/{result.solvent} (ε={result.dielectric_constant:.2f})\n{'='*40}\n"
            f"Gas Energy:      {result.gas_energy:.10f} Eh\n"
            f"Solution Energy: {result.solution_energy:.10f} Eh\n"
            f"ΔG(solv):        {result.solvation_energy:.10f} Eh\n"
            f"             = {result.solvation_energy * HARTREE_TO_KCAL:.4f} kcal/mol"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_ddcosmo(geometry: str, solvent: str = "water", **kwargs: Any) -> ToolOutput:
    """Calculate ddCOSMO solvation energy."""
    return ddCOSMOTool().run({"geometry": geometry, "solvent": solvent, **kwargs})
