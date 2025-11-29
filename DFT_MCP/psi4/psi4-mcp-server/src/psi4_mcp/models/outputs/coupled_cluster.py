"""
Coupled Cluster Output Models.

This module provides Pydantic models for representing coupled cluster
calculation results, including CCSD, CCSD(T), EOM-CC, and related methods.

Key Classes:
    - CCSDOutput: CCSD calculation results
    - CCSDTOutput: CCSD(T) results with triples
    - EOMCCOutput: Equation-of-motion CC results
    - CCAmplitudes: CC amplitude information
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel, CalculationOutput


# =============================================================================
# CC AMPLITUDES AND DIAGNOSTICS
# =============================================================================

class CCAmplitudes(Psi4BaseModel):
    """
    Coupled cluster amplitude statistics.
    
    Attributes:
        largest_t1: Largest T1 amplitude.
        largest_t1_indices: Indices (i, a) for largest T1.
        largest_t2: Largest T2 amplitude.
        largest_t2_indices: Indices (i, j, a, b) for largest T2.
        t1_norm: Frobenius norm of T1 amplitudes.
        t2_norm: Frobenius norm of T2 amplitudes.
        n_t1: Number of T1 amplitudes.
        n_t2: Number of T2 amplitudes.
    """
    
    largest_t1: Optional[float] = Field(
        default=None,
        description="Largest T1 amplitude",
    )
    largest_t1_indices: Optional[list[int]] = Field(
        default=None,
        description="Indices for largest T1",
    )
    largest_t2: Optional[float] = Field(
        default=None,
        description="Largest T2 amplitude",
    )
    largest_t2_indices: Optional[list[int]] = Field(
        default=None,
        description="Indices for largest T2",
    )
    t1_norm: Optional[float] = Field(
        default=None,
        ge=0,
        description="T1 Frobenius norm",
    )
    t2_norm: Optional[float] = Field(
        default=None,
        ge=0,
        description="T2 Frobenius norm",
    )
    n_t1: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of T1 amplitudes",
    )
    n_t2: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of T2 amplitudes",
    )


class CCDiagnostics(Psi4BaseModel):
    """
    Coupled cluster diagnostic values.
    
    Attributes:
        t1_diagnostic: T1 diagnostic (measures single-reference character).
        d1_diagnostic: D1 diagnostic (orbital-invariant T1 diagnostic).
        d2_diagnostic: D2 diagnostic (double excitation diagnostic).
        s2: <S^2> expectation value.
        s2_expected: Expected <S^2> = S(S+1).
        percent_singles: Percent singles contribution.
        percent_doubles: Percent doubles contribution.
    """
    
    t1_diagnostic: Optional[float] = Field(
        default=None,
        ge=0,
        description="T1 diagnostic",
    )
    d1_diagnostic: Optional[float] = Field(
        default=None,
        ge=0,
        description="D1 diagnostic",
    )
    d2_diagnostic: Optional[float] = Field(
        default=None,
        ge=0,
        description="D2 diagnostic",
    )
    s2: Optional[float] = Field(
        default=None,
        ge=0,
        description="<S^2> value",
    )
    s2_expected: Optional[float] = Field(
        default=None,
        ge=0,
        description="Expected <S^2>",
    )
    percent_singles: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Singles contribution %",
    )
    percent_doubles: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Doubles contribution %",
    )
    
    @property
    def is_single_reference(self) -> bool:
        """
        Check if single-reference treatment is likely adequate.
        
        Returns True if T1 diagnostic < 0.02 (standard threshold).
        """
        if self.t1_diagnostic is None:
            return True  # Assume OK if not computed
        return self.t1_diagnostic < 0.02
    
    @property
    def spin_contamination(self) -> Optional[float]:
        """Spin contamination: <S^2> - S(S+1)."""
        if self.s2 is not None and self.s2_expected is not None:
            return self.s2 - self.s2_expected
        return None
    
    @property
    def needs_multireference(self) -> bool:
        """
        Suggest if multireference treatment may be needed.
        
        Returns True if T1 diagnostic > 0.02 or D1 > 0.05.
        """
        if self.t1_diagnostic is not None and self.t1_diagnostic > 0.02:
            return True
        if self.d1_diagnostic is not None and self.d1_diagnostic > 0.05:
            return True
        return False


class CCConvergence(Psi4BaseModel):
    """
    Coupled cluster convergence information.
    
    Attributes:
        converged: Whether CC converged.
        iterations: Number of iterations.
        final_energy_change: Final energy change.
        final_residual: Final residual norm.
        final_t1_residual: Final T1 residual.
        final_t2_residual: Final T2 residual.
        diis_vectors: Number of DIIS vectors used.
    """
    
    converged: bool = Field(
        ...,
        description="Convergence status",
    )
    iterations: int = Field(
        ...,
        ge=0,
        description="Number of iterations",
    )
    final_energy_change: Optional[float] = Field(
        default=None,
        description="Final energy change",
    )
    final_residual: Optional[float] = Field(
        default=None,
        description="Final residual",
    )
    final_t1_residual: Optional[float] = Field(
        default=None,
        description="Final T1 residual",
    )
    final_t2_residual: Optional[float] = Field(
        default=None,
        description="Final T2 residual",
    )
    diis_vectors: Optional[int] = Field(
        default=None,
        ge=0,
        description="DIIS vectors",
    )


# =============================================================================
# CCSD OUTPUT
# =============================================================================

class CCSDOutput(CalculationOutput):
    """
    Complete CCSD calculation output.
    
    Attributes:
        ccsd_correlation_energy: CCSD correlation energy.
        ccsd_total_energy: Total CCSD energy.
        reference_energy: Reference (HF) energy.
        same_spin_correlation: Same-spin correlation.
        opposite_spin_correlation: Opposite-spin correlation.
        singles_energy: Energy from singles.
        doubles_energy: Energy from doubles.
        amplitudes: Amplitude statistics.
        diagnostics: Diagnostic values.
        convergence: Convergence information.
        frozen_core: Whether core was frozen.
        n_frozen_core: Number of frozen core orbitals.
        n_occupied: Number of occupied orbitals.
        n_virtual: Number of virtual orbitals.
    """
    
    ccsd_correlation_energy: float = Field(
        ...,
        description="CCSD correlation energy",
    )
    ccsd_total_energy: float = Field(
        ...,
        description="Total CCSD energy",
    )
    reference_energy: float = Field(
        ...,
        description="Reference (HF) energy",
    )
    same_spin_correlation: Optional[float] = Field(
        default=None,
        description="Same-spin correlation",
    )
    opposite_spin_correlation: Optional[float] = Field(
        default=None,
        description="Opposite-spin correlation",
    )
    singles_energy: Optional[float] = Field(
        default=None,
        description="Singles contribution",
    )
    doubles_energy: Optional[float] = Field(
        default=None,
        description="Doubles contribution",
    )
    amplitudes: Optional[CCAmplitudes] = Field(
        default=None,
        description="Amplitude info",
    )
    diagnostics: Optional[CCDiagnostics] = Field(
        default=None,
        description="Diagnostics",
    )
    convergence: Optional[CCConvergence] = Field(
        default=None,
        description="Convergence info",
    )
    frozen_core: bool = Field(
        default=True,
        description="Core frozen",
    )
    n_frozen_core: Optional[int] = Field(
        default=None,
        ge=0,
        description="Frozen core orbitals",
    )
    n_occupied: Optional[int] = Field(
        default=None,
        ge=0,
        description="Occupied orbitals",
    )
    n_virtual: Optional[int] = Field(
        default=None,
        ge=0,
        description="Virtual orbitals",
    )
    
    @model_validator(mode="after")
    def validate_energies(self) -> "CCSDOutput":
        """Validate energy consistency."""
        computed_total = self.reference_energy + self.ccsd_correlation_energy
        if abs(computed_total - self.ccsd_total_energy) > 1e-8:
            object.__setattr__(self, 'ccsd_total_energy', computed_total)
        return self


# =============================================================================
# CCSD(T) OUTPUT
# =============================================================================

class CCSDTOutput(CCSDOutput):
    """
    CCSD(T) calculation output with perturbative triples.
    
    Attributes:
        triples_correction: (T) perturbative triples correction.
        ccsd_t_total_energy: Total CCSD(T) energy.
        triples_same_spin: Same-spin triples contribution.
        triples_opposite_spin: Opposite-spin triples contribution.
        triples_aaa: AAA triples.
        triples_aab: AAB triples.
        triples_abb: ABB triples.
        triples_bbb: BBB triples.
        triples_wall_time: Wall time for triples in seconds.
    """
    
    triples_correction: float = Field(
        ...,
        description="(T) correction",
    )
    ccsd_t_total_energy: float = Field(
        ...,
        description="Total CCSD(T) energy",
    )
    triples_same_spin: Optional[float] = Field(
        default=None,
        description="Same-spin triples",
    )
    triples_opposite_spin: Optional[float] = Field(
        default=None,
        description="Opposite-spin triples",
    )
    triples_aaa: Optional[float] = Field(
        default=None,
        description="AAA triples",
    )
    triples_aab: Optional[float] = Field(
        default=None,
        description="AAB triples",
    )
    triples_abb: Optional[float] = Field(
        default=None,
        description="ABB triples",
    )
    triples_bbb: Optional[float] = Field(
        default=None,
        description="BBB triples",
    )
    triples_wall_time: Optional[float] = Field(
        default=None,
        ge=0,
        description="Triples wall time (s)",
    )
    
    @model_validator(mode="after")
    def validate_ccsd_t_energy(self) -> "CCSDTOutput":
        """Validate CCSD(T) energy consistency."""
        computed = self.ccsd_total_energy + self.triples_correction
        if abs(computed - self.ccsd_t_total_energy) > 1e-8:
            object.__setattr__(self, 'ccsd_t_total_energy', computed)
        return self
    
    @property
    def total_correlation_energy(self) -> float:
        """Total correlation energy including triples."""
        return self.ccsd_correlation_energy + self.triples_correction


# =============================================================================
# EOM-CC OUTPUT
# =============================================================================

class EOMCCState(Psi4BaseModel):
    """
    Single EOM-CC excited state.
    
    Attributes:
        state_number: State index (1-indexed).
        symmetry: State symmetry.
        excitation_energy_hartree: Excitation energy in Hartree.
        excitation_energy_ev: Excitation energy in eV.
        total_energy: Total state energy.
        r1_norm: Norm of R1 amplitudes.
        r2_norm: Norm of R2 amplitudes.
        oscillator_strength: Oscillator strength (if computed).
        dominant_transitions: Major orbital contributions.
        converged: Whether state converged.
        iterations: Iterations for this state.
    """
    
    state_number: int = Field(
        ...,
        ge=1,
        description="State number",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="State symmetry",
    )
    excitation_energy_hartree: float = Field(
        ...,
        description="Excitation energy (Hartree)",
    )
    excitation_energy_ev: Optional[float] = Field(
        default=None,
        description="Excitation energy (eV)",
    )
    total_energy: float = Field(
        ...,
        description="Total state energy",
    )
    r1_norm: Optional[float] = Field(
        default=None,
        ge=0,
        description="R1 norm",
    )
    r2_norm: Optional[float] = Field(
        default=None,
        ge=0,
        description="R2 norm",
    )
    oscillator_strength: Optional[float] = Field(
        default=None,
        ge=0,
        description="Oscillator strength",
    )
    dominant_transitions: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Major transitions",
    )
    converged: bool = Field(
        default=True,
        description="Convergence status",
    )
    iterations: Optional[int] = Field(
        default=None,
        ge=0,
        description="Iterations",
    )
    
    @model_validator(mode="after")
    def compute_ev(self) -> "EOMCCState":
        """Compute energy in eV."""
        if self.excitation_energy_ev is None:
            from psi4_mcp.utils.helpers.units import HARTREE_TO_EV
            ev = self.excitation_energy_hartree * HARTREE_TO_EV
            object.__setattr__(self, 'excitation_energy_ev', ev)
        return self
    
    @property
    def is_singles_dominated(self) -> bool:
        """Check if state is dominated by singles."""
        if self.r1_norm is not None and self.r2_norm is not None:
            total = self.r1_norm + self.r2_norm
            if total > 0:
                return self.r1_norm / total > 0.8
        return True


class EOMCCOutput(CalculationOutput):
    """
    Complete EOM-CC calculation output.
    
    Attributes:
        eom_type: Type of EOM-CC (EE, IP, EA, SF).
        ground_state_energy: Ground state energy.
        states: List of excited states.
        n_states: Number of states computed.
        reference_symmetry: Reference state symmetry.
        target_symmetries: Target state symmetries.
        davidson_converged: Overall Davidson convergence.
    """
    
    eom_type: Literal["EE", "IP", "EA", "SF", "DIP", "DEA"] = Field(
        ...,
        description="EOM-CC type",
    )
    ground_state_energy: float = Field(
        ...,
        description="Ground state energy",
    )
    states: list[EOMCCState] = Field(
        ...,
        description="Excited states",
    )
    n_states: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of states",
    )
    reference_symmetry: Optional[str] = Field(
        default=None,
        description="Reference symmetry",
    )
    target_symmetries: Optional[list[str]] = Field(
        default=None,
        description="Target symmetries",
    )
    davidson_converged: bool = Field(
        default=True,
        description="Davidson convergence",
    )
    
    @model_validator(mode="after")
    def count_states(self) -> "EOMCCOutput":
        """Count states."""
        if self.n_states is None:
            object.__setattr__(self, 'n_states', len(self.states))
        return self
    
    def get_state(self, number: int) -> Optional[EOMCCState]:
        """Get state by number."""
        for state in self.states:
            if state.state_number == number:
                return state
        return None
    
    def get_bright_states(self, threshold: float = 0.01) -> list[EOMCCState]:
        """Get states with significant oscillator strength."""
        return [
            s for s in self.states 
            if s.oscillator_strength is not None and s.oscillator_strength >= threshold
        ]
    
    @property
    def vertical_excitation_energies(self) -> list[float]:
        """Get all excitation energies in eV."""
        return [s.excitation_energy_ev or 0.0 for s in self.states]


# =============================================================================
# CC2 OUTPUT
# =============================================================================

class CC2Output(CalculationOutput):
    """
    CC2 calculation output.
    
    Attributes:
        cc2_correlation_energy: CC2 correlation energy.
        cc2_total_energy: Total CC2 energy.
        reference_energy: Reference energy.
        mp2_correlation_energy: MP2 correlation (for comparison).
        diagnostics: CC diagnostics.
        convergence: Convergence info.
    """
    
    cc2_correlation_energy: float = Field(
        ...,
        description="CC2 correlation energy",
    )
    cc2_total_energy: float = Field(
        ...,
        description="Total CC2 energy",
    )
    reference_energy: float = Field(
        ...,
        description="Reference energy",
    )
    mp2_correlation_energy: Optional[float] = Field(
        default=None,
        description="MP2 correlation",
    )
    diagnostics: Optional[CCDiagnostics] = Field(
        default=None,
        description="Diagnostics",
    )
    convergence: Optional[CCConvergence] = Field(
        default=None,
        description="Convergence",
    )


# =============================================================================
# DLPNO-CCSD(T) OUTPUT
# =============================================================================

class DLPNOOutput(CalculationOutput):
    """
    DLPNO-CCSD(T) calculation output.
    
    Attributes:
        dlpno_correlation_energy: DLPNO correlation energy.
        dlpno_total_energy: Total DLPNO energy.
        reference_energy: Reference energy.
        triples_correction: Triples correction.
        pno_threshold: PNO truncation threshold.
        n_pno_pairs: Number of PNO pairs.
        strong_pairs: Number of strong pairs.
        weak_pairs: Number of weak pairs.
        pno_incompleteness: PNO incompleteness error estimate.
    """
    
    dlpno_correlation_energy: float = Field(
        ...,
        description="DLPNO correlation energy",
    )
    dlpno_total_energy: float = Field(
        ...,
        description="Total DLPNO energy",
    )
    reference_energy: float = Field(
        ...,
        description="Reference energy",
    )
    triples_correction: Optional[float] = Field(
        default=None,
        description="Triples correction",
    )
    pno_threshold: float = Field(
        default=1e-7,
        description="PNO threshold",
    )
    n_pno_pairs: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of PNO pairs",
    )
    strong_pairs: Optional[int] = Field(
        default=None,
        ge=0,
        description="Strong pairs",
    )
    weak_pairs: Optional[int] = Field(
        default=None,
        ge=0,
        description="Weak pairs",
    )
    pno_incompleteness: Optional[float] = Field(
        default=None,
        description="PNO incompleteness",
    )
