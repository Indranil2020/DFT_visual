"""
Physical constants, element data, and other shared constants for DFT Flight Simulator.

This module contains all constant data used across the application.
No computations, just data definitions.
"""

# ==================== PHYSICAL CONSTANTS ====================

# Conversion factors
BOHR_TO_ANGSTROM = 0.529177210903  # Bohr radius to Angstrom
ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM
HARTREE_TO_EV = 27.211386245988  # Hartree to electron volts
EV_TO_HARTREE = 1.0 / HARTREE_TO_EV
HARTREE_TO_KCAL_MOL = 627.509474  # Hartree to kcal/mol

# Fundamental constants
ELECTRON_MASS = 9.1093837015e-31  # kg
ELECTRON_CHARGE = 1.602176634e-19  # C
PLANCK_CONSTANT = 6.62607015e-34  # J⋅s
SPEED_OF_LIGHT = 299792458  # m/s

# ==================== ELEMENT DATA ====================

# Atomic numbers to symbols
ELEMENTS = {
    1: 'H', 2: 'He',
    3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar',
    19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn',
    26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
    37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc',
    44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd',
    49: 'In', 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe',
    55: 'Cs', 56: 'Ba', 57: 'La',
    72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn',
}

# Element full names
ELEMENT_NAMES = {
    1: 'Hydrogen', 2: 'Helium',
    3: 'Lithium', 4: 'Beryllium', 5: 'Boron', 6: 'Carbon', 7: 'Nitrogen', 8: 'Oxygen', 9: 'Fluorine', 10: 'Neon',
    11: 'Sodium', 12: 'Magnesium', 13: 'Aluminum', 14: 'Silicon', 15: 'Phosphorus', 16: 'Sulfur', 17: 'Chlorine', 18: 'Argon',
    19: 'Potassium', 20: 'Calcium', 21: 'Scandium', 22: 'Titanium', 23: 'Vanadium', 24: 'Chromium', 25: 'Manganese',
    26: 'Iron', 27: 'Cobalt', 28: 'Nickel', 29: 'Copper', 30: 'Zinc',
    31: 'Gallium', 32: 'Germanium', 33: 'Arsenic', 34: 'Selenium', 35: 'Bromine', 36: 'Krypton',
    37: 'Rubidium', 38: 'Strontium', 39: 'Yttrium', 40: 'Zirconium', 41: 'Niobium', 42: 'Molybdenum', 43: 'Technetium',
    44: 'Ruthenium', 45: 'Rhodium', 46: 'Palladium', 47: 'Silver', 48: 'Cadmium',
    49: 'Indium', 50: 'Tin', 51: 'Antimony', 52: 'Tellurium', 53: 'Iodine', 54: 'Xenon',
    55: 'Cesium', 56: 'Barium', 57: 'Lanthanum',
    72: 'Hafnium', 73: 'Tantalum', 74: 'Tungsten', 75: 'Rhenium', 76: 'Osmium', 77: 'Iridium', 78: 'Platinum', 79: 'Gold', 80: 'Mercury',
    81: 'Thallium', 82: 'Lead', 83: 'Bismuth', 84: 'Polonium', 85: 'Astatine', 86: 'Radon',
}

# Symbols to atomic numbers
ATOMIC_NUMBERS = {symbol: z for z, symbol in ELEMENTS.items()}

# Periodic table layout (for UI display)
PERIODIC_TABLE = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10],
    [11, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
    [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
    [55, 56, 57, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
]

# ==================== XC FUNCTIONAL DATA ====================

# Functional categories (Jacob's Ladder)
FUNCTIONAL_TYPES = {
    'LDA': {
        'functionals': ['SVWN', 'VWN', 'PZ', 'PW', 'VWN5'],
        'description': 'Local Density Approximation - depends only on density',
        'rung': 1,
        'cost': 'Very Fast'
    },
    'GGA': {
        'functionals': ['PBE', 'PW91', 'BLYP', 'B88', 'PBEsol', 'RPBE'],
        'description': 'Generalized Gradient Approximation - includes density gradient',
        'rung': 2,
        'cost': 'Fast'
    },
    'meta-GGA': {
        'functionals': ['TPSS', 'M06-L', 'SCAN', 'MN15-L'],
        'description': 'Meta-GGA - includes kinetic energy density',
        'rung': 3,
        'cost': 'Medium'
    },
    'Hybrid': {
        'functionals': ['B3LYP', 'PBE0', 'HSE06', 'M06', 'M06-2X'],
        'description': 'Hybrid - mixes exact exchange with DFT',
        'rung': 4,
        'cost': 'Slow'
    },
    'Double-Hybrid': {
        'functionals': ['B2PLYP', 'mPW2PLYP'],
        'description': 'Double-Hybrid - includes MP2 correlation',
        'rung': 5,
        'cost': 'Very Slow'
    }
}

# Detailed functional information
FUNCTIONAL_INFO = {
    # LDA
    'SVWN': {
        'name': 'Slater-Vosko-Wilk-Nusair',
        'type': 'LDA',
        'year': 1980,
        'description': 'Standard LDA functional',
        'reference': 'Can. J. Phys. 58, 1200 (1980)'
    },
    'VWN': {
        'name': 'Vosko-Wilk-Nusair',
        'type': 'LDA',
        'year': 1980,
        'description': 'LDA correlation functional',
        'reference': 'Can. J. Phys. 58, 1200 (1980)'
    },
    
    # GGA
    'PBE': {
        'name': 'Perdew-Burke-Ernzerhof',
        'type': 'GGA',
        'year': 1996,
        'description': 'Most popular GGA for solids and molecules',
        'reference': 'Phys. Rev. Lett. 77, 3865 (1996)',
        'parameters': {'kappa': 0.804, 'mu': 0.21951}
    },
    'PW91': {
        'name': 'Perdew-Wang 91',
        'type': 'GGA',
        'year': 1991,
        'description': 'Predecessor to PBE',
        'reference': 'Phys. Rev. B 46, 6671 (1992)'
    },
    'BLYP': {
        'name': 'Becke-Lee-Yang-Parr',
        'type': 'GGA',
        'year': 1988,
        'description': 'Popular for molecular systems',
        'reference': 'Phys. Rev. A 38, 3098 (1988)'
    },
    'B88': {
        'name': 'Becke 88',
        'type': 'GGA',
        'year': 1988,
        'description': 'Becke exchange functional',
        'reference': 'Phys. Rev. A 38, 3098 (1988)',
        'parameters': {'beta': 0.0042}
    },
    
    # Hybrid
    'B3LYP': {
        'name': 'Becke 3-parameter Lee-Yang-Parr',
        'type': 'Hybrid',
        'year': 1994,
        'description': 'Most popular hybrid functional for chemistry',
        'reference': 'J. Chem. Phys. 98, 5648 (1993)',
        'exact_exchange': 0.20
    },
    'PBE0': {
        'name': 'PBE0 (PBE1PBE)',
        'type': 'Hybrid',
        'year': 1999,
        'description': 'Hybrid version of PBE',
        'reference': 'J. Chem. Phys. 110, 6158 (1999)',
        'exact_exchange': 0.25
    },
    'HSE06': {
        'name': 'Heyd-Scuseria-Ernzerhof',
        'type': 'Hybrid',
        'year': 2006,
        'description': 'Range-separated hybrid, good for solids',
        'reference': 'J. Chem. Phys. 124, 219906 (2006)',
        'exact_exchange': 0.25,
        'screening': 0.11
    },
}

# ==================== PSEUDOPOTENTIAL DATA ====================

# Pseudopotential types
PSEUDO_TYPES = {
    'norm-conserving': {
        'description': 'Norm-conserving pseudopotentials',
        'accuracy': 'High',
        'cost': 'High (many plane waves needed)'
    },
    'ultrasoft': {
        'description': 'Ultrasoft pseudopotentials',
        'accuracy': 'Medium-High',
        'cost': 'Medium'
    },
    'PAW': {
        'description': 'Projector Augmented Wave',
        'accuracy': 'Very High',
        'cost': 'Medium-High'
    }
}

# PseudoDojo accuracy levels
PSEUDO_ACCURACY = {
    'standard': {
        'description': 'Standard accuracy (soft pseudopotentials)',
        'cutoff_range': '30-50 Ry',
        'use_case': 'Fast calculations, testing'
    },
    'stringent': {
        'description': 'Stringent accuracy (hard pseudopotentials)',
        'cutoff_range': '50-100 Ry',
        'use_case': 'Production calculations, publications'
    }
}

# ==================== BASIS SET DATA ====================

# Basis set families
BASIS_SET_FAMILIES = {
    'Pople': ['STO-3G', '3-21G', '6-31G', '6-31G*', '6-31G**', '6-311G', '6-311G*', '6-311G**'],
    'Dunning': ['cc-pVDZ', 'cc-pVTZ', 'cc-pVQZ', 'cc-pV5Z', 'aug-cc-pVDZ', 'aug-cc-pVTZ'],
    'Ahlrichs': ['def2-SVP', 'def2-TZVP', 'def2-QZVP', 'def2-TZVPP'],
    'Karlsruhe': ['def-SV(P)', 'def-TZVP', 'def-QZVP'],
}

# Zeta level descriptions
ZETA_DESCRIPTIONS = {
    'SZ': 'Single-Zeta - One basis function per orbital (minimal)',
    'DZ': 'Double-Zeta - Two basis functions per orbital',
    'TZ': 'Triple-Zeta - Three basis functions per orbital',
    'QZ': 'Quadruple-Zeta - Four basis functions per orbital',
    '5Z': 'Quintuple-Zeta - Five basis functions per orbital',
}

# ==================== ANGULAR MOMENTUM ====================

# Angular momentum quantum numbers
ANGULAR_MOMENTUM = {
    0: 's',
    1: 'p',
    2: 'd',
    3: 'f',
    4: 'g',
    5: 'h',
}

# Reverse mapping
ANGULAR_MOMENTUM_SYMBOLS = {v: k for k, v in ANGULAR_MOMENTUM.items()}

# Number of orbitals for each angular momentum
ORBITAL_COUNTS = {
    0: 1,   # s: 1 orbital
    1: 3,   # p: 3 orbitals (px, py, pz)
    2: 5,   # d: 5 orbitals
    3: 7,   # f: 7 orbitals
    4: 9,   # g: 9 orbitals
}

# ==================== UI COLORS ====================

# Color schemes for plots
PLOT_COLORS = {
    'primary': '#3b82f6',      # Blue
    'secondary': '#10b981',    # Green
    'accent': '#f59e0b',       # Orange
    'danger': '#ef4444',       # Red
    'info': '#06b6d4',         # Cyan
    'warning': '#f59e0b',      # Orange
    'success': '#10b981',      # Green
}

# Orbital colors
ORBITAL_COLORS = {
    's': '#3b82f6',   # Blue
    'p': '#10b981',   # Green
    'd': '#f59e0b',   # Orange
    'f': '#ef4444',   # Red
}

# ==================== EDUCATIONAL CONTENT ====================

# Key concepts for each module
MODULE_CONCEPTS = {
    'basis_sets': {
        'title': 'Basis Sets: The Input',
        'key_points': [
            'Basis sets define where electrons can be',
            'Larger basis sets = more accuracy = slower',
            'Polarization functions (*, **) add flexibility',
            'Diffuse functions (aug-) for anions and excited states'
        ]
    },
    'pseudopotentials': {
        'title': 'Pseudopotentials: The Core',
        'key_points': [
            'Replace -Z/r singularity with smooth potential',
            'Core electrons frozen, only valence electrons treated',
            'Pseudopotential must match XC functional used',
            'Standard = fast, Stringent = accurate'
        ]
    },
    'xc_functionals': {
        'title': 'XC Functionals: The Engine',
        'key_points': [
            'LDA: Local density only (fast, less accurate)',
            'GGA: Includes density gradient (better for molecules)',
            'Hybrid: Mixes exact exchange (best for chemistry)',
            'Higher rung = more accurate = more expensive'
        ]
    }
}

# ==================== EXPORT ====================

__all__ = [
    # Physical constants
    'BOHR_TO_ANGSTROM', 'ANGSTROM_TO_BOHR',
    'HARTREE_TO_EV', 'EV_TO_HARTREE',
    'HARTREE_TO_KCAL_MOL',
    
    # Elements
    'ELEMENTS', 'ELEMENT_NAMES', 'ATOMIC_NUMBERS',
    'PERIODIC_TABLE',
    
    # Functionals
    'FUNCTIONAL_TYPES', 'FUNCTIONAL_INFO',
    
    # Pseudopotentials
    'PSEUDO_TYPES', 'PSEUDO_ACCURACY',
    
    # Basis sets
    'BASIS_SET_FAMILIES', 'ZETA_DESCRIPTIONS',
    
    # Angular momentum
    'ANGULAR_MOMENTUM', 'ANGULAR_MOMENTUM_SYMBOLS', 'ORBITAL_COUNTS',
    
    # UI
    'PLOT_COLORS', 'ORBITAL_COLORS',
    
    # Educational
    'MODULE_CONCEPTS',
]
