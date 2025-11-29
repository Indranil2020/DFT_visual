"""
Physical and Chemical Constants for Quantum Chemistry Calculations.

This module provides fundamental physical constants, atomic data, and
conversion factors used throughout the Psi4 MCP server. All values are
from CODATA 2018 recommended values unless otherwise noted.

References:
    - CODATA 2018: https://physics.nist.gov/cuu/Constants/
    - Psi4 internal constants
    - IUPAC atomic weights 2021
"""

from typing import Final
import math


# =============================================================================
# FUNDAMENTAL PHYSICAL CONSTANTS (CODATA 2018)
# =============================================================================

# Speed of light in vacuum (m/s)
SPEED_OF_LIGHT: Final[float] = 299792458.0

# Planck constant (J·s)
PLANCK_CONSTANT: Final[float] = 6.62607015e-34

# Reduced Planck constant (J·s)
HBAR: Final[float] = PLANCK_CONSTANT / (2.0 * math.pi)

# Elementary charge (C)
ELEMENTARY_CHARGE: Final[float] = 1.602176634e-19

# Electron mass (kg)
ELECTRON_MASS: Final[float] = 9.1093837015e-31

# Proton mass (kg)
PROTON_MASS: Final[float] = 1.67262192369e-27

# Neutron mass (kg)
NEUTRON_MASS: Final[float] = 1.67492749804e-27

# Atomic mass unit (kg)
ATOMIC_MASS_UNIT: Final[float] = 1.66053906660e-27

# Avogadro constant (mol^-1)
AVOGADRO: Final[float] = 6.02214076e23

# Boltzmann constant (J/K)
BOLTZMANN: Final[float] = 1.380649e-23

# Molar gas constant (J/(mol·K))
GAS_CONSTANT: Final[float] = AVOGADRO * BOLTZMANN

# Vacuum permittivity (F/m)
VACUUM_PERMITTIVITY: Final[float] = 8.8541878128e-12

# Vacuum permeability (N/A^2)
VACUUM_PERMEABILITY: Final[float] = 1.25663706212e-6

# Fine-structure constant (dimensionless)
FINE_STRUCTURE: Final[float] = 7.2973525693e-3

# Bohr radius (m)
BOHR_RADIUS: Final[float] = 5.29177210903e-11

# Hartree energy (J)
HARTREE: Final[float] = 4.3597447222071e-18


# =============================================================================
# ATOMIC UNITS (used internally by Psi4)
# =============================================================================

# In atomic units, these quantities are defined as 1:
# - Electron mass (m_e = 1)
# - Elementary charge (e = 1)
# - Reduced Planck constant (ℏ = 1)
# - Coulomb constant (4πε₀ = 1)
# - Bohr radius (a₀ = 1)
# - Hartree energy (E_h = 1)

# Atomic unit of length (Bohr) in meters
AU_LENGTH: Final[float] = BOHR_RADIUS

# Atomic unit of energy (Hartree) in Joules
AU_ENERGY: Final[float] = HARTREE

# Atomic unit of time in seconds
AU_TIME: Final[float] = HBAR / HARTREE

# Atomic unit of electric dipole moment (e·a₀) in C·m
AU_DIPOLE: Final[float] = ELEMENTARY_CHARGE * BOHR_RADIUS

# Atomic unit of electric field (E_h/(e·a₀)) in V/m
AU_ELECTRIC_FIELD: Final[float] = HARTREE / (ELEMENTARY_CHARGE * BOHR_RADIUS)


# =============================================================================
# ENERGY CONVERSION FACTORS (from Hartree to other units)
# =============================================================================

# Hartree to eV
HARTREE_TO_EV: Final[float] = 27.211386245988

# Hartree to kJ/mol
HARTREE_TO_KJMOL: Final[float] = 2625.4996394799

# Hartree to kcal/mol
HARTREE_TO_KCALMOL: Final[float] = 627.5094740631

# Hartree to cm^-1 (wavenumbers)
HARTREE_TO_CM: Final[float] = 219474.63136320

# Hartree to MHz
HARTREE_TO_MHZ: Final[float] = 6.579683920502e9

# Hartree to Kelvin
HARTREE_TO_KELVIN: Final[float] = 315775.02480407

# Hartree to Joules
HARTREE_TO_JOULE: Final[float] = HARTREE

# Inverse conversions
EV_TO_HARTREE: Final[float] = 1.0 / HARTREE_TO_EV
KJMOL_TO_HARTREE: Final[float] = 1.0 / HARTREE_TO_KJMOL
KCALMOL_TO_HARTREE: Final[float] = 1.0 / HARTREE_TO_KCALMOL
CM_TO_HARTREE: Final[float] = 1.0 / HARTREE_TO_CM
MHZ_TO_HARTREE: Final[float] = 1.0 / HARTREE_TO_MHZ


# =============================================================================
# LENGTH CONVERSION FACTORS
# =============================================================================

# Bohr to Angstrom
BOHR_TO_ANGSTROM: Final[float] = 0.529177210903

# Angstrom to Bohr
ANGSTROM_TO_BOHR: Final[float] = 1.0 / BOHR_TO_ANGSTROM

# Bohr to nanometers
BOHR_TO_NM: Final[float] = BOHR_TO_ANGSTROM / 10.0

# Bohr to picometers
BOHR_TO_PM: Final[float] = BOHR_TO_ANGSTROM * 100.0


# =============================================================================
# DIPOLE MOMENT CONVERSION FACTORS
# =============================================================================

# Atomic units (e·a₀) to Debye
AU_TO_DEBYE: Final[float] = 2.541746473

# Debye to atomic units
DEBYE_TO_AU: Final[float] = 1.0 / AU_TO_DEBYE

# Debye to C·m
DEBYE_TO_CM: Final[float] = 3.33564e-30


# =============================================================================
# POLARIZABILITY CONVERSION FACTORS
# =============================================================================

# Atomic units to Angstrom^3
AU_TO_ANGSTROM3: Final[float] = BOHR_TO_ANGSTROM ** 3


# =============================================================================
# MASS CONVERSION FACTORS
# =============================================================================

# Atomic mass unit to electron masses
AMU_TO_ME: Final[float] = ATOMIC_MASS_UNIT / ELECTRON_MASS

# Electron mass to AMU
ME_TO_AMU: Final[float] = 1.0 / AMU_TO_ME


# =============================================================================
# TIME AND FREQUENCY CONVERSION FACTORS
# =============================================================================

# Atomic unit of time to femtoseconds
AU_TIME_TO_FS: Final[float] = AU_TIME * 1e15

# cm^-1 to Hz
CM_TO_HZ: Final[float] = SPEED_OF_LIGHT * 100.0

# cm^-1 to THz
CM_TO_THZ: Final[float] = CM_TO_HZ / 1e12


# =============================================================================
# THERMODYNAMIC CONSTANTS
# =============================================================================

# Standard temperature (K)
STANDARD_TEMPERATURE: Final[float] = 298.15

# Standard pressure (Pa)
STANDARD_PRESSURE: Final[float] = 101325.0

# Standard pressure (atm)
STANDARD_PRESSURE_ATM: Final[float] = 1.0

# Calorie to Joule
CALORIE_TO_JOULE: Final[float] = 4.184

# Joule to calorie
JOULE_TO_CALORIE: Final[float] = 1.0 / CALORIE_TO_JOULE


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================

# Pi (high precision)
PI: Final[float] = math.pi

# 2*Pi
TWO_PI: Final[float] = 2.0 * math.pi

# 4*Pi
FOUR_PI: Final[float] = 4.0 * math.pi

# Square root of 2
SQRT2: Final[float] = math.sqrt(2.0)

# Square root of 3
SQRT3: Final[float] = math.sqrt(3.0)

# Natural logarithm of 2
LN2: Final[float] = math.log(2.0)

# Natural logarithm of 10
LN10: Final[float] = math.log(10.0)


# =============================================================================
# ELEMENT DATA: ATOMIC NUMBERS
# =============================================================================

ATOMIC_NUMBERS: Final[dict[str, int]] = {
    "X": 0,    # Ghost atom
    "H": 1,    "He": 2,
    "Li": 3,   "Be": 4,   "B": 5,    "C": 6,    "N": 7,    "O": 8,    "F": 9,    "Ne": 10,
    "Na": 11,  "Mg": 12,  "Al": 13,  "Si": 14,  "P": 15,   "S": 16,   "Cl": 17,  "Ar": 18,
    "K": 19,   "Ca": 20,  "Sc": 21,  "Ti": 22,  "V": 23,   "Cr": 24,  "Mn": 25,  "Fe": 26,
    "Co": 27,  "Ni": 28,  "Cu": 29,  "Zn": 30,  "Ga": 31,  "Ge": 32,  "As": 33,  "Se": 34,
    "Br": 35,  "Kr": 36,  "Rb": 37,  "Sr": 38,  "Y": 39,   "Zr": 40,  "Nb": 41,  "Mo": 42,
    "Tc": 43,  "Ru": 44,  "Rh": 45,  "Pd": 46,  "Ag": 47,  "Cd": 48,  "In": 49,  "Sn": 50,
    "Sb": 51,  "Te": 52,  "I": 53,   "Xe": 54,  "Cs": 55,  "Ba": 56,  "La": 57,  "Ce": 58,
    "Pr": 59,  "Nd": 60,  "Pm": 61,  "Sm": 62,  "Eu": 63,  "Gd": 64,  "Tb": 65,  "Dy": 66,
    "Ho": 67,  "Er": 68,  "Tm": 69,  "Yb": 70,  "Lu": 71,  "Hf": 72,  "Ta": 73,  "W": 74,
    "Re": 75,  "Os": 76,  "Ir": 77,  "Pt": 78,  "Au": 79,  "Hg": 80,  "Tl": 81,  "Pb": 82,
    "Bi": 83,  "Po": 84,  "At": 85,  "Rn": 86,  "Fr": 87,  "Ra": 88,  "Ac": 89,  "Th": 90,
    "Pa": 91,  "U": 92,   "Np": 93,  "Pu": 94,  "Am": 95,  "Cm": 96,  "Bk": 97,  "Cf": 98,
    "Es": 99,  "Fm": 100, "Md": 101, "No": 102, "Lr": 103, "Rf": 104, "Db": 105, "Sg": 106,
    "Bh": 107, "Hs": 108, "Mt": 109, "Ds": 110, "Rg": 111, "Cn": 112, "Nh": 113, "Fl": 114,
    "Mc": 115, "Lv": 116, "Ts": 117, "Og": 118,
}

# Reverse mapping: atomic number to symbol
ELEMENT_SYMBOLS: Final[dict[int, str]] = {v: k for k, v in ATOMIC_NUMBERS.items()}


# =============================================================================
# ELEMENT DATA: ATOMIC MASSES (IUPAC 2021, in AMU)
# =============================================================================

ATOMIC_MASSES: Final[dict[str, float]] = {
    "X": 0.0,
    "H": 1.00794, "He": 4.002602,
    "Li": 6.941, "Be": 9.012182, "B": 10.811, "C": 12.0107, "N": 14.0067, 
    "O": 15.9994, "F": 18.9984032, "Ne": 20.1797,
    "Na": 22.98976928, "Mg": 24.305, "Al": 26.9815386, "Si": 28.0855, 
    "P": 30.973762, "S": 32.065, "Cl": 35.453, "Ar": 39.948,
    "K": 39.0983, "Ca": 40.078, "Sc": 44.955912, "Ti": 47.867, 
    "V": 50.9415, "Cr": 51.9961, "Mn": 54.938045, "Fe": 55.845,
    "Co": 58.933195, "Ni": 58.6934, "Cu": 63.546, "Zn": 65.38, 
    "Ga": 69.723, "Ge": 72.64, "As": 74.9216, "Se": 78.96,
    "Br": 79.904, "Kr": 83.798, "Rb": 85.4678, "Sr": 87.62, 
    "Y": 88.90585, "Zr": 91.224, "Nb": 92.90638, "Mo": 95.96,
    "Tc": 98.0, "Ru": 101.07, "Rh": 102.9055, "Pd": 106.42, 
    "Ag": 107.8682, "Cd": 112.411, "In": 114.818, "Sn": 118.71,
    "Sb": 121.76, "Te": 127.6, "I": 126.90447, "Xe": 131.293, 
    "Cs": 132.9054519, "Ba": 137.327, "La": 138.90547, "Ce": 140.116,
    "Pr": 140.90765, "Nd": 144.242, "Pm": 145.0, "Sm": 150.36, 
    "Eu": 151.964, "Gd": 157.25, "Tb": 158.92535, "Dy": 162.5,
    "Ho": 164.93032, "Er": 167.259, "Tm": 168.93421, "Yb": 173.054, 
    "Lu": 174.9668, "Hf": 178.49, "Ta": 180.94788, "W": 183.84,
    "Re": 186.207, "Os": 190.23, "Ir": 192.217, "Pt": 195.084, 
    "Au": 196.966569, "Hg": 200.59, "Tl": 204.3833, "Pb": 207.2,
    "Bi": 208.9804, "Po": 209.0, "At": 210.0, "Rn": 222.0, 
    "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.03806,
    "Pa": 231.03588, "U": 238.02891, "Np": 237.0, "Pu": 244.0, 
    "Am": 243.0, "Cm": 247.0, "Bk": 247.0, "Cf": 251.0,
    "Es": 252.0, "Fm": 257.0, "Md": 258.0, "No": 259.0, 
    "Lr": 262.0, "Rf": 267.0, "Db": 268.0, "Sg": 269.0,
    "Bh": 270.0, "Hs": 277.0, "Mt": 278.0, "Ds": 281.0, 
    "Rg": 282.0, "Cn": 285.0, "Nh": 286.0, "Fl": 289.0,
    "Mc": 290.0, "Lv": 293.0, "Ts": 294.0, "Og": 294.0,
}


# =============================================================================
# ELEMENT DATA: COVALENT RADII (in Angstrom, from Cordero et al. 2008)
# =============================================================================

COVALENT_RADII: Final[dict[str, float]] = {
    "H": 0.31, "He": 0.28,
    "Li": 1.28, "Be": 0.96, "B": 0.84, "C": 0.76, "N": 0.71, 
    "O": 0.66, "F": 0.57, "Ne": 0.58,
    "Na": 1.66, "Mg": 1.41, "Al": 1.21, "Si": 1.11, "P": 1.07, 
    "S": 1.05, "Cl": 1.02, "Ar": 1.06,
    "K": 2.03, "Ca": 1.76, "Sc": 1.70, "Ti": 1.60, "V": 1.53, 
    "Cr": 1.39, "Mn": 1.39, "Fe": 1.32,
    "Co": 1.26, "Ni": 1.24, "Cu": 1.32, "Zn": 1.22, "Ga": 1.22, 
    "Ge": 1.20, "As": 1.19, "Se": 1.20,
    "Br": 1.20, "Kr": 1.16, "Rb": 2.20, "Sr": 1.95, "Y": 1.90, 
    "Zr": 1.75, "Nb": 1.64, "Mo": 1.54,
    "Tc": 1.47, "Ru": 1.46, "Rh": 1.42, "Pd": 1.39, "Ag": 1.45, 
    "Cd": 1.44, "In": 1.42, "Sn": 1.39,
    "Sb": 1.39, "Te": 1.38, "I": 1.39, "Xe": 1.40, "Cs": 2.44, 
    "Ba": 2.15, "La": 2.07, "Ce": 2.04,
    "Pr": 2.03, "Nd": 2.01, "Pm": 1.99, "Sm": 1.98, "Eu": 1.98, 
    "Gd": 1.96, "Tb": 1.94, "Dy": 1.92,
    "Ho": 1.92, "Er": 1.89, "Tm": 1.90, "Yb": 1.87, "Lu": 1.87, 
    "Hf": 1.75, "Ta": 1.70, "W": 1.62,
    "Re": 1.51, "Os": 1.44, "Ir": 1.41, "Pt": 1.36, "Au": 1.36, 
    "Hg": 1.32, "Tl": 1.45, "Pb": 1.46,
    "Bi": 1.48, "Po": 1.40, "At": 1.50, "Rn": 1.50, "Fr": 2.60, 
    "Ra": 2.21, "Ac": 2.15, "Th": 2.06,
    "Pa": 2.00, "U": 1.96, "Np": 1.90, "Pu": 1.87, "Am": 1.80, 
    "Cm": 1.69,
}


# =============================================================================
# ELEMENT DATA: VAN DER WAALS RADII (in Angstrom, from Bondi 1964 / Mantina 2009)
# =============================================================================

VDW_RADII: Final[dict[str, float]] = {
    "H": 1.20, "He": 1.40,
    "Li": 1.82, "Be": 1.53, "B": 1.92, "C": 1.70, "N": 1.55, 
    "O": 1.52, "F": 1.47, "Ne": 1.54,
    "Na": 2.27, "Mg": 1.73, "Al": 1.84, "Si": 2.10, "P": 1.80, 
    "S": 1.80, "Cl": 1.75, "Ar": 1.88,
    "K": 2.75, "Ca": 2.31, "Ga": 1.87, "Ge": 2.11, "As": 1.85, 
    "Se": 1.90, "Br": 1.85, "Kr": 2.02,
    "Rb": 3.03, "Sr": 2.49, "In": 1.93, "Sn": 2.17, "Sb": 2.06, 
    "Te": 2.06, "I": 1.98, "Xe": 2.16,
    "Cs": 3.43, "Ba": 2.68, "Tl": 1.96, "Pb": 2.02, "Bi": 2.07, 
    "Po": 1.97, "At": 2.02, "Rn": 2.20,
}


# =============================================================================
# ELEMENT GROUPS AND PERIODS
# =============================================================================

# Main group elements
MAIN_GROUP_ELEMENTS: Final[frozenset[str]] = frozenset({
    "H", "He",
    "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
    "K", "Ca", "Ga", "Ge", "As", "Se", "Br", "Kr",
    "Rb", "Sr", "In", "Sn", "Sb", "Te", "I", "Xe",
    "Cs", "Ba", "Tl", "Pb", "Bi", "Po", "At", "Rn",
    "Fr", "Ra", "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
})

# Transition metals
TRANSITION_METALS: Final[frozenset[str]] = frozenset({
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
    "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn",
})

# Lanthanides
LANTHANIDES: Final[frozenset[str]] = frozenset({
    "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", 
    "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu",
})

# Actinides
ACTINIDES: Final[frozenset[str]] = frozenset({
    "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", 
    "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr",
})

# Noble gases
NOBLE_GASES: Final[frozenset[str]] = frozenset({
    "He", "Ne", "Ar", "Kr", "Xe", "Rn", "Og",
})

# Halogens
HALOGENS: Final[frozenset[str]] = frozenset({
    "F", "Cl", "Br", "I", "At", "Ts",
})


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_atomic_number(symbol: str) -> int:
    """
    Get the atomic number for an element symbol.
    
    Args:
        symbol: Element symbol (case-insensitive, e.g., "H", "he", "Fe").
        
    Returns:
        Atomic number, or -1 if symbol is not recognized.
    """
    # Normalize: capitalize first letter, lowercase rest
    normalized = symbol.capitalize()
    return ATOMIC_NUMBERS.get(normalized, -1)


def get_element_symbol(atomic_number: int) -> str:
    """
    Get the element symbol for an atomic number.
    
    Args:
        atomic_number: The atomic number (1-118).
        
    Returns:
        Element symbol, or empty string if not found.
    """
    return ELEMENT_SYMBOLS.get(atomic_number, "")


def get_atomic_mass(symbol: str) -> float:
    """
    Get the atomic mass for an element symbol in AMU.
    
    Args:
        symbol: Element symbol (case-insensitive).
        
    Returns:
        Atomic mass in AMU, or 0.0 if symbol is not recognized.
    """
    normalized = symbol.capitalize()
    return ATOMIC_MASSES.get(normalized, 0.0)


def get_covalent_radius(symbol: str) -> float:
    """
    Get the covalent radius for an element symbol in Angstrom.
    
    Args:
        symbol: Element symbol (case-insensitive).
        
    Returns:
        Covalent radius in Angstrom, or 0.0 if not available.
    """
    normalized = symbol.capitalize()
    return COVALENT_RADII.get(normalized, 0.0)


def get_vdw_radius(symbol: str) -> float:
    """
    Get the van der Waals radius for an element symbol in Angstrom.
    
    Args:
        symbol: Element symbol (case-insensitive).
        
    Returns:
        Van der Waals radius in Angstrom, or 0.0 if not available.
    """
    normalized = symbol.capitalize()
    return VDW_RADII.get(normalized, 0.0)


def is_valid_element(symbol: str) -> bool:
    """
    Check if a string is a valid element symbol.
    
    Args:
        symbol: String to check.
        
    Returns:
        True if valid element symbol, False otherwise.
    """
    normalized = symbol.capitalize()
    return normalized in ATOMIC_NUMBERS


def mass_to_atomic_units(mass_amu: float) -> float:
    """
    Convert mass from AMU to atomic units (electron masses).
    
    Args:
        mass_amu: Mass in atomic mass units.
        
    Returns:
        Mass in atomic units (electron masses).
    """
    return mass_amu * AMU_TO_ME
