"""
Basis Set Enumerations for Quantum Chemistry Calculations.

This module defines comprehensive enumerations for basis sets used in
quantum chemistry calculations. Basis sets are organized by family
(Pople, Dunning, Karlsruhe, etc.) and include metadata about their
properties and recommended usage.

Basis Set Families:
    - Pople: 3-21G, 6-31G, 6-311G with polarization/diffuse functions
    - Dunning: Correlation-consistent cc-pVXZ series
    - Karlsruhe: def2 series (SVP, TZVP, QZVP)
    - ANO: Atomic Natural Orbital basis sets
    - Auxiliary: Density fitting and RI basis sets
"""

from enum import Enum
from typing import Final


class BasisSetFamily(str, Enum):
    """
    High-level classification of basis set families.
    
    Attributes:
        MINIMAL: Minimal basis sets (STO-nG)
        POPLE: Split-valence Pople basis sets
        DUNNING: Correlation-consistent Dunning basis sets
        KARLSRUHE: Ahlrichs/Karlsruhe def2 basis sets
        JENSEN: Polarization-consistent Jensen basis sets
        ANO: Atomic Natural Orbital basis sets
        AUXILIARY: Auxiliary basis sets for DF/RI
        EFFECTIVE_CORE: Effective core potentials (ECPs)
        CUSTOM: User-defined or other basis sets
    """
    MINIMAL = "minimal"
    POPLE = "pople"
    DUNNING = "dunning"
    KARLSRUHE = "karlsruhe"
    JENSEN = "jensen"
    ANO = "ano"
    AUXILIARY = "auxiliary"
    EFFECTIVE_CORE = "ecp"
    CUSTOM = "custom"


class BasisSetSize(str, Enum):
    """
    Classification of basis set size/quality.
    
    Attributes:
        MINIMAL: Minimal basis (STO-3G level)
        SMALL: Small double-zeta (3-21G, 6-31G level)
        MEDIUM: Double-zeta with polarization (6-31G*, cc-pVDZ)
        LARGE: Triple-zeta (6-311G**, cc-pVTZ, def2-TZVP)
        VERY_LARGE: Quadruple-zeta (cc-pVQZ, def2-QZVP)
        HUGE: Quintuple-zeta and beyond (cc-pV5Z, cc-pV6Z)
    """
    MINIMAL = "minimal"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"
    HUGE = "huge"


class MinimalBasis(str, Enum):
    """
    Minimal basis sets (Slater-type orbital approximations).
    
    These are small basis sets primarily used for quick preliminary
    calculations or educational purposes.
    """
    STO_3G = "sto-3g"
    STO_4G = "sto-4g"
    STO_6G = "sto-6g"
    MINIX = "minix"
    MINI = "mini"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value


class PopleBasis(str, Enum):
    """
    Pople-style split-valence basis sets.
    
    Naming convention:
        - Base: 3-21G, 6-31G, 6-311G
        - Polarization: * or (d) for heavy atoms, ** or (d,p) includes H
        - Diffuse: + for heavy atoms, ++ includes H
    """
    # 3-21G series
    G3_21 = "3-21g"
    G3_21_D = "3-21g*"
    G3_21_DP = "3-21g**"
    
    # 6-31G series
    G6_31 = "6-31g"
    G6_31_D = "6-31g*"
    G6_31_DP = "6-31g**"
    G6_31_PLUS_D = "6-31+g*"
    G6_31_PLUS_DP = "6-31+g**"
    G6_31_PLUSPLUS_D = "6-31++g*"
    G6_31_PLUSPLUS_DP = "6-31++g**"
    G6_31_2D = "6-31g(2d)"
    G6_31_2DF = "6-31g(2df)"
    G6_31_2DF_2P = "6-31g(2df,2p)"
    G6_31_3DF_3PD = "6-31g(3df,3pd)"
    
    # 6-311G series
    G6_311 = "6-311g"
    G6_311_D = "6-311g*"
    G6_311_DP = "6-311g**"
    G6_311_PLUS_D = "6-311+g*"
    G6_311_PLUS_DP = "6-311+g**"
    G6_311_PLUSPLUS_D = "6-311++g*"
    G6_311_PLUSPLUS_DP = "6-311++g**"
    G6_311_2D = "6-311g(2d)"
    G6_311_2DF = "6-311g(2df)"
    G6_311_2DF_2P = "6-311g(2df,2p)"
    G6_311_3DF_3PD = "6-311g(3df,3pd)"
    G6_311_PLUSPLUS_3DF_3PD = "6-311++g(3df,3pd)"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value
    
    def has_diffuse(self) -> bool:
        """Check if this basis includes diffuse functions."""
        return "+" in self.value
    
    def has_polarization(self) -> bool:
        """Check if this basis includes polarization functions."""
        return "*" in self.value or "(" in self.value


class DunningBasis(str, Enum):
    """
    Dunning correlation-consistent basis sets.
    
    These basis sets are designed for systematic convergence to the
    complete basis set (CBS) limit and are recommended for correlated
    calculations (MP2, CCSD, etc.).
    
    Naming convention:
        - cc-pVXZ: Correlation-consistent polarized Valence X-Zeta
        - aug-: Augmented with diffuse functions
        - d-: Doubly augmented
        - core/all-electron variants with tight functions
    """
    # Standard cc-pVXZ
    CC_PVDZ = "cc-pvdz"
    CC_PVTZ = "cc-pvtz"
    CC_PVQZ = "cc-pvqz"
    CC_PV5Z = "cc-pv5z"
    CC_PV6Z = "cc-pv6z"
    
    # Augmented (diffuse functions)
    AUG_CC_PVDZ = "aug-cc-pvdz"
    AUG_CC_PVTZ = "aug-cc-pvtz"
    AUG_CC_PVQZ = "aug-cc-pvqz"
    AUG_CC_PV5Z = "aug-cc-pv5z"
    AUG_CC_PV6Z = "aug-cc-pv6z"
    
    # Doubly augmented
    D_AUG_CC_PVDZ = "d-aug-cc-pvdz"
    D_AUG_CC_PVTZ = "d-aug-cc-pvtz"
    D_AUG_CC_PVQZ = "d-aug-cc-pvqz"
    
    # Core-valence (tight functions for core correlation)
    CC_PCVDZ = "cc-pcvdz"
    CC_PCVTZ = "cc-pcvtz"
    CC_PCVQZ = "cc-pcvqz"
    CC_PCV5Z = "cc-pcv5z"
    
    # Augmented core-valence
    AUG_CC_PCVDZ = "aug-cc-pcvdz"
    AUG_CC_PCVTZ = "aug-cc-pcvtz"
    AUG_CC_PCVQZ = "aug-cc-pcvqz"
    
    # Weighted core-valence
    CC_PWCVDZ = "cc-pwcvdz"
    CC_PWCVTZ = "cc-pwcvtz"
    CC_PWCVQZ = "cc-pwcvqz"
    CC_PWCV5Z = "cc-pwcv5z"
    
    AUG_CC_PWCVDZ = "aug-cc-pwcvdz"
    AUG_CC_PWCVTZ = "aug-cc-pwcvtz"
    AUG_CC_PWCVQZ = "aug-cc-pwcvqz"
    
    # Heavy elements (with ECP)
    CC_PVDZ_PP = "cc-pvdz-pp"
    CC_PVTZ_PP = "cc-pvtz-pp"
    CC_PVQZ_PP = "cc-pvqz-pp"
    
    AUG_CC_PVDZ_PP = "aug-cc-pvdz-pp"
    AUG_CC_PVTZ_PP = "aug-cc-pvtz-pp"
    AUG_CC_PVQZ_PP = "aug-cc-pvqz-pp"
    
    # F12 explicit correlation
    CC_PVDZ_F12 = "cc-pvdz-f12"
    CC_PVTZ_F12 = "cc-pvtz-f12"
    CC_PVQZ_F12 = "cc-pvqz-f12"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value
    
    def get_zeta_level(self) -> int:
        """Get the zeta level (D=2, T=3, Q=4, 5, 6)."""
        value_lower = self.value.lower()
        if "pvdz" in value_lower:
            return 2
        elif "pvtz" in value_lower:
            return 3
        elif "pvqz" in value_lower:
            return 4
        elif "pv5z" in value_lower:
            return 5
        elif "pv6z" in value_lower:
            return 6
        return 0
    
    def has_diffuse(self) -> bool:
        """Check if this basis includes diffuse functions."""
        return "aug" in self.value.lower()
    
    def has_core_functions(self) -> bool:
        """Check if this basis has core correlation functions."""
        return "cv" in self.value.lower()


class KarlsruheBasis(str, Enum):
    """
    Karlsruhe (Ahlrichs) def2 basis sets.
    
    These basis sets are efficient and well-balanced, recommended for
    DFT and general-purpose calculations. They have good coverage of
    the periodic table including heavy elements.
    
    Naming convention:
        - def2-SVP: Split-valence + polarization
        - def2-TZVP: Triple-zeta valence + polarization
        - def2-QZVP: Quadruple-zeta valence + polarization
        - D: Diffuse functions added
    """
    # def2 series
    DEF2_SV_P = "def2-sv(p)"
    DEF2_SVP = "def2-svp"
    DEF2_SVPD = "def2-svpd"
    DEF2_TZVP = "def2-tzvp"
    DEF2_TZVPD = "def2-tzvpd"
    DEF2_TZVPP = "def2-tzvpp"
    DEF2_TZVPPD = "def2-tzvppd"
    DEF2_QZVP = "def2-qzvp"
    DEF2_QZVPD = "def2-qzvpd"
    DEF2_QZVPP = "def2-qzvpp"
    DEF2_QZVPPD = "def2-qzvppd"
    
    # Older def series (for reference)
    DEF_SVP = "def-svp"
    DEF_TZVP = "def-tzvp"
    DEF_QZVP = "def-qzvp"
    
    # DKH relativistic versions
    DEF2_SVP_DKH = "def2-svp-dk"
    DEF2_TZVP_DKH = "def2-tzvp-dk"
    DEF2_QZVP_DKH = "def2-qzvp-dk"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value
    
    def has_diffuse(self) -> bool:
        """Check if this basis includes diffuse functions."""
        return self.value.endswith("d") or self.value.endswith("d-dk")


class JensenBasis(str, Enum):
    """
    Jensen polarization-consistent basis sets.
    
    These basis sets are optimized for DFT calculations and provide
    systematic convergence for DFT energies and properties.
    """
    PC_0 = "pc-0"
    PC_1 = "pc-1"
    PC_2 = "pc-2"
    PC_3 = "pc-3"
    PC_4 = "pc-4"
    
    AUG_PC_0 = "aug-pc-0"
    AUG_PC_1 = "aug-pc-1"
    AUG_PC_2 = "aug-pc-2"
    AUG_PC_3 = "aug-pc-3"
    AUG_PC_4 = "aug-pc-4"
    
    PCSSEG_0 = "pcseg-0"
    PCSSEG_1 = "pcseg-1"
    PCSSEG_2 = "pcseg-2"
    PCSSEG_3 = "pcseg-3"
    PCSSEG_4 = "pcseg-4"
    
    AUG_PCSSEG_0 = "aug-pcseg-0"
    AUG_PCSSEG_1 = "aug-pcseg-1"
    AUG_PCSSEG_2 = "aug-pcseg-2"
    AUG_PCSSEG_3 = "aug-pcseg-3"
    AUG_PCSSEG_4 = "aug-pcseg-4"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value


class AuxiliaryBasis(str, Enum):
    """
    Auxiliary basis sets for density fitting (DF) and resolution
    of identity (RI) approximations.
    
    These basis sets are used to speed up calculations by approximating
    four-center integrals with three-center integrals.
    """
    # Coulomb fitting (J)
    DEF2_UNIVERSAL_JFIT = "def2-universal-jfit"
    
    # JK fitting (Coulomb + Exchange)
    DEF2_SVP_JKFIT = "def2-svp-jkfit"
    DEF2_TZVP_JKFIT = "def2-tzvp-jkfit"
    DEF2_QZVP_JKFIT = "def2-qzvp-jkfit"
    
    CC_PVDZ_JKFIT = "cc-pvdz-jkfit"
    CC_PVTZ_JKFIT = "cc-pvtz-jkfit"
    CC_PVQZ_JKFIT = "cc-pvqz-jkfit"
    
    AUG_CC_PVDZ_JKFIT = "aug-cc-pvdz-jkfit"
    AUG_CC_PVTZ_JKFIT = "aug-cc-pvtz-jkfit"
    AUG_CC_PVQZ_JKFIT = "aug-cc-pvqz-jkfit"
    
    # RI/MP2 fitting
    DEF2_SVP_RIFIT = "def2-svp-rifit"
    DEF2_TZVP_RIFIT = "def2-tzvp-rifit"
    DEF2_TZVPP_RIFIT = "def2-tzvpp-rifit"
    DEF2_QZVP_RIFIT = "def2-qzvp-rifit"
    DEF2_QZVPP_RIFIT = "def2-qzvpp-rifit"
    
    CC_PVDZ_RI = "cc-pvdz-ri"
    CC_PVTZ_RI = "cc-pvtz-ri"
    CC_PVQZ_RI = "cc-pvqz-ri"
    CC_PV5Z_RI = "cc-pv5z-ri"
    
    AUG_CC_PVDZ_RI = "aug-cc-pvdz-ri"
    AUG_CC_PVTZ_RI = "aug-cc-pvtz-ri"
    AUG_CC_PVQZ_RI = "aug-cc-pvqz-ri"
    
    # CABS for F12
    CC_PVDZ_F12_OPTRI = "cc-pvdz-f12-optri"
    CC_PVTZ_F12_OPTRI = "cc-pvtz-f12-optri"
    CC_PVQZ_F12_OPTRI = "cc-pvqz-f12-optri"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value
    
    def get_fitting_type(self) -> str:
        """Get the type of fitting (J, JK, RI, etc.)."""
        value_lower = self.value.lower()
        if "jkfit" in value_lower:
            return "jkfit"
        elif "jfit" in value_lower:
            return "jfit"
        elif "rifit" in value_lower or "-ri" in value_lower:
            return "rifit"
        elif "optri" in value_lower or "cabs" in value_lower:
            return "cabs"
        return "unknown"


class ECPBasis(str, Enum):
    """
    Effective Core Potential (ECP) basis sets.
    
    ECPs replace inner core electrons with a pseudopotential, reducing
    computational cost for heavy elements while including scalar
    relativistic effects.
    """
    # Stuttgart ECPs
    STUTTGART_RSC = "stuttgart-rsc"
    STUTTGART_RSC_1997 = "stuttgart-rsc-1997"
    
    # LANL series
    LANL2DZ = "lanl2dz"
    LANL2TZ = "lanl2tz"
    LANL2TZ_F = "lanl2tz(f)"
    LANL08 = "lanl08"
    LANL08_F = "lanl08(f)"
    LANL08_D = "lanl08(d)"
    
    # CRENBL
    CRENBL = "crenbl"
    CRENBS = "crenbs"
    
    # SDD
    SDD = "sdd"
    SDD_ALL = "sdd-all"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value


# =============================================================================
# UNIFIED BASIS SET TYPE
# =============================================================================

class BasisSet(str, Enum):
    """
    Common basis sets across all families for easy access.
    
    This provides quick access to the most commonly used basis sets.
    """
    # Minimal
    STO_3G = "sto-3g"
    
    # Pople (common)
    G6_31G_D = "6-31g*"
    G6_31G_DP = "6-31g**"
    G6_311G_DP = "6-311g**"
    G6_311_PLUS_G_DP = "6-311+g**"
    G6_311_PLUSPLUS_G_DP = "6-311++g**"
    
    # Dunning (common)
    CC_PVDZ = "cc-pvdz"
    CC_PVTZ = "cc-pvtz"
    CC_PVQZ = "cc-pvqz"
    AUG_CC_PVDZ = "aug-cc-pvdz"
    AUG_CC_PVTZ = "aug-cc-pvtz"
    AUG_CC_PVQZ = "aug-cc-pvqz"
    
    # Karlsruhe (common)
    DEF2_SVP = "def2-svp"
    DEF2_TZVP = "def2-tzvp"
    DEF2_TZVPP = "def2-tzvpp"
    DEF2_QZVP = "def2-qzvp"
    DEF2_QZVPP = "def2-qzvpp"
    
    def to_psi4_basis(self) -> str:
        """Convert to Psi4 basis string."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> "BasisSet":
        """
        Create a BasisSet from a string (case-insensitive).
        
        Args:
            value: String name of the basis set.
            
        Returns:
            Corresponding BasisSet enum, or CC_PVDZ if not found.
        """
        normalized = value.lower().strip()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.CC_PVDZ
    
    def get_family(self) -> BasisSetFamily:
        """Get the basis set family."""
        value_lower = self.value.lower()
        
        if value_lower.startswith("sto"):
            return BasisSetFamily.MINIMAL
        elif any(value_lower.startswith(p) for p in ["3-21", "6-31", "6-311"]):
            return BasisSetFamily.POPLE
        elif "cc-p" in value_lower:
            return BasisSetFamily.DUNNING
        elif value_lower.startswith("def"):
            return BasisSetFamily.KARLSRUHE
        elif value_lower.startswith("pc"):
            return BasisSetFamily.JENSEN
        else:
            return BasisSetFamily.CUSTOM
    
    def get_size_category(self) -> BasisSetSize:
        """Get the size category of the basis set."""
        value_lower = self.value.lower()
        
        if value_lower == "sto-3g":
            return BasisSetSize.MINIMAL
        elif "svp" in value_lower or "pvdz" in value_lower or "6-31g" in value_lower:
            return BasisSetSize.MEDIUM
        elif "tzvp" in value_lower or "pvtz" in value_lower or "6-311g" in value_lower:
            return BasisSetSize.LARGE
        elif "qzvp" in value_lower or "pvqz" in value_lower:
            return BasisSetSize.VERY_LARGE
        elif "pv5z" in value_lower or "pv6z" in value_lower:
            return BasisSetSize.HUGE
        else:
            return BasisSetSize.MEDIUM


# =============================================================================
# BASIS SET RECOMMENDATIONS
# =============================================================================

# Recommended basis sets by method type
RECOMMENDED_BASIS: Final[dict[str, list[str]]] = {
    "hf": ["cc-pvtz", "def2-tzvp", "6-311g**"],
    "dft": ["def2-tzvp", "cc-pvtz", "6-311+g**"],
    "mp2": ["cc-pvtz", "aug-cc-pvtz", "def2-tzvpp"],
    "ccsd": ["cc-pvtz", "aug-cc-pvtz", "cc-pvqz"],
    "ccsd(t)": ["cc-pvtz", "aug-cc-pvtz", "cc-pvqz"],
    "sapt": ["aug-cc-pvdz", "aug-cc-pvtz", "jun-cc-pvdz"],
    "tddft": ["def2-tzvp", "6-311+g**", "aug-cc-pvtz"],
    "nmr": ["pcsseg-2", "aug-cc-pvtz-j", "6-311+g(2d,p)"],
}

# Minimum recommended basis by method
MINIMUM_BASIS: Final[dict[str, str]] = {
    "hf": "6-31g*",
    "dft": "def2-svp",
    "mp2": "cc-pvdz",
    "ccsd": "cc-pvdz",
    "ccsd(t)": "cc-pvdz",
    "sapt": "aug-cc-pvdz",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_matching_auxiliary_basis(
    orbital_basis: str, 
    fitting_type: str = "rifit"
) -> str:
    """
    Get a matching auxiliary basis for a given orbital basis.
    
    Args:
        orbital_basis: Name of the orbital basis set.
        fitting_type: Type of fitting ("jkfit", "rifit", or "jfit").
        
    Returns:
        Name of the recommended auxiliary basis, or empty string if none found.
    """
    basis_lower = orbital_basis.lower()
    
    # Mapping of orbital to auxiliary basis
    aux_mapping: dict[str, dict[str, str]] = {
        "cc-pvdz": {
            "jkfit": "cc-pvdz-jkfit",
            "rifit": "cc-pvdz-ri",
            "jfit": "def2-universal-jfit",
        },
        "cc-pvtz": {
            "jkfit": "cc-pvtz-jkfit",
            "rifit": "cc-pvtz-ri",
            "jfit": "def2-universal-jfit",
        },
        "cc-pvqz": {
            "jkfit": "cc-pvqz-jkfit",
            "rifit": "cc-pvqz-ri",
            "jfit": "def2-universal-jfit",
        },
        "aug-cc-pvdz": {
            "jkfit": "aug-cc-pvdz-jkfit",
            "rifit": "aug-cc-pvdz-ri",
            "jfit": "def2-universal-jfit",
        },
        "aug-cc-pvtz": {
            "jkfit": "aug-cc-pvtz-jkfit",
            "rifit": "aug-cc-pvtz-ri",
            "jfit": "def2-universal-jfit",
        },
        "def2-svp": {
            "jkfit": "def2-svp-jkfit",
            "rifit": "def2-svp-rifit",
            "jfit": "def2-universal-jfit",
        },
        "def2-tzvp": {
            "jkfit": "def2-tzvp-jkfit",
            "rifit": "def2-tzvp-rifit",
            "jfit": "def2-universal-jfit",
        },
        "def2-qzvp": {
            "jkfit": "def2-qzvp-jkfit",
            "rifit": "def2-qzvp-rifit",
            "jfit": "def2-universal-jfit",
        },
    }
    
    if basis_lower in aux_mapping:
        return aux_mapping[basis_lower].get(fitting_type, "")
    
    # Default fallback
    return "def2-universal-jfit" if fitting_type == "jfit" else ""


def estimate_basis_functions(
    basis_name: str, 
    n_atoms: int, 
    avg_atomic_number: float = 6.0
) -> int:
    """
    Estimate the number of basis functions for a calculation.
    
    This provides a rough estimate useful for memory/resource planning.
    
    Args:
        basis_name: Name of the basis set.
        n_atoms: Number of atoms in the molecule.
        avg_atomic_number: Average atomic number (default ~carbon).
        
    Returns:
        Estimated number of basis functions.
    """
    # Approximate basis functions per atom for different basis qualities
    # These are rough estimates for typical organic molecules
    basis_lower = basis_name.lower()
    
    if "sto-3g" in basis_lower:
        funcs_per_atom = 5
    elif "6-31g*" in basis_lower or "def2-svp" in basis_lower or "pvdz" in basis_lower:
        funcs_per_atom = 15
    elif "6-311g**" in basis_lower or "def2-tzvp" in basis_lower or "pvtz" in basis_lower:
        funcs_per_atom = 30
    elif "def2-qzvp" in basis_lower or "pvqz" in basis_lower:
        funcs_per_atom = 55
    elif "pv5z" in basis_lower:
        funcs_per_atom = 90
    else:
        funcs_per_atom = 20  # Default estimate
    
    # Adjust for augmented basis sets
    if "aug" in basis_lower or "++" in basis_lower:
        funcs_per_atom = int(funcs_per_atom * 1.4)
    elif "+" in basis_lower:
        funcs_per_atom = int(funcs_per_atom * 1.2)
    
    # Scale with atomic number (heavier atoms have more basis functions)
    scale_factor = 1.0 + 0.02 * (avg_atomic_number - 6.0)
    
    return int(n_atoms * funcs_per_atom * scale_factor)


def validate_basis_for_elements(
    basis_name: str, 
    element_symbols: list[str]
) -> tuple[bool, list[str]]:
    """
    Check if a basis set is defined for all elements in a molecule.
    
    Args:
        basis_name: Name of the basis set.
        element_symbols: List of element symbols in the molecule.
        
    Returns:
        Tuple of (is_valid, list of unsupported elements).
    """
    # Define element coverage for common basis set families
    # This is a simplified version - real validation should query Psi4
    
    basis_lower = basis_name.lower()
    
    # Pople bases typically cover H-Kr
    pople_elements = {
        "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
        "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
        "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
        "Ga", "Ge", "As", "Se", "Br", "Kr"
    }
    
    # def2 bases cover most of periodic table
    def2_elements = pople_elements | {
        "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
        "In", "Sn", "Sb", "Te", "I", "Xe",
        "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
        "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt",
        "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn"
    }
    
    # Determine supported elements based on basis family
    if any(p in basis_lower for p in ["6-31", "6-311", "3-21"]):
        supported = pople_elements
    elif "def2" in basis_lower:
        supported = def2_elements
    elif "cc-p" in basis_lower:
        # Dunning bases vary - assume at least main group supported
        supported = def2_elements
    else:
        # Assume all elements for unknown bases
        supported = def2_elements
    
    unsupported = [e for e in element_symbols if e not in supported]
    
    return (len(unsupported) == 0, unsupported)
