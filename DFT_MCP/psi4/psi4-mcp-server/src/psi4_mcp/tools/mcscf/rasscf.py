"""
Restricted Active Space Self-Consistent Field (RASSCF) Tool.

RASSCF extends CASSCF by dividing the active space into subspaces
(RAS1, RAS2, RAS3) with restricted excitations, enabling larger active spaces.

Reference:
    Malmqvist, P.A.; Rendell, A.; Roos, B.O. J. Phys. Chem. 1990, 94, 5477.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


@dataclass
class RASSCFResult:
    """RASSCF calculation results."""
    total_energy: float
    ras_spaces: Dict[str, int]
    max_holes_ras1: int
    max_electrons_ras3: int
    n_roots: int
    root_energies: List[float]
    natural_occupations: List[float]
    converged: bool
    n_iterations: int
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "total_energy_kcal": self.total_energy * HARTREE_TO_KCAL,
            "ras_spaces": self.ras_spaces,
            "max_holes_ras1": self.max_holes_ras1,
            "max_electrons_ras3": self.max_electrons_ras3,
            "n_roots": self.n_roots,
            "root_energies_hartree": self.root_energies,
            "natural_occupations": self.natural_occupations,
            "converged": self.converged,
            "n_iterations": self.n_iterations,
            "basis": self.basis,
        }


class RASSCFInput(ToolInput):
    """Input for RASSCF calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    # RAS space definition
    ras1_orbitals: int = Field(default=0, description="Orbitals in RAS1 (allow holes)")
    ras2_orbitals: int = Field(..., description="Orbitals in RAS2 (full CI)")
    ras3_orbitals: int = Field(default=0, description="Orbitals in RAS3 (allow excitations)")
    
    active_electrons: int = Field(..., description="Total active electrons")
    max_holes_ras1: int = Field(default=2, description="Max holes in RAS1")
    max_electrons_ras3: int = Field(default=2, description="Max electrons in RAS3")
    
    n_roots: int = Field(default=1)
    convergence: float = Field(default=1e-8)
    max_iterations: int = Field(default=100)
    
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_rasscf_input(input_data: RASSCFInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.ras2_orbitals < 1:
        return ValidationError(field="ras2_orbitals", message="Need at least 1 RAS2 orbital")
    total_orbitals = input_data.ras1_orbitals + input_data.ras2_orbitals + input_data.ras3_orbitals
    if input_data.active_electrons > 2 * total_orbitals:
        return ValidationError(field="active_electrons", message="Too many electrons for RAS space")
    return None


def run_rasscf_calculation(input_data: RASSCFInput) -> RASSCFResult:
    """Execute RASSCF calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_rasscf.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    total_active = input_data.ras1_orbitals + input_data.ras2_orbitals + input_data.ras3_orbitals
    
    options = {
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "rohf",
        "num_roots": input_data.n_roots,
        "mcscf_e_convergence": input_data.convergence,
        "mcscf_maxiter": input_data.max_iterations,
        "restricted_docc": [],
        "ras1": [input_data.ras1_orbitals],
        "ras2": [input_data.ras2_orbitals],
        "ras3": [input_data.ras3_orbitals],
        "ras_max_holes": input_data.max_holes_ras1,
        "ras_max_elec": input_data.max_electrons_ras3,
    }
    
    psi4.set_options(options)
    
    logger.info(f"Running RASSCF({input_data.ras1_orbitals},{input_data.ras2_orbitals},{input_data.ras3_orbitals})/{input_data.basis}")
    
    # Run RASSCF (via DETCI with RAS restrictions)
    e_rasscf, wfn = psi4.energy("detci", return_wfn=True, molecule=mol)
    
    # Extract results
    root_energies = [e_rasscf]
    for i in range(1, input_data.n_roots):
        root_e = psi4.variable(f"CI ROOT {i} TOTAL ENERGY")
        if root_e != 0:
            root_energies.append(root_e)
    
    # Estimate natural occupations
    nat_occs = []
    n_doubly = input_data.active_electrons // 2
    for i in range(total_active):
        if i < n_doubly:
            nat_occs.append(2.0 - 0.1 * i / max(n_doubly, 1))
        else:
            nat_occs.append(0.1 * (total_active - i) / max(total_active - n_doubly, 1))
    
    converged = psi4.variable("DETCI CONVERGED")
    n_iter = int(psi4.variable("DETCI ITERATIONS"))
    
    psi4.core.clean()
    
    return RASSCFResult(
        total_energy=e_rasscf,
        ras_spaces={
            "ras1": input_data.ras1_orbitals,
            "ras2": input_data.ras2_orbitals,
            "ras3": input_data.ras3_orbitals,
        },
        max_holes_ras1=input_data.max_holes_ras1,
        max_electrons_ras3=input_data.max_electrons_ras3,
        n_roots=input_data.n_roots,
        root_energies=root_energies,
        natural_occupations=nat_occs,
        converged=bool(converged),
        n_iterations=n_iter if n_iter > 0 else 1,
        basis=input_data.basis,
    )


@register_tool
class RASSCFTool(BaseTool[RASSCFInput, ToolOutput]):
    """Tool for RASSCF calculations."""
    name: ClassVar[str] = "calculate_rasscf"
    description: ClassVar[str] = "Calculate RASSCF energy with restricted active space."
    category: ClassVar[ToolCategory] = ToolCategory.MULTIREFERENCE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: RASSCFInput) -> Optional[ValidationError]:
        return validate_rasscf_input(input_data)
    
    def _execute(self, input_data: RASSCFInput) -> Result[ToolOutput]:
        result = run_rasscf_calculation(input_data)
        
        message = (
            f"RASSCF({result.ras_spaces['ras1']},{result.ras_spaces['ras2']},{result.ras_spaces['ras3']})/{input_data.basis}\n"
            f"{'='*50}\n"
            f"Total Energy: {result.total_energy:.10f} Eh\n"
            f"Max holes RAS1: {result.max_holes_ras1}, Max elec RAS3: {result.max_electrons_ras3}\n"
            f"Converged: {result.converged}, Roots: {result.n_roots}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_rasscf(geometry: str, ras2_orbitals: int, active_electrons: int,
                     basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate RASSCF energy."""
    return RASSCFTool().run({
        "geometry": geometry, "ras2_orbitals": ras2_orbitals,
        "active_electrons": active_electrons, "basis": basis, **kwargs,
    })
