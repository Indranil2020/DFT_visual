"""
Basis Set Library for Psi4 MCP Server.

Provides access to basis set information, metadata, and recommendations
for computational chemistry calculations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class BasisSetFamily(str, Enum):
    """Basis set family classifications."""
    POPLE = "pople"
    DUNNING = "dunning"
    KARLSRUHE = "karlsruhe"
    AHLRICHS = "ahlrichs"
    JENSEN = "jensen"
    ANO = "ano"
    MINIMAL = "minimal"
    CUSTOM = "custom"


class BasisSetSize(str, Enum):
    """Basis set size classifications."""
    MINIMAL = "minimal"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    VERY_LARGE = "very_large"
    HUGE = "huge"


@dataclass
class BasisSetInfo:
    """Information about a basis set."""
    name: str
    family: BasisSetFamily
    size: BasisSetSize
    polarization: bool
    diffuse: bool
    contracted: bool
    elements_supported: Set[str]
    description: str
    citation: str
    aliases: List[str] = field(default_factory=list)
    recommended_methods: List[str] = field(default_factory=list)
    recommended_for: List[str] = field(default_factory=list)
    
    @property
    def is_correlation_consistent(self) -> bool:
        """Check if this is a correlation-consistent basis."""
        return self.family == BasisSetFamily.DUNNING
    
    @property
    def supports_extrapolation(self) -> bool:
        """Check if this basis is suitable for CBS extrapolation."""
        return "cc-pv" in self.name.lower() or "def2" in self.name.lower()


class BasisSetLibrary:
    """
    Library of basis set information and utilities.
    
    Provides access to metadata about basis sets including elements
    supported, recommended uses, and citations.
    """
    
    # All elements in periodic table (H-Og, 118 elements)
    ALL_ELEMENTS: Set[str] = {
        "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
        "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
        "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
        "Ga", "Ge", "As", "Se", "Br", "Kr",
        "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
        "In", "Sn", "Sb", "Te", "I", "Xe",
        "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
        "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt",
        "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn",
        "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf",
        "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds",
        "Rg", "Cn", "Nh", "Fl", "Mc", "Lv", "Ts", "Og"
    }
    
    # Light main group elements (H-Ar)
    LIGHT_ELEMENTS: Set[str] = {
        "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
        "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar"
    }
    
    # Extended main group (H-Kr)
    EXTENDED_MAIN_GROUP: Set[str] = LIGHT_ELEMENTS | {
        "K", "Ca", "Ga", "Ge", "As", "Se", "Br", "Kr"
    }
    
    # First row transition metals
    FIRST_ROW_TM: Set[str] = {
        "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"
    }
    
    # Basis set database
    _BASIS_SETS: Dict[str, BasisSetInfo] = {
        # Minimal basis sets
        "sto-3g": BasisSetInfo(
            name="STO-3G",
            family=BasisSetFamily.MINIMAL,
            size=BasisSetSize.MINIMAL,
            polarization=False,
            diffuse=False,
            contracted=True,
            elements_supported=ALL_ELEMENTS,
            description="Minimal basis set, 3 Gaussians per STO",
            citation="Hehre, Stewart, Pople, J. Chem. Phys. 51, 2657 (1969)",
            aliases=["sto3g", "sto-3g"],
            recommended_methods=["hf"],
            recommended_for=["initial_geometry", "very_large_systems"],
        ),
        
        # Pople basis sets
        "3-21g": BasisSetInfo(
            name="3-21G",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.SMALL,
            polarization=False,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Split-valence double-zeta basis",
            citation="Binkley, Pople, Hehre, J. Am. Chem. Soc. 102, 939 (1980)",
            aliases=["3-21g", "321g"],
            recommended_methods=["hf", "dft"],
            recommended_for=["initial_screening", "large_systems"],
        ),
        
        "6-31g": BasisSetInfo(
            name="6-31G",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.SMALL,
            polarization=False,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Split-valence double-zeta basis",
            citation="Hehre, Ditchfield, Pople, J. Chem. Phys. 56, 2257 (1972)",
            aliases=["6-31g", "631g"],
            recommended_methods=["hf", "dft"],
            recommended_for=["general_organic"],
        ),
        
        "6-31g*": BasisSetInfo(
            name="6-31G*",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.MEDIUM,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Split-valence DZ with d polarization on heavy atoms",
            citation="Hariharan, Pople, Theor. Chim. Acta 28, 213 (1973)",
            aliases=["6-31g*", "6-31g(d)", "631gd"],
            recommended_methods=["hf", "dft", "mp2"],
            recommended_for=["geometry_optimization", "general_chemistry"],
        ),
        
        "6-31g**": BasisSetInfo(
            name="6-31G**",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.MEDIUM,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Split-valence DZ with d,p polarization",
            citation="Hariharan, Pople, Theor. Chim. Acta 28, 213 (1973)",
            aliases=["6-31g**", "6-31g(d,p)", "631gdp"],
            recommended_methods=["hf", "dft", "mp2"],
            recommended_for=["geometry_optimization", "hydrogen_bonding"],
        ),
        
        "6-311g**": BasisSetInfo(
            name="6-311G**",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Triple-zeta valence with d,p polarization",
            citation="Krishnan et al., J. Chem. Phys. 72, 650 (1980)",
            aliases=["6-311g**", "6-311g(d,p)"],
            recommended_methods=["hf", "dft", "mp2"],
            recommended_for=["accurate_energies", "vibrational_frequencies"],
        ),
        
        "6-311+g**": BasisSetInfo(
            name="6-311+G**",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=True,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS,
            description="Triple-zeta with diffuse functions on heavy atoms",
            citation="Clark et al., J. Comp. Chem. 4, 294 (1983)",
            aliases=["6-311+g**", "6-311+g(d,p)"],
            recommended_methods=["hf", "dft", "mp2"],
            recommended_for=["anions", "excited_states", "polarizability"],
        ),
        
        "6-311++g**": BasisSetInfo(
            name="6-311++G**",
            family=BasisSetFamily.POPLE,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=True,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS,
            description="Triple-zeta with diffuse functions on all atoms",
            citation="Clark et al., J. Comp. Chem. 4, 294 (1983)",
            aliases=["6-311++g**", "6-311++g(d,p)"],
            recommended_methods=["hf", "dft", "mp2"],
            recommended_for=["anions", "hydrogen_bonding", "weak_interactions"],
        ),
        
        # Dunning correlation-consistent basis sets
        "cc-pvdz": BasisSetInfo(
            name="cc-pVDZ",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.MEDIUM,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | {"Ca", "Sc", "Ti", "V", "Cr", 
                                                  "Mn", "Fe", "Co", "Ni", "Cu", "Zn"},
            description="Correlation-consistent polarized valence double-zeta",
            citation="Dunning, J. Chem. Phys. 90, 1007 (1989)",
            aliases=["cc-pvdz", "ccpvdz"],
            recommended_methods=["mp2", "ccsd", "dft"],
            recommended_for=["correlated_methods", "geometry_optimization"],
        ),
        
        "cc-pvtz": BasisSetInfo(
            name="cc-pVTZ",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Correlation-consistent polarized valence triple-zeta",
            citation="Dunning, J. Chem. Phys. 90, 1007 (1989)",
            aliases=["cc-pvtz", "ccpvtz"],
            recommended_methods=["mp2", "ccsd", "ccsd(t)"],
            recommended_for=["accurate_energies", "cbs_extrapolation"],
        ),
        
        "cc-pvqz": BasisSetInfo(
            name="cc-pVQZ",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.VERY_LARGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Correlation-consistent polarized valence quadruple-zeta",
            citation="Dunning, J. Chem. Phys. 90, 1007 (1989)",
            aliases=["cc-pvqz", "ccpvqz"],
            recommended_methods=["ccsd(t)", "mp2"],
            recommended_for=["benchmark", "cbs_extrapolation"],
        ),
        
        "cc-pv5z": BasisSetInfo(
            name="cc-pV5Z",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.HUGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS,
            description="Correlation-consistent polarized valence quintuple-zeta",
            citation="Dunning, J. Chem. Phys. 90, 1007 (1989)",
            aliases=["cc-pv5z", "ccpv5z"],
            recommended_methods=["ccsd(t)"],
            recommended_for=["benchmark", "cbs_limit"],
        ),
        
        # Augmented Dunning sets
        "aug-cc-pvdz": BasisSetInfo(
            name="aug-cc-pVDZ",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.MEDIUM,
            polarization=True,
            diffuse=True,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Augmented cc-pVDZ with diffuse functions",
            citation="Kendall, Dunning, Harrison, J. Chem. Phys. 96, 6796 (1992)",
            aliases=["aug-cc-pvdz", "augccpvdz"],
            recommended_methods=["mp2", "ccsd", "tddft"],
            recommended_for=["anions", "excited_states", "response_properties"],
        ),
        
        "aug-cc-pvtz": BasisSetInfo(
            name="aug-cc-pVTZ",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=True,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS | FIRST_ROW_TM,
            description="Augmented cc-pVTZ with diffuse functions",
            citation="Kendall, Dunning, Harrison, J. Chem. Phys. 96, 6796 (1992)",
            aliases=["aug-cc-pvtz", "augccpvtz"],
            recommended_methods=["mp2", "ccsd", "ccsd(t)", "tddft"],
            recommended_for=["accurate_properties", "sapt", "cbs_extrapolation"],
        ),
        
        "aug-cc-pvqz": BasisSetInfo(
            name="aug-cc-pVQZ",
            family=BasisSetFamily.DUNNING,
            size=BasisSetSize.VERY_LARGE,
            polarization=True,
            diffuse=True,
            contracted=True,
            elements_supported=LIGHT_ELEMENTS,
            description="Augmented cc-pVQZ with diffuse functions",
            citation="Kendall, Dunning, Harrison, J. Chem. Phys. 96, 6796 (1992)",
            aliases=["aug-cc-pvqz", "augccpvqz"],
            recommended_methods=["ccsd(t)"],
            recommended_for=["benchmark", "high_accuracy"],
        ),
        
        # Karlsruhe/Ahlrichs basis sets
        "def2-svp": BasisSetInfo(
            name="def2-SVP",
            family=BasisSetFamily.KARLSRUHE,
            size=BasisSetSize.SMALL,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=ALL_ELEMENTS - {"Fr", "Ra"} - {"Rf", "Db", "Sg", 
                                                               "Bh", "Hs", "Mt",
                                                               "Ds", "Rg", "Cn",
                                                               "Nh", "Fl", "Mc",
                                                               "Lv", "Ts", "Og"},
            description="Split-valence polarization basis",
            citation="Weigend, Ahlrichs, Phys. Chem. Chem. Phys. 7, 3297 (2005)",
            aliases=["def2-svp", "def2svp"],
            recommended_methods=["dft", "hf"],
            recommended_for=["fast_screening", "large_systems"],
        ),
        
        "def2-tzvp": BasisSetInfo(
            name="def2-TZVP",
            family=BasisSetFamily.KARLSRUHE,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=ALL_ELEMENTS - {"Fr", "Ra"} - {"Rf", "Db", "Sg",
                                                               "Bh", "Hs", "Mt",
                                                               "Ds", "Rg", "Cn",
                                                               "Nh", "Fl", "Mc",
                                                               "Lv", "Ts", "Og"},
            description="Triple-zeta valence polarization basis",
            citation="Weigend, Ahlrichs, Phys. Chem. Chem. Phys. 7, 3297 (2005)",
            aliases=["def2-tzvp", "def2tzvp"],
            recommended_methods=["dft", "mp2", "ccsd"],
            recommended_for=["production_dft", "all_elements"],
        ),
        
        "def2-tzvpp": BasisSetInfo(
            name="def2-TZVPP",
            family=BasisSetFamily.KARLSRUHE,
            size=BasisSetSize.LARGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=ALL_ELEMENTS - {"Fr", "Ra"} - {"Rf", "Db", "Sg",
                                                               "Bh", "Hs", "Mt",
                                                               "Ds", "Rg", "Cn",
                                                               "Nh", "Fl", "Mc",
                                                               "Lv", "Ts", "Og"},
            description="Triple-zeta valence with extra polarization",
            citation="Weigend, Ahlrichs, Phys. Chem. Chem. Phys. 7, 3297 (2005)",
            aliases=["def2-tzvpp", "def2tzvpp"],
            recommended_methods=["dft", "mp2", "ccsd"],
            recommended_for=["accurate_dft", "correlated_methods"],
        ),
        
        "def2-qzvp": BasisSetInfo(
            name="def2-QZVP",
            family=BasisSetFamily.KARLSRUHE,
            size=BasisSetSize.VERY_LARGE,
            polarization=True,
            diffuse=False,
            contracted=True,
            elements_supported=ALL_ELEMENTS - {"Fr", "Ra"} - {"Rf", "Db", "Sg",
                                                               "Bh", "Hs", "Mt",
                                                               "Ds", "Rg", "Cn",
                                                               "Nh", "Fl", "Mc",
                                                               "Lv", "Ts", "Og"},
            description="Quadruple-zeta valence polarization basis",
            citation="Weigend, Ahlrichs, Phys. Chem. Chem. Phys. 7, 3297 (2005)",
            aliases=["def2-qzvp", "def2qzvp"],
            recommended_methods=["dft", "ccsd(t)"],
            recommended_for=["benchmark", "high_accuracy"],
        ),
    }
    
    @classmethod
    def get_basis_set(cls, name: str) -> Optional[BasisSetInfo]:
        """
        Get basis set information by name.
        
        Args:
            name: Basis set name (case-insensitive)
            
        Returns:
            BasisSetInfo if found, None otherwise
        """
        normalized = name.lower().replace("_", "-")
        
        # Direct lookup
        if normalized in cls._BASIS_SETS:
            return cls._BASIS_SETS[normalized]
        
        # Search aliases
        for basis_info in cls._BASIS_SETS.values():
            if normalized in [a.lower() for a in basis_info.aliases]:
                return basis_info
        
        return None
    
    @classmethod
    def list_all(cls) -> List[BasisSetInfo]:
        """Get list of all basis sets."""
        return list(cls._BASIS_SETS.values())
    
    @classmethod
    def list_by_family(cls, family: BasisSetFamily) -> List[BasisSetInfo]:
        """Get basis sets by family."""
        return [b for b in cls._BASIS_SETS.values() if b.family == family]
    
    @classmethod
    def list_by_size(cls, size: BasisSetSize) -> List[BasisSetInfo]:
        """Get basis sets by size."""
        return [b for b in cls._BASIS_SETS.values() if b.size == size]
    
    @classmethod
    def list_supporting_element(cls, element: str) -> List[BasisSetInfo]:
        """Get basis sets supporting a specific element."""
        element_norm = element.capitalize()
        return [
            b for b in cls._BASIS_SETS.values() 
            if element_norm in b.elements_supported
        ]
    
    @classmethod
    def get_recommended_for_method(cls, method: str) -> List[BasisSetInfo]:
        """Get basis sets recommended for a method."""
        method_lower = method.lower()
        return [
            b for b in cls._BASIS_SETS.values()
            if method_lower in [m.lower() for m in b.recommended_methods]
        ]


def get_basis_set_info(name: str) -> Optional[BasisSetInfo]:
    """
    Get information about a basis set.
    
    Args:
        name: Basis set name
        
    Returns:
        BasisSetInfo or None if not found
    """
    return BasisSetLibrary.get_basis_set(name)


def list_basis_sets(
    family: Optional[BasisSetFamily] = None,
    size: Optional[BasisSetSize] = None,
    diffuse: Optional[bool] = None,
    polarization: Optional[bool] = None,
) -> List[BasisSetInfo]:
    """
    List basis sets with optional filtering.
    
    Args:
        family: Filter by family
        size: Filter by size
        diffuse: Filter by diffuse functions
        polarization: Filter by polarization functions
        
    Returns:
        List of matching basis sets
    """
    basis_sets = BasisSetLibrary.list_all()
    
    if family is not None:
        basis_sets = [b for b in basis_sets if b.family == family]
    
    if size is not None:
        basis_sets = [b for b in basis_sets if b.size == size]
    
    if diffuse is not None:
        basis_sets = [b for b in basis_sets if b.diffuse == diffuse]
    
    if polarization is not None:
        basis_sets = [b for b in basis_sets if b.polarization == polarization]
    
    return basis_sets


def get_recommended_basis(
    method: str,
    property_type: str = "energy",
    accuracy: str = "medium",
    elements: Optional[List[str]] = None,
) -> Optional[BasisSetInfo]:
    """
    Get recommended basis set for a calculation.
    
    Args:
        method: Computational method (hf, dft, mp2, ccsd, etc.)
        property_type: Property type (energy, geometry, frequencies, etc.)
        accuracy: Desired accuracy (low, medium, high, benchmark)
        elements: Elements in the system
        
    Returns:
        Recommended basis set or None
    """
    method_lower = method.lower()
    
    # Accuracy to size mapping
    accuracy_sizes = {
        "low": [BasisSetSize.SMALL, BasisSetSize.MINIMAL],
        "medium": [BasisSetSize.MEDIUM, BasisSetSize.SMALL],
        "high": [BasisSetSize.LARGE, BasisSetSize.VERY_LARGE],
        "benchmark": [BasisSetSize.VERY_LARGE, BasisSetSize.HUGE],
    }
    
    target_sizes = accuracy_sizes.get(accuracy.lower(), [BasisSetSize.MEDIUM])
    
    # Get candidates
    candidates = []
    for basis in BasisSetLibrary.list_all():
        if method_lower in [m.lower() for m in basis.recommended_methods]:
            if basis.size in target_sizes:
                candidates.append(basis)
    
    # Filter by element support if specified
    if elements:
        elements_set = {e.capitalize() for e in elements}
        candidates = [
            b for b in candidates
            if elements_set.issubset(b.elements_supported)
        ]
    
    # Property-specific preferences
    if property_type in ("excited_states", "tddft", "response"):
        # Prefer diffuse functions
        diffuse_candidates = [c for c in candidates if c.diffuse]
        if diffuse_candidates:
            candidates = diffuse_candidates
    
    # Sort by size (smaller first for same recommendations)
    size_order = {
        BasisSetSize.MINIMAL: 0,
        BasisSetSize.SMALL: 1,
        BasisSetSize.MEDIUM: 2,
        BasisSetSize.LARGE: 3,
        BasisSetSize.VERY_LARGE: 4,
        BasisSetSize.HUGE: 5,
    }
    candidates.sort(key=lambda b: size_order.get(b.size, 3))
    
    return candidates[0] if candidates else None


def is_basis_available(name: str) -> bool:
    """Check if a basis set is available."""
    return BasisSetLibrary.get_basis_set(name) is not None


def get_elements_supported(name: str) -> Optional[Set[str]]:
    """Get elements supported by a basis set."""
    basis = BasisSetLibrary.get_basis_set(name)
    if basis is None:
        return None
    return basis.elements_supported
