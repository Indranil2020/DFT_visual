"""
Basis Set Format Conversion Utilities.

This module provides functions for working with basis set specifications,
including parsing, validation, and format conversion.

Key Features:
    - Parse basis set names and aliases
    - Generate basis set specifications for Psi4
    - Handle mixed basis set specifications
    - Auxiliary basis set matching
"""

from typing import Optional, Sequence
from dataclasses import dataclass, field
from enum import Enum

from psi4_mcp.models.enums.basis_sets import (
    BasisSet,
    BasisSetFamily,
    DunningBasis,
    KarlsruheBasis,
    PopleBasis,
    AuxiliaryBasis,
    get_matching_auxiliary_basis,
)
from psi4_mcp.utils.helpers.constants import ATOMIC_NUMBERS


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class BasisSetSpecification:
    """
    Specification for a basis set, possibly with per-element overrides.
    
    Attributes:
        default_basis: Default basis set for all elements.
        element_basis: Dictionary mapping elements to specific basis sets.
        auxiliary_basis: Auxiliary basis for density fitting.
        auxiliary_type: Type of auxiliary basis (jkfit, rifit, etc.).
    """
    default_basis: str
    element_basis: dict[str, str] = field(default_factory=dict)
    auxiliary_basis: Optional[str] = None
    auxiliary_type: Optional[str] = None
    
    def get_basis_for_element(self, element: str) -> str:
        """Get the basis set for a specific element."""
        element_upper = element.upper() if len(element) == 1 else element.capitalize()
        return self.element_basis.get(element_upper, self.default_basis)
    
    def to_psi4_dict(self) -> dict[str, str]:
        """
        Convert to Psi4 basis specification dictionary.
        
        Returns:
            Dictionary suitable for psi4.set_options().
        """
        result: dict[str, str] = {"basis": self.default_basis}
        
        # Add element-specific bases
        for element, basis in self.element_basis.items():
            # Psi4 uses format like "basis_h" for hydrogen
            key = f"basis_{element.lower()}"
            result[key] = basis
        
        # Add auxiliary basis
        if self.auxiliary_basis:
            aux_key = "df_basis_scf" if self.auxiliary_type == "jkfit" else "df_basis_mp2"
            result[aux_key] = self.auxiliary_basis
        
        return result
    
    def to_psi4_string(self) -> str:
        """
        Convert to Psi4 basis block string.
        
        Returns:
            String suitable for psi4 input file basis block.
        """
        lines = [f"basis {{"]
        lines.append(f"    assign {self.default_basis}")
        
        for element, basis in sorted(self.element_basis.items()):
            lines.append(f"    assign {element} {basis}")
        
        lines.append("}")
        
        return "\n".join(lines)


@dataclass
class BasisFunction:
    """
    Represents a single basis function (primitive or contracted).
    
    Attributes:
        angular_momentum: Angular momentum (0=s, 1=p, 2=d, etc.).
        exponents: List of primitive exponents.
        coefficients: List of contraction coefficients.
    """
    angular_momentum: int
    exponents: list[float] = field(default_factory=list)
    coefficients: list[float] = field(default_factory=list)
    
    @property
    def n_primitives(self) -> int:
        """Number of primitive functions."""
        return len(self.exponents)
    
    @property
    def angular_momentum_symbol(self) -> str:
        """Get angular momentum letter (s, p, d, f, g, h)."""
        symbols = "spdfghiklmn"
        if 0 <= self.angular_momentum < len(symbols):
            return symbols[self.angular_momentum]
        return "?"
    
    def to_gbs_string(self) -> str:
        """Format as Gaussian basis set format."""
        lines = [f"{self.angular_momentum_symbol.upper()}   {self.n_primitives}   1.00"]
        for exp, coef in zip(self.exponents, self.coefficients):
            lines.append(f"     {exp:20.10E}  {coef:20.10E}")
        return "\n".join(lines)


@dataclass
class ElementBasis:
    """
    Basis set definition for a single element.
    
    Attributes:
        element: Element symbol.
        functions: List of basis functions.
        name: Basis set name.
    """
    element: str
    functions: list[BasisFunction] = field(default_factory=list)
    name: str = ""
    
    @property
    def n_functions(self) -> int:
        """Total number of contracted functions."""
        return len(self.functions)
    
    @property
    def n_primitives(self) -> int:
        """Total number of primitive functions."""
        return sum(f.n_primitives for f in self.functions)
    
    def to_gbs_string(self) -> str:
        """Format as Gaussian basis set format."""
        lines = [f"****", f"{self.element}     0"]
        for func in self.functions:
            lines.append(func.to_gbs_string())
        lines.append("****")
        return "\n".join(lines)


# =============================================================================
# BASIS SET NAME PARSING
# =============================================================================

# Common basis set aliases
_BASIS_ALIASES: dict[str, str] = {
    # Pople aliases
    "631g": "6-31g",
    "631g*": "6-31g*",
    "631g**": "6-31g**",
    "631+g*": "6-31+g*",
    "631+g**": "6-31+g**",
    "631++g**": "6-31++g**",
    "6311g": "6-311g",
    "6311g*": "6-311g*",
    "6311g**": "6-311g**",
    "6311+g*": "6-311+g*",
    "6311+g**": "6-311+g**",
    "6311++g**": "6-311++g**",
    "321g": "3-21g",
    
    # Dunning aliases
    "pvdz": "cc-pvdz",
    "pvtz": "cc-pvtz",
    "pvqz": "cc-pvqz",
    "pv5z": "cc-pv5z",
    "avdz": "aug-cc-pvdz",
    "avtz": "aug-cc-pvtz",
    "avqz": "aug-cc-pvqz",
    "av5z": "aug-cc-pv5z",
    "ccpvdz": "cc-pvdz",
    "ccpvtz": "cc-pvtz",
    "ccpvqz": "cc-pvqz",
    "augccpvdz": "aug-cc-pvdz",
    "augccpvtz": "aug-cc-pvtz",
    "augccpvqz": "aug-cc-pvqz",
    
    # Karlsruhe aliases
    "svp": "def2-svp",
    "tzvp": "def2-tzvp",
    "tzvpp": "def2-tzvpp",
    "qzvp": "def2-qzvp",
    "qzvpp": "def2-qzvpp",
    "def2svp": "def2-svp",
    "def2tzvp": "def2-tzvp",
    "def2qzvp": "def2-qzvp",
    
    # Minimal
    "sto3g": "sto-3g",
    "minao": "minao",
}


def normalize_basis_name(name: str) -> str:
    """
    Normalize a basis set name to standard form.
    
    Args:
        name: Basis set name (possibly with non-standard formatting).
        
    Returns:
        Normalized basis set name.
    """
    # Remove spaces and convert to lowercase
    normalized = name.lower().replace(" ", "").replace("_", "-")
    
    # Check for aliases
    if normalized in _BASIS_ALIASES:
        return _BASIS_ALIASES[normalized]
    
    # Handle common variations
    # Add hyphens where expected
    if normalized.startswith("aug") and not normalized.startswith("aug-"):
        normalized = "aug-" + normalized[3:]
    if normalized.startswith("d-aug") and not normalized.startswith("d-aug-"):
        normalized = "d-aug-" + normalized[5:]
    
    return normalized


def parse_basis_name(name: str) -> tuple[str, BasisSetFamily, dict[str, bool]]:
    """
    Parse a basis set name into components.
    
    Args:
        name: Basis set name.
        
    Returns:
        Tuple of (normalized_name, family, properties_dict).
        Properties include: has_diffuse, has_polarization, has_core_functions.
    """
    normalized = normalize_basis_name(name)
    
    # Determine family
    family = BasisSetFamily.CUSTOM
    if any(p in normalized for p in ["6-31", "6-311", "3-21"]):
        family = BasisSetFamily.POPLE
    elif "cc-p" in normalized:
        family = BasisSetFamily.DUNNING
    elif "def2" in normalized or "def-" in normalized:
        family = BasisSetFamily.KARLSRUHE
    elif normalized.startswith("pc") or "pcseg" in normalized:
        family = BasisSetFamily.JENSEN
    elif normalized.startswith("sto") or normalized == "minao":
        family = BasisSetFamily.MINIMAL
    elif any(x in normalized for x in ["jkfit", "rifit", "-ri", "-jk"]):
        family = BasisSetFamily.AUXILIARY
    
    # Determine properties
    properties = {
        "has_diffuse": "aug" in normalized or "+" in normalized or normalized.endswith("d"),
        "has_polarization": "*" in normalized or "p" in normalized.split("-")[-1],
        "has_core_functions": "cv" in normalized or "wc" in normalized,
        "has_ecp": "-pp" in normalized or "ecp" in normalized,
    }
    
    return (normalized, family, properties)


def get_zeta_level(basis_name: str) -> int:
    """
    Determine the zeta level of a basis set.
    
    Args:
        basis_name: Basis set name.
        
    Returns:
        Zeta level (2 for DZ, 3 for TZ, 4 for QZ, etc.), or 0 if unknown.
    """
    normalized = normalize_basis_name(basis_name).lower()
    
    # Dunning-style
    if "pvdz" in normalized or "vdz" in normalized:
        return 2
    if "pvtz" in normalized or "vtz" in normalized:
        return 3
    if "pvqz" in normalized or "vqz" in normalized:
        return 4
    if "pv5z" in normalized or "v5z" in normalized:
        return 5
    if "pv6z" in normalized or "v6z" in normalized:
        return 6
    
    # Karlsruhe-style
    if "svp" in normalized:
        return 2
    if "tzvp" in normalized:
        return 3
    if "qzvp" in normalized:
        return 4
    
    # Pople-style (approximate)
    if "6-311" in normalized:
        return 3
    if "6-31" in normalized:
        return 2
    if "3-21" in normalized:
        return 2
    
    # Jensen-style
    for i in range(5):
        if f"pc-{i}" in normalized or f"pcseg-{i}" in normalized:
            return i + 1
    
    # Minimal
    if "sto" in normalized or normalized == "minao":
        return 1
    
    return 0


# =============================================================================
# AUXILIARY BASIS HANDLING
# =============================================================================

def select_auxiliary_basis(
    orbital_basis: str,
    fitting_type: str = "jkfit",
    fallback: bool = True
) -> Optional[str]:
    """
    Select an appropriate auxiliary basis for a given orbital basis.
    
    Args:
        orbital_basis: Name of the orbital basis set.
        fitting_type: Type of fitting ("jkfit", "rifit", "jfit").
        fallback: If True, return a default if no match found.
        
    Returns:
        Name of auxiliary basis, or None if not found.
    """
    normalized = normalize_basis_name(orbital_basis)
    
    # Try exact match first
    result = get_matching_auxiliary_basis(normalized, fitting_type)
    if result:
        return result
    
    # Try to infer from basis family and size
    _, family, _ = parse_basis_name(normalized)
    zeta = get_zeta_level(normalized)
    has_diffuse = "aug" in normalized or "+" in normalized
    
    if family == BasisSetFamily.DUNNING:
        if fitting_type == "jkfit":
            if has_diffuse:
                if zeta == 2:
                    return "aug-cc-pvdz-jkfit"
                elif zeta == 3:
                    return "aug-cc-pvtz-jkfit"
                elif zeta >= 4:
                    return "aug-cc-pvqz-jkfit"
            else:
                if zeta == 2:
                    return "cc-pvdz-jkfit"
                elif zeta == 3:
                    return "cc-pvtz-jkfit"
                elif zeta >= 4:
                    return "cc-pvqz-jkfit"
        elif fitting_type == "rifit":
            if has_diffuse:
                if zeta == 2:
                    return "aug-cc-pvdz-ri"
                elif zeta == 3:
                    return "aug-cc-pvtz-ri"
                elif zeta >= 4:
                    return "aug-cc-pvqz-ri"
            else:
                if zeta == 2:
                    return "cc-pvdz-ri"
                elif zeta == 3:
                    return "cc-pvtz-ri"
                elif zeta >= 4:
                    return "cc-pvqz-ri"
    
    elif family == BasisSetFamily.KARLSRUHE:
        if fitting_type == "jkfit":
            if zeta == 2:
                return "def2-svp-jkfit"
            elif zeta == 3:
                return "def2-tzvp-jkfit"
            elif zeta >= 4:
                return "def2-qzvp-jkfit"
        elif fitting_type == "rifit":
            if zeta == 2:
                return "def2-svp-rifit"
            elif zeta == 3:
                return "def2-tzvp-rifit"
            elif zeta >= 4:
                return "def2-qzvp-rifit"
    
    # Fallback
    if fallback:
        if fitting_type == "jfit":
            return "def2-universal-jfit"
        elif fitting_type == "jkfit":
            return "def2-tzvp-jkfit"
        elif fitting_type == "rifit":
            return "def2-tzvp-rifit"
    
    return None


# =============================================================================
# BASIS SET VALIDATION
# =============================================================================

def validate_basis_for_elements(
    basis_name: str,
    elements: Sequence[str]
) -> tuple[bool, list[str]]:
    """
    Validate that a basis set is available for given elements.
    
    Args:
        basis_name: Name of the basis set.
        elements: List of element symbols.
        
    Returns:
        Tuple of (is_valid, list of unsupported elements).
    """
    normalized = normalize_basis_name(basis_name)
    _, family, properties = parse_basis_name(normalized)
    
    # Define element coverage for different basis families
    # These are approximate - actual availability depends on the specific basis
    
    first_row = {"H", "He"}
    second_row = {"Li", "Be", "B", "C", "N", "O", "F", "Ne"}
    third_row = {"Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar"}
    fourth_row = {"K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", 
                  "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr"}
    
    light_elements = first_row | second_row | third_row | fourth_row
    
    # Most bases cover at least these
    supported = light_elements.copy()
    
    if family == BasisSetFamily.KARLSRUHE:
        # def2 bases have very broad coverage
        supported = set(ATOMIC_NUMBERS.keys()) - {"X"}
    
    elif family == BasisSetFamily.DUNNING:
        # Standard Dunning bases are more limited
        if properties.get("has_ecp"):
            # PP bases cover heavy elements
            supported = set(ATOMIC_NUMBERS.keys()) - {"X"}
        else:
            # Regular Dunning covers up to Kr typically
            supported = light_elements
    
    elif family == BasisSetFamily.POPLE:
        # Pople bases typically cover up to Kr
        supported = light_elements
    
    # Check each element
    unsupported = []
    for element in elements:
        elem_normalized = element.capitalize()
        if elem_normalized == "X":
            continue  # Ghost atoms are always OK
        if elem_normalized not in supported:
            unsupported.append(elem_normalized)
    
    return (len(unsupported) == 0, unsupported)


def suggest_basis_for_system(
    elements: Sequence[str],
    method: str = "dft",
    accuracy: str = "medium"
) -> str:
    """
    Suggest an appropriate basis set for a molecular system.
    
    Args:
        elements: List of element symbols in the system.
        method: Calculation method (hf, dft, mp2, ccsd, etc.).
        accuracy: Desired accuracy level (low, medium, high, very_high).
        
    Returns:
        Recommended basis set name.
    """
    method_lower = method.lower()
    
    # Check for heavy elements
    heavy_elements = {"Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd",
                      "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba"}
    has_heavy = any(e.capitalize() in heavy_elements for e in elements)
    
    # Base recommendation by method
    if method_lower in ("hf", "scf"):
        if accuracy == "low":
            basis = "6-31g*"
        elif accuracy == "medium":
            basis = "def2-tzvp"
        elif accuracy == "high":
            basis = "cc-pvtz"
        else:
            basis = "cc-pvqz"
    
    elif method_lower in ("dft", "b3lyp", "pbe", "pbe0"):
        if accuracy == "low":
            basis = "def2-svp"
        elif accuracy == "medium":
            basis = "def2-tzvp"
        elif accuracy == "high":
            basis = "def2-tzvpp"
        else:
            basis = "def2-qzvp"
    
    elif method_lower in ("mp2", "mp3"):
        if accuracy == "low":
            basis = "cc-pvdz"
        elif accuracy == "medium":
            basis = "cc-pvtz"
        elif accuracy == "high":
            basis = "aug-cc-pvtz"
        else:
            basis = "aug-cc-pvqz"
    
    elif method_lower in ("ccsd", "ccsd(t)", "cc2"):
        if accuracy == "low":
            basis = "cc-pvdz"
        elif accuracy == "medium":
            basis = "cc-pvtz"
        elif accuracy == "high":
            basis = "aug-cc-pvtz"
        else:
            basis = "aug-cc-pvqz"
    
    elif method_lower in ("sapt", "sapt0", "sapt2+"):
        if accuracy == "low":
            basis = "jun-cc-pvdz"
        elif accuracy == "medium":
            basis = "aug-cc-pvdz"
        else:
            basis = "aug-cc-pvtz"
    
    else:
        # Default
        basis = "def2-tzvp"
    
    # Adjust for heavy elements
    if has_heavy and "def2" not in basis:
        # Switch to def2 bases which have better heavy element coverage
        if "aug" in basis:
            basis = "def2-tzvpd"
        else:
            basis = "def2-tzvp"
    
    return basis


# =============================================================================
# BASIS SET EXTRAPOLATION
# =============================================================================

@dataclass
class CBSExtrapolation:
    """
    Complete Basis Set (CBS) extrapolation specification.
    
    Attributes:
        basis_small: Smaller basis set.
        basis_large: Larger basis set.
        scf_scheme: Extrapolation scheme for SCF energy.
        correlation_scheme: Extrapolation scheme for correlation energy.
    """
    basis_small: str
    basis_large: str
    scf_scheme: str = "exponential"
    correlation_scheme: str = "inverse_cubic"
    
    def extrapolate_scf(
        self, 
        energy_small: float, 
        energy_large: float
    ) -> float:
        """
        Extrapolate SCF energy to CBS limit.
        
        Args:
            energy_small: SCF energy with smaller basis.
            energy_large: SCF energy with larger basis.
            
        Returns:
            Extrapolated CBS limit energy.
        """
        x_small = get_zeta_level(self.basis_small)
        x_large = get_zeta_level(self.basis_large)
        
        if x_small == 0 or x_large == 0:
            return energy_large  # Can't extrapolate
        
        if self.scf_scheme == "exponential":
            # E(X) = E_CBS + A * exp(-B * X)
            # Two-point extrapolation
            import math
            ratio = energy_small / energy_large
            if ratio <= 0 or ratio >= 1:
                return energy_large
            
            # Simplified two-point formula
            alpha = 1.63  # Empirical parameter
            factor = math.exp(-alpha * x_large) / (
                math.exp(-alpha * x_small) - math.exp(-alpha * x_large)
            )
            return energy_large + factor * (energy_large - energy_small)
        
        else:
            # Default to larger basis value
            return energy_large
    
    def extrapolate_correlation(
        self,
        corr_small: float,
        corr_large: float
    ) -> float:
        """
        Extrapolate correlation energy to CBS limit.
        
        Args:
            corr_small: Correlation energy with smaller basis.
            corr_large: Correlation energy with larger basis.
            
        Returns:
            Extrapolated CBS limit correlation energy.
        """
        x_small = get_zeta_level(self.basis_small)
        x_large = get_zeta_level(self.basis_large)
        
        if x_small == 0 or x_large == 0:
            return corr_large
        
        if self.correlation_scheme == "inverse_cubic":
            # E_corr(X) = E_CBS + A / X^3
            # Helgaker formula
            x_small_cubed = x_small ** 3
            x_large_cubed = x_large ** 3
            
            numerator = x_large_cubed * corr_large - x_small_cubed * corr_small
            denominator = x_large_cubed - x_small_cubed
            
            if abs(denominator) < 1e-10:
                return corr_large
            
            return numerator / denominator
        
        else:
            return corr_large


def get_cbs_pair(basis_name: str) -> Optional[tuple[str, str]]:
    """
    Get a pair of basis sets suitable for CBS extrapolation.
    
    Args:
        basis_name: Name of one basis set in the pair.
        
    Returns:
        Tuple of (smaller_basis, larger_basis), or None if no pair found.
    """
    normalized = normalize_basis_name(basis_name)
    zeta = get_zeta_level(normalized)
    
    # Dunning pairs
    dunning_pairs = {
        2: ("cc-pvdz", "cc-pvtz"),
        3: ("cc-pvtz", "cc-pvqz"),
        4: ("cc-pvqz", "cc-pv5z"),
        5: ("cc-pv5z", "cc-pv6z"),
    }
    
    aug_dunning_pairs = {
        2: ("aug-cc-pvdz", "aug-cc-pvtz"),
        3: ("aug-cc-pvtz", "aug-cc-pvqz"),
        4: ("aug-cc-pvqz", "aug-cc-pv5z"),
    }
    
    if "cc-p" in normalized:
        if "aug" in normalized:
            return aug_dunning_pairs.get(zeta)
        else:
            return dunning_pairs.get(zeta)
    
    # Karlsruhe pairs
    karlsruhe_pairs = {
        2: ("def2-svp", "def2-tzvp"),
        3: ("def2-tzvp", "def2-qzvp"),
    }
    
    if "def2" in normalized:
        return karlsruhe_pairs.get(zeta)
    
    return None
