"""
Unit Conversion Module for Quantum Chemistry Calculations.

This module provides comprehensive unit conversion functions for all
quantities commonly used in quantum chemistry calculations. It includes
energy, length, angle, time, mass, dipole moment, polarizability,
and other physical quantities.

All conversions are based on CODATA 2018 recommended values.
"""

from typing import Final
from enum import Enum, auto


# =============================================================================
# UNIT ENUMERATIONS
# =============================================================================

class EnergyUnit(Enum):
    """Enumeration of supported energy units."""
    HARTREE = auto()
    EV = auto()
    KCAL_MOL = auto()
    KJ_MOL = auto()
    CM_INV = auto()  # Wavenumbers (cm^-1)
    JOULE = auto()
    CAL = auto()
    KELVIN = auto()
    MHZ = auto()
    HZ = auto()


class LengthUnit(Enum):
    """Enumeration of supported length units."""
    BOHR = auto()
    ANGSTROM = auto()
    NANOMETER = auto()
    PICOMETER = auto()
    METER = auto()


class AngleUnit(Enum):
    """Enumeration of supported angle units."""
    RADIAN = auto()
    DEGREE = auto()
    MILLIRADIAN = auto()


class TimeUnit(Enum):
    """Enumeration of supported time units."""
    AU = auto()  # Atomic units
    SECOND = auto()
    FEMTOSECOND = auto()
    PICOSECOND = auto()
    ATTOSECOND = auto()


class MassUnit(Enum):
    """Enumeration of supported mass units."""
    AMU = auto()
    ELECTRON_MASS = auto()
    KG = auto()
    GRAM = auto()


class DipoleUnit(Enum):
    """Enumeration of supported dipole moment units."""
    AU = auto()  # e·a₀
    DEBYE = auto()
    COULOMB_METER = auto()


class PolarizabilityUnit(Enum):
    """Enumeration of supported polarizability units."""
    AU = auto()  # a₀³
    ANGSTROM3 = auto()
    BOHR3 = auto()


class ForceUnit(Enum):
    """Enumeration of supported force units."""
    HARTREE_BOHR = auto()  # Hartree/Bohr
    EV_ANGSTROM = auto()
    NEWTON = auto()
    MILLIDYNE = auto()


class PressureUnit(Enum):
    """Enumeration of supported pressure units."""
    AU = auto()
    PASCAL = auto()
    KILOPASCAL = auto()
    MEGAPASCAL = auto()
    GIGAPASCAL = auto()
    ATM = auto()
    BAR = auto()


# =============================================================================
# CONVERSION FACTORS (to SI base units or atomic units)
# =============================================================================

# Energy conversion factors (relative to Hartree)
_ENERGY_TO_HARTREE: Final[dict[EnergyUnit, float]] = {
    EnergyUnit.HARTREE: 1.0,
    EnergyUnit.EV: 1.0 / 27.211386245988,
    EnergyUnit.KCAL_MOL: 1.0 / 627.5094740631,
    EnergyUnit.KJ_MOL: 1.0 / 2625.4996394799,
    EnergyUnit.CM_INV: 1.0 / 219474.63136320,
    EnergyUnit.JOULE: 1.0 / 4.3597447222071e-18,
    EnergyUnit.CAL: 1.0 / (4.3597447222071e-18 / 4.184),
    EnergyUnit.KELVIN: 1.0 / 315775.02480407,
    EnergyUnit.MHZ: 1.0 / 6.579683920502e9,
    EnergyUnit.HZ: 1.0 / 6.579683920502e15,
}

# Length conversion factors (relative to Bohr)
_LENGTH_TO_BOHR: Final[dict[LengthUnit, float]] = {
    LengthUnit.BOHR: 1.0,
    LengthUnit.ANGSTROM: 1.0 / 0.529177210903,
    LengthUnit.NANOMETER: 1.0 / 0.0529177210903,
    LengthUnit.PICOMETER: 1.0 / 52.9177210903,
    LengthUnit.METER: 1.0 / 5.29177210903e-11,
}

# Angle conversion factors (relative to radians)
_ANGLE_TO_RADIAN: Final[dict[AngleUnit, float]] = {
    AngleUnit.RADIAN: 1.0,
    AngleUnit.DEGREE: 3.14159265358979323846 / 180.0,
    AngleUnit.MILLIRADIAN: 0.001,
}

# Time conversion factors (relative to atomic units)
_TIME_TO_AU: Final[dict[TimeUnit, float]] = {
    TimeUnit.AU: 1.0,
    TimeUnit.SECOND: 1.0 / 2.4188843265857e-17,
    TimeUnit.FEMTOSECOND: 1.0 / 2.4188843265857e-2,
    TimeUnit.PICOSECOND: 1.0 / 2.4188843265857e1,
    TimeUnit.ATTOSECOND: 1.0 / 2.4188843265857e-5,
}

# Mass conversion factors (relative to electron mass)
_MASS_TO_ME: Final[dict[MassUnit, float]] = {
    MassUnit.ELECTRON_MASS: 1.0,
    MassUnit.AMU: 1822.888486209,
    MassUnit.KG: 1.0 / 9.1093837015e-31,
    MassUnit.GRAM: 1.0 / 9.1093837015e-28,
}

# Dipole conversion factors (relative to atomic units)
_DIPOLE_TO_AU: Final[dict[DipoleUnit, float]] = {
    DipoleUnit.AU: 1.0,
    DipoleUnit.DEBYE: 1.0 / 2.541746473,
    DipoleUnit.COULOMB_METER: 1.0 / 8.4783536255e-30,
}

# Polarizability conversion factors (relative to atomic units / Bohr^3)
_POLARIZABILITY_TO_AU: Final[dict[PolarizabilityUnit, float]] = {
    PolarizabilityUnit.AU: 1.0,
    PolarizabilityUnit.BOHR3: 1.0,
    PolarizabilityUnit.ANGSTROM3: 1.0 / (0.529177210903 ** 3),
}

# Force conversion factors (relative to Hartree/Bohr)
_FORCE_TO_HARTREE_BOHR: Final[dict[ForceUnit, float]] = {
    ForceUnit.HARTREE_BOHR: 1.0,
    ForceUnit.EV_ANGSTROM: 0.529177210903 / 27.211386245988,
    ForceUnit.NEWTON: 1.0 / 8.2387234983e-8,
    ForceUnit.MILLIDYNE: 1.0 / 8.2387234983e-5,
}

# Pressure conversion factors (relative to atomic units)
_PRESSURE_TO_AU: Final[dict[PressureUnit, float]] = {
    PressureUnit.AU: 1.0,
    PressureUnit.PASCAL: 1.0 / 2.9421015697e13,
    PressureUnit.KILOPASCAL: 1.0 / 2.9421015697e10,
    PressureUnit.MEGAPASCAL: 1.0 / 2.9421015697e7,
    PressureUnit.GIGAPASCAL: 1.0 / 2.9421015697e4,
    PressureUnit.ATM: 1.0 / 2.9037166529e8,
    PressureUnit.BAR: 1.0 / 2.9421015697e8,
}


# =============================================================================
# GENERIC CONVERSION FUNCTION
# =============================================================================

def convert_energy(value: float, from_unit: EnergyUnit, to_unit: EnergyUnit) -> float:
    """
    Convert energy between different units.
    
    Args:
        value: The energy value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted energy value.
    """
    # Convert to Hartree first, then to target unit
    hartree_value = value * _ENERGY_TO_HARTREE[from_unit]
    return hartree_value / _ENERGY_TO_HARTREE[to_unit]


def convert_length(value: float, from_unit: LengthUnit, to_unit: LengthUnit) -> float:
    """
    Convert length between different units.
    
    Args:
        value: The length value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted length value.
    """
    bohr_value = value * _LENGTH_TO_BOHR[from_unit]
    return bohr_value / _LENGTH_TO_BOHR[to_unit]


def convert_angle(value: float, from_unit: AngleUnit, to_unit: AngleUnit) -> float:
    """
    Convert angle between different units.
    
    Args:
        value: The angle value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted angle value.
    """
    radian_value = value * _ANGLE_TO_RADIAN[from_unit]
    return radian_value / _ANGLE_TO_RADIAN[to_unit]


def convert_time(value: float, from_unit: TimeUnit, to_unit: TimeUnit) -> float:
    """
    Convert time between different units.
    
    Args:
        value: The time value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted time value.
    """
    au_value = value * _TIME_TO_AU[from_unit]
    return au_value / _TIME_TO_AU[to_unit]


def convert_mass(value: float, from_unit: MassUnit, to_unit: MassUnit) -> float:
    """
    Convert mass between different units.
    
    Args:
        value: The mass value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted mass value.
    """
    me_value = value * _MASS_TO_ME[from_unit]
    return me_value / _MASS_TO_ME[to_unit]


def convert_dipole(value: float, from_unit: DipoleUnit, to_unit: DipoleUnit) -> float:
    """
    Convert dipole moment between different units.
    
    Args:
        value: The dipole moment value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted dipole moment value.
    """
    au_value = value * _DIPOLE_TO_AU[from_unit]
    return au_value / _DIPOLE_TO_AU[to_unit]


def convert_polarizability(
    value: float, 
    from_unit: PolarizabilityUnit, 
    to_unit: PolarizabilityUnit
) -> float:
    """
    Convert polarizability between different units.
    
    Args:
        value: The polarizability value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted polarizability value.
    """
    au_value = value * _POLARIZABILITY_TO_AU[from_unit]
    return au_value / _POLARIZABILITY_TO_AU[to_unit]


def convert_force(value: float, from_unit: ForceUnit, to_unit: ForceUnit) -> float:
    """
    Convert force between different units.
    
    Args:
        value: The force value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted force value.
    """
    au_value = value * _FORCE_TO_HARTREE_BOHR[from_unit]
    return au_value / _FORCE_TO_HARTREE_BOHR[to_unit]


def convert_pressure(value: float, from_unit: PressureUnit, to_unit: PressureUnit) -> float:
    """
    Convert pressure between different units.
    
    Args:
        value: The pressure value to convert.
        from_unit: The unit of the input value.
        to_unit: The desired output unit.
        
    Returns:
        The converted pressure value.
    """
    au_value = value * _PRESSURE_TO_AU[from_unit]
    return au_value / _PRESSURE_TO_AU[to_unit]


# =============================================================================
# CONVENIENCE FUNCTIONS: ENERGY
# =============================================================================

def hartree_to_ev(hartree: float) -> float:
    """Convert energy from Hartree to electronvolts."""
    return hartree * 27.211386245988


def ev_to_hartree(ev: float) -> float:
    """Convert energy from electronvolts to Hartree."""
    return ev / 27.211386245988


def hartree_to_kcal_mol(hartree: float) -> float:
    """Convert energy from Hartree to kcal/mol."""
    return hartree * 627.5094740631


def kcal_mol_to_hartree(kcal_mol: float) -> float:
    """Convert energy from kcal/mol to Hartree."""
    return kcal_mol / 627.5094740631


def hartree_to_kj_mol(hartree: float) -> float:
    """Convert energy from Hartree to kJ/mol."""
    return hartree * 2625.4996394799


def kj_mol_to_hartree(kj_mol: float) -> float:
    """Convert energy from kJ/mol to Hartree."""
    return kj_mol / 2625.4996394799


def hartree_to_cm_inv(hartree: float) -> float:
    """Convert energy from Hartree to wavenumbers (cm^-1)."""
    return hartree * 219474.63136320


def cm_inv_to_hartree(cm_inv: float) -> float:
    """Convert energy from wavenumbers (cm^-1) to Hartree."""
    return cm_inv / 219474.63136320


def hartree_to_kelvin(hartree: float) -> float:
    """Convert energy from Hartree to Kelvin."""
    return hartree * 315775.02480407


def kelvin_to_hartree(kelvin: float) -> float:
    """Convert energy from Kelvin to Hartree."""
    return kelvin / 315775.02480407


def ev_to_cm_inv(ev: float) -> float:
    """Convert energy from electronvolts to wavenumbers (cm^-1)."""
    return ev * 8065.54393734921


def cm_inv_to_ev(cm_inv: float) -> float:
    """Convert energy from wavenumbers (cm^-1) to electronvolts."""
    return cm_inv / 8065.54393734921


def ev_to_nm(ev: float) -> float:
    """Convert energy (in eV) to wavelength (in nm)."""
    if ev <= 0:
        return float('inf')
    return 1239.84193 / ev


def nm_to_ev(nm: float) -> float:
    """Convert wavelength (in nm) to energy (in eV)."""
    if nm <= 0:
        return float('inf')
    return 1239.84193 / nm


def cm_inv_to_nm(cm_inv: float) -> float:
    """Convert wavenumber (cm^-1) to wavelength (nm)."""
    if cm_inv <= 0:
        return float('inf')
    return 1e7 / cm_inv


def nm_to_cm_inv(nm: float) -> float:
    """Convert wavelength (nm) to wavenumber (cm^-1)."""
    if nm <= 0:
        return float('inf')
    return 1e7 / nm


# =============================================================================
# CONVENIENCE FUNCTIONS: LENGTH
# =============================================================================

def bohr_to_angstrom(bohr: float) -> float:
    """Convert length from Bohr to Angstrom."""
    return bohr * 0.529177210903


def angstrom_to_bohr(angstrom: float) -> float:
    """Convert length from Angstrom to Bohr."""
    return angstrom / 0.529177210903


def bohr_to_nm(bohr: float) -> float:
    """Convert length from Bohr to nanometers."""
    return bohr * 0.0529177210903


def nm_to_bohr(nm: float) -> float:
    """Convert length from nanometers to Bohr."""
    return nm / 0.0529177210903


def angstrom_to_nm(angstrom: float) -> float:
    """Convert length from Angstrom to nanometers."""
    return angstrom * 0.1


def nm_to_angstrom(nm: float) -> float:
    """Convert length from nanometers to Angstrom."""
    return nm * 10.0


# =============================================================================
# CONVENIENCE FUNCTIONS: ANGLE
# =============================================================================

def degrees_to_radians(degrees: float) -> float:
    """Convert angle from degrees to radians."""
    return degrees * 3.14159265358979323846 / 180.0


def radians_to_degrees(radians: float) -> float:
    """Convert angle from radians to degrees."""
    return radians * 180.0 / 3.14159265358979323846


# =============================================================================
# CONVENIENCE FUNCTIONS: DIPOLE MOMENT
# =============================================================================

def au_to_debye(au: float) -> float:
    """Convert dipole moment from atomic units (e·a₀) to Debye."""
    return au * 2.541746473


def debye_to_au(debye: float) -> float:
    """Convert dipole moment from Debye to atomic units (e·a₀)."""
    return debye / 2.541746473


# =============================================================================
# CONVENIENCE FUNCTIONS: FORCE
# =============================================================================

def hartree_bohr_to_ev_angstrom(force: float) -> float:
    """Convert force from Hartree/Bohr to eV/Angstrom."""
    return force * 27.211386245988 / 0.529177210903


def ev_angstrom_to_hartree_bohr(force: float) -> float:
    """Convert force from eV/Angstrom to Hartree/Bohr."""
    return force * 0.529177210903 / 27.211386245988


# =============================================================================
# CONVENIENCE FUNCTIONS: FREQUENCY / SPECTROSCOPY
# =============================================================================

def cm_inv_to_thz(cm_inv: float) -> float:
    """Convert frequency from wavenumbers (cm^-1) to THz."""
    return cm_inv * 0.0299792458


def thz_to_cm_inv(thz: float) -> float:
    """Convert frequency from THz to wavenumbers (cm^-1)."""
    return thz / 0.0299792458


def cm_inv_to_mev(cm_inv: float) -> float:
    """Convert frequency from wavenumbers (cm^-1) to meV."""
    return cm_inv * 0.12398419843320028


def mev_to_cm_inv(mev: float) -> float:
    """Convert frequency from meV to wavenumbers (cm^-1)."""
    return mev / 0.12398419843320028


# =============================================================================
# THERMODYNAMIC CONVERSIONS
# =============================================================================

def celsius_to_kelvin(celsius: float) -> float:
    """Convert temperature from Celsius to Kelvin."""
    return celsius + 273.15


def kelvin_to_celsius(kelvin: float) -> float:
    """Convert temperature from Kelvin to Celsius."""
    return kelvin - 273.15


def fahrenheit_to_kelvin(fahrenheit: float) -> float:
    """Convert temperature from Fahrenheit to Kelvin."""
    return (fahrenheit - 32.0) * 5.0 / 9.0 + 273.15


def kelvin_to_fahrenheit(kelvin: float) -> float:
    """Convert temperature from Kelvin to Fahrenheit."""
    return (kelvin - 273.15) * 9.0 / 5.0 + 32.0


def atm_to_pascal(atm: float) -> float:
    """Convert pressure from atmospheres to Pascal."""
    return atm * 101325.0


def pascal_to_atm(pascal: float) -> float:
    """Convert pressure from Pascal to atmospheres."""
    return pascal / 101325.0


def bar_to_pascal(bar: float) -> float:
    """Convert pressure from bar to Pascal."""
    return bar * 100000.0


def pascal_to_bar(pascal: float) -> float:
    """Convert pressure from Pascal to bar."""
    return pascal / 100000.0


# =============================================================================
# MASS CONVERSIONS
# =============================================================================

def amu_to_kg(amu: float) -> float:
    """Convert mass from atomic mass units to kilograms."""
    return amu * 1.66053906660e-27


def kg_to_amu(kg: float) -> float:
    """Convert mass from kilograms to atomic mass units."""
    return kg / 1.66053906660e-27


def amu_to_electron_mass(amu: float) -> float:
    """Convert mass from atomic mass units to electron masses."""
    return amu * 1822.888486209


def electron_mass_to_amu(me: float) -> float:
    """Convert mass from electron masses to atomic mass units."""
    return me / 1822.888486209


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_energy_unit_label(unit: EnergyUnit) -> str:
    """
    Get the standard label/symbol for an energy unit.
    
    Args:
        unit: The energy unit enum value.
        
    Returns:
        Standard string representation of the unit.
    """
    labels: dict[EnergyUnit, str] = {
        EnergyUnit.HARTREE: "E_h",
        EnergyUnit.EV: "eV",
        EnergyUnit.KCAL_MOL: "kcal/mol",
        EnergyUnit.KJ_MOL: "kJ/mol",
        EnergyUnit.CM_INV: "cm⁻¹",
        EnergyUnit.JOULE: "J",
        EnergyUnit.CAL: "cal",
        EnergyUnit.KELVIN: "K",
        EnergyUnit.MHZ: "MHz",
        EnergyUnit.HZ: "Hz",
    }
    return labels.get(unit, str(unit))


def get_length_unit_label(unit: LengthUnit) -> str:
    """
    Get the standard label/symbol for a length unit.
    
    Args:
        unit: The length unit enum value.
        
    Returns:
        Standard string representation of the unit.
    """
    labels: dict[LengthUnit, str] = {
        LengthUnit.BOHR: "a₀",
        LengthUnit.ANGSTROM: "Å",
        LengthUnit.NANOMETER: "nm",
        LengthUnit.PICOMETER: "pm",
        LengthUnit.METER: "m",
    }
    return labels.get(unit, str(unit))


def get_angle_unit_label(unit: AngleUnit) -> str:
    """
    Get the standard label/symbol for an angle unit.
    
    Args:
        unit: The angle unit enum value.
        
    Returns:
        Standard string representation of the unit.
    """
    labels: dict[AngleUnit, str] = {
        AngleUnit.RADIAN: "rad",
        AngleUnit.DEGREE: "°",
        AngleUnit.MILLIRADIAN: "mrad",
    }
    return labels.get(unit, str(unit))
