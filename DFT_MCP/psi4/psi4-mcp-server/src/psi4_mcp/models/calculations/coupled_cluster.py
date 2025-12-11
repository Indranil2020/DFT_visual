"""
Coupled Cluster Calculation Models.

Pydantic models for Coupled Cluster calculations:
    - CC2
    - CCSD
    - CCSD(T)
    - CC3
    - CCSDT
    - EOM-CCSD
    - Linear Response CCSD
"""

from typing import Any, Optional, Literal
from pydantic import Field

from psi4_mcp.models.base import BaseInput, BaseOutput
from psi4_mcp.models.molecules import MoleculeInput


# =============================================================================
# COUPLED CLUSTER INPUT MODELS
# =============================================================================

class CoupledClusterInput(BaseInput):
    """
    Base input for Coupled Cluster calculations.
    
    Attributes:
        molecule: Molecular specification.
        cc_method: CC method to use.
        basis: Basis set name.
        reference: Reference wavefunction.
        frozen_core: Whether to freeze core orbitals.
        convergence: Energy convergence threshold.
        max_iterations: Maximum CC iterations.
        brueckner: Use Brueckner orbitals.
        df: Use density fitting.
    """
    
    molecule: MoleculeInput = Field(..., description="Molecular specification")
    cc_method: Literal["cc2", "ccsd", "ccsd(t)", "cc3", "ccsdt", "ccsdtq"] = Field(
        default="ccsd",
        description="Coupled Cluster method"
    )
    basis: str = Field(default="cc-pvdz", description="Basis set")
    reference: str = Field(default="rhf", description="Reference wavefunction")
    frozen_core: bool = Field(default=True, description="Freeze core orbitals")
    convergence: float = Field(default=1e-8, description="Energy convergence")
    max_iterations: int = Field(default=100, ge=1, description="Max iterations")
    brueckner: bool = Field(default=False, description="Use Brueckner orbitals")
    df: bool = Field(default=False, description="Use density fitting")
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        return {
            "basis": self.basis,
            "reference": self.reference,
            "freeze_core": self.frozen_core,
            "e_convergence": self.convergence,
            "cc_maxiter": self.max_iterations,
        }
    
    def get_psi4_method(self) -> str:
        """Get Psi4 method string."""
        method = self.cc_method.lower()
        if self.df and method == "ccsd":
            return "df-ccsd"
        return method


class CC2Input(CoupledClusterInput):
    """CC2-specific input."""
    cc_method: Literal["cc2"] = "cc2"


class CCSDInput(CoupledClusterInput):
    """CCSD-specific input."""
    cc_method: Literal["ccsd"] = "ccsd"
    t1_diagnostic_threshold: float = Field(
        default=0.02,
        description="T1 diagnostic threshold for multireference warning"
    )


class CCSD_T_Input(CoupledClusterInput):
    """CCSD(T)-specific input (gold standard)."""
    cc_method: Literal["ccsd(t)"] = "ccsd(t)"
    t1_diagnostic_threshold: float = Field(default=0.02)


class CC3Input(CoupledClusterInput):
    """CC3-specific input."""
    cc_method: Literal["cc3"] = "cc3"


class CCSDTInput(CoupledClusterInput):
    """CCSDT-specific input."""
    cc_method: Literal["ccsdt"] = "ccsdt"


class EOMCCInput(CoupledClusterInput):
    """
    EOM-CC input for excited states.
    
    Attributes:
        eom_type: Type of EOM calculation (ee, ip, ea, sf).
        n_states: Number of excited states per irrep.
        eom_convergence: EOM convergence threshold.
    """
    
    cc_method: Literal["ccsd"] = "ccsd"
    eom_type: Literal["ee", "ip", "ea", "sf", "dip", "dea"] = Field(
        default="ee",
        description="EOM type: ee (excitation), ip (ionization), ea (attachment), sf (spin-flip)"
    )
    n_states: int = Field(default=3, ge=1, description="Number of states per irrep")
    eom_convergence: float = Field(default=1e-6, description="EOM convergence")
    
    def get_psi4_method(self) -> str:
        """Get Psi4 method string for EOM-CC."""
        return f"eom-{self.cc_method}"
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options including EOM settings."""
        options = super().to_psi4_options()
        options["roots_per_irrep"] = [self.n_states]
        options["r_convergence"] = self.eom_convergence
        return options


# =============================================================================
# COUPLED CLUSTER OUTPUT MODELS
# =============================================================================

class CCAmplitudes(BaseOutput):
    """Coupled cluster amplitude information."""
    t1_norm: float = Field(description="T1 amplitude norm")
    t1_diagnostic: float = Field(description="T1 diagnostic (< 0.02 for single-ref)")
    t2_norm: Optional[float] = Field(default=None, description="T2 amplitude norm")
    largest_t1: Optional[float] = Field(default=None, description="Largest T1 amplitude")
    largest_t2: Optional[float] = Field(default=None, description="Largest T2 amplitude")


class CCConvergence(BaseOutput):
    """CC convergence information."""
    converged: bool = Field(description="Whether calculation converged")
    iterations: int = Field(description="Number of iterations")
    final_energy_change: float = Field(description="Final energy change")
    final_amplitude_change: Optional[float] = Field(default=None)


class CoupledClusterOutput(BaseOutput):
    """
    Coupled Cluster calculation output.
    
    Attributes:
        reference_energy: SCF reference energy.
        correlation_energy: CC correlation energy.
        total_energy: Total CC energy.
        triples_correction: (T) correction if applicable.
        amplitudes: Amplitude information including T1 diagnostic.
        convergence: Convergence details.
    """
    
    reference_energy: float = Field(description="SCF reference energy")
    correlation_energy: float = Field(description="Correlation energy")
    total_energy: float = Field(description="Total CC energy")
    triples_correction: Optional[float] = Field(
        default=None, description="Perturbative triples correction"
    )
    amplitudes: Optional[CCAmplitudes] = Field(default=None)
    convergence: Optional[CCConvergence] = Field(default=None)
    cc_method: str = Field(description="CC method used")
    basis: str = Field(description="Basis set")
    is_single_reference: bool = Field(
        default=True,
        description="T1 diagnostic suggests single-reference character"
    )


class CCSDOutput(CoupledClusterOutput):
    """CCSD-specific output."""
    cc_method: str = "CCSD"
    singles_energy: Optional[float] = Field(default=None)
    doubles_energy: Optional[float] = Field(default=None)


class CCSD_T_Output(CoupledClusterOutput):
    """CCSD(T)-specific output (gold standard)."""
    cc_method: str = "CCSD(T)"
    ccsd_energy: float = Field(description="CCSD energy (without triples)")
    triples_correction: float = Field(description="(T) correction")


class EOMCCState(BaseOutput):
    """Single EOM-CC excited state."""
    state_number: int = Field(description="State index")
    total_energy: float = Field(description="Total state energy")
    excitation_energy: float = Field(description="Excitation energy (Hartree)")
    excitation_energy_ev: float = Field(description="Excitation energy (eV)")
    r1_norm: Optional[float] = Field(default=None, description="R1 norm")
    r2_norm: Optional[float] = Field(default=None, description="R2 norm")
    symmetry: Optional[str] = Field(default=None, description="State symmetry")


class EOMCCOutput(BaseOutput):
    """
    EOM-CC excited state output.
    
    Attributes:
        reference_energy: Ground state CC energy.
        states: List of excited states.
        eom_type: Type of EOM calculation.
    """
    
    reference_energy: float = Field(description="Ground state CC energy")
    states: list[EOMCCState] = Field(default_factory=list)
    eom_type: str = Field(description="EOM type (EE, IP, EA, SF)")
    cc_method: str = Field(default="CCSD")
    basis: str = Field(description="Basis set")
    n_states: int = Field(description="Number of states computed")
