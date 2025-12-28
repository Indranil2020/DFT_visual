"""
Basis Set Validation for Psi4 MCP Server.

Validates basis set inputs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


# Known basis sets supported by Psi4
AVAILABLE_BASIS_SETS = {
    # Minimal
    "sto-3g", "sto-6g",
    # Pople
    "3-21g", "6-31g", "6-31g*", "6-31g**", "6-31+g", "6-31+g*", "6-31+g**",
    "6-31++g", "6-31++g*", "6-31++g**",
    "6-311g", "6-311g*", "6-311g**", "6-311+g", "6-311+g*", "6-311+g**",
    "6-311++g", "6-311++g*", "6-311++g**",
    # Dunning
    "cc-pvdz", "cc-pvtz", "cc-pvqz", "cc-pv5z", "cc-pv6z",
    "aug-cc-pvdz", "aug-cc-pvtz", "aug-cc-pvqz", "aug-cc-pv5z",
    "d-aug-cc-pvdz", "d-aug-cc-pvtz", "d-aug-cc-pvqz",
    # Core-valence
    "cc-pcvdz", "cc-pcvtz", "cc-pcvqz",
    "aug-cc-pcvdz", "aug-cc-pcvtz", "aug-cc-pcvqz",
    # Karlsruhe
    "def2-svp", "def2-svpd", "def2-tzvp", "def2-tzvpd", "def2-tzvpp",
    "def2-qzvp", "def2-qzvpd", "def2-qzvpp",
    # Jensen
    "pc-0", "pc-1", "pc-2", "pc-3", "pc-4",
    "aug-pc-0", "aug-pc-1", "aug-pc-2", "aug-pc-3", "aug-pc-4",
    # Auxiliary
    "cc-pvdz-ri", "cc-pvtz-ri", "cc-pvqz-ri",
    "cc-pvdz-jkfit", "cc-pvtz-jkfit", "cc-pvqz-jkfit",
    "def2-svp-ri", "def2-tzvp-ri", "def2-qzvp-ri",
}

# Element coverage for common basis sets
BASIS_ELEMENT_COVERAGE = {
    "sto-3g": {"H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar"},
    "cc-pvdz": {"H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "Ca"},
    "def2-svp": {"H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
                 "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr"},
}


@dataclass
class BasisValidationResult:
    """Result of basis set validation."""
    valid: bool
    basis_name: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggested_alternatives: List[str] = field(default_factory=list)


class BasisSetValidator:
    """Validates basis set inputs."""
    
    def __init__(self):
        self.available = AVAILABLE_BASIS_SETS
        self.coverage = BASIS_ELEMENT_COVERAGE
    
    def validate(self, basis: str, elements: Optional[List[str]] = None) -> BasisValidationResult:
        """Validate basis set."""
        errors = []
        warnings = []
        alternatives = []
        
        basis_lower = basis.lower().strip()
        
        # Check if basis exists
        if basis_lower not in self.available:
            # Try common variations
            variations = [
                basis_lower.replace("*", "d").replace("**", "dp"),
                basis_lower.replace("(", "").replace(")", ""),
            ]
            found = False
            for var in variations:
                if var in self.available:
                    warnings.append(f"Using basis '{var}' instead of '{basis}'")
                    basis_lower = var
                    found = True
                    break
            
            if not found:
                errors.append(f"Unknown basis set: {basis}")
                # Suggest similar
                for avail in self.available:
                    if basis_lower[:3] in avail or avail[:3] in basis_lower:
                        alternatives.append(avail)
                alternatives = alternatives[:5]
        
        # Check element coverage
        if elements and basis_lower in self.coverage:
            coverage = self.coverage[basis_lower]
            missing = [e for e in elements if e not in coverage]
            if missing:
                errors.append(f"Basis {basis} not available for elements: {', '.join(missing)}")
        
        return BasisValidationResult(
            valid=len(errors) == 0,
            basis_name=basis_lower,
            errors=errors,
            warnings=warnings,
            suggested_alternatives=alternatives,
        )
    
    def normalize_name(self, basis: str) -> str:
        """Normalize basis set name."""
        return basis.lower().strip()


def validate_basis_set(basis: str, elements: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """Validate basis set."""
    validator = BasisSetValidator()
    result = validator.validate(basis, elements)
    return result.valid, result.errors


def is_valid_basis(basis: str) -> bool:
    """Check if basis set is valid."""
    return basis.lower().strip() in AVAILABLE_BASIS_SETS


def get_available_basis_sets() -> List[str]:
    """Get list of available basis sets."""
    return sorted(AVAILABLE_BASIS_SETS)


def check_basis_for_elements(basis: str, elements: List[str]) -> Tuple[bool, List[str]]:
    """Check if basis set covers all elements."""
    basis_lower = basis.lower().strip()
    if basis_lower not in BASIS_ELEMENT_COVERAGE:
        return True, []  # Assume available if not in coverage map
    
    coverage = BASIS_ELEMENT_COVERAGE[basis_lower]
    missing = [e for e in elements if e not in coverage]
    return len(missing) == 0, missing
