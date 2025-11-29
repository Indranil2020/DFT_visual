"""
TDDFT and Excited State Output Models.

This module provides Pydantic models for representing time-dependent
DFT (TDDFT) and other excited state calculation results.

Key Classes:
    - TDDFTState: Single TDDFT excited state
    - TDDFTOutput: Complete TDDFT calculation
    - NaturalTransitionOrbital: NTO analysis
    - ExcitedStateAnalysis: Detailed state analysis
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel, CalculationOutput


# =============================================================================
# ORBITAL TRANSITIONS
# =============================================================================

class OrbitalTransition(Psi4BaseModel):
    """
    Single orbital transition contribution.
    
    Attributes:
        from_orbital: Source orbital index.
        to_orbital: Target orbital index.
        from_spin: Source spin (alpha/beta).
        to_spin: Target spin (alpha/beta).
        coefficient: Transition coefficient.
        percent: Percentage contribution.
        from_symmetry: Source orbital symmetry.
        to_symmetry: Target orbital symmetry.
    """
    
    from_orbital: int = Field(
        ...,
        ge=0,
        description="Source orbital index",
    )
    to_orbital: int = Field(
        ...,
        ge=0,
        description="Target orbital index",
    )
    from_spin: Literal["alpha", "beta"] = Field(
        default="alpha",
        description="Source spin",
    )
    to_spin: Literal["alpha", "beta"] = Field(
        default="alpha",
        description="Target spin",
    )
    coefficient: float = Field(
        ...,
        description="Transition coefficient",
    )
    percent: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Percentage contribution",
    )
    from_symmetry: Optional[str] = Field(
        default=None,
        description="Source symmetry",
    )
    to_symmetry: Optional[str] = Field(
        default=None,
        description="Target symmetry",
    )
    
    @property
    def is_homo_lumo(self) -> bool:
        """Check if this is a HOMO->LUMO transition."""
        # This is a simplified check; would need orbital info for accurate determination
        return self.percent is not None and self.percent > 70
    
    @property
    def coefficient_squared(self) -> float:
        """Square of coefficient (contribution weight)."""
        return self.coefficient ** 2
    
    def __str__(self) -> str:
        """String representation."""
        pct = f" ({self.percent:.1f}%)" if self.percent else ""
        return f"{self.from_orbital} -> {self.to_orbital}{pct}"


class NaturalTransitionOrbital(Psi4BaseModel):
    """
    Natural Transition Orbital (NTO) data.
    
    Attributes:
        pair_index: NTO pair index.
        occupation: NTO occupation (singular value squared).
        hole_orbital: Hole NTO coefficients.
        particle_orbital: Particle NTO coefficients.
        percent_contribution: Percentage contribution to transition.
    """
    
    pair_index: int = Field(
        ...,
        ge=0,
        description="NTO pair index",
    )
    occupation: float = Field(
        ...,
        ge=0,
        le=2,
        description="NTO occupation",
    )
    hole_orbital: Optional[list[float]] = Field(
        default=None,
        description="Hole NTO coefficients",
    )
    particle_orbital: Optional[list[float]] = Field(
        default=None,
        description="Particle NTO coefficients",
    )
    percent_contribution: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Percentage contribution",
    )


# =============================================================================
# EXCITED STATE
# =============================================================================

class ExcitedStateCharacter(Psi4BaseModel):
    """
    Character analysis of an excited state.
    
    Attributes:
        state_type: Type of state (local, CT, Rydberg, etc.).
        ct_number: Charge transfer number.
        ct_distance: Charge transfer distance in Angstrom.
        participation_ratio: Participation ratio (delocalization).
        attachment_density: Attachment density info.
        detachment_density: Detachment density info.
        hole_position: Hole centroid position.
        particle_position: Particle centroid position.
    """
    
    state_type: Optional[str] = Field(
        default=None,
        description="State type (local, CT, Rydberg)",
    )
    ct_number: Optional[float] = Field(
        default=None,
        ge=0,
        description="CT number",
    )
    ct_distance: Optional[float] = Field(
        default=None,
        ge=0,
        description="CT distance (Angstrom)",
    )
    participation_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        description="Participation ratio",
    )
    attachment_density: Optional[dict[str, Any]] = Field(
        default=None,
        description="Attachment density info",
    )
    detachment_density: Optional[dict[str, Any]] = Field(
        default=None,
        description="Detachment density info",
    )
    hole_position: Optional[list[float]] = Field(
        default=None,
        description="Hole centroid [x, y, z]",
    )
    particle_position: Optional[list[float]] = Field(
        default=None,
        description="Particle centroid [x, y, z]",
    )
    
    @property
    def is_charge_transfer(self) -> bool:
        """Check if this is a charge-transfer state."""
        if self.ct_number is not None:
            return self.ct_number > 0.5
        if self.state_type:
            return "ct" in self.state_type.lower()
        return False


class TDDFTState(Psi4BaseModel):
    """
    Single TDDFT excited state.
    
    Attributes:
        state_number: State index (1-indexed).
        multiplicity: Spin multiplicity.
        symmetry: State symmetry label.
        excitation_energy_hartree: Excitation energy in Hartree.
        excitation_energy_ev: Excitation energy in eV.
        excitation_energy_nm: Wavelength in nm.
        excitation_energy_cm_inv: Energy in cm^-1.
        total_energy: Total state energy.
        oscillator_strength: Oscillator strength.
        rotatory_strength_length: Rotatory strength (length gauge).
        rotatory_strength_velocity: Rotatory strength (velocity gauge).
        transition_dipole: Transition dipole moment [x, y, z].
        transition_dipole_magnitude: Transition dipole magnitude.
        magnetic_dipole: Magnetic transition dipole.
        transitions: Orbital transitions.
        ntos: Natural Transition Orbitals.
        character: State character analysis.
        s2: <S^2> value.
        converged: Whether state converged.
    """
    
    state_number: int = Field(
        ...,
        ge=1,
        description="State number",
    )
    multiplicity: int = Field(
        default=1,
        ge=1,
        description="Multiplicity",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="Symmetry",
    )
    excitation_energy_hartree: float = Field(
        ...,
        description="Excitation energy (Hartree)",
    )
    excitation_energy_ev: Optional[float] = Field(
        default=None,
        description="Excitation energy (eV)",
    )
    excitation_energy_nm: Optional[float] = Field(
        default=None,
        gt=0,
        description="Wavelength (nm)",
    )
    excitation_energy_cm_inv: Optional[float] = Field(
        default=None,
        description="Energy (cm^-1)",
    )
    total_energy: Optional[float] = Field(
        default=None,
        description="Total state energy",
    )
    oscillator_strength: float = Field(
        default=0.0,
        ge=0,
        description="Oscillator strength",
    )
    rotatory_strength_length: Optional[float] = Field(
        default=None,
        description="Rotatory strength (length)",
    )
    rotatory_strength_velocity: Optional[float] = Field(
        default=None,
        description="Rotatory strength (velocity)",
    )
    transition_dipole: Optional[list[float]] = Field(
        default=None,
        description="Transition dipole [x, y, z]",
    )
    transition_dipole_magnitude: Optional[float] = Field(
        default=None,
        ge=0,
        description="Transition dipole magnitude",
    )
    magnetic_dipole: Optional[list[float]] = Field(
        default=None,
        description="Magnetic dipole [x, y, z]",
    )
    transitions: list[OrbitalTransition] = Field(
        default_factory=list,
        description="Orbital transitions",
    )
    ntos: list[NaturalTransitionOrbital] = Field(
        default_factory=list,
        description="NTOs",
    )
    character: Optional[ExcitedStateCharacter] = Field(
        default=None,
        description="State character",
    )
    s2: Optional[float] = Field(
        default=None,
        ge=0,
        description="<S^2> value",
    )
    converged: bool = Field(
        default=True,
        description="Convergence status",
    )
    
    @model_validator(mode="after")
    def compute_energy_conversions(self) -> "TDDFTState":
        """Compute energy unit conversions."""
        from psi4_mcp.utils.helpers.units import HARTREE_TO_EV
        
        if self.excitation_energy_ev is None:
            ev = self.excitation_energy_hartree * HARTREE_TO_EV
            object.__setattr__(self, 'excitation_energy_ev', ev)
        
        if self.excitation_energy_nm is None and self.excitation_energy_ev:
            # lambda (nm) = 1239.84 / E (eV)
            if self.excitation_energy_ev > 0:
                nm = 1239.84 / self.excitation_energy_ev
                object.__setattr__(self, 'excitation_energy_nm', nm)
        
        if self.excitation_energy_cm_inv is None and self.excitation_energy_ev:
            # E (cm^-1) = E (eV) * 8065.54
            cm_inv = self.excitation_energy_ev * 8065.54
            object.__setattr__(self, 'excitation_energy_cm_inv', cm_inv)
        
        return self
    
    @property
    def is_bright(self) -> bool:
        """Check if state is optically bright."""
        return self.oscillator_strength > 0.01
    
    @property
    def is_dark(self) -> bool:
        """Check if state is optically dark."""
        return self.oscillator_strength < 0.001
    
    @property
    def is_singlet(self) -> bool:
        """Check if this is a singlet state."""
        return self.multiplicity == 1
    
    @property
    def is_triplet(self) -> bool:
        """Check if this is a triplet state."""
        return self.multiplicity == 3
    
    def get_dominant_transition(self) -> Optional[OrbitalTransition]:
        """Get the dominant orbital transition."""
        if not self.transitions:
            return None
        return max(self.transitions, key=lambda t: abs(t.coefficient))


# =============================================================================
# TDDFT OUTPUT
# =============================================================================

class TDDFTConvergence(Psi4BaseModel):
    """
    TDDFT convergence information.
    
    Attributes:
        algorithm: Algorithm used (Davidson, etc.).
        converged: Whether all roots converged.
        n_converged: Number of converged roots.
        n_requested: Number of requested roots.
        n_iterations: Number of iterations.
        residual_threshold: Residual convergence threshold.
    """
    
    algorithm: str = Field(
        default="Davidson",
        description="Algorithm",
    )
    converged: bool = Field(
        ...,
        description="Overall convergence",
    )
    n_converged: int = Field(
        ...,
        ge=0,
        description="Converged roots",
    )
    n_requested: int = Field(
        ...,
        ge=0,
        description="Requested roots",
    )
    n_iterations: int = Field(
        ...,
        ge=0,
        description="Iterations",
    )
    residual_threshold: float = Field(
        default=1e-6,
        gt=0,
        description="Residual threshold",
    )


class TDDFTOutput(CalculationOutput):
    """
    Complete TDDFT calculation output.
    
    Attributes:
        method: TDDFT method (TDDFT, TDA, RPA).
        functional: DFT functional.
        states: List of excited states.
        n_singlets: Number of singlet states.
        n_triplets: Number of triplet states.
        ground_state_energy: Ground state energy.
        convergence: Convergence information.
        response_type: Response type (linear, quadratic).
        tamm_dancoff: Whether Tamm-Dancoff approximation was used.
        singlet_triplet_gap: Lowest S-T gap in eV.
    """
    
    method: str = Field(
        default="TDDFT",
        description="Method",
    )
    functional: Optional[str] = Field(
        default=None,
        description="Functional",
    )
    states: list[TDDFTState] = Field(
        ...,
        description="Excited states",
    )
    n_singlets: int = Field(
        default=0,
        ge=0,
        description="Singlet states",
    )
    n_triplets: int = Field(
        default=0,
        ge=0,
        description="Triplet states",
    )
    ground_state_energy: float = Field(
        ...,
        description="Ground state energy",
    )
    convergence: Optional[TDDFTConvergence] = Field(
        default=None,
        description="Convergence info",
    )
    response_type: str = Field(
        default="linear",
        description="Response type",
    )
    tamm_dancoff: bool = Field(
        default=False,
        description="TDA used",
    )
    singlet_triplet_gap: Optional[float] = Field(
        default=None,
        description="Lowest S-T gap (eV)",
    )
    
    @property
    def n_states(self) -> int:
        """Total number of excited states."""
        return len(self.states)
    
    def get_singlets(self) -> list[TDDFTState]:
        """Get all singlet states."""
        return [s for s in self.states if s.is_singlet]
    
    def get_triplets(self) -> list[TDDFTState]:
        """Get all triplet states."""
        return [s for s in self.states if s.is_triplet]
    
    def get_bright_states(self, threshold: float = 0.01) -> list[TDDFTState]:
        """Get states with oscillator strength above threshold."""
        return [s for s in self.states if s.oscillator_strength >= threshold]
    
    def get_states_in_range(
        self, 
        low_ev: float, 
        high_ev: float
    ) -> list[TDDFTState]:
        """Get states in an energy range (eV)."""
        return [
            s for s in self.states
            if s.excitation_energy_ev is not None 
            and low_ev <= s.excitation_energy_ev <= high_ev
        ]
    
    def get_state(self, number: int) -> Optional[TDDFTState]:
        """Get state by number."""
        for state in self.states:
            if state.state_number == number:
                return state
        return None
    
    @property
    def lowest_singlet(self) -> Optional[TDDFTState]:
        """Get lowest singlet excited state (S1)."""
        singlets = self.get_singlets()
        if singlets:
            return min(singlets, key=lambda s: s.excitation_energy_hartree)
        return None
    
    @property
    def lowest_triplet(self) -> Optional[TDDFTState]:
        """Get lowest triplet excited state (T1)."""
        triplets = self.get_triplets()
        if triplets:
            return min(triplets, key=lambda s: s.excitation_energy_hartree)
        return None
    
    @property
    def absorption_maximum(self) -> Optional[TDDFTState]:
        """Get state with highest oscillator strength."""
        if not self.states:
            return None
        return max(self.states, key=lambda s: s.oscillator_strength)


# =============================================================================
# ADC OUTPUT
# =============================================================================

class ADCState(TDDFTState):
    """
    ADC excited state (extends TDDFT state).
    
    Additional Attributes:
        adc_level: ADC level (1, 2, 3).
        doubles_norm: Norm of doubles contribution.
    """
    
    adc_level: int = Field(
        default=2,
        ge=1,
        le=3,
        description="ADC level",
    )
    doubles_norm: Optional[float] = Field(
        default=None,
        ge=0,
        description="Doubles norm",
    )


class ADCOutput(CalculationOutput):
    """
    ADC calculation output.
    
    Attributes:
        adc_level: ADC level (ADC(1), ADC(2), ADC(3)).
        states: List of ADC excited states.
        mp2_correlation_energy: MP2 correlation energy.
        ground_state_energy: Ground state energy.
        is_strict: Whether strict ADC was used.
        is_cvs: Whether CVS (core-valence separation) was used.
    """
    
    adc_level: int = Field(
        ...,
        ge=1,
        le=3,
        description="ADC level",
    )
    states: list[ADCState] = Field(
        ...,
        description="Excited states",
    )
    mp2_correlation_energy: Optional[float] = Field(
        default=None,
        description="MP2 correlation",
    )
    ground_state_energy: float = Field(
        ...,
        description="Ground state energy",
    )
    is_strict: bool = Field(
        default=False,
        description="Strict ADC",
    )
    is_cvs: bool = Field(
        default=False,
        description="CVS used",
    )
    
    @property
    def method_name(self) -> str:
        """Get method name string."""
        prefix = "CVS-" if self.is_cvs else ""
        suffix = "-s" if self.is_strict else ""
        return f"{prefix}ADC({self.adc_level}){suffix}"


# =============================================================================
# CIS OUTPUT
# =============================================================================

class CISOutput(CalculationOutput):
    """
    CIS (Configuration Interaction Singles) output.
    
    Attributes:
        states: CIS excited states.
        ground_state_energy: HF ground state energy.
        cis_type: CIS variant (CIS, CIS(D), etc.).
        doubles_correction: (D) correction if applicable.
    """
    
    states: list[TDDFTState] = Field(
        ...,
        description="CIS states",
    )
    ground_state_energy: float = Field(
        ...,
        description="Ground state energy",
    )
    cis_type: str = Field(
        default="CIS",
        description="CIS variant",
    )
    doubles_correction: Optional[float] = Field(
        default=None,
        description="(D) correction",
    )
