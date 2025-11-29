"""
Spectroscopy Output Models.

This module provides Pydantic models for representing various spectroscopic
calculations including IR, Raman, UV-Vis, NMR, and EPR.

Key Classes:
    - IRSpectrum: Infrared spectrum
    - RamanSpectrum: Raman spectrum
    - UVVisSpectrum: UV-Visible spectrum
    - NMROutput: NMR shieldings and couplings
    - EPROutput: EPR parameters
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel


# =============================================================================
# IR SPECTRUM
# =============================================================================

class IRPeak(Psi4BaseModel):
    """
    Single IR absorption peak.
    
    Attributes:
        frequency: Frequency in cm^-1.
        intensity: Intensity in km/mol.
        symmetry: Symmetry label.
        mode_number: Associated vibrational mode.
        assignment: Mode assignment/description.
    """
    
    frequency: float = Field(
        ...,
        description="Frequency in cm^-1",
    )
    intensity: float = Field(
        ...,
        ge=0,
        description="Intensity in km/mol",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="Symmetry label",
    )
    mode_number: Optional[int] = Field(
        default=None,
        ge=1,
        description="Vibrational mode number",
    )
    assignment: Optional[str] = Field(
        default=None,
        description="Mode assignment",
    )
    
    @property
    def wavelength_um(self) -> Optional[float]:
        """Wavelength in micrometers."""
        if abs(self.frequency) < 1e-6:
            return None
        return 10000.0 / self.frequency


class IRSpectrum(Psi4BaseModel):
    """
    Complete IR spectrum output.
    
    Attributes:
        peaks: List of IR peaks.
        n_peaks: Number of peaks.
        frequency_range: [min, max] frequency range.
        strongest_peak: Frequency of most intense peak.
        method: Calculation method.
        scale_factor: Frequency scale factor applied.
        broadening: Line broadening (FWHM) in cm^-1.
        simulated_x: Simulated spectrum x values (frequencies).
        simulated_y: Simulated spectrum y values (intensities).
    """
    
    peaks: list[IRPeak] = Field(
        ...,
        description="IR peaks",
    )
    n_peaks: Optional[int] = Field(
        default=None,
        description="Number of peaks",
    )
    frequency_range: Optional[list[float]] = Field(
        default=None,
        description="Frequency range [min, max]",
    )
    strongest_peak: Optional[float] = Field(
        default=None,
        description="Strongest peak frequency",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        description="Scale factor",
    )
    broadening: float = Field(
        default=10.0,
        gt=0,
        description="Broadening FWHM in cm^-1",
    )
    simulated_x: Optional[list[float]] = Field(
        default=None,
        description="Simulated x values",
    )
    simulated_y: Optional[list[float]] = Field(
        default=None,
        description="Simulated y values",
    )
    
    @model_validator(mode="after")
    def compute_derived(self) -> "IRSpectrum":
        """Compute derived quantities."""
        if self.n_peaks is None:
            object.__setattr__(self, 'n_peaks', len(self.peaks))
        
        if self.peaks and self.frequency_range is None:
            freqs = [p.frequency for p in self.peaks]
            object.__setattr__(self, 'frequency_range', [min(freqs), max(freqs)])
        
        if self.peaks and self.strongest_peak is None:
            max_peak = max(self.peaks, key=lambda p: p.intensity)
            object.__setattr__(self, 'strongest_peak', max_peak.frequency)
        
        return self
    
    def get_peaks_in_range(self, low: float, high: float) -> list[IRPeak]:
        """Get peaks within a frequency range."""
        return [p for p in self.peaks if low <= p.frequency <= high]
    
    def get_peaks_above_intensity(self, threshold: float) -> list[IRPeak]:
        """Get peaks above an intensity threshold."""
        return [p for p in self.peaks if p.intensity >= threshold]


# =============================================================================
# RAMAN SPECTRUM
# =============================================================================

class RamanPeak(Psi4BaseModel):
    """
    Single Raman peak.
    
    Attributes:
        frequency: Raman shift in cm^-1.
        activity: Raman activity in A^4/amu.
        depolarization_ratio: Depolarization ratio.
        symmetry: Symmetry label.
        mode_number: Associated vibrational mode.
        assignment: Mode assignment.
    """
    
    frequency: float = Field(
        ...,
        description="Raman shift in cm^-1",
    )
    activity: float = Field(
        ...,
        ge=0,
        description="Raman activity in A^4/amu",
    )
    depolarization_ratio: Optional[float] = Field(
        default=None,
        ge=0,
        le=0.75,
        description="Depolarization ratio",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="Symmetry",
    )
    mode_number: Optional[int] = Field(
        default=None,
        ge=1,
        description="Mode number",
    )
    assignment: Optional[str] = Field(
        default=None,
        description="Assignment",
    )
    
    @property
    def is_polarized(self) -> bool:
        """Check if peak is polarized (low depol ratio)."""
        if self.depolarization_ratio is None:
            return False
        return self.depolarization_ratio < 0.1


class RamanSpectrum(Psi4BaseModel):
    """
    Complete Raman spectrum output.
    
    Attributes:
        peaks: List of Raman peaks.
        excitation_wavelength: Excitation wavelength in nm.
        temperature: Temperature in K.
        method: Calculation method.
        scale_factor: Frequency scale factor.
    """
    
    peaks: list[RamanPeak] = Field(
        ...,
        description="Raman peaks",
    )
    excitation_wavelength: float = Field(
        default=514.5,
        gt=0,
        description="Excitation wavelength in nm",
    )
    temperature: float = Field(
        default=298.15,
        gt=0,
        description="Temperature in K",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        description="Scale factor",
    )
    
    def get_polarized_peaks(self) -> list[RamanPeak]:
        """Get polarized peaks."""
        return [p for p in self.peaks if p.is_polarized]


# =============================================================================
# UV-VIS SPECTRUM
# =============================================================================

class ElectronicTransition(Psi4BaseModel):
    """
    Single electronic transition.
    
    Attributes:
        state_number: Excited state number.
        energy_ev: Transition energy in eV.
        energy_nm: Wavelength in nm.
        energy_cm_inv: Energy in cm^-1.
        oscillator_strength: Oscillator strength.
        rotatory_strength: Rotatory strength (for CD).
        symmetry: State symmetry.
        multiplicity: Spin multiplicity.
        transition_dipole: Transition dipole moment [x, y, z].
        dominant_contributions: Major orbital contributions.
        character: State character description.
    """
    
    state_number: int = Field(
        ...,
        ge=1,
        description="Excited state number",
    )
    energy_ev: float = Field(
        ...,
        description="Energy in eV",
    )
    energy_nm: Optional[float] = Field(
        default=None,
        gt=0,
        description="Wavelength in nm",
    )
    energy_cm_inv: Optional[float] = Field(
        default=None,
        description="Energy in cm^-1",
    )
    oscillator_strength: float = Field(
        ...,
        ge=0,
        description="Oscillator strength",
    )
    rotatory_strength: Optional[float] = Field(
        default=None,
        description="Rotatory strength",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="Symmetry",
    )
    multiplicity: int = Field(
        default=1,
        ge=1,
        description="Multiplicity",
    )
    transition_dipole: Optional[list[float]] = Field(
        default=None,
        description="Transition dipole [x, y, z]",
    )
    dominant_contributions: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Orbital contributions",
    )
    character: Optional[str] = Field(
        default=None,
        description="State character",
    )
    
    @model_validator(mode="after")
    def compute_conversions(self) -> "ElectronicTransition":
        """Compute energy unit conversions."""
        if self.energy_nm is None:
            # E(eV) = 1239.84 / lambda(nm)
            nm = 1239.84 / self.energy_ev if self.energy_ev > 0 else 0
            object.__setattr__(self, 'energy_nm', nm)
        
        if self.energy_cm_inv is None:
            # E(cm^-1) = E(eV) * 8065.54
            cm_inv = self.energy_ev * 8065.54
            object.__setattr__(self, 'energy_cm_inv', cm_inv)
        
        return self
    
    @property
    def is_bright(self) -> bool:
        """Check if transition is optically bright."""
        return self.oscillator_strength > 0.01
    
    @property
    def is_dark(self) -> bool:
        """Check if transition is optically dark."""
        return self.oscillator_strength < 0.001


class UVVisSpectrum(Psi4BaseModel):
    """
    Complete UV-Vis spectrum output.
    
    Attributes:
        transitions: List of electronic transitions.
        n_states: Number of excited states.
        method: Calculation method (TDDFT, CIS, etc.).
        functional: DFT functional (if applicable).
        basis: Basis set.
        wavelength_range: [min, max] wavelength range in nm.
        strongest_transition: Most intense transition.
        simulated_x: Simulated spectrum wavelengths.
        simulated_y: Simulated spectrum intensities.
        broadening: Gaussian broadening in eV.
    """
    
    transitions: list[ElectronicTransition] = Field(
        ...,
        description="Transitions",
    )
    n_states: Optional[int] = Field(
        default=None,
        description="Number of states",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    functional: Optional[str] = Field(
        default=None,
        description="Functional",
    )
    basis: Optional[str] = Field(
        default=None,
        description="Basis set",
    )
    wavelength_range: Optional[list[float]] = Field(
        default=None,
        description="Wavelength range [min, max]",
    )
    strongest_transition: Optional[int] = Field(
        default=None,
        description="Strongest transition state number",
    )
    simulated_x: Optional[list[float]] = Field(
        default=None,
        description="Simulated wavelengths",
    )
    simulated_y: Optional[list[float]] = Field(
        default=None,
        description="Simulated intensities",
    )
    broadening: float = Field(
        default=0.3,
        gt=0,
        description="Broadening in eV",
    )
    
    @model_validator(mode="after")
    def compute_derived(self) -> "UVVisSpectrum":
        """Compute derived quantities."""
        if self.n_states is None:
            object.__setattr__(self, 'n_states', len(self.transitions))
        
        if self.transitions and self.strongest_transition is None:
            max_trans = max(self.transitions, key=lambda t: t.oscillator_strength)
            object.__setattr__(self, 'strongest_transition', max_trans.state_number)
        
        return self
    
    def get_bright_transitions(self, threshold: float = 0.01) -> list[ElectronicTransition]:
        """Get transitions with oscillator strength above threshold."""
        return [t for t in self.transitions if t.oscillator_strength >= threshold]
    
    def get_transitions_in_range(self, low_nm: float, high_nm: float) -> list[ElectronicTransition]:
        """Get transitions in a wavelength range."""
        return [
            t for t in self.transitions 
            if t.energy_nm is not None and low_nm <= t.energy_nm <= high_nm
        ]


# =============================================================================
# CIRCULAR DICHROISM
# =============================================================================

class CDSpectrum(Psi4BaseModel):
    """
    Circular dichroism spectrum output.
    
    Attributes:
        transitions: Electronic transitions with rotatory strengths.
        method: Calculation method.
        gauge: Gauge used (length, velocity).
        simulated_x: Simulated wavelengths.
        simulated_y: Simulated CD intensities.
    """
    
    transitions: list[ElectronicTransition] = Field(
        ...,
        description="Transitions",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    gauge: str = Field(
        default="length",
        description="Gauge",
    )
    simulated_x: Optional[list[float]] = Field(
        default=None,
        description="Simulated wavelengths",
    )
    simulated_y: Optional[list[float]] = Field(
        default=None,
        description="Simulated CD",
    )


# =============================================================================
# NMR
# =============================================================================

class NMRShielding(Psi4BaseModel):
    """
    NMR chemical shielding for a single nucleus.
    
    Attributes:
        atom_index: Atom index (0-indexed).
        symbol: Element symbol.
        isotropic: Isotropic shielding in ppm.
        anisotropy: Shielding anisotropy in ppm.
        tensor: Full shielding tensor [[xx,xy,xz],[yx,yy,yz],[zx,zy,zz]].
        principal_values: Principal values [sigma_11, sigma_22, sigma_33].
        chemical_shift: Chemical shift (relative to reference).
        reference: Reference compound.
    """
    
    atom_index: int = Field(
        ...,
        ge=0,
        description="Atom index",
    )
    symbol: str = Field(
        ...,
        description="Element symbol",
    )
    isotropic: float = Field(
        ...,
        description="Isotropic shielding in ppm",
    )
    anisotropy: Optional[float] = Field(
        default=None,
        description="Anisotropy in ppm",
    )
    tensor: Optional[list[list[float]]] = Field(
        default=None,
        description="Shielding tensor",
    )
    principal_values: Optional[list[float]] = Field(
        default=None,
        description="Principal values",
    )
    chemical_shift: Optional[float] = Field(
        default=None,
        description="Chemical shift in ppm",
    )
    reference: Optional[str] = Field(
        default=None,
        description="Reference compound",
    )


class NMRCoupling(Psi4BaseModel):
    """
    NMR spin-spin coupling constant.
    
    Attributes:
        atom1_index: First atom index.
        atom2_index: Second atom index.
        atom1_symbol: First atom symbol.
        atom2_symbol: Second atom symbol.
        total_coupling: Total J coupling in Hz.
        fermi_contact: Fermi contact contribution.
        spin_dipolar: Spin-dipolar contribution.
        paramagnetic_so: Paramagnetic SO contribution.
        diamagnetic_so: Diamagnetic SO contribution.
        n_bonds: Number of bonds between atoms.
    """
    
    atom1_index: int = Field(..., ge=0, description="Atom 1 index")
    atom2_index: int = Field(..., ge=0, description="Atom 2 index")
    atom1_symbol: str = Field(..., description="Atom 1 symbol")
    atom2_symbol: str = Field(..., description="Atom 2 symbol")
    total_coupling: float = Field(..., description="Total J in Hz")
    fermi_contact: Optional[float] = Field(default=None, description="FC contribution")
    spin_dipolar: Optional[float] = Field(default=None, description="SD contribution")
    paramagnetic_so: Optional[float] = Field(default=None, description="PSO contribution")
    diamagnetic_so: Optional[float] = Field(default=None, description="DSO contribution")
    n_bonds: Optional[int] = Field(default=None, ge=1, description="Number of bonds")


class NMROutput(Psi4BaseModel):
    """
    Complete NMR calculation output.
    
    Attributes:
        shieldings: Chemical shieldings.
        couplings: Spin-spin couplings.
        method: Calculation method.
        basis: Basis set.
        gauge: Gauge origin (GIAO, IGLO, etc.).
    """
    
    shieldings: list[NMRShielding] = Field(
        default_factory=list,
        description="Shieldings",
    )
    couplings: list[NMRCoupling] = Field(
        default_factory=list,
        description="Couplings",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    basis: Optional[str] = Field(
        default=None,
        description="Basis set",
    )
    gauge: str = Field(
        default="GIAO",
        description="Gauge origin",
    )
    
    def get_shieldings_by_element(self, element: str) -> list[NMRShielding]:
        """Get shieldings for a specific element."""
        return [s for s in self.shieldings if s.symbol == element]
    
    def get_coupling(self, atom1: int, atom2: int) -> Optional[NMRCoupling]:
        """Get coupling between two atoms."""
        for c in self.couplings:
            if (c.atom1_index == atom1 and c.atom2_index == atom2) or \
               (c.atom1_index == atom2 and c.atom2_index == atom1):
                return c
        return None


# =============================================================================
# EPR
# =============================================================================

class EPRGTensor(Psi4BaseModel):
    """
    EPR g-tensor.
    
    Attributes:
        gxx: XX component.
        gyy: YY component.
        gzz: ZZ component.
        gxy: XY component.
        gxz: XZ component.
        gyz: YZ component.
        g_iso: Isotropic g value.
        principal_values: Principal values.
        delta_g: Deviation from free electron g.
    """
    
    gxx: float = Field(..., description="g_xx")
    gyy: float = Field(..., description="g_yy")
    gzz: float = Field(..., description="g_zz")
    gxy: float = Field(default=0.0, description="g_xy")
    gxz: float = Field(default=0.0, description="g_xz")
    gyz: float = Field(default=0.0, description="g_yz")
    g_iso: Optional[float] = Field(default=None, description="Isotropic g")
    principal_values: Optional[list[float]] = Field(default=None, description="Principal values")
    delta_g: Optional[list[float]] = Field(default=None, description="Delta g from g_e")
    
    @model_validator(mode="after")
    def compute_isotropic(self) -> "EPRGTensor":
        """Compute isotropic g value."""
        if self.g_iso is None:
            g_iso = (self.gxx + self.gyy + self.gzz) / 3.0
            object.__setattr__(self, 'g_iso', g_iso)
        return self


class HyperfineCoupling(Psi4BaseModel):
    """
    Hyperfine coupling for a single nucleus.
    
    Attributes:
        atom_index: Atom index.
        symbol: Element symbol.
        isotope: Isotope mass number.
        a_iso: Isotropic hyperfine coupling in MHz.
        a_tensor: Full A tensor in MHz.
        a_dip: Dipolar part of A tensor.
    """
    
    atom_index: int = Field(..., ge=0, description="Atom index")
    symbol: str = Field(..., description="Element symbol")
    isotope: Optional[int] = Field(default=None, description="Isotope")
    a_iso: float = Field(..., description="Isotropic A in MHz")
    a_tensor: Optional[list[list[float]]] = Field(default=None, description="A tensor")
    a_dip: Optional[list[float]] = Field(default=None, description="Dipolar A")


class EPROutput(Psi4BaseModel):
    """
    Complete EPR calculation output.
    
    Attributes:
        g_tensor: g-tensor.
        hyperfine_couplings: Hyperfine couplings.
        d_tensor: Zero-field splitting D tensor.
        spin: Total spin quantum number.
        multiplicity: Spin multiplicity.
        method: Calculation method.
    """
    
    g_tensor: Optional[EPRGTensor] = Field(
        default=None,
        description="g-tensor",
    )
    hyperfine_couplings: list[HyperfineCoupling] = Field(
        default_factory=list,
        description="Hyperfine couplings",
    )
    d_tensor: Optional[dict[str, float]] = Field(
        default=None,
        description="D tensor",
    )
    spin: float = Field(
        default=0.5,
        description="Total spin S",
    )
    multiplicity: int = Field(
        default=2,
        ge=1,
        description="Multiplicity",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
