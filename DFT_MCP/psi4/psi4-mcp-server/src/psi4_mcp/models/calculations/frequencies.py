"""
Frequency Calculation Input Models.

This module provides Pydantic models for specifying vibrational frequency
calculations, thermodynamic analyses, and related inputs.

Key Classes:
    - FrequencyInput: Basic frequency calculation
    - ThermochemistryInput: Thermodynamic property calculation
    - AnharmonicInput: Anharmonic frequency calculation
"""

from typing import Any, Optional, Literal
from pydantic import Field, field_validator, model_validator

from psi4_mcp.models.base import Psi4BaseModel
from psi4_mcp.models.calculations.energy import MoleculeInput, EnergyInput
from psi4_mcp.models.options import FrequencyOptions, SCFOptions


# =============================================================================
# FREQUENCY INPUT
# =============================================================================

class FrequencyInput(EnergyInput):
    """
    Vibrational frequency calculation input.
    
    Attributes:
        freq_options: Frequency calculation options.
        dertype: Derivative type (energy, gradient, hessian).
        analytical: Use analytical derivatives if available.
        project_rot: Project out rotations.
        project_trans: Project out translations.
        scale_factor: Frequency scaling factor.
        compute_ir: Compute IR intensities.
        compute_raman: Compute Raman activities.
        compute_thermo: Compute thermodynamic properties.
        temperature: Temperature for thermodynamics.
        pressure: Pressure for thermodynamics.
    """
    
    freq_options: FrequencyOptions = Field(
        default_factory=FrequencyOptions,
        description="Frequency options",
    )
    dertype: Literal["energy", "gradient", "hessian"] = Field(
        default="hessian",
        description="Derivative type",
    )
    analytical: bool = Field(
        default=True,
        description="Use analytical derivatives",
    )
    project_rot: bool = Field(
        default=True,
        description="Project rotations",
    )
    project_trans: bool = Field(
        default=True,
        description="Project translations",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        le=2.0,
        description="Frequency scaling factor",
    )
    compute_ir: bool = Field(
        default=True,
        description="Compute IR intensities",
    )
    compute_raman: bool = Field(
        default=False,
        description="Compute Raman activities",
    )
    compute_thermo: bool = Field(
        default=True,
        description="Compute thermodynamics",
    )
    temperature: float = Field(
        default=298.15,
        gt=0,
        le=10000,
        description="Temperature in K",
    )
    pressure: float = Field(
        default=1.0,
        gt=0,
        le=1000,
        description="Pressure in atm",
    )
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = self.freq_options.to_psi4_options()
        opts.update(self.options)
        
        opts["t"] = self.temperature
        opts["p"] = self.pressure
        
        if self.compute_raman:
            opts["activity"] = True
        
        return opts


# =============================================================================
# THERMOCHEMISTRY INPUT
# =============================================================================

class ThermochemistryInput(Psi4BaseModel):
    """
    Thermochemistry calculation input.
    
    This is typically run after a frequency calculation to compute
    thermodynamic properties at different conditions.
    
    Attributes:
        molecule: Molecule specification.
        frequencies: Pre-computed frequencies in cm^-1.
        electronic_energy: Electronic energy in Hartree.
        temperature: Temperature in K.
        pressure: Pressure in atm.
        scale_factor: Frequency scaling factor.
        symmetry_number: Rotational symmetry number.
        multiplicity: Electronic spin multiplicity.
        is_linear: Is the molecule linear.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    frequencies: list[float] = Field(
        ...,
        min_length=1,
        description="Frequencies in cm^-1",
    )
    electronic_energy: float = Field(
        ...,
        description="Electronic energy in Hartree",
    )
    temperature: float = Field(
        default=298.15,
        gt=0,
        le=10000,
        description="Temperature in K",
    )
    pressure: float = Field(
        default=1.0,
        gt=0,
        le=1000,
        description="Pressure in atm",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        le=2.0,
        description="Frequency scale factor",
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
    is_linear: bool = Field(
        default=False,
        description="Is molecule linear",
    )
    
    @property
    def scaled_frequencies(self) -> list[float]:
        """Get frequencies with scaling applied."""
        return [f * self.scale_factor for f in self.frequencies]
    
    @property
    def real_frequencies(self) -> list[float]:
        """Get only real (positive) frequencies."""
        return [f for f in self.frequencies if f > 0]
    
    @property
    def n_imaginary(self) -> int:
        """Number of imaginary frequencies."""
        return sum(1 for f in self.frequencies if f < 0)


class MultiTemperatureInput(Psi4BaseModel):
    """
    Thermochemistry at multiple temperatures.
    
    Attributes:
        molecule: Molecule specification.
        frequencies: Frequencies in cm^-1.
        electronic_energy: Electronic energy in Hartree.
        temperatures: List of temperatures in K.
        pressure: Pressure in atm.
        scale_factor: Frequency scaling factor.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule",
    )
    frequencies: list[float] = Field(
        ...,
        min_length=1,
        description="Frequencies in cm^-1",
    )
    electronic_energy: float = Field(
        ...,
        description="Electronic energy in Hartree",
    )
    temperatures: list[float] = Field(
        default_factory=lambda: [298.15],
        description="Temperatures in K",
    )
    pressure: float = Field(
        default=1.0,
        gt=0,
        description="Pressure in atm",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        description="Scale factor",
    )
    
    @field_validator("temperatures")
    @classmethod
    def validate_temperatures(cls, v: list[float]) -> list[float]:
        """Validate temperatures."""
        for t in v:
            if t <= 0:
                raise ValueError(f"Temperature must be positive: {t}")
            if t > 10000:
                raise ValueError(f"Temperature too high: {t}")
        return sorted(v)


# =============================================================================
# ANHARMONIC INPUT
# =============================================================================

class AnharmonicInput(Psi4BaseModel):
    """
    Anharmonic frequency calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        vpt2: Use VPT2 perturbation theory.
        vscf: Use VSCF method.
        vci: Use VCI method.
        vci_excitations: Maximum VCI excitation level.
        fermi_resonance: Include Fermi resonance treatment.
        fermi_threshold: Fermi resonance threshold in cm^-1.
        modes: Specific modes to treat anharmonically.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    method: str = Field(
        default="hf",
        description="Calculation method",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    vpt2: bool = Field(
        default=True,
        description="Use VPT2",
    )
    vscf: bool = Field(
        default=False,
        description="Use VSCF",
    )
    vci: bool = Field(
        default=False,
        description="Use VCI",
    )
    vci_excitations: int = Field(
        default=4,
        ge=2,
        le=10,
        description="VCI excitation level",
    )
    fermi_resonance: bool = Field(
        default=True,
        description="Include Fermi resonance",
    )
    fermi_threshold: float = Field(
        default=200.0,
        gt=0,
        description="Fermi threshold in cm^-1",
    )
    modes: Optional[list[int]] = Field(
        default=None,
        description="Specific modes (1-indexed)",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Number of threads",
    )
    
    @model_validator(mode="after")
    def validate_method_combination(self) -> "AnharmonicInput":
        """Validate method combinations."""
        if self.vscf and self.vpt2:
            # VSCF and VPT2 can be combined (VSCF-PT2)
            pass
        if self.vci and not self.vscf:
            raise ValueError("VCI requires VSCF")
        return self


# =============================================================================
# HESSIAN INPUT
# =============================================================================

class HessianInput(EnergyInput):
    """
    Hessian (force constant) matrix calculation input.
    
    Attributes:
        dertype: Derivative type.
        analytical: Use analytical Hessian if available.
        numerical_step: Step size for numerical Hessian.
        five_point: Use 5-point numerical differentiation.
        save_hessian: Save Hessian to file.
        hessian_file: Hessian filename.
    """
    
    dertype: Literal["energy", "gradient"] = Field(
        default="gradient",
        description="Derivative type for numerical Hessian",
    )
    analytical: bool = Field(
        default=True,
        description="Use analytical Hessian",
    )
    numerical_step: float = Field(
        default=0.005,
        gt=0,
        le=0.1,
        description="Step size for numerical Hessian (Bohr)",
    )
    five_point: bool = Field(
        default=False,
        description="Use 5-point formula",
    )
    save_hessian: bool = Field(
        default=False,
        description="Save Hessian to file",
    )
    hessian_file: Optional[str] = Field(
        default=None,
        description="Hessian filename",
    )
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = {}
        opts.update(self.options)
        
        if not self.analytical:
            opts["findif_points"] = 5 if self.five_point else 3
            opts["findif_displacement"] = self.numerical_step
        
        return opts


# =============================================================================
# NORMAL MODE INPUT
# =============================================================================

class NormalModeInput(Psi4BaseModel):
    """
    Normal mode analysis input.
    
    Attributes:
        hessian: Hessian matrix (flat list, row-major).
        masses: Atomic masses in amu.
        coordinates: Atomic coordinates (flat list).
        n_atoms: Number of atoms.
        project_rot_trans: Project out rotations and translations.
    """
    
    hessian: list[float] = Field(
        ...,
        description="Hessian matrix (flat, row-major)",
    )
    masses: list[float] = Field(
        ...,
        min_length=1,
        description="Atomic masses in amu",
    )
    coordinates: list[float] = Field(
        ...,
        description="Coordinates (flat list)",
    )
    n_atoms: int = Field(
        ...,
        ge=1,
        description="Number of atoms",
    )
    project_rot_trans: bool = Field(
        default=True,
        description="Project rot/trans",
    )
    
    @model_validator(mode="after")
    def validate_dimensions(self) -> "NormalModeInput":
        """Validate array dimensions."""
        n = self.n_atoms
        expected_coords = 3 * n
        expected_hess = (3 * n) ** 2
        
        if len(self.masses) != n:
            raise ValueError(f"Expected {n} masses, got {len(self.masses)}")
        if len(self.coordinates) != expected_coords:
            raise ValueError(f"Expected {expected_coords} coordinates")
        if len(self.hessian) != expected_hess:
            raise ValueError(f"Expected {expected_hess} Hessian elements")
        
        return self


# =============================================================================
# ISOTOPE SUBSTITUTION
# =============================================================================

class IsotopeFrequencyInput(Psi4BaseModel):
    """
    Frequency calculation with isotope substitution.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        isotope_substitutions: Dictionary of atom index -> mass.
        reference_frequencies: Reference frequencies from parent isotopologue.
        reference_hessian: Reference Hessian (optional).
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule",
    )
    method: str = Field(
        default="hf",
        description="Method",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    isotope_substitutions: dict[int, float] = Field(
        ...,
        description="Atom index -> mass (amu)",
    )
    reference_frequencies: Optional[list[float]] = Field(
        default=None,
        description="Reference frequencies",
    )
    reference_hessian: Optional[list[float]] = Field(
        default=None,
        description="Reference Hessian",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    def get_isotope_labels(self) -> dict[int, str]:
        """Get isotope labels based on masses."""
        # Common isotope masses
        isotope_masses = {
            1.008: "H", 2.014: "D", 3.016: "T",
            12.000: "C", 13.003: "13C",
            14.003: "N", 15.000: "15N",
            15.995: "O", 17.999: "18O",
        }
        
        labels = {}
        for atom_idx, mass in self.isotope_substitutions.items():
            # Find closest match
            closest = min(isotope_masses.keys(), key=lambda m: abs(m - mass))
            if abs(closest - mass) < 0.01:
                labels[atom_idx] = isotope_masses[closest]
            else:
                labels[atom_idx] = f"m={mass:.3f}"
        
        return labels
