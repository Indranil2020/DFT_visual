"""
MCSCF (Multi-Configuration SCF) Calculation Models.

Pydantic models for multi-configurational methods:
    - CASSCF (Complete Active Space SCF)
    - RASSCF (Restricted Active Space SCF)
    - MCSCF gradients
"""

from typing import Any, Optional, Literal
from pydantic import Field

from psi4_mcp.models.base import BaseInput, BaseOutput
from psi4_mcp.models.molecules import MoleculeInput


# =============================================================================
# ACTIVE SPACE SPECIFICATION
# =============================================================================

class ActiveSpace(BaseOutput):
    """
    Active space specification for MCSCF.
    
    Attributes:
        n_electrons: Number of active electrons.
        n_orbitals: Number of active orbitals.
        n_alpha: Number of alpha electrons (optional).
        n_beta: Number of beta electrons (optional).
        orbital_indices: Specific orbital indices (optional).
    """
    
    n_electrons: int = Field(ge=0, description="Number of active electrons")
    n_orbitals: int = Field(ge=1, description="Number of active orbitals")
    n_alpha: Optional[int] = Field(default=None, description="Alpha active electrons")
    n_beta: Optional[int] = Field(default=None, description="Beta active electrons")
    orbital_indices: Optional[list[int]] = Field(default=None, description="Orbital indices")
    
    def to_cas_string(self) -> str:
        """Get CAS notation string like (6,6)."""
        return f"({self.n_electrons},{self.n_orbitals})"


# =============================================================================
# MCSCF INPUT MODELS
# =============================================================================

class MCSCFInput(BaseInput):
    """
    Base input for MCSCF calculations.
    
    Attributes:
        molecule: Molecular specification.
        active_space: Active space definition.
        basis: Basis set name.
        mcscf_type: Type of MCSCF (casscf, rasscf).
        num_roots: Number of states to compute.
        state_average: Whether to state-average.
        state_weights: Weights for state averaging.
        max_iterations: Maximum MCSCF iterations.
    """
    
    molecule: MoleculeInput = Field(..., description="Molecular specification")
    active_space: ActiveSpace = Field(..., description="Active space specification")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    mcscf_type: Literal["casscf", "rasscf"] = Field(default="casscf")
    num_roots: int = Field(default=1, ge=1, description="Number of roots")
    state_average: bool = Field(default=False, description="State-average calculation")
    state_weights: Optional[list[float]] = Field(
        default=None,
        description="Weights for state averaging (normalized)"
    )
    max_iterations: int = Field(default=200, ge=1, description="Max iterations")
    convergence: float = Field(default=1e-8, description="Energy convergence")
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        options = {
            "basis": self.basis,
            "active": [self.active_space.n_orbitals],
            "mcscf_maxiter": self.max_iterations,
            "mcscf_e_convergence": self.convergence,
        }
        if self.num_roots > 1:
            options["num_roots"] = self.num_roots
        if self.state_average:
            options["avg_states"] = list(range(self.num_roots))
            if self.state_weights:
                options["avg_weights"] = self.state_weights
        return options


class CASSCFInput(MCSCFInput):
    """
    CASSCF-specific input.
    
    Complete Active Space SCF performs a full CI within the active space
    while optimizing the orbitals.
    """
    mcscf_type: Literal["casscf"] = "casscf"
    
    # CASSCF-specific options
    restricted_docc: Optional[list[int]] = Field(
        default=None,
        description="Restricted doubly occupied orbitals per irrep"
    )
    active_orbitals: Optional[list[int]] = Field(
        default=None,
        description="Active orbitals per irrep"
    )


class RASSCFInput(MCSCFInput):
    """
    RASSCF-specific input.
    
    Restricted Active Space SCF divides the active space into
    RAS1, RAS2, and RAS3 subspaces with excitation restrictions.
    """
    mcscf_type: Literal["rasscf"] = "rasscf"
    
    # RAS space definitions
    ras1: Optional[list[int]] = Field(
        default=None,
        description="RAS1 orbitals (holes allowed)"
    )
    ras2: Optional[list[int]] = Field(
        default=None,
        description="RAS2 orbitals (full CI)"
    )
    ras3: Optional[list[int]] = Field(
        default=None,
        description="RAS3 orbitals (particles allowed)"
    )
    max_holes: int = Field(default=2, ge=0, description="Max holes in RAS1")
    max_particles: int = Field(default=2, ge=0, description="Max particles in RAS3")


# =============================================================================
# MCSCF OUTPUT MODELS
# =============================================================================

class MCSCFRoot(BaseOutput):
    """Single MCSCF root information."""
    root_number: int = Field(description="Root index")
    energy: float = Field(description="Total energy")
    weight: Optional[float] = Field(default=None, description="State average weight")
    ci_coefficient_sum: Optional[float] = Field(default=None)
    leading_configuration: Optional[str] = Field(default=None)


class OrbitalRotation(BaseOutput):
    """Orbital rotation information."""
    pair: tuple[int, int] = Field(description="Orbital pair (i, j)")
    rotation_angle: float = Field(description="Rotation angle")


class MCSCFConvergence(BaseOutput):
    """MCSCF convergence information."""
    converged: bool = Field(description="Whether converged")
    iterations: int = Field(description="Number of iterations")
    final_energy_change: float = Field(description="Final energy change")
    final_gradient_norm: Optional[float] = Field(default=None)


class MCSCFOutput(BaseOutput):
    """
    MCSCF calculation output.
    
    Attributes:
        total_energy: Total MCSCF energy.
        roots: List of computed roots.
        active_space: Active space used.
        natural_occupations: Natural orbital occupations.
        convergence: Convergence details.
    """
    
    total_energy: float = Field(description="Total MCSCF energy")
    roots: list[MCSCFRoot] = Field(default_factory=list)
    active_space: ActiveSpace = Field(description="Active space used")
    natural_occupations: Optional[list[float]] = Field(
        default=None,
        description="Natural orbital occupations in active space"
    )
    convergence: Optional[MCSCFConvergence] = Field(default=None)
    mcscf_type: str = Field(description="MCSCF type")
    basis: str = Field(description="Basis set")
    is_state_averaged: bool = Field(default=False)


class CASSCFOutput(MCSCFOutput):
    """CASSCF-specific output."""
    mcscf_type: str = "CASSCF"
    n_configurations: Optional[int] = Field(default=None, description="Number of CSFs")


class RASSCFOutput(MCSCFOutput):
    """RASSCF-specific output."""
    mcscf_type: str = "RASSCF"
    ras1_occupations: Optional[list[float]] = Field(default=None)
    ras2_occupations: Optional[list[float]] = Field(default=None)
    ras3_occupations: Optional[list[float]] = Field(default=None)
