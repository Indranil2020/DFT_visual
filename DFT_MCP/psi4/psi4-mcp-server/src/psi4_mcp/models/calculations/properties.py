"""
Property Calculation Input Models.

This module provides Pydantic models for specifying molecular property
calculations including multipole moments, polarizabilities, and
various response properties.

Key Classes:
    - PropertyInput: General property calculation
    - MultipoleInput: Multipole moment calculation
    - PolarizabilityInput: Polarizability calculation
    - ResponseInput: Response property calculation
    - PopulationInput: Population analysis
"""

from typing import Any, Optional, Literal
from pydantic import Field, field_validator, model_validator

from psi4_mcp.models.base import Psi4BaseModel
from psi4_mcp.models.calculations.energy import MoleculeInput, EnergyInput
from psi4_mcp.models.options import PropertyOptions


# =============================================================================
# GENERAL PROPERTY INPUT
# =============================================================================

class PropertyInput(EnergyInput):
    """
    General molecular property calculation input.
    
    Attributes:
        property_options: Property calculation options.
        properties: List of properties to compute.
        all_properties: Compute all available properties.
    """
    
    property_options: PropertyOptions = Field(
        default_factory=PropertyOptions,
        description="Property options",
    )
    properties: list[str] = Field(
        default_factory=list,
        description="Properties to compute",
    )
    all_properties: bool = Field(
        default=False,
        description="Compute all properties",
    )
    
    @field_validator("properties")
    @classmethod
    def validate_properties(cls, v: list[str]) -> list[str]:
        """Validate property names."""
        valid_props = {
            # Multipoles
            "dipole", "quadrupole", "octupole", "hexadecapole",
            # Charges
            "mulliken_charges", "lowdin_charges", "mbis_charges",
            "mbis_volume_ratios",
            # Bond analysis
            "wiberg_bond_indices", "mayer_bond_indices",
            # Orbitals
            "no_occupations",
            # Electrostatics
            "grid_esp", "grid_field",
            # Response
            "polarizability", "hyperpolarizability",
            # Other
            "spin_density", "frontier_orbitals",
        }
        normalized = []
        for prop in v:
            prop_lower = prop.lower().replace("-", "_")
            if prop_lower not in valid_props:
                # Allow unknown, Psi4 might support more
                pass
            normalized.append(prop_lower)
        return normalized
    
    def get_psi4_properties(self) -> list[str]:
        """Get property list for Psi4."""
        if self.all_properties:
            return ["dipole", "quadrupole", "mulliken_charges", 
                    "lowdin_charges", "wiberg_bond_indices",
                    "mayer_bond_indices", "no_occupations"]
        return self.properties


# =============================================================================
# MULTIPOLE INPUT
# =============================================================================

class MultipoleInput(Psi4BaseModel):
    """
    Multipole moment calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        max_order: Maximum multipole order (1=dipole, 2=quadrupole, etc.).
        origin: Multipole origin [x, y, z] or "com" or "nuclear".
        traceless: Use traceless multipoles.
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
    max_order: int = Field(
        default=2,
        ge=1,
        le=4,
        description="Maximum order (1-4)",
    )
    origin: str = Field(
        default="com",
        description="Origin (com, nuclear, or [x,y,z])",
    )
    traceless: bool = Field(
        default=True,
        description="Traceless multipoles",
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
    
    def get_properties(self) -> list[str]:
        """Get property list based on max_order."""
        props = ["dipole"]
        if self.max_order >= 2:
            props.append("quadrupole")
        if self.max_order >= 3:
            props.append("octupole")
        if self.max_order >= 4:
            props.append("hexadecapole")
        return props


# =============================================================================
# POLARIZABILITY INPUT
# =============================================================================

class PolarizabilityInput(Psi4BaseModel):
    """
    Polarizability calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        static: Compute static polarizability.
        frequencies: Frequencies for dynamic polarizability (a.u.).
        wavelengths: Wavelengths for dynamic polarizability (nm).
        gauge: Gauge choice (length, velocity).
        response_solver: Response equation solver.
        convergence: Convergence threshold.
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
        default="aug-cc-pvdz",
        description="Basis set",
    )
    static: bool = Field(
        default=True,
        description="Compute static polarizability",
    )
    frequencies: list[float] = Field(
        default_factory=list,
        description="Frequencies in a.u.",
    )
    wavelengths: list[float] = Field(
        default_factory=list,
        description="Wavelengths in nm",
    )
    gauge: Literal["length", "velocity"] = Field(
        default="length",
        description="Gauge choice",
    )
    response_solver: str = Field(
        default="iterative",
        description="Response solver",
    )
    convergence: float = Field(
        default=1e-7,
        gt=0,
        description="Convergence threshold",
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
    
    @model_validator(mode="after")
    def convert_wavelengths(self) -> "PolarizabilityInput":
        """Convert wavelengths to frequencies."""
        if self.wavelengths:
            # E(a.u.) = 45.5634 / lambda(nm)
            new_freqs = list(self.frequencies)
            for nm in self.wavelengths:
                if nm > 0:
                    freq_au = 45.5634 / nm
                    if freq_au not in new_freqs:
                        new_freqs.append(freq_au)
            object.__setattr__(self, 'frequencies', sorted(new_freqs))
        return self


class HyperpolarizabilityInput(Psi4BaseModel):
    """
    Hyperpolarizability calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        beta: Compute first hyperpolarizability (beta).
        gamma: Compute second hyperpolarizability (gamma).
        frequencies: Frequencies for dynamic calculation.
        process: NLO process (shg, or, eope, etc.).
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
        default="aug-cc-pvdz",
        description="Basis set",
    )
    beta: bool = Field(
        default=True,
        description="Compute beta",
    )
    gamma: bool = Field(
        default=False,
        description="Compute gamma",
    )
    frequencies: list[float] = Field(
        default_factory=lambda: [0.0],
        description="Frequencies in a.u.",
    )
    process: str = Field(
        default="static",
        description="NLO process",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @field_validator("process")
    @classmethod
    def validate_process(cls, v: str) -> str:
        """Validate NLO process."""
        valid = {
            "static", "shg", "or", "eope", "efishg", "thg", "dfwm"
        }
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid NLO process: {v}")
        return normalized


# =============================================================================
# RESPONSE INPUT
# =============================================================================

class ResponseInput(Psi4BaseModel):
    """
    General linear response calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        property_type: Type of response property.
        operators: Perturbation operators.
        frequencies: Frequencies for dynamic response.
        gauge: Gauge choice.
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
    property_type: str = Field(
        default="polarizability",
        description="Property type",
    )
    operators: list[str] = Field(
        default_factory=lambda: ["dipole"],
        description="Perturbation operators",
    )
    frequencies: list[float] = Field(
        default_factory=lambda: [0.0],
        description="Frequencies in a.u.",
    )
    gauge: str = Field(
        default="length",
        description="Gauge choice",
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


# =============================================================================
# POPULATION ANALYSIS INPUT
# =============================================================================

class PopulationInput(Psi4BaseModel):
    """
    Population analysis calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        analysis_types: Types of population analysis.
        nbo: Perform NBO analysis.
        nbo_options: NBO-specific options.
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
    analysis_types: list[str] = Field(
        default_factory=lambda: ["mulliken", "lowdin"],
        description="Analysis types",
    )
    nbo: bool = Field(
        default=False,
        description="Perform NBO analysis",
    )
    nbo_options: dict[str, Any] = Field(
        default_factory=dict,
        description="NBO options",
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
    
    @field_validator("analysis_types")
    @classmethod
    def validate_analysis_types(cls, v: list[str]) -> list[str]:
        """Validate analysis types."""
        valid = {
            "mulliken", "lowdin", "npa", "hirshfeld", "mbis",
            "esp", "resp", "chelpg", "cm5",
        }
        normalized = []
        for t in v:
            t_lower = t.lower().strip()
            if t_lower not in valid:
                raise ValueError(f"Invalid analysis type: {t}")
            normalized.append(t_lower)
        return normalized


class NBOInput(Psi4BaseModel):
    """
    Natural Bond Orbital analysis input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        nbo_analysis: NBO analysis options.
        nrt: Perform Natural Resonance Theory.
        nlmo: Compute Natural Localized MOs.
        steric: Compute steric analysis.
        second_order: Compute second-order interactions.
        threshold: Threshold for interaction printing.
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
    nbo_analysis: list[str] = Field(
        default_factory=lambda: ["nbo", "npa"],
        description="NBO analyses",
    )
    nrt: bool = Field(
        default=False,
        description="Natural Resonance Theory",
    )
    nlmo: bool = Field(
        default=False,
        description="Natural Localized MOs",
    )
    steric: bool = Field(
        default=False,
        description="Steric analysis",
    )
    second_order: bool = Field(
        default=True,
        description="Second-order interactions",
    )
    threshold: float = Field(
        default=0.5,
        gt=0,
        description="Print threshold (kcal/mol)",
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


# =============================================================================
# ELECTROSTATIC POTENTIAL INPUT
# =============================================================================

class ESPInput(Psi4BaseModel):
    """
    Electrostatic potential calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        grid_type: Type of grid for ESP.
        grid_spacing: Grid spacing in Angstrom.
        iso_density: Isodensity value for surface.
        fit_charges: Fit atomic charges to ESP.
        restraint: Restraint type for charge fitting.
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
    grid_type: Literal["cubic", "surface", "points"] = Field(
        default="surface",
        description="Grid type",
    )
    grid_spacing: float = Field(
        default=0.5,
        gt=0,
        le=2.0,
        description="Grid spacing in Angstrom",
    )
    iso_density: float = Field(
        default=0.001,
        gt=0,
        description="Isodensity value",
    )
    fit_charges: bool = Field(
        default=True,
        description="Fit charges to ESP",
    )
    restraint: Literal["none", "resp", "chelpg"] = Field(
        default="resp",
        description="Restraint type",
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


# =============================================================================
# ORBITAL ANALYSIS INPUT
# =============================================================================

class OrbitalAnalysisInput(Psi4BaseModel):
    """
    Orbital analysis calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        localization: Localization method.
        n_orbitals: Number of orbitals to analyze.
        orbital_range: Range of orbitals [start, end].
        compute_nao: Compute Natural Atomic Orbitals.
        compute_ibo: Compute Intrinsic Bond Orbitals.
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
    localization: Optional[str] = Field(
        default=None,
        description="Localization method",
    )
    n_orbitals: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of orbitals",
    )
    orbital_range: Optional[list[int]] = Field(
        default=None,
        description="Orbital range [start, end]",
    )
    compute_nao: bool = Field(
        default=False,
        description="Compute NAOs",
    )
    compute_ibo: bool = Field(
        default=False,
        description="Compute IBOs",
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
    
    @field_validator("localization")
    @classmethod
    def validate_localization(cls, v: Optional[str]) -> Optional[str]:
        """Validate localization method."""
        if v is None:
            return None
        valid = {"boys", "pm", "pipek-mezey", "ibo", "er", "foster-boys"}
        normalized = v.lower().strip().replace("_", "-")
        if normalized not in valid:
            raise ValueError(f"Invalid localization method: {v}")
        return normalized
