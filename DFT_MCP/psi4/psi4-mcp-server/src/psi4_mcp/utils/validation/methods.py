"""
Method Validation for Psi4 MCP Server.

Validates computational method inputs.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


# Available methods organized by category
AVAILABLE_METHODS = {
    # Hartree-Fock
    "hf", "rhf", "uhf", "rohf",
    # DFT - LDA
    "svwn", "svwn5", "lda",
    # DFT - GGA
    "blyp", "bp86", "pbe", "pw91",
    # DFT - meta-GGA
    "tpss", "m06-l", "scan",
    # DFT - Hybrid
    "b3lyp", "b3lyp5", "pbe0", "b97", "b97-1", "b97-2",
    # DFT - meta-Hybrid
    "m06", "m06-2x", "m06-hf", "tpssh",
    # DFT - Range-separated
    "wb97", "wb97x", "wb97x-d", "wb97x-d3", "cam-b3lyp", "lc-wpbe",
    # DFT - Double-hybrid
    "b2plyp", "b2plyp-d3",
    # MP2
    "mp2", "df-mp2", "ri-mp2", "scs-mp2", "sos-mp2",
    # Higher perturbation
    "mp3", "mp4", "mp4(sdq)",
    # Coupled Cluster
    "ccsd", "ccsd(t)", "cc2", "cc3", "ccsdt", "ccsdt(q)",
    # EOM-CC
    "eom-ccsd", "eom-cc2",
    # Configuration Interaction
    "cisd", "cisdt", "cisdtq", "fci", "detci",
    # MCSCF
    "casscf", "rasscf",
    # SAPT
    "sapt0", "sapt2", "sapt2+", "sapt2+(3)", "sapt2+3",
    # ADC
    "adc(1)", "adc(2)", "adc(2)-x", "adc(3)",
}

# Methods requiring specific references
UNRESTRICTED_METHODS = {"uhf", "uks"}
RESTRICTED_OPEN_METHODS = {"rohf", "roks"}

# Method scaling (computational cost)
METHOD_SCALING = {
    "hf": "N^4", "rhf": "N^4", "uhf": "N^4",
    "b3lyp": "N^3", "pbe": "N^3", "pbe0": "N^3",
    "mp2": "N^5", "df-mp2": "N^4",
    "ccsd": "N^6", "ccsd(t)": "N^7",
    "cisd": "N^6", "fci": "N!",
}


@dataclass
class MethodValidationResult:
    """Result of method validation."""
    valid: bool
    method_name: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    scaling: str = ""


class MethodValidator:
    """Validates computational method inputs."""
    
    def __init__(self):
        self.available = AVAILABLE_METHODS
        self.scaling = METHOD_SCALING
    
    def validate(
        self,
        method: str,
        multiplicity: int = 1,
        reference: Optional[str] = None,
    ) -> MethodValidationResult:
        """Validate method."""
        errors = []
        warnings = []
        
        method_lower = method.lower().strip()
        
        # Check if method exists
        if method_lower not in self.available:
            # Try without hyphens
            alt = method_lower.replace("-", "")
            if alt in self.available:
                method_lower = alt
            else:
                errors.append(f"Unknown method: {method}")
                return MethodValidationResult(
                    valid=False, method_name=method_lower, errors=errors
                )
        
        # Check reference consistency
        if multiplicity > 1:
            if reference and reference.lower() == "rhf":
                warnings.append("RHF reference not appropriate for open-shell system")
        
        # Get scaling
        scaling = self.scaling.get(method_lower, "unknown")
        
        return MethodValidationResult(
            valid=len(errors) == 0,
            method_name=method_lower,
            errors=errors,
            warnings=warnings,
            scaling=scaling,
        )
    
    def get_recommended_reference(self, method: str, multiplicity: int) -> str:
        """Get recommended reference type."""
        if multiplicity == 1:
            return "rhf"
        elif method.lower() in UNRESTRICTED_METHODS:
            return "uhf"
        else:
            return "uhf"  # Default for open-shell


def validate_method(method: str, multiplicity: int = 1) -> Tuple[bool, List[str]]:
    """Validate method."""
    validator = MethodValidator()
    result = validator.validate(method, multiplicity)
    return result.valid, result.errors


def is_valid_method(method: str) -> bool:
    """Check if method is valid."""
    return method.lower().strip() in AVAILABLE_METHODS


def get_available_methods() -> List[str]:
    """Get list of available methods."""
    return sorted(AVAILABLE_METHODS)


def check_method_basis_compatibility(method: str, basis: str) -> Tuple[bool, List[str]]:
    """Check method/basis compatibility."""
    warnings = []
    method_lower = method.lower()
    basis_lower = basis.lower()
    
    # High-level methods with small basis
    if method_lower in ("ccsd", "ccsd(t)", "ccsdt") and "sto" in basis_lower:
        warnings.append(f"Coupled cluster with minimal basis {basis} not recommended")
    
    # DFT with very large basis
    if method_lower in ("b3lyp", "pbe") and ("5z" in basis_lower or "6z" in basis_lower):
        warnings.append(f"DFT with {basis} may be overkill; cc-pVTZ usually sufficient")
    
    return len(warnings) == 0, warnings
