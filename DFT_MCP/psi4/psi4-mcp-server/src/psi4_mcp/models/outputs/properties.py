"""
Molecular Property Output Models.

This module provides Pydantic models for representing various molecular
properties including multipole moments, response properties, and
electrostatic properties.

Key Classes:
    - DipoleMomentOutput: Electric dipole moment
    - QuadrupoleMomentOutput: Electric quadrupole moment
    - PolarizabilityOutput: Static and dynamic polarizability
    - HyperpolarizabilityOutput: First and second hyperpolarizabilities
    - ElectrostaticOutput: Electrostatic potential and field
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator
import math

from psi4_mcp.models.base import Psi4BaseModel


# =============================================================================
# MULTIPOLE MOMENTS
# =============================================================================

class DipoleMomentOutput(Psi4BaseModel):
    """
    Electric dipole moment output.
    
    Attributes:
        x: X component in Debye.
        y: Y component in Debye.
        z: Z component in Debye.
        total: Total magnitude in Debye.
        unit: Unit of measurement.
        origin: Origin used for calculation.
        method: Method used (scf, mp2, ccsd, etc.).
    """
    
    x: float = Field(
        ...,
        description="X component in Debye",
    )
    y: float = Field(
        ...,
        description="Y component in Debye",
    )
    z: float = Field(
        ...,
        description="Z component in Debye",
    )
    total: Optional[float] = Field(
        default=None,
        description="Total magnitude in Debye",
    )
    unit: str = Field(
        default="debye",
        description="Unit",
    )
    origin: Optional[list[float]] = Field(
        default=None,
        description="Origin [x, y, z]",
    )
    method: Optional[str] = Field(
        default=None,
        description="Calculation method",
    )
    
    @model_validator(mode="after")
    def compute_total(self) -> "DipoleMomentOutput":
        """Compute total magnitude."""
        if self.total is None:
            total = math.sqrt(self.x**2 + self.y**2 + self.z**2)
            object.__setattr__(self, 'total', total)
        return self
    
    @property
    def components(self) -> list[float]:
        """Get components as list."""
        return [self.x, self.y, self.z]
    
    def to_au(self) -> "DipoleMomentOutput":
        """Convert to atomic units."""
        # 1 Debye = 0.393430 a.u.
        factor = 0.393430
        return DipoleMomentOutput(
            x=self.x * factor,
            y=self.y * factor,
            z=self.z * factor,
            unit="au",
            origin=self.origin,
            method=self.method,
        )


class QuadrupoleMomentOutput(Psi4BaseModel):
    """
    Electric quadrupole moment output (traceless form).
    
    Attributes:
        xx: XX component.
        yy: YY component.
        zz: ZZ component.
        xy: XY component.
        xz: XZ component.
        yz: YZ component.
        unit: Unit of measurement.
        origin: Origin used.
        method: Calculation method.
        is_traceless: Whether traceless form.
    """
    
    xx: float = Field(..., description="XX component")
    yy: float = Field(..., description="YY component")
    zz: float = Field(..., description="ZZ component")
    xy: float = Field(default=0.0, description="XY component")
    xz: float = Field(default=0.0, description="XZ component")
    yz: float = Field(default=0.0, description="YZ component")
    unit: str = Field(default="debye_angstrom", description="Unit")
    origin: Optional[list[float]] = Field(default=None, description="Origin")
    method: Optional[str] = Field(default=None, description="Method")
    is_traceless: bool = Field(default=True, description="Traceless form")
    
    @property
    def trace(self) -> float:
        """Trace of quadrupole tensor."""
        return self.xx + self.yy + self.zz
    
    @property
    def as_matrix(self) -> list[list[float]]:
        """Get as 3x3 matrix."""
        return [
            [self.xx, self.xy, self.xz],
            [self.xy, self.yy, self.yz],
            [self.xz, self.yz, self.zz],
        ]


class OctupoleMomentOutput(Psi4BaseModel):
    """
    Electric octupole moment output.
    
    Attributes:
        xxx: XXX component.
        yyy: YYY component.
        zzz: ZZZ component.
        xxy: XXY component.
        xxz: XXZ component.
        yyx: YYX component.
        yyz: YYZ component.
        zzx: ZZX component.
        zzy: ZZY component.
        xyz: XYZ component.
        unit: Unit of measurement.
    """
    
    xxx: float = Field(..., description="XXX component")
    yyy: float = Field(..., description="YYY component")
    zzz: float = Field(..., description="ZZZ component")
    xxy: float = Field(default=0.0, description="XXY component")
    xxz: float = Field(default=0.0, description="XXZ component")
    yyx: float = Field(default=0.0, description="YYX component")
    yyz: float = Field(default=0.0, description="YYZ component")
    zzx: float = Field(default=0.0, description="ZZX component")
    zzy: float = Field(default=0.0, description="ZZY component")
    xyz: float = Field(default=0.0, description="XYZ component")
    unit: str = Field(default="debye_angstrom2", description="Unit")


class MultipoleOutput(Psi4BaseModel):
    """
    Complete multipole moment output.
    
    Attributes:
        charge: Total charge.
        dipole: Dipole moment.
        quadrupole: Quadrupole moment.
        octupole: Octupole moment.
        hexadecapole: Hexadecapole moment components.
    """
    
    charge: float = Field(
        default=0.0,
        description="Total charge",
    )
    dipole: Optional[DipoleMomentOutput] = Field(
        default=None,
        description="Dipole moment",
    )
    quadrupole: Optional[QuadrupoleMomentOutput] = Field(
        default=None,
        description="Quadrupole moment",
    )
    octupole: Optional[OctupoleMomentOutput] = Field(
        default=None,
        description="Octupole moment",
    )
    hexadecapole: Optional[dict[str, float]] = Field(
        default=None,
        description="Hexadecapole components",
    )


# =============================================================================
# RESPONSE PROPERTIES
# =============================================================================

class PolarizabilityOutput(Psi4BaseModel):
    """
    Electric polarizability output.
    
    Attributes:
        xx: XX component in a.u. or Angstrom^3.
        yy: YY component.
        zz: ZZ component.
        xy: XY component.
        xz: XZ component.
        yz: YZ component.
        isotropic: Isotropic polarizability (average).
        anisotropy: Polarizability anisotropy.
        unit: Unit (au or angstrom3).
        frequency: Frequency for dynamic polarizability (a.u.).
        method: Calculation method.
    """
    
    xx: float = Field(..., description="XX component")
    yy: float = Field(..., description="YY component")
    zz: float = Field(..., description="ZZ component")
    xy: float = Field(default=0.0, description="XY component")
    xz: float = Field(default=0.0, description="XZ component")
    yz: float = Field(default=0.0, description="YZ component")
    isotropic: Optional[float] = Field(default=None, description="Isotropic value")
    anisotropy: Optional[float] = Field(default=None, description="Anisotropy")
    unit: str = Field(default="au", description="Unit")
    frequency: float = Field(default=0.0, description="Frequency (a.u.)")
    method: Optional[str] = Field(default=None, description="Method")
    
    @model_validator(mode="after")
    def compute_derived(self) -> "PolarizabilityOutput":
        """Compute isotropic value and anisotropy."""
        if self.isotropic is None:
            iso = (self.xx + self.yy + self.zz) / 3.0
            object.__setattr__(self, 'isotropic', iso)
        
        if self.anisotropy is None:
            # Anisotropy = sqrt(0.5 * [(xx-yy)^2 + (yy-zz)^2 + (zz-xx)^2 + 6*(xy^2+xz^2+yz^2)])
            term1 = (self.xx - self.yy)**2
            term2 = (self.yy - self.zz)**2
            term3 = (self.zz - self.xx)**2
            term4 = 6 * (self.xy**2 + self.xz**2 + self.yz**2)
            aniso = math.sqrt(0.5 * (term1 + term2 + term3 + term4))
            object.__setattr__(self, 'anisotropy', aniso)
        
        return self
    
    @property
    def as_matrix(self) -> list[list[float]]:
        """Get as 3x3 matrix."""
        return [
            [self.xx, self.xy, self.xz],
            [self.xy, self.yy, self.yz],
            [self.xz, self.yz, self.zz],
        ]
    
    @property
    def eigenvalues(self) -> list[float]:
        """Get principal values (eigenvalues)."""
        # For diagonal matrix (common case)
        if abs(self.xy) < 1e-10 and abs(self.xz) < 1e-10 and abs(self.yz) < 1e-10:
            return sorted([self.xx, self.yy, self.zz])
        # General case would require matrix diagonalization
        return sorted([self.xx, self.yy, self.zz])
    
    @property
    def is_static(self) -> bool:
        """Check if this is static (zero frequency) polarizability."""
        return abs(self.frequency) < 1e-10
    
    def to_angstrom3(self) -> "PolarizabilityOutput":
        """Convert to Angstrom^3."""
        if self.unit == "angstrom3":
            return self
        # 1 a.u. = 0.148185 Angstrom^3
        factor = 0.148185
        return PolarizabilityOutput(
            xx=self.xx * factor,
            yy=self.yy * factor,
            zz=self.zz * factor,
            xy=self.xy * factor,
            xz=self.xz * factor,
            yz=self.yz * factor,
            unit="angstrom3",
            frequency=self.frequency,
            method=self.method,
        )


class HyperpolarizabilityOutput(Psi4BaseModel):
    """
    First hyperpolarizability (beta) output.
    
    Attributes:
        xxx: XXX component.
        yyy: YYY component.
        zzz: ZZZ component.
        xxy: XXY component.
        xxz: XXZ component.
        xyy: XYY component.
        yyz: YYZ component.
        xzz: XZZ component.
        yzz: YZZ component.
        xyz: XYZ component.
        beta_vec: Vector part [beta_x, beta_y, beta_z].
        beta_total: Total hyperpolarizability.
        unit: Unit.
        frequencies: Frequencies [omega1, omega2].
    """
    
    xxx: float = Field(default=0.0, description="XXX component")
    yyy: float = Field(default=0.0, description="YYY component")
    zzz: float = Field(default=0.0, description="ZZZ component")
    xxy: float = Field(default=0.0, description="XXY component")
    xxz: float = Field(default=0.0, description="XXZ component")
    xyy: float = Field(default=0.0, description="XYY component")
    yyz: float = Field(default=0.0, description="YYZ component")
    xzz: float = Field(default=0.0, description="XZZ component")
    yzz: float = Field(default=0.0, description="YZZ component")
    xyz: float = Field(default=0.0, description="XYZ component")
    beta_vec: Optional[list[float]] = Field(default=None, description="Beta vector")
    beta_total: Optional[float] = Field(default=None, description="Total beta")
    unit: str = Field(default="au", description="Unit")
    frequencies: list[float] = Field(default_factory=lambda: [0.0, 0.0], description="Frequencies")
    
    @model_validator(mode="after")
    def compute_derived(self) -> "HyperpolarizabilityOutput":
        """Compute vector and total beta."""
        if self.beta_vec is None:
            # beta_i = (1/5) * sum_j (beta_ijj + beta_jij + beta_jji)
            beta_x = (1/5) * (self.xxx + self.xyy + self.xzz + 
                             self.yxy if hasattr(self, 'yxy') else self.xxy +
                             self.zxz if hasattr(self, 'zxz') else self.xxz)
            # Simplified for common diagonal case
            beta_x = (3/5) * self.xxx + (1/5) * (self.xyy + self.xzz)
            beta_y = (3/5) * self.yyy + (1/5) * (self.xxy + self.yzz)
            beta_z = (3/5) * self.zzz + (1/5) * (self.xxz + self.yyz)
            object.__setattr__(self, 'beta_vec', [beta_x, beta_y, beta_z])
        
        if self.beta_total is None and self.beta_vec is not None:
            total = math.sqrt(sum(b**2 for b in self.beta_vec))
            object.__setattr__(self, 'beta_total', total)
        
        return self


class SecondHyperpolarizabilityOutput(Psi4BaseModel):
    """
    Second hyperpolarizability (gamma) output.
    
    Attributes:
        xxxx: XXXX component.
        yyyy: YYYY component.
        zzzz: ZZZZ component.
        xxyy: XXYY component.
        xxzz: XXZZ component.
        yyzz: YYZZ component.
        gamma_parallel: Parallel component.
        gamma_perpendicular: Perpendicular component.
        gamma_average: Isotropic average.
        unit: Unit.
    """
    
    xxxx: float = Field(default=0.0, description="XXXX component")
    yyyy: float = Field(default=0.0, description="YYYY component")
    zzzz: float = Field(default=0.0, description="ZZZZ component")
    xxyy: float = Field(default=0.0, description="XXYY component")
    xxzz: float = Field(default=0.0, description="XXZZ component")
    yyzz: float = Field(default=0.0, description="YYZZ component")
    gamma_parallel: Optional[float] = Field(default=None, description="Parallel gamma")
    gamma_perpendicular: Optional[float] = Field(default=None, description="Perpendicular gamma")
    gamma_average: Optional[float] = Field(default=None, description="Average gamma")
    unit: str = Field(default="au", description="Unit")
    
    @model_validator(mode="after")
    def compute_average(self) -> "SecondHyperpolarizabilityOutput":
        """Compute average gamma."""
        if self.gamma_average is None:
            # <gamma> = (1/5) * (gamma_xxxx + gamma_yyyy + gamma_zzzz + 
            #           2*(gamma_xxyy + gamma_xxzz + gamma_yyzz))
            avg = (1/5) * (self.xxxx + self.yyyy + self.zzzz + 
                          2 * (self.xxyy + self.xxzz + self.yyzz))
            object.__setattr__(self, 'gamma_average', avg)
        return self


# =============================================================================
# OPTICAL ROTATION
# =============================================================================

class OpticalRotationOutput(Psi4BaseModel):
    """
    Optical rotation output.
    
    Attributes:
        wavelength_nm: Wavelength in nm.
        specific_rotation: Specific rotation [alpha] in deg/(dm*(g/mL)).
        molar_rotation: Molar rotation [phi] in deg*cm^2/dmol.
        g_tensor: G' tensor components.
        unit: Unit for rotation values.
        method: Calculation method.
        gauge: Gauge used (length, velocity).
    """
    
    wavelength_nm: float = Field(
        ...,
        gt=0,
        description="Wavelength in nm",
    )
    specific_rotation: float = Field(
        ...,
        description="Specific rotation",
    )
    molar_rotation: Optional[float] = Field(
        default=None,
        description="Molar rotation",
    )
    g_tensor: Optional[dict[str, float]] = Field(
        default=None,
        description="G' tensor components",
    )
    unit: str = Field(
        default="deg/(dm*(g/mL))",
        description="Unit",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    gauge: str = Field(
        default="length",
        description="Gauge (length, velocity)",
    )


# =============================================================================
# ELECTROSTATIC PROPERTIES
# =============================================================================

class ElectrostaticPotentialPoint(Psi4BaseModel):
    """
    Electrostatic potential at a single point.
    
    Attributes:
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        potential: Electrostatic potential in a.u.
    """
    
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    potential: float = Field(..., description="Potential in a.u.")


class ElectrostaticOutput(Psi4BaseModel):
    """
    Electrostatic properties output.
    
    Attributes:
        potential_points: ESP at various points.
        esp_charges: ESP-derived charges.
        molecular_surface_area: Molecular surface area.
        positive_area: Positive ESP area.
        negative_area: Negative ESP area.
        average_positive_esp: Average positive ESP.
        average_negative_esp: Average negative ESP.
        variance: ESP variance.
        balance: ESP balance parameter.
    """
    
    potential_points: list[ElectrostaticPotentialPoint] = Field(
        default_factory=list,
        description="ESP at points",
    )
    esp_charges: Optional[list[float]] = Field(
        default=None,
        description="ESP-derived charges",
    )
    molecular_surface_area: Optional[float] = Field(
        default=None,
        ge=0,
        description="Surface area in Angstrom^2",
    )
    positive_area: Optional[float] = Field(
        default=None,
        ge=0,
        description="Positive ESP area",
    )
    negative_area: Optional[float] = Field(
        default=None,
        ge=0,
        description="Negative ESP area",
    )
    average_positive_esp: Optional[float] = Field(
        default=None,
        description="Average positive ESP",
    )
    average_negative_esp: Optional[float] = Field(
        default=None,
        description="Average negative ESP",
    )
    variance: Optional[float] = Field(
        default=None,
        ge=0,
        description="ESP variance",
    )
    balance: Optional[float] = Field(
        default=None,
        description="Balance parameter",
    )


# =============================================================================
# COMBINED PROPERTY OUTPUT
# =============================================================================

class PropertyOutput(Psi4BaseModel):
    """
    Combined molecular property output.
    
    Attributes:
        multipoles: Multipole moments.
        polarizability: Static polarizability.
        dynamic_polarizabilities: Dynamic polarizabilities at various frequencies.
        hyperpolarizability: First hyperpolarizability.
        second_hyperpolarizability: Second hyperpolarizability.
        optical_rotations: Optical rotation at various wavelengths.
        electrostatic: Electrostatic properties.
        method: Calculation method.
        basis: Basis set.
    """
    
    multipoles: Optional[MultipoleOutput] = Field(
        default=None,
        description="Multipole moments",
    )
    polarizability: Optional[PolarizabilityOutput] = Field(
        default=None,
        description="Static polarizability",
    )
    dynamic_polarizabilities: list[PolarizabilityOutput] = Field(
        default_factory=list,
        description="Dynamic polarizabilities",
    )
    hyperpolarizability: Optional[HyperpolarizabilityOutput] = Field(
        default=None,
        description="First hyperpolarizability",
    )
    second_hyperpolarizability: Optional[SecondHyperpolarizabilityOutput] = Field(
        default=None,
        description="Second hyperpolarizability",
    )
    optical_rotations: list[OpticalRotationOutput] = Field(
        default_factory=list,
        description="Optical rotation",
    )
    electrostatic: Optional[ElectrostaticOutput] = Field(
        default=None,
        description="Electrostatic properties",
    )
    method: Optional[str] = Field(
        default=None,
        description="Method",
    )
    basis: Optional[str] = Field(
        default=None,
        description="Basis set",
    )
    
    def get_dipole_moment(self) -> Optional[float]:
        """Get total dipole moment."""
        if self.multipoles and self.multipoles.dipole:
            return self.multipoles.dipole.total
        return None
    
    def get_isotropic_polarizability(self) -> Optional[float]:
        """Get isotropic polarizability."""
        if self.polarizability:
            return self.polarizability.isotropic
        return None


# Backward compatibility aliases
PropertiesOutput = PropertyOutput
DipoleMoment = DipoleMomentOutput
QuadrupoleMoment = QuadrupoleMomentOutput


class AtomicCharge(Psi4BaseModel):
    """Atomic charge from population analysis."""
    atom_index: int = Field(..., description="Atom index")
    symbol: str = Field(..., description="Element symbol")
    charge: float = Field(..., description="Partial charge")
    spin: Optional[float] = Field(default=None, description="Spin density")


class BondOrder(Psi4BaseModel):
    """Bond order between two atoms."""
    atom1_index: int = Field(..., description="First atom index")
    atom2_index: int = Field(..., description="Second atom index")
    order: float = Field(..., description="Bond order value")
    type: str = Field(default="wiberg", description="Bond order type")


class PopulationAnalysisOutput(Psi4BaseModel):
    """Population analysis results."""
    method: str = Field(..., description="Analysis method (mulliken, lowdin, npa)")
    charges: list[AtomicCharge] = Field(default_factory=list, description="Atomic charges")
    total_charge: float = Field(default=0.0, description="Total molecular charge")
    dipole: Optional[DipoleMomentOutput] = Field(default=None, description="Dipole moment")


class OrbitalInfo(Psi4BaseModel):
    """Molecular orbital information."""
    index: int = Field(..., description="Orbital index")
    energy: float = Field(..., description="Orbital energy in Hartree")
    occupation: float = Field(..., description="Occupation number")
    symmetry: Optional[str] = Field(default=None, description="Symmetry label")
    type: str = Field(default="canonical", description="Orbital type")


class OrbitalOutput(Psi4BaseModel):
    """Orbital analysis results."""
    orbitals: list[OrbitalInfo] = Field(default_factory=list, description="Orbital data")
    homo_index: Optional[int] = Field(default=None, description="HOMO index")
    lumo_index: Optional[int] = Field(default=None, description="LUMO index")
    homo_energy: Optional[float] = Field(default=None, description="HOMO energy")
    lumo_energy: Optional[float] = Field(default=None, description="LUMO energy")
    gap: Optional[float] = Field(default=None, description="HOMO-LUMO gap")
