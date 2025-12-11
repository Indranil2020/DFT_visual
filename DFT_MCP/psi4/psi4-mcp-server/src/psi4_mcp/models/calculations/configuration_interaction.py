"""
Configuration Interaction Calculation Models.

Pydantic models for Configuration Interaction calculations:
    - CISD (CI Singles and Doubles)
    - CISDT (CI Singles, Doubles, and Triples)
    - FCI (Full CI)
    - DETCI (Determinant CI)
"""

from typing import Any, Optional, Literal
from pydantic import Field

from psi4_mcp.models.base import BaseInput, BaseOutput
from psi4_mcp.models.molecules import MoleculeInput


# =============================================================================
# CI INPUT MODELS
# =============================================================================

class CIInput(BaseInput):
    """
    Base input for Configuration Interaction calculations.
    
    Attributes:
        molecule: Molecular specification.
        ci_type: Type of CI calculation.
        basis: Basis set name.
        reference: Reference wavefunction (rhf, uhf, rohf).
        frozen_core: Whether to freeze core orbitals.
        frozen_virtual: Number of frozen virtual orbitals.
        num_roots: Number of CI roots to compute.
        max_iterations: Maximum CI iterations.
    """
    
    molecule: MoleculeInput = Field(..., description="Molecular specification")
    ci_type: Literal["cisd", "cisdt", "fci", "detci"] = Field(
        default="cisd",
        description="Type of CI calculation"
    )
    basis: str = Field(default="cc-pvdz", description="Basis set")
    reference: str = Field(default="rhf", description="Reference wavefunction")
    frozen_core: bool = Field(default=True, description="Freeze core orbitals")
    frozen_virtual: int = Field(default=0, description="Number of frozen virtuals")
    num_roots: int = Field(default=1, ge=1, description="Number of roots")
    max_iterations: int = Field(default=100, ge=1, description="Max iterations")
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        options = {
            "basis": self.basis,
            "reference": self.reference,
            "freeze_core": self.frozen_core,
            "num_roots": self.num_roots,
            "ci_maxiter": self.max_iterations,
        }
        if self.frozen_virtual > 0:
            options["frozen_docc"] = self.frozen_virtual
        return options


class CISDInput(CIInput):
    """CISD-specific input."""
    ci_type: Literal["cisd"] = "cisd"


class CISDTInput(CIInput):
    """CISDT-specific input."""
    ci_type: Literal["cisdt"] = "cisdt"


class FCIInput(CIInput):
    """FCI-specific input."""
    ci_type: Literal["fci"] = "fci"
    # FCI is expensive, add warnings
    max_determinants: Optional[int] = Field(
        default=None,
        description="Maximum number of determinants"
    )


class DETCIInput(CIInput):
    """
    Determinant CI input.
    
    DETCI allows more flexible excitation level control.
    """
    ci_type: Literal["detci"] = "detci"
    excitation_level: int = Field(default=2, ge=1, le=10, description="Max excitation level")
    wfn_type: Literal["ci", "zaptn", "mpn"] = Field(default="ci", description="Wavefunction type")


# =============================================================================
# CI OUTPUT MODELS
# =============================================================================

class CIRoot(BaseOutput):
    """Single CI root information."""
    root_number: int = Field(description="Root index (0-based)")
    energy: float = Field(description="Total energy in Hartree")
    excitation_energy: Optional[float] = Field(
        default=None, description="Excitation energy relative to ground state"
    )
    excitation_energy_ev: Optional[float] = Field(
        default=None, description="Excitation energy in eV"
    )
    ci_vector_norm: Optional[float] = Field(default=None, description="CI vector norm")
    leading_coefficient: Optional[float] = Field(
        default=None, description="Largest CI coefficient"
    )
    leading_configuration: Optional[str] = Field(
        default=None, description="Configuration with largest coefficient"
    )


class CIOutput(BaseOutput):
    """
    Configuration Interaction calculation output.
    
    Attributes:
        reference_energy: Reference (HF/DFT) energy.
        correlation_energy: Correlation energy.
        total_energy: Total CI energy.
        roots: List of CI roots computed.
        n_determinants: Number of determinants in CI space.
        converged: Whether CI converged.
        iterations: Number of iterations.
    """
    
    reference_energy: float = Field(description="Reference energy")
    correlation_energy: float = Field(description="Correlation energy")
    total_energy: float = Field(description="Total CI energy")
    roots: list[CIRoot] = Field(default_factory=list, description="CI roots")
    n_determinants: Optional[int] = Field(default=None, description="Number of determinants")
    converged: bool = Field(default=True, description="Whether converged")
    iterations: int = Field(default=0, description="Number of iterations")
    ci_type: str = Field(description="Type of CI calculation")
    basis: str = Field(description="Basis set used")


class CISDOutput(CIOutput):
    """CISD-specific output."""
    ci_type: str = "CISD"
    singles_contribution: Optional[float] = Field(default=None)
    doubles_contribution: Optional[float] = Field(default=None)


class FCIOutput(CIOutput):
    """FCI-specific output."""
    ci_type: str = "FCI"
    # FCI is exact within basis, so special fields
    is_exact_correlation: bool = Field(default=True, description="FCI is exact in basis")
