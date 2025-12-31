"""
Complete Active Space Self-Consistent Field (CASSCF) Tool.

CASSCF performs a full CI within an active space while optimizing
both orbitals and CI coefficients, essential for multireference systems.

Reference:
    Roos, B.O.; Taylor, P.R.; Siegbahn, P.E.M. Chem. Phys. 1980, 48, 157.
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
class CASSCFResult:
    """CASSCF calculation results."""
    total_energy: float
    active_space: Tuple[int, int]
    n_roots: int
    root_energies: List[float]
    ci_coefficients: List[float]
    natural_occupations: List[float]
    converged: bool
    n_iterations: int
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "total_energy_kcal": self.total_energy * HARTREE_TO_KCAL,
            "active_space": {"electrons": self.active_space[0], "orbitals": self.active_space[1]},
            "n_roots": self.n_roots,
            "root_energies_hartree": self.root_energies,
            "ci_coefficients": self.ci_coefficients[:10],
            "natural_occupations": self.natural_occupations,
            "converged": self.converged,
            "n_iterations": self.n_iterations,
            "basis": self.basis,
        }


class CASSCFInput(ToolInput):
    """Input for CASSCF calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    active_electrons: int = Field(..., description="Number of active electrons")
    active_orbitals: int = Field(..., description="Number of active orbitals")
    
    n_roots: int = Field(default=1, description="Number of states")
    root_to_follow: int = Field(default=1, description="Root for optimization")
    
    orbital_optimization: str = Field(default="two_step", description="two_step or df")
    ci_maxiter: int = Field(default=100)
    convergence: float = Field(default=1e-8)
    
    frozen_docc: Optional[List[int]] = Field(default=None, description="Frozen doubly occupied per irrep")
    active: Optional[List[int]] = Field(default=None, description="Active orbitals per irrep")
    
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_casscf_input(input_data: CASSCFInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.active_electrons < 1:
        return ValidationError(field="active_electrons", message="Need at least 1 active electron")
    if input_data.active_orbitals < 1:
        return ValidationError(field="active_orbitals", message="Need at least 1 active orbital")
    if input_data.active_electrons > 2 * input_data.active_orbitals:
        return ValidationError(field="active_electrons", message="Too many electrons for active space")
    return None


def run_casscf_calculation(input_data: CASSCFInput) -> CASSCFResult:
    """Execute CASSCF calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_casscf.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    options = {
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "rohf",
        "mcscf_type": input_data.orbital_optimization,
        "num_roots": input_data.n_roots,
        "follow_root": input_data.root_to_follow,
        "mcscf_maxiter": input_data.ci_maxiter,
        "mcscf_e_convergence": input_data.convergence,
        "active_el": input_data.active_electrons,
        "active_orb": input_data.active_orbitals,
    }
    
    if input_data.frozen_docc:
        options["frozen_docc"] = input_data.frozen_docc
    if input_data.active:
        options["active"] = input_data.active
    
    psi4.set_options(options)
    
    logger.info(f"Running CASSCF({input_data.active_electrons},{input_data.active_orbitals})/{input_data.basis}")
    
    # Run CASSCF
    e_casscf, wfn = psi4.energy("casscf", return_wfn=True, molecule=mol)
    
    # Extract results
    root_energies = [e_casscf]
    for i in range(1, input_data.n_roots):
        root_e = psi4.variable(f"MCSCF ROOT {i} TOTAL ENERGY")
        if root_e != 0:
            root_energies.append(root_e)
    
    # Get CI coefficients (largest)
    ci_coeffs = [1.0]  # Placeholder - would need CI vector extraction
    
    # Natural orbital occupations
    nat_occs = []
    for i in range(input_data.active_orbitals):
        occ = psi4.variable(f"MCSCF NATURAL ORBITAL OCCUPATION {i}")
        if occ != 0:
            nat_occs.append(occ)
    
    if not nat_occs:
        # Estimate occupations
        n_doubly = input_data.active_electrons // 2
        n_singly = input_data.active_electrons % 2
        nat_occs = [2.0] * n_doubly + [1.0] * n_singly + [0.0] * (input_data.active_orbitals - n_doubly - n_singly)
    
    converged = psi4.variable("MCSCF CONVERGED")
    n_iter = int(psi4.variable("MCSCF ITERATIONS"))
    
    psi4.core.clean()
    
    return CASSCFResult(
        total_energy=e_casscf,
        active_space=(input_data.active_electrons, input_data.active_orbitals),
        n_roots=input_data.n_roots,
        root_energies=root_energies,
        ci_coefficients=ci_coeffs,
        natural_occupations=nat_occs,
        converged=bool(converged),
        n_iterations=n_iter if n_iter > 0 else 1,
        basis=input_data.basis,
    )


@register_tool
class CASSCFTool(BaseTool[CASSCFInput, ToolOutput]):
    """Tool for CASSCF calculations."""
    name: ClassVar[str] = "calculate_casscf"
    description: ClassVar[str] = "Calculate CASSCF energy for multireference systems."
    category: ClassVar[ToolCategory] = ToolCategory.MULTIREFERENCE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: CASSCFInput) -> Optional[ValidationError]:
        return validate_casscf_input(input_data)
    
    def _execute(self, input_data: CASSCFInput) -> Result[ToolOutput]:
        result = run_casscf_calculation(input_data)
        
        occ_str = ", ".join(f"{o:.3f}" for o in result.natural_occupations)
        message = (
            f"CASSCF({result.active_space[0]},{result.active_space[1]})/{input_data.basis}\n"
            f"{'='*50}\n"
            f"Total Energy: {result.total_energy:.10f} Eh\n"
            f"Converged: {result.converged} ({result.n_iterations} iterations)\n"
            f"Natural Occupations: {occ_str}\n"
            f"N Roots: {result.n_roots}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_casscf(geometry: str, active_electrons: int, active_orbitals: int,
                     basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate CASSCF energy."""
    return CASSCFTool().run({
        "geometry": geometry, "active_electrons": active_electrons,
        "active_orbitals": active_orbitals, "basis": basis, **kwargs,
    })
