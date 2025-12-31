"""
MCSCF Analytical Gradients Tool.

Computes analytical nuclear gradients for MCSCF wavefunctions,
enabling geometry optimization and property calculations.

Reference:
    Shepard, R. Int. J. Quantum Chem. 1987, 31, 33.
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
BOHR_TO_ANGSTROM = 0.529177249


@dataclass
class MCSCFGradientResult:
    """MCSCF gradient calculation results."""
    energy: float
    gradient: List[List[float]]  # N_atoms x 3
    gradient_norm: float
    max_gradient: float
    rms_gradient: float
    active_space: Tuple[int, int]
    root: int
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "energy_hartree": self.energy,
            "gradient_hartree_bohr": self.gradient,
            "gradient_norm": self.gradient_norm,
            "max_gradient": self.max_gradient,
            "rms_gradient": self.rms_gradient,
            "active_space": {"electrons": self.active_space[0], "orbitals": self.active_space[1]},
            "root": self.root,
            "basis": self.basis,
        }


class MCSCFGradientInput(ToolInput):
    """Input for MCSCF gradient calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    active_electrons: int = Field(..., description="Number of active electrons")
    active_orbitals: int = Field(..., description="Number of active orbitals")
    
    root: int = Field(default=1, description="Root for gradient")
    n_roots: int = Field(default=1, description="Total number of roots")
    
    method: str = Field(default="casscf", description="casscf or rasscf")
    
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_mcscf_gradient_input(input_data: MCSCFGradientInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    if input_data.active_electrons < 1:
        return ValidationError(field="active_electrons", message="Need at least 1 active electron")
    if input_data.active_orbitals < 1:
        return ValidationError(field="active_orbitals", message="Need at least 1 active orbital")
    return None


def compute_gradient_stats(gradient: List[List[float]]) -> Tuple[float, float, float]:
    """Compute gradient statistics."""
    all_values = [abs(g) for atom_grad in gradient for g in atom_grad]
    
    if not all_values:
        return 0.0, 0.0, 0.0
    
    max_grad = max(all_values)
    rms_grad = (sum(g**2 for g in all_values) / len(all_values)) ** 0.5
    norm = sum(g**2 for g in all_values) ** 0.5
    
    return norm, max_grad, rms_grad


def run_mcscf_gradient(input_data: MCSCFGradientInput) -> MCSCFGradientResult:
    """Execute MCSCF gradient calculation."""
    import psi4
    import numpy as np
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_mcscf_grad.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    options = {
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "rohf",
        "num_roots": input_data.n_roots,
        "follow_root": input_data.root,
        "active_el": input_data.active_electrons,
        "active_orb": input_data.active_orbitals,
    }
    
    psi4.set_options(options)
    
    method = input_data.method.lower()
    logger.info(f"Running {method.upper()} gradient ({input_data.active_electrons},{input_data.active_orbitals})/{input_data.basis}")
    
    # Compute gradient
    grad_matrix, wfn = psi4.gradient(method, return_wfn=True, molecule=mol)
    energy = wfn.energy()
    
    # Convert to list format
    grad_array = np.array(grad_matrix)
    gradient = grad_array.tolist()
    
    # Compute statistics
    norm, max_grad, rms_grad = compute_gradient_stats(gradient)
    
    psi4.core.clean()
    
    return MCSCFGradientResult(
        energy=energy,
        gradient=gradient,
        gradient_norm=norm,
        max_gradient=max_grad,
        rms_gradient=rms_grad,
        active_space=(input_data.active_electrons, input_data.active_orbitals),
        root=input_data.root,
        basis=input_data.basis,
    )


@register_tool
class MCSCFGradientTool(BaseTool[MCSCFGradientInput, ToolOutput]):
    """Tool for MCSCF gradient calculations."""
    name: ClassVar[str] = "calculate_mcscf_gradient"
    description: ClassVar[str] = "Calculate MCSCF analytical gradients."
    category: ClassVar[ToolCategory] = ToolCategory.MULTIREFERENCE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: MCSCFGradientInput) -> Optional[ValidationError]:
        return validate_mcscf_gradient_input(input_data)
    
    def _execute(self, input_data: MCSCFGradientInput) -> Result[ToolOutput]:
        result = run_mcscf_gradient(input_data)
        
        message = (
            f"MCSCF Gradient ({result.active_space[0]},{result.active_space[1]})/{input_data.basis}\n"
            f"{'='*50}\n"
            f"Energy:       {result.energy:.10f} Eh\n"
            f"Gradient Norm: {result.gradient_norm:.6f} Eh/bohr\n"
            f"Max Gradient:  {result.max_gradient:.6f} Eh/bohr\n"
            f"RMS Gradient:  {result.rms_gradient:.6f} Eh/bohr\n"
            f"Root: {result.root}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_mcscf_gradient(geometry: str, active_electrons: int, active_orbitals: int,
                             basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate MCSCF gradient."""
    return MCSCFGradientTool().run({
        "geometry": geometry, "active_electrons": active_electrons,
        "active_orbitals": active_orbitals, "basis": basis, **kwargs,
    })
