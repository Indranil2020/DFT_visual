"""
Unit Conversion Utilities for Quantum Chemistry.

This module provides high-level unit conversion functions that build upon
the basic conversion factors from the helpers module. It includes batch
conversion functions, automatic unit detection, and formatted output.

Key Features:
    - Batch conversion of arrays/lists
    - Automatic unit detection from strings
    - Conversion with uncertainty propagation
    - Formatted output with units
"""

from typing import Sequence, Union, Optional
from dataclasses import dataclass
from enum import Enum

from psi4_mcp.utils.helpers.units import (
    EnergyUnit,
    LengthUnit,
    AngleUnit,
    TimeUnit,
    MassUnit,
    DipoleUnit,
    ForceUnit,
    PressureUnit,
    convert_energy,
    convert_length,
    convert_angle,
    convert_time,
    convert_mass,
    convert_dipole,
    convert_force,
    convert_pressure,
)


# =============================================================================
# TYPE ALIASES
# =============================================================================

NumericType = Union[int, float]
NumericSequence = Sequence[NumericType]


# =============================================================================
# UNIT DETECTION
# =============================================================================

# Mapping of common unit strings to EnergyUnit enum
_ENERGY_UNIT_MAP: dict[str, EnergyUnit] = {
    # Hartree
    "hartree": EnergyUnit.HARTREE,
    "hartrees": EnergyUnit.HARTREE,
    "eh": EnergyUnit.HARTREE,
    "e_h": EnergyUnit.HARTREE,
    "au": EnergyUnit.HARTREE,
    "a.u.": EnergyUnit.HARTREE,
    
    # Electronvolts
    "ev": EnergyUnit.EV,
    "electronvolt": EnergyUnit.EV,
    "electronvolts": EnergyUnit.EV,
    
    # kcal/mol
    "kcal/mol": EnergyUnit.KCAL_MOL,
    "kcal": EnergyUnit.KCAL_MOL,
    "kcalmol": EnergyUnit.KCAL_MOL,
    "kcal_mol": EnergyUnit.KCAL_MOL,
    
    # kJ/mol
    "kj/mol": EnergyUnit.KJ_MOL,
    "kj": EnergyUnit.KJ_MOL,
    "kjmol": EnergyUnit.KJ_MOL,
    "kj_mol": EnergyUnit.KJ_MOL,
    
    # Wavenumbers
    "cm-1": EnergyUnit.CM_INV,
    "cm^-1": EnergyUnit.CM_INV,
    "cm_inv": EnergyUnit.CM_INV,
    "wavenumber": EnergyUnit.CM_INV,
    "wavenumbers": EnergyUnit.CM_INV,
    
    # Joule
    "j": EnergyUnit.JOULE,
    "joule": EnergyUnit.JOULE,
    "joules": EnergyUnit.JOULE,
    
    # Kelvin
    "k": EnergyUnit.KELVIN,
    "kelvin": EnergyUnit.KELVIN,
    
    # MHz/Hz
    "mhz": EnergyUnit.MHZ,
    "hz": EnergyUnit.HZ,
}

# Mapping of common unit strings to LengthUnit enum
_LENGTH_UNIT_MAP: dict[str, LengthUnit] = {
    # Bohr
    "bohr": LengthUnit.BOHR,
    "bohrs": LengthUnit.BOHR,
    "a0": LengthUnit.BOHR,
    "a_0": LengthUnit.BOHR,
    "au": LengthUnit.BOHR,
    
    # Angstrom
    "angstrom": LengthUnit.ANGSTROM,
    "angstroms": LengthUnit.ANGSTROM,
    "a": LengthUnit.ANGSTROM,
    "å": LengthUnit.ANGSTROM,
    
    # Nanometer
    "nm": LengthUnit.NANOMETER,
    "nanometer": LengthUnit.NANOMETER,
    "nanometers": LengthUnit.NANOMETER,
    
    # Picometer
    "pm": LengthUnit.PICOMETER,
    "picometer": LengthUnit.PICOMETER,
    "picometers": LengthUnit.PICOMETER,
    
    # Meter
    "m": LengthUnit.METER,
    "meter": LengthUnit.METER,
    "meters": LengthUnit.METER,
}

# Mapping of common unit strings to AngleUnit enum
_ANGLE_UNIT_MAP: dict[str, AngleUnit] = {
    "rad": AngleUnit.RADIAN,
    "radian": AngleUnit.RADIAN,
    "radians": AngleUnit.RADIAN,
    "deg": AngleUnit.DEGREE,
    "degree": AngleUnit.DEGREE,
    "degrees": AngleUnit.DEGREE,
    "°": AngleUnit.DEGREE,
    "mrad": AngleUnit.MILLIRADIAN,
    "milliradian": AngleUnit.MILLIRADIAN,
}


def detect_energy_unit(unit_string: str) -> Optional[EnergyUnit]:
    """
    Detect the energy unit from a string.
    
    Args:
        unit_string: String representation of the unit.
        
    Returns:
        EnergyUnit enum value, or None if not recognized.
    """
    normalized = unit_string.lower().strip().replace(" ", "")
    return _ENERGY_UNIT_MAP.get(normalized)


def detect_length_unit(unit_string: str) -> Optional[LengthUnit]:
    """
    Detect the length unit from a string.
    
    Args:
        unit_string: String representation of the unit.
        
    Returns:
        LengthUnit enum value, or None if not recognized.
    """
    normalized = unit_string.lower().strip().replace(" ", "")
    return _LENGTH_UNIT_MAP.get(normalized)


def detect_angle_unit(unit_string: str) -> Optional[AngleUnit]:
    """
    Detect the angle unit from a string.
    
    Args:
        unit_string: String representation of the unit.
        
    Returns:
        AngleUnit enum value, or None if not recognized.
    """
    normalized = unit_string.lower().strip().replace(" ", "")
    return _ANGLE_UNIT_MAP.get(normalized)


# =============================================================================
# VALUE WITH UNIT
# =============================================================================

@dataclass
class ValueWithUnit:
    """
    A numeric value paired with its unit.
    
    Attributes:
        value: The numeric value.
        unit: String representation of the unit.
        uncertainty: Optional uncertainty (standard deviation).
    """
    value: float
    unit: str
    uncertainty: Optional[float] = None
    
    def __str__(self) -> str:
        if self.uncertainty is not None:
            return f"{self.value:.6g} ± {self.uncertainty:.2g} {self.unit}"
        return f"{self.value:.6g} {self.unit}"
    
    def __repr__(self) -> str:
        return f"ValueWithUnit({self.value}, '{self.unit}', {self.uncertainty})"


@dataclass 
class EnergyValue:
    """
    An energy value with automatic unit conversion.
    
    Stores the value in Hartree internally and provides conversion methods.
    """
    hartree: float
    uncertainty_hartree: Optional[float] = None
    
    @classmethod
    def from_hartree(cls, value: float, uncertainty: Optional[float] = None) -> "EnergyValue":
        """Create from Hartree value."""
        return cls(hartree=value, uncertainty_hartree=uncertainty)
    
    @classmethod
    def from_ev(cls, value: float, uncertainty: Optional[float] = None) -> "EnergyValue":
        """Create from electronvolt value."""
        hartree = convert_energy(value, EnergyUnit.EV, EnergyUnit.HARTREE)
        unc_hartree = None
        if uncertainty is not None:
            unc_hartree = convert_energy(uncertainty, EnergyUnit.EV, EnergyUnit.HARTREE)
        return cls(hartree=hartree, uncertainty_hartree=unc_hartree)
    
    @classmethod
    def from_kcal_mol(cls, value: float, uncertainty: Optional[float] = None) -> "EnergyValue":
        """Create from kcal/mol value."""
        hartree = convert_energy(value, EnergyUnit.KCAL_MOL, EnergyUnit.HARTREE)
        unc_hartree = None
        if uncertainty is not None:
            unc_hartree = convert_energy(uncertainty, EnergyUnit.KCAL_MOL, EnergyUnit.HARTREE)
        return cls(hartree=hartree, uncertainty_hartree=unc_hartree)
    
    @classmethod
    def from_kj_mol(cls, value: float, uncertainty: Optional[float] = None) -> "EnergyValue":
        """Create from kJ/mol value."""
        hartree = convert_energy(value, EnergyUnit.KJ_MOL, EnergyUnit.HARTREE)
        unc_hartree = None
        if uncertainty is not None:
            unc_hartree = convert_energy(uncertainty, EnergyUnit.KJ_MOL, EnergyUnit.HARTREE)
        return cls(hartree=hartree, uncertainty_hartree=unc_hartree)
    
    @classmethod
    def from_cm_inv(cls, value: float, uncertainty: Optional[float] = None) -> "EnergyValue":
        """Create from wavenumber (cm^-1) value."""
        hartree = convert_energy(value, EnergyUnit.CM_INV, EnergyUnit.HARTREE)
        unc_hartree = None
        if uncertainty is not None:
            unc_hartree = convert_energy(uncertainty, EnergyUnit.CM_INV, EnergyUnit.HARTREE)
        return cls(hartree=hartree, uncertainty_hartree=unc_hartree)
    
    def to_hartree(self) -> float:
        """Get value in Hartree."""
        return self.hartree
    
    def to_ev(self) -> float:
        """Get value in electronvolts."""
        return convert_energy(self.hartree, EnergyUnit.HARTREE, EnergyUnit.EV)
    
    def to_kcal_mol(self) -> float:
        """Get value in kcal/mol."""
        return convert_energy(self.hartree, EnergyUnit.HARTREE, EnergyUnit.KCAL_MOL)
    
    def to_kj_mol(self) -> float:
        """Get value in kJ/mol."""
        return convert_energy(self.hartree, EnergyUnit.HARTREE, EnergyUnit.KJ_MOL)
    
    def to_cm_inv(self) -> float:
        """Get value in wavenumbers (cm^-1)."""
        return convert_energy(self.hartree, EnergyUnit.HARTREE, EnergyUnit.CM_INV)
    
    def to_kelvin(self) -> float:
        """Get value in Kelvin."""
        return convert_energy(self.hartree, EnergyUnit.HARTREE, EnergyUnit.KELVIN)
    
    def to_unit(self, unit: EnergyUnit) -> float:
        """Get value in specified unit."""
        return convert_energy(self.hartree, EnergyUnit.HARTREE, unit)
    
    def with_unit(self, unit: EnergyUnit) -> ValueWithUnit:
        """Get as ValueWithUnit in specified unit."""
        value = self.to_unit(unit)
        uncertainty = None
        if self.uncertainty_hartree is not None:
            uncertainty = convert_energy(
                self.uncertainty_hartree, EnergyUnit.HARTREE, unit
            )
        unit_labels = {
            EnergyUnit.HARTREE: "Hartree",
            EnergyUnit.EV: "eV",
            EnergyUnit.KCAL_MOL: "kcal/mol",
            EnergyUnit.KJ_MOL: "kJ/mol",
            EnergyUnit.CM_INV: "cm⁻¹",
            EnergyUnit.KELVIN: "K",
        }
        return ValueWithUnit(value, unit_labels.get(unit, str(unit)), uncertainty)
    
    def __add__(self, other: "EnergyValue") -> "EnergyValue":
        new_hartree = self.hartree + other.hartree
        new_unc = None
        if self.uncertainty_hartree is not None and other.uncertainty_hartree is not None:
            # Propagate uncertainty (assuming uncorrelated)
            new_unc = (self.uncertainty_hartree**2 + other.uncertainty_hartree**2)**0.5
        elif self.uncertainty_hartree is not None:
            new_unc = self.uncertainty_hartree
        elif other.uncertainty_hartree is not None:
            new_unc = other.uncertainty_hartree
        return EnergyValue(new_hartree, new_unc)
    
    def __sub__(self, other: "EnergyValue") -> "EnergyValue":
        new_hartree = self.hartree - other.hartree
        new_unc = None
        if self.uncertainty_hartree is not None and other.uncertainty_hartree is not None:
            new_unc = (self.uncertainty_hartree**2 + other.uncertainty_hartree**2)**0.5
        elif self.uncertainty_hartree is not None:
            new_unc = self.uncertainty_hartree
        elif other.uncertainty_hartree is not None:
            new_unc = other.uncertainty_hartree
        return EnergyValue(new_hartree, new_unc)
    
    def __neg__(self) -> "EnergyValue":
        return EnergyValue(-self.hartree, self.uncertainty_hartree)
    
    def __mul__(self, scalar: float) -> "EnergyValue":
        new_unc = None
        if self.uncertainty_hartree is not None:
            new_unc = abs(scalar) * self.uncertainty_hartree
        return EnergyValue(self.hartree * scalar, new_unc)
    
    def __rmul__(self, scalar: float) -> "EnergyValue":
        return self.__mul__(scalar)
    
    def __str__(self) -> str:
        return str(self.with_unit(EnergyUnit.HARTREE))


@dataclass
class LengthValue:
    """
    A length value with automatic unit conversion.
    
    Stores the value in Bohr internally and provides conversion methods.
    """
    bohr: float
    uncertainty_bohr: Optional[float] = None
    
    @classmethod
    def from_bohr(cls, value: float, uncertainty: Optional[float] = None) -> "LengthValue":
        """Create from Bohr value."""
        return cls(bohr=value, uncertainty_bohr=uncertainty)
    
    @classmethod
    def from_angstrom(cls, value: float, uncertainty: Optional[float] = None) -> "LengthValue":
        """Create from Angstrom value."""
        bohr = convert_length(value, LengthUnit.ANGSTROM, LengthUnit.BOHR)
        unc_bohr = None
        if uncertainty is not None:
            unc_bohr = convert_length(uncertainty, LengthUnit.ANGSTROM, LengthUnit.BOHR)
        return cls(bohr=bohr, uncertainty_bohr=unc_bohr)
    
    @classmethod
    def from_nm(cls, value: float, uncertainty: Optional[float] = None) -> "LengthValue":
        """Create from nanometer value."""
        bohr = convert_length(value, LengthUnit.NANOMETER, LengthUnit.BOHR)
        unc_bohr = None
        if uncertainty is not None:
            unc_bohr = convert_length(uncertainty, LengthUnit.NANOMETER, LengthUnit.BOHR)
        return cls(bohr=bohr, uncertainty_bohr=unc_bohr)
    
    @classmethod
    def from_pm(cls, value: float, uncertainty: Optional[float] = None) -> "LengthValue":
        """Create from picometer value."""
        bohr = convert_length(value, LengthUnit.PICOMETER, LengthUnit.BOHR)
        unc_bohr = None
        if uncertainty is not None:
            unc_bohr = convert_length(uncertainty, LengthUnit.PICOMETER, LengthUnit.BOHR)
        return cls(bohr=bohr, uncertainty_bohr=unc_bohr)
    
    def to_bohr(self) -> float:
        """Get value in Bohr."""
        return self.bohr
    
    def to_angstrom(self) -> float:
        """Get value in Angstrom."""
        return convert_length(self.bohr, LengthUnit.BOHR, LengthUnit.ANGSTROM)
    
    def to_nm(self) -> float:
        """Get value in nanometers."""
        return convert_length(self.bohr, LengthUnit.BOHR, LengthUnit.NANOMETER)
    
    def to_pm(self) -> float:
        """Get value in picometers."""
        return convert_length(self.bohr, LengthUnit.BOHR, LengthUnit.PICOMETER)
    
    def to_unit(self, unit: LengthUnit) -> float:
        """Get value in specified unit."""
        return convert_length(self.bohr, LengthUnit.BOHR, unit)
    
    def with_unit(self, unit: LengthUnit) -> ValueWithUnit:
        """Get as ValueWithUnit in specified unit."""
        value = self.to_unit(unit)
        uncertainty = None
        if self.uncertainty_bohr is not None:
            uncertainty = convert_length(
                self.uncertainty_bohr, LengthUnit.BOHR, unit
            )
        unit_labels = {
            LengthUnit.BOHR: "Bohr",
            LengthUnit.ANGSTROM: "Å",
            LengthUnit.NANOMETER: "nm",
            LengthUnit.PICOMETER: "pm",
            LengthUnit.METER: "m",
        }
        return ValueWithUnit(value, unit_labels.get(unit, str(unit)), uncertainty)
    
    def __str__(self) -> str:
        return str(self.with_unit(LengthUnit.ANGSTROM))


# =============================================================================
# BATCH CONVERSION FUNCTIONS
# =============================================================================

def convert_energy_array(
    values: NumericSequence,
    from_unit: EnergyUnit,
    to_unit: EnergyUnit
) -> list[float]:
    """
    Convert an array of energy values between units.
    
    Args:
        values: Sequence of energy values.
        from_unit: Source unit.
        to_unit: Target unit.
        
    Returns:
        List of converted values.
    """
    return [convert_energy(v, from_unit, to_unit) for v in values]


def convert_length_array(
    values: NumericSequence,
    from_unit: LengthUnit,
    to_unit: LengthUnit
) -> list[float]:
    """
    Convert an array of length values between units.
    
    Args:
        values: Sequence of length values.
        from_unit: Source unit.
        to_unit: Target unit.
        
    Returns:
        List of converted values.
    """
    return [convert_length(v, from_unit, to_unit) for v in values]


def convert_coordinates_to_bohr(
    coordinates: Sequence[Sequence[float]],
    from_unit: LengthUnit = LengthUnit.ANGSTROM
) -> list[list[float]]:
    """
    Convert a list of 3D coordinates to Bohr.
    
    Args:
        coordinates: List of [x, y, z] coordinates.
        from_unit: Source unit (default: Angstrom).
        
    Returns:
        Coordinates in Bohr.
    """
    result = []
    for coord in coordinates:
        converted = [
            convert_length(c, from_unit, LengthUnit.BOHR) 
            for c in coord
        ]
        result.append(converted)
    return result


def convert_coordinates_to_angstrom(
    coordinates: Sequence[Sequence[float]],
    from_unit: LengthUnit = LengthUnit.BOHR
) -> list[list[float]]:
    """
    Convert a list of 3D coordinates to Angstrom.
    
    Args:
        coordinates: List of [x, y, z] coordinates.
        from_unit: Source unit (default: Bohr).
        
    Returns:
        Coordinates in Angstrom.
    """
    result = []
    for coord in coordinates:
        converted = [
            convert_length(c, from_unit, LengthUnit.ANGSTROM) 
            for c in coord
        ]
        result.append(converted)
    return result


def convert_gradient_to_hartree_bohr(
    gradient: Sequence[Sequence[float]],
    from_energy_unit: EnergyUnit = EnergyUnit.HARTREE,
    from_length_unit: LengthUnit = LengthUnit.ANGSTROM
) -> list[list[float]]:
    """
    Convert gradient (force) values to Hartree/Bohr.
    
    Gradient has units of Energy/Length.
    
    Args:
        gradient: List of [gx, gy, gz] gradient components per atom.
        from_energy_unit: Source energy unit.
        from_length_unit: Source length unit.
        
    Returns:
        Gradient in Hartree/Bohr.
    """
    # Conversion factor: (to Hartree) / (to Bohr) = (to Hartree) * (from Bohr)
    energy_factor = convert_energy(1.0, from_energy_unit, EnergyUnit.HARTREE)
    length_factor = convert_length(1.0, LengthUnit.BOHR, from_length_unit)
    factor = energy_factor * length_factor
    
    result = []
    for grad in gradient:
        converted = [g * factor for g in grad]
        result.append(converted)
    return result


def convert_hessian_to_hartree_bohr2(
    hessian: Sequence[Sequence[float]],
    from_energy_unit: EnergyUnit = EnergyUnit.HARTREE,
    from_length_unit: LengthUnit = LengthUnit.ANGSTROM
) -> list[list[float]]:
    """
    Convert Hessian (force constant matrix) to Hartree/Bohr².
    
    Hessian has units of Energy/Length².
    
    Args:
        hessian: 2D Hessian matrix.
        from_energy_unit: Source energy unit.
        from_length_unit: Source length unit.
        
    Returns:
        Hessian in Hartree/Bohr².
    """
    # Conversion factor: (to Hartree) / (to Bohr)²
    energy_factor = convert_energy(1.0, from_energy_unit, EnergyUnit.HARTREE)
    length_factor = convert_length(1.0, LengthUnit.BOHR, from_length_unit)
    factor = energy_factor * length_factor * length_factor
    
    result = []
    for row in hessian:
        converted_row = [h * factor for h in row]
        result.append(converted_row)
    return result


# =============================================================================
# STRING PARSING FUNCTIONS
# =============================================================================

def parse_energy_string(s: str) -> Optional[EnergyValue]:
    """
    Parse an energy value from a string with unit.
    
    Accepts formats like:
        - "-76.123 Hartree"
        - "5.2 eV"
        - "-123.4 kcal/mol"
    
    Args:
        s: String containing value and unit.
        
    Returns:
        EnergyValue object, or None if parsing fails.
    """
    parts = s.strip().split()
    if len(parts) < 2:
        return None
    
    # Try to parse the numeric value
    value_str = parts[0]
    unit_str = " ".join(parts[1:])
    
    # Handle Fortran-style exponents
    value_str = value_str.replace('D', 'E').replace('d', 'e')
    
    # Validate numeric
    value: float
    if not _is_float(value_str):
        return None
    value = float(value_str)
    
    # Detect unit
    unit = detect_energy_unit(unit_str)
    if unit is None:
        return None
    
    # Convert to Hartree
    hartree = convert_energy(value, unit, EnergyUnit.HARTREE)
    return EnergyValue(hartree)


def parse_length_string(s: str) -> Optional[LengthValue]:
    """
    Parse a length value from a string with unit.
    
    Accepts formats like:
        - "1.52 Angstrom"
        - "2.87 Bohr"
        - "0.152 nm"
    
    Args:
        s: String containing value and unit.
        
    Returns:
        LengthValue object, or None if parsing fails.
    """
    parts = s.strip().split()
    if len(parts) < 2:
        return None
    
    value_str = parts[0]
    unit_str = " ".join(parts[1:])
    
    value_str = value_str.replace('D', 'E').replace('d', 'e')
    
    if not _is_float(value_str):
        return None
    value = float(value_str)
    
    unit = detect_length_unit(unit_str)
    if unit is None:
        return None
    
    bohr = convert_length(value, unit, LengthUnit.BOHR)
    return LengthValue(bohr)


def _is_float(s: str) -> bool:
    """Check if string can be converted to float."""
    if not s:
        return False
    # Remove leading/trailing whitespace
    s = s.strip()
    # Check for valid float pattern
    if s.startswith('+') or s.startswith('-'):
        s = s[1:]
    parts = s.split('e')
    if len(parts) > 2:
        return False
    if len(parts) == 2:
        if not _is_simple_float(parts[0]) or not _is_int(parts[1]):
            return False
        return True
    return _is_simple_float(s)


def _is_simple_float(s: str) -> bool:
    """Check if string is a simple float (no exponent)."""
    if not s:
        return False
    parts = s.split('.')
    if len(parts) > 2:
        return False
    for part in parts:
        if part and not part.isdigit():
            return False
    return True


def _is_int(s: str) -> bool:
    """Check if string is an integer (possibly signed)."""
    if not s:
        return False
    if s.startswith('+') or s.startswith('-'):
        s = s[1:]
    return s.isdigit()


# =============================================================================
# FORMATTED OUTPUT
# =============================================================================

def format_energy_table(
    energies: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    units: Sequence[EnergyUnit] = (
        EnergyUnit.HARTREE, 
        EnergyUnit.EV, 
        EnergyUnit.KCAL_MOL
    ),
    precision: int = 6
) -> str:
    """
    Format energy values as a table with multiple units.
    
    Args:
        energies: Energy values in Hartree.
        labels: Optional labels for each energy.
        units: Units to display.
        precision: Number of decimal places.
        
    Returns:
        Formatted table string.
    """
    unit_names = {
        EnergyUnit.HARTREE: "Hartree",
        EnergyUnit.EV: "eV",
        EnergyUnit.KCAL_MOL: "kcal/mol",
        EnergyUnit.KJ_MOL: "kJ/mol",
        EnergyUnit.CM_INV: "cm⁻¹",
        EnergyUnit.KELVIN: "K",
    }
    
    # Build header
    header_parts = ["Label"] if labels else ["#"]
    for unit in units:
        header_parts.append(unit_names.get(unit, str(unit)))
    
    # Build rows
    rows = []
    for i, energy in enumerate(energies):
        row_parts = []
        if labels:
            row_parts.append(labels[i] if i < len(labels) else f"E{i+1}")
        else:
            row_parts.append(str(i + 1))
        
        for unit in units:
            converted = convert_energy(energy, EnergyUnit.HARTREE, unit)
            row_parts.append(f"{converted:.{precision}f}")
        
        rows.append(row_parts)
    
    # Format table
    return _format_simple_table(header_parts, rows)


def format_length_table(
    lengths: Sequence[float],
    labels: Optional[Sequence[str]] = None,
    units: Sequence[LengthUnit] = (
        LengthUnit.ANGSTROM,
        LengthUnit.BOHR,
        LengthUnit.PICOMETER
    ),
    precision: int = 4
) -> str:
    """
    Format length values as a table with multiple units.
    
    Args:
        lengths: Length values in Angstrom.
        labels: Optional labels for each length.
        units: Units to display.
        precision: Number of decimal places.
        
    Returns:
        Formatted table string.
    """
    unit_names = {
        LengthUnit.ANGSTROM: "Å",
        LengthUnit.BOHR: "Bohr",
        LengthUnit.NANOMETER: "nm",
        LengthUnit.PICOMETER: "pm",
        LengthUnit.METER: "m",
    }
    
    header_parts = ["Label"] if labels else ["#"]
    for unit in units:
        header_parts.append(unit_names.get(unit, str(unit)))
    
    rows = []
    for i, length in enumerate(lengths):
        row_parts = []
        if labels:
            row_parts.append(labels[i] if i < len(labels) else f"R{i+1}")
        else:
            row_parts.append(str(i + 1))
        
        for unit in units:
            converted = convert_length(length, LengthUnit.ANGSTROM, unit)
            row_parts.append(f"{converted:.{precision}f}")
        
        rows.append(row_parts)
    
    return _format_simple_table(header_parts, rows)


def _format_simple_table(
    headers: Sequence[str], 
    rows: Sequence[Sequence[str]]
) -> str:
    """Format a simple text table."""
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))
    
    # Build table
    lines = []
    
    # Header
    header_line = " | ".join(
        headers[i].center(widths[i]) for i in range(len(headers))
    )
    lines.append(header_line)
    
    # Separator
    sep_line = "-+-".join("-" * w for w in widths)
    lines.append(sep_line)
    
    # Rows
    for row in rows:
        row_line = " | ".join(
            (row[i] if i < len(row) else "").rjust(widths[i])
            for i in range(len(widths))
        )
        lines.append(row_line)
    
    return "\n".join(lines)
