"""
Options Validation for Psi4 MCP Server.

Validates calculation options.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


# Valid option names and their types
VALID_OPTIONS = {
    # SCF options
    "maxiter": int,
    "e_convergence": float,
    "d_convergence": float,
    "scf_type": str,
    "guess": str,
    "soscf": bool,
    "damping_percentage": float,
    "diis_max_vecs": int,
    "level_shift": float,
    # Geometry optimization
    "geom_maxiter": int,
    "g_convergence": str,
    "full_hess_every": int,
    "opt_coordinates": str,
    # Frequencies
    "normal_modes_write": bool,
    "t": float,  # temperature
    "p": float,  # pressure
    # DFT
    "dft_radial_points": int,
    "dft_spherical_points": int,
    # Coupled cluster
    "cc_maxiter": int,
    "freeze_core": bool,
    # TDDFT
    "tdscf_states": int,
    "tdscf_tda": bool,
    "roots_per_irrep": list,
}

# Valid values for string options
VALID_STRING_VALUES = {
    "scf_type": ["pk", "direct", "df", "cd", "mem_df", "out_of_core"],
    "guess": ["auto", "sad", "gwh", "read", "core", "huckel"],
    "g_convergence": ["gau", "gau_loose", "gau_tight", "gau_verytight", "interfrag_tight"],
    "opt_coordinates": ["cartesian", "internal", "both", "redundant"],
}


@dataclass
class OptionsValidationResult:
    """Result of options validation."""
    valid: bool
    validated_options: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class OptionsValidator:
    """Validates calculation options."""
    
    def __init__(self):
        self.valid_options = VALID_OPTIONS
        self.valid_values = VALID_STRING_VALUES
    
    def validate(self, options: Dict[str, Any]) -> OptionsValidationResult:
        """Validate options dictionary."""
        errors = []
        warnings = []
        validated = {}
        
        for key, value in options.items():
            key_lower = key.lower()
            
            # Check if option is known
            if key_lower not in self.valid_options:
                warnings.append(f"Unknown option: {key}")
                validated[key_lower] = value
                continue
            
            # Check type
            expected_type = self.valid_options[key_lower]
            if not isinstance(value, expected_type):
                # Try conversion
                if expected_type == int and isinstance(value, (float, str)):
                    try:
                        value = int(float(value))
                    except ValueError:
                        errors.append(f"Option {key}: expected int, got {type(value).__name__}")
                        continue
                elif expected_type == float and isinstance(value, (int, str)):
                    try:
                        value = float(value)
                    except ValueError:
                        errors.append(f"Option {key}: expected float, got {type(value).__name__}")
                        continue
                elif expected_type == bool and isinstance(value, str):
                    value = value.lower() in ("true", "yes", "1", "on")
            
            # Check valid string values
            if key_lower in self.valid_values and isinstance(value, str):
                if value.lower() not in self.valid_values[key_lower]:
                    errors.append(f"Option {key}: invalid value '{value}'. Valid: {self.valid_values[key_lower]}")
                    continue
            
            validated[key_lower] = value
        
        return OptionsValidationResult(
            valid=len(errors) == 0,
            validated_options=validated,
            errors=errors,
            warnings=warnings,
        )


def validate_options(options: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Validate options dictionary."""
    validator = OptionsValidator()
    result = validator.validate(options)
    return result.valid, result.validated_options, result.errors


def validate_memory_string(memory: str) -> Tuple[bool, float, str]:
    """Validate and parse memory string. Returns (valid, mb_value, error)."""
    memory = memory.strip().upper()
    
    pattern = r"^(\d+\.?\d*)\s*(B|KB|MB|GB|TB)?$"
    match = re.match(pattern, memory)
    
    if not match:
        return False, 0.0, f"Invalid memory format: {memory}"
    
    value = float(match.group(1))
    unit = match.group(2) or "MB"
    
    multipliers = {"B": 1e-6, "KB": 1e-3, "MB": 1.0, "GB": 1024.0, "TB": 1024*1024}
    mb_value = value * multipliers.get(unit, 1.0)
    
    if mb_value < 100:
        return False, mb_value, "Memory too low (minimum 100 MB)"
    if mb_value > 1024 * 1024:  # 1 TB
        return False, mb_value, "Memory too high (maximum 1 TB)"
    
    return True, mb_value, ""


def validate_convergence_options(options: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate convergence-related options."""
    errors = []
    
    if "e_convergence" in options:
        e_conv = options["e_convergence"]
        if not (1e-12 <= e_conv <= 1e-3):
            errors.append(f"e_convergence {e_conv} out of range [1e-12, 1e-3]")
    
    if "d_convergence" in options:
        d_conv = options["d_convergence"]
        if not (1e-12 <= d_conv <= 1e-3):
            errors.append(f"d_convergence {d_conv} out of range [1e-12, 1e-3]")
    
    if "maxiter" in options:
        maxiter = options["maxiter"]
        if not (1 <= maxiter <= 1000):
            errors.append(f"maxiter {maxiter} out of range [1, 1000]")
    
    return len(errors) == 0, errors
