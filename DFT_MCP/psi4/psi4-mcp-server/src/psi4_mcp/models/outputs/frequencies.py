"""
Vibrational Frequency and Thermodynamics Output Models.

This module provides Pydantic models for representing vibrational
frequency calculations and thermodynamic property results.

Key Classes:
    - VibrationalMode: Single vibrational mode data
    - FrequencyOutput: Complete frequency calculation result
    - ThermodynamicsOutput: Thermodynamic properties
    - AnharmonicOutput: Anharmonic frequency data
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator
import math

from psi4_mcp.models.base import Psi4BaseModel, CalculationOutput


# =============================================================================
# VIBRATIONAL MODE
# =============================================================================

class VibrationalMode(Psi4BaseModel):
    """
    Data for a single vibrational mode.
    
    Attributes:
        mode_number: Mode index (1-indexed).
        frequency: Frequency in cm^-1.
        frequency_scaled: Scaled frequency in cm^-1.
        ir_intensity: IR intensity in km/mol.
        raman_activity: Raman activity in A^4/amu.
        depolarization_ratio: Raman depolarization ratio.
        reduced_mass: Reduced mass in amu.
        force_constant: Force constant in mDyne/A.
        displacement: Displacement vectors [[dx,dy,dz], ...].
        symmetry: Symmetry label (if available).
        is_imaginary: Whether this is an imaginary frequency.
    """
    
    mode_number: int = Field(
        ...,
        ge=1,
        description="Mode number (1-indexed)",
    )
    frequency: float = Field(
        ...,
        description="Frequency in cm^-1",
    )
    frequency_scaled: Optional[float] = Field(
        default=None,
        description="Scaled frequency in cm^-1",
    )
    ir_intensity: Optional[float] = Field(
        default=None,
        ge=0,
        description="IR intensity in km/mol",
    )
    raman_activity: Optional[float] = Field(
        default=None,
        ge=0,
        description="Raman activity in A^4/amu",
    )
    depolarization_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=0.75,
        description="Raman depolarization ratio",
    )
    reduced_mass: Optional[float] = Field(
        default=None,
        gt=0,
        description="Reduced mass in amu",
    )
    force_constant: Optional[float] = Field(
        default=None,
        description="Force constant in mDyne/A",
    )
    displacement: Optional[list[list[float]]] = Field(
        default=None,
        description="Displacement vectors",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="Symmetry label",
    )
    is_imaginary: bool = Field(
        default=False,
        description="Whether imaginary frequency",
    )
    
    @model_validator(mode="after")
    def check_imaginary(self) -> "VibrationalMode":
        """Set imaginary flag based on frequency."""
        if self.frequency < 0 and not self.is_imaginary:
            object.__setattr__(self, 'is_imaginary', True)
        return self
    
    @property
    def frequency_hz(self) -> float:
        """Frequency in Hz."""
        c = 2.99792458e10  # speed of light in cm/s
        return abs(self.frequency) * c
    
    @property
    def wavenumber(self) -> float:
        """Wavenumber (same as frequency in cm^-1)."""
        return self.frequency
    
    @property
    def wavelength_um(self) -> Optional[float]:
        """Wavelength in micrometers."""
        if abs(self.frequency) < 1e-6:
            return None
        return 10000.0 / abs(self.frequency)
    
    @property
    def period_fs(self) -> Optional[float]:
        """Vibrational period in femtoseconds."""
        if abs(self.frequency) < 1e-6:
            return None
        # period = 1/frequency, frequency in Hz
        c = 2.99792458e10  # cm/s
        freq_hz = abs(self.frequency) * c
        return 1e15 / freq_hz  # Convert s to fs
    
    @property
    def zpve_contribution(self) -> float:
        """Zero-point energy contribution from this mode in Hartree."""
        # ZPVE = (1/2) * h * nu
        # In cm^-1: ZPVE (Hartree) = 0.5 * frequency (cm^-1) * 4.556335e-6
        if self.is_imaginary:
            return 0.0
        return 0.5 * abs(self.frequency) * 4.556335e-6


# =============================================================================
# FREQUENCY SUMMARY
# =============================================================================

class FrequencySummary(Psi4BaseModel):
    """
    Summary statistics for vibrational frequencies.
    
    Attributes:
        n_modes: Total number of vibrational modes.
        n_imaginary: Number of imaginary frequencies.
        n_real: Number of real frequencies.
        lowest_real: Lowest real frequency.
        highest_frequency: Highest frequency.
        zpve: Zero-point vibrational energy in Hartree.
        zpve_kcal_mol: ZPVE in kcal/mol.
        imaginary_frequencies: List of imaginary frequencies.
    """
    
    n_modes: int = Field(
        ...,
        ge=0,
        description="Total vibrational modes",
    )
    n_imaginary: int = Field(
        default=0,
        ge=0,
        description="Number of imaginary frequencies",
    )
    n_real: int = Field(
        default=0,
        ge=0,
        description="Number of real frequencies",
    )
    lowest_real: Optional[float] = Field(
        default=None,
        description="Lowest real frequency in cm^-1",
    )
    highest_frequency: Optional[float] = Field(
        default=None,
        description="Highest frequency in cm^-1",
    )
    zpve: float = Field(
        default=0.0,
        description="ZPVE in Hartree",
    )
    zpve_kcal_mol: float = Field(
        default=0.0,
        description="ZPVE in kcal/mol",
    )
    imaginary_frequencies: list[float] = Field(
        default_factory=list,
        description="List of imaginary frequencies",
    )
    
    @classmethod
    def from_modes(cls, modes: list[VibrationalMode]) -> "FrequencySummary":
        """Create summary from list of modes."""
        from psi4_mcp.utils.helpers.units import HARTREE_TO_KCAL_MOL
        
        n_modes = len(modes)
        imaginary = [m for m in modes if m.is_imaginary]
        real = [m for m in modes if not m.is_imaginary]
        
        zpve = sum(m.zpve_contribution for m in real)
        
        return cls(
            n_modes=n_modes,
            n_imaginary=len(imaginary),
            n_real=len(real),
            lowest_real=min(m.frequency for m in real) if real else None,
            highest_frequency=max(m.frequency for m in modes) if modes else None,
            zpve=zpve,
            zpve_kcal_mol=zpve * HARTREE_TO_KCAL_MOL,
            imaginary_frequencies=[m.frequency for m in imaginary],
        )


# =============================================================================
# THERMODYNAMICS
# =============================================================================

class MomentOfInertia(Psi4BaseModel):
    """
    Rotational moments of inertia.
    
    Attributes:
        ia: Moment along a-axis in amu*Bohr^2.
        ib: Moment along b-axis in amu*Bohr^2.
        ic: Moment along c-axis in amu*Bohr^2.
        rotational_constants: Rotational constants [A, B, C] in cm^-1.
        is_linear: Whether molecule is linear.
        rotor_type: Type of rotor (spherical, symmetric, asymmetric).
    """
    
    ia: float = Field(
        ...,
        ge=0,
        description="Moment Ia in amu*Bohr^2",
    )
    ib: float = Field(
        ...,
        ge=0,
        description="Moment Ib in amu*Bohr^2",
    )
    ic: float = Field(
        ...,
        ge=0,
        description="Moment Ic in amu*Bohr^2",
    )
    rotational_constants: Optional[list[float]] = Field(
        default=None,
        description="Rotational constants [A, B, C] in cm^-1",
    )
    is_linear: bool = Field(
        default=False,
        description="Whether molecule is linear",
    )
    rotor_type: Optional[str] = Field(
        default=None,
        description="Rotor type",
    )
    
    @model_validator(mode="after")
    def determine_rotor_type(self) -> "MomentOfInertia":
        """Determine rotor type from moments."""
        if self.rotor_type is not None:
            return self
        
        tol = 1e-6
        
        if self.ia < tol:
            rotor = "linear"
        elif abs(self.ia - self.ib) < tol and abs(self.ib - self.ic) < tol:
            rotor = "spherical"
        elif abs(self.ia - self.ib) < tol or abs(self.ib - self.ic) < tol:
            rotor = "symmetric"
        else:
            rotor = "asymmetric"
        
        object.__setattr__(self, 'rotor_type', rotor)
        return self


class ThermodynamicQuantities(Psi4BaseModel):
    """
    Thermodynamic quantities at a specific temperature/pressure.
    
    Attributes:
        temperature: Temperature in Kelvin.
        pressure: Pressure in atm.
        electronic_energy: Electronic energy in Hartree.
        zpve: Zero-point vibrational energy in Hartree.
        thermal_energy: Thermal energy correction in Hartree.
        enthalpy: Enthalpy (H) in Hartree.
        entropy: Entropy (S) in cal/(mol*K).
        gibbs_free_energy: Gibbs free energy (G) in Hartree.
        heat_capacity_cv: Heat capacity Cv in cal/(mol*K).
        heat_capacity_cp: Heat capacity Cp in cal/(mol*K).
        internal_energy: Internal energy (U) in Hartree.
    """
    
    temperature: float = Field(
        default=298.15,
        gt=0,
        description="Temperature in K",
    )
    pressure: float = Field(
        default=1.0,
        gt=0,
        description="Pressure in atm",
    )
    electronic_energy: float = Field(
        ...,
        description="Electronic energy in Hartree",
    )
    zpve: float = Field(
        default=0.0,
        description="ZPVE in Hartree",
    )
    thermal_energy: float = Field(
        default=0.0,
        description="Thermal energy correction in Hartree",
    )
    enthalpy: float = Field(
        ...,
        description="Enthalpy in Hartree",
    )
    entropy: float = Field(
        default=0.0,
        description="Entropy in cal/(mol*K)",
    )
    gibbs_free_energy: float = Field(
        ...,
        description="Gibbs free energy in Hartree",
    )
    heat_capacity_cv: Optional[float] = Field(
        default=None,
        description="Cv in cal/(mol*K)",
    )
    heat_capacity_cp: Optional[float] = Field(
        default=None,
        description="Cp in cal/(mol*K)",
    )
    internal_energy: Optional[float] = Field(
        default=None,
        description="Internal energy in Hartree",
    )
    
    @property
    def e_plus_zpve(self) -> float:
        """Electronic energy plus ZPVE."""
        return self.electronic_energy + self.zpve
    
    @property
    def entropy_hartree(self) -> float:
        """Entropy in Hartree/K."""
        # Convert cal/(mol*K) to Hartree/K
        # 1 Hartree = 627.5095 kcal/mol
        return self.entropy / (627.5095 * 1000)


class ThermodynamicComponents(Psi4BaseModel):
    """
    Breakdown of thermodynamic contributions.
    
    Attributes:
        translational: Translational contributions.
        rotational: Rotational contributions.
        vibrational: Vibrational contributions.
        electronic: Electronic contributions.
    """
    
    translational: Optional[dict[str, float]] = Field(
        default=None,
        description="Translational contributions",
    )
    rotational: Optional[dict[str, float]] = Field(
        default=None,
        description="Rotational contributions",
    )
    vibrational: Optional[dict[str, float]] = Field(
        default=None,
        description="Vibrational contributions",
    )
    electronic: Optional[dict[str, float]] = Field(
        default=None,
        description="Electronic contributions",
    )


class ThermodynamicsOutput(Psi4BaseModel):
    """
    Complete thermodynamics calculation output.
    
    Attributes:
        quantities: Primary thermodynamic quantities.
        components: Breakdown by contribution type.
        moments_of_inertia: Rotational moments of inertia.
        molecular_mass: Total molecular mass in amu.
        symmetry_number: Rotational symmetry number.
        multiplicity: Electronic spin multiplicity.
        n_atoms: Number of atoms.
        is_linear: Whether molecule is linear.
        scale_factor: Frequency scale factor used.
    """
    
    quantities: ThermodynamicQuantities = Field(
        ...,
        description="Thermodynamic quantities",
    )
    components: Optional[ThermodynamicComponents] = Field(
        default=None,
        description="Contribution breakdown",
    )
    moments_of_inertia: Optional[MomentOfInertia] = Field(
        default=None,
        description="Moments of inertia",
    )
    molecular_mass: float = Field(
        ...,
        gt=0,
        description="Molecular mass in amu",
    )
    symmetry_number: int = Field(
        default=1,
        ge=1,
        description="Rotational symmetry number",
    )
    multiplicity: int = Field(
        default=1,
        ge=1,
        description="Spin multiplicity",
    )
    n_atoms: int = Field(
        ...,
        ge=1,
        description="Number of atoms",
    )
    is_linear: bool = Field(
        default=False,
        description="Whether molecule is linear",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        description="Frequency scale factor",
    )


# =============================================================================
# FREQUENCY OUTPUT
# =============================================================================

class FrequencyOutput(CalculationOutput):
    """
    Complete vibrational frequency calculation output.
    
    Attributes:
        modes: List of vibrational modes.
        summary: Frequency summary statistics.
        thermodynamics: Thermodynamic properties.
        electronic_energy: Electronic energy at geometry.
        hessian: Hessian matrix (if requested).
        symbols: Atomic symbols.
        coordinates: Atomic coordinates.
        mass_weighted: Whether mass-weighted coordinates were used.
        analytical: Whether analytical derivatives were used.
        temperature: Temperature for thermodynamics.
        pressure: Pressure for thermodynamics.
        scale_factor: Frequency scaling factor.
        point_group: Point group symmetry.
    """
    
    modes: list[VibrationalMode] = Field(
        default_factory=list,
        description="Vibrational modes",
    )
    summary: Optional[FrequencySummary] = Field(
        default=None,
        description="Frequency summary",
    )
    thermodynamics: Optional[ThermodynamicsOutput] = Field(
        default=None,
        description="Thermodynamic properties",
    )
    electronic_energy: float = Field(
        ...,
        description="Electronic energy in Hartree",
    )
    hessian: Optional[list[list[float]]] = Field(
        default=None,
        description="Hessian matrix",
    )
    symbols: list[str] = Field(
        ...,
        min_length=1,
        description="Atomic symbols",
    )
    coordinates: list[list[float]] = Field(
        ...,
        description="Atomic coordinates",
    )
    mass_weighted: bool = Field(
        default=True,
        description="Mass-weighted coordinates",
    )
    analytical: bool = Field(
        default=True,
        description="Analytical derivatives",
    )
    temperature: float = Field(
        default=298.15,
        gt=0,
        description="Temperature in K",
    )
    pressure: float = Field(
        default=1.0,
        gt=0,
        description="Pressure in atm",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        description="Frequency scale factor",
    )
    point_group: Optional[str] = Field(
        default=None,
        description="Point group symmetry",
    )
    
    @model_validator(mode="after")
    def compute_summary(self) -> "FrequencyOutput":
        """Compute summary if not provided."""
        if self.summary is None and self.modes:
            summary = FrequencySummary.from_modes(self.modes)
            object.__setattr__(self, 'summary', summary)
        return self
    
    @property
    def n_modes(self) -> int:
        """Number of vibrational modes."""
        return len(self.modes)
    
    @property
    def n_imaginary(self) -> int:
        """Number of imaginary frequencies."""
        return sum(1 for m in self.modes if m.is_imaginary)
    
    @property
    def zpve(self) -> float:
        """Zero-point vibrational energy in Hartree."""
        return sum(m.zpve_contribution for m in self.modes if not m.is_imaginary)
    
    @property
    def is_minimum(self) -> bool:
        """Check if this is a minimum (no imaginary frequencies)."""
        return self.n_imaginary == 0
    
    @property
    def is_transition_state(self) -> bool:
        """Check if this is a transition state (one imaginary frequency)."""
        return self.n_imaginary == 1
    
    def get_imaginary_modes(self) -> list[VibrationalMode]:
        """Get all imaginary modes."""
        return [m for m in self.modes if m.is_imaginary]
    
    def get_frequency_range(self, low: float, high: float) -> list[VibrationalMode]:
        """Get modes within a frequency range."""
        return [m for m in self.modes if low <= m.frequency <= high]
    
    def get_ir_active_modes(self, threshold: float = 1.0) -> list[VibrationalMode]:
        """Get IR-active modes above intensity threshold."""
        return [
            m for m in self.modes 
            if m.ir_intensity is not None and m.ir_intensity >= threshold
        ]
    
    def get_raman_active_modes(self, threshold: float = 1.0) -> list[VibrationalMode]:
        """Get Raman-active modes above activity threshold."""
        return [
            m for m in self.modes 
            if m.raman_activity is not None and m.raman_activity >= threshold
        ]


# =============================================================================
# ANHARMONIC OUTPUT
# =============================================================================

class AnharmonicMode(Psi4BaseModel):
    """
    Anharmonic correction data for a vibrational mode.
    
    Attributes:
        mode_number: Mode number.
        harmonic_frequency: Harmonic frequency in cm^-1.
        anharmonic_frequency: Anharmonic frequency in cm^-1.
        anharmonicity_constant: Anharmonicity constant (chi) in cm^-1.
        correction: Anharmonic correction in cm^-1.
    """
    
    mode_number: int = Field(
        ...,
        ge=1,
        description="Mode number",
    )
    harmonic_frequency: float = Field(
        ...,
        description="Harmonic frequency in cm^-1",
    )
    anharmonic_frequency: float = Field(
        ...,
        description="Anharmonic frequency in cm^-1",
    )
    anharmonicity_constant: Optional[float] = Field(
        default=None,
        description="Anharmonicity constant (chi) in cm^-1",
    )
    correction: Optional[float] = Field(
        default=None,
        description="Anharmonic correction in cm^-1",
    )
    
    @model_validator(mode="after")
    def compute_correction(self) -> "AnharmonicMode":
        """Compute correction if not provided."""
        if self.correction is None:
            corr = self.anharmonic_frequency - self.harmonic_frequency
            object.__setattr__(self, 'correction', corr)
        return self


class AnharmonicOutput(Psi4BaseModel):
    """
    Anharmonic frequency calculation output.
    
    Attributes:
        modes: List of anharmonic modes.
        harmonic_zpve: Harmonic ZPVE in Hartree.
        anharmonic_zpve: Anharmonic ZPVE in Hartree.
        zpve_correction: ZPVE anharmonic correction.
        xij_matrix: Anharmonicity matrix.
    """
    
    modes: list[AnharmonicMode] = Field(
        ...,
        description="Anharmonic modes",
    )
    harmonic_zpve: float = Field(
        ...,
        description="Harmonic ZPVE in Hartree",
    )
    anharmonic_zpve: float = Field(
        ...,
        description="Anharmonic ZPVE in Hartree",
    )
    zpve_correction: Optional[float] = Field(
        default=None,
        description="ZPVE anharmonic correction",
    )
    xij_matrix: Optional[list[list[float]]] = Field(
        default=None,
        description="Anharmonicity matrix",
    )
    
    @model_validator(mode="after")
    def compute_zpve_correction(self) -> "AnharmonicOutput":
        """Compute ZPVE correction if not provided."""
        if self.zpve_correction is None:
            corr = self.anharmonic_zpve - self.harmonic_zpve
            object.__setattr__(self, 'zpve_correction', corr)
        return self
