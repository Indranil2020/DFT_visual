"""
Response Property Calculation Models.

Pydantic models for linear and nonlinear response properties:
    - Polarizability (static and dynamic)
    - Hyperpolarizability
    - Optical rotation
    - NMR shielding tensors
    - EPR g-tensors
"""

from typing import Any, Optional, Literal
from pydantic import Field

from psi4_mcp.models.base import BaseInput, BaseOutput
from psi4_mcp.models.molecules import MoleculeInput


# =============================================================================
# RESPONSE INPUT MODELS
# =============================================================================

class ResponseInput(BaseInput):
    """
    Base input for response property calculations.
    
    Attributes:
        molecule: Molecular specification.
        method: Calculation method.
        basis: Basis set name.
        response_type: Type of response calculation.
        frequencies: Frequencies for dynamic properties.
    """
    
    molecule: MoleculeInput = Field(..., description="Molecular specification")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    response_type: Literal[
        "polarizability",
        "hyperpolarizability",
        "optical_rotation",
        "nmr_shielding",
        "epr_gtensor"
    ] = Field(description="Type of response property")
    frequencies: Optional[list[float]] = Field(
        default=None,
        description="Frequencies for dynamic properties (a.u.)"
    )
    gauge: Literal["length", "velocity"] = Field(
        default="length",
        description="Gauge for response properties"
    )
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        options = {
            "basis": self.basis,
        }
        if self.frequencies:
            options["omega"] = self.frequencies
        return options


class PolarizabilityInput(ResponseInput):
    """
    Input for polarizability calculations.
    
    Computes static or dynamic (frequency-dependent) polarizability.
    """
    response_type: Literal["polarizability"] = "polarizability"
    static: bool = Field(default=True, description="Compute static polarizability")
    dynamic_frequencies: Optional[list[float]] = Field(
        default=None,
        description="Frequencies for dynamic polarizability (nm)"
    )


class HyperpolarizabilityInput(ResponseInput):
    """
    Input for hyperpolarizability calculations.
    
    First hyperpolarizability (β) for nonlinear optics.
    """
    response_type: Literal["hyperpolarizability"] = "hyperpolarizability"
    process: Literal["shg", "or", "eope"] = Field(
        default="shg",
        description="Nonlinear process: shg (SHG), or (optical rectification), eope (electro-optic)"
    )


class OpticalRotationInput(ResponseInput):
    """
    Input for optical rotation calculations.
    
    Computes specific rotation [α] for chiral molecules.
    """
    response_type: Literal["optical_rotation"] = "optical_rotation"
    wavelengths: list[float] = Field(
        default=[589.3],  # Sodium D-line
        description="Wavelengths for optical rotation (nm)"
    )


class NMRShieldingInput(ResponseInput):
    """
    Input for NMR shielding tensor calculations.
    
    Attributes:
        nuclei: Nuclei to compute shielding for.
        giao: Use gauge-including atomic orbitals.
    """
    response_type: Literal["nmr_shielding"] = "nmr_shielding"
    nuclei: Optional[list[str]] = Field(
        default=None,
        description="Nuclei to compute (None = all)"
    )
    giao: bool = Field(default=True, description="Use GIAO method")
    reference_compound: Optional[str] = Field(
        default=None,
        description="Reference compound for chemical shifts"
    )


class EPRGTensorInput(ResponseInput):
    """
    Input for EPR g-tensor calculations.
    
    For paramagnetic (open-shell) systems.
    """
    response_type: Literal["epr_gtensor"] = "epr_gtensor"
    spin_orbit: bool = Field(default=True, description="Include spin-orbit coupling")


# =============================================================================
# RESPONSE OUTPUT MODELS
# =============================================================================

class PolarizabilityTensor(BaseOutput):
    """Polarizability tensor."""
    xx: float = Field(description="αxx component")
    yy: float = Field(description="αyy component")
    zz: float = Field(description="αzz component")
    xy: float = Field(default=0.0, description="αxy component")
    xz: float = Field(default=0.0, description="αxz component")
    yz: float = Field(default=0.0, description="αyz component")
    isotropic: float = Field(description="Isotropic polarizability")
    anisotropy: float = Field(description="Polarizability anisotropy")
    unit: str = Field(default="a.u.", description="Units")


class DynamicPolarizability(BaseOutput):
    """Frequency-dependent polarizability."""
    frequency: float = Field(description="Frequency (a.u. or nm)")
    frequency_unit: str = Field(default="a.u.")
    tensor: PolarizabilityTensor = Field(description="Polarizability tensor")


class PolarizabilityOutput(BaseOutput):
    """
    Polarizability calculation output.
    
    Attributes:
        static: Static polarizability tensor.
        dynamic: Dynamic polarizabilities at various frequencies.
    """
    static: Optional[PolarizabilityTensor] = Field(default=None)
    dynamic: list[DynamicPolarizability] = Field(default_factory=list)
    method: str = Field(description="Method used")
    basis: str = Field(description="Basis set")


class HyperpolarizabilityOutput(BaseOutput):
    """
    Hyperpolarizability calculation output.
    
    First hyperpolarizability tensor β.
    """
    beta_vec: list[float] = Field(description="β vector (x, y, z)")
    beta_magnitude: float = Field(description="β magnitude")
    beta_parallel: float = Field(description="β∥ (along dipole)")
    process: str = Field(description="Nonlinear process computed")
    frequency: Optional[float] = Field(default=None)
    method: str = Field(description="Method used")
    basis: str = Field(description="Basis set")


class OpticalRotationOutput(BaseOutput):
    """
    Optical rotation calculation output.
    
    Specific rotation [α] in deg/(dm·g/mL).
    """
    rotations: dict[float, float] = Field(
        description="Specific rotation at each wavelength"
    )
    wavelength_unit: str = Field(default="nm")
    gauge: str = Field(description="Gauge used")
    method: str = Field(description="Method used")
    basis: str = Field(description="Basis set")


class NMRShielding(BaseOutput):
    """NMR shielding for single nucleus."""
    atom_index: int = Field(description="Atom index")
    element: str = Field(description="Element symbol")
    isotropic: float = Field(description="Isotropic shielding (ppm)")
    anisotropy: float = Field(description="Shielding anisotropy")
    tensor: list[list[float]] = Field(description="3x3 shielding tensor")
    chemical_shift: Optional[float] = Field(
        default=None,
        description="Chemical shift relative to reference"
    )


class NMRShieldingOutput(BaseOutput):
    """
    NMR shielding calculation output.
    
    Attributes:
        shieldings: Shielding tensors for each nucleus.
        reference: Reference compound if chemical shifts computed.
    """
    shieldings: list[NMRShielding] = Field(default_factory=list)
    reference: Optional[str] = Field(default=None)
    giao: bool = Field(description="Whether GIAO was used")
    method: str = Field(description="Method used")
    basis: str = Field(description="Basis set")


class EPRGTensor(BaseOutput):
    """EPR g-tensor."""
    g_iso: float = Field(description="Isotropic g-value")
    g_xx: float = Field(description="gxx component")
    g_yy: float = Field(description="gyy component")
    g_zz: float = Field(description="gzz component")
    g_shift: float = Field(description="g-shift from free electron")
    principal_values: list[float] = Field(description="Principal values")
    principal_axes: list[list[float]] = Field(description="Principal axes")


class EPRGTensorOutput(BaseOutput):
    """
    EPR g-tensor calculation output.
    """
    g_tensor: EPRGTensor = Field(description="g-tensor")
    spin_orbit_contribution: Optional[float] = Field(default=None)
    method: str = Field(description="Method used")
    basis: str = Field(description="Basis set")
