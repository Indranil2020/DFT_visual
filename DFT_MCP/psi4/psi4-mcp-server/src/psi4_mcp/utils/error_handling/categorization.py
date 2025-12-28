"""
Error Categorization for Psi4 MCP Server.

Provides error classification and categorization functionality.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ErrorCategory(str, Enum):
    """Categories of errors in Psi4 calculations."""
    # Convergence errors
    CONVERGENCE = "convergence"
    SCF_CONVERGENCE = "scf_convergence"
    GEOMETRY_CONVERGENCE = "geometry_convergence"
    TDDFT_CONVERGENCE = "tddft_convergence"
    CC_CONVERGENCE = "cc_convergence"
    
    # Resource errors
    MEMORY = "memory"
    DISK = "disk"
    TIMEOUT = "timeout"
    
    # Input errors
    GEOMETRY = "geometry"
    BASIS_SET = "basis_set"
    METHOD = "method"
    OPTIONS = "options"
    SYMMETRY = "symmetry"
    
    # System errors
    LINEAR_DEPENDENCY = "linear_dependency"
    SINGULARITY = "singularity"
    NUMERICAL = "numerical"
    
    # Configuration errors
    ENVIRONMENT = "environment"
    INSTALLATION = "installation"
    
    # Unknown
    UNKNOWN = "unknown"


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""
    CRITICAL = "critical"  # Calculation cannot proceed
    ERROR = "error"        # Calculation failed
    WARNING = "warning"    # Potential issue
    INFO = "info"          # Informational


@dataclass
class ErrorInfo:
    """Information about a detected error."""
    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    original_error: Optional[str] = None
    error_code: Optional[str] = None
    line_number: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)
    recoverable: bool = False
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "original_error": self.original_error,
            "error_code": self.error_code,
            "line_number": self.line_number,
            "context": self.context,
            "recoverable": self.recoverable,
            "suggestions": self.suggestions,
        }


# Error categorization patterns
_CATEGORY_PATTERNS: Dict[ErrorCategory, List[str]] = {
    ErrorCategory.SCF_CONVERGENCE: [
        "scf not converge",
        "could not converge scf",
        "diis error",
        "scf iterations exceeded",
        "scf failed to converge",
        "density not converged",
    ],
    ErrorCategory.GEOMETRY_CONVERGENCE: [
        "optimization not converge",
        "geom_maxiter exceeded",
        "geometry optimization failed",
        "step size too large",
        "gradient threshold not met",
    ],
    ErrorCategory.TDDFT_CONVERGENCE: [
        "tddft not converge",
        "tdscf_maxiter exceeded",
        "davidson failed",
        "root collapse",
    ],
    ErrorCategory.CC_CONVERGENCE: [
        "ccsd not converge",
        "coupled cluster failed",
        "cc amplitudes diverge",
    ],
    ErrorCategory.MEMORY: [
        "memory",
        "malloc failed",
        "cannot allocate",
        "out of memory",
        "insufficient memory",
        "memory limit exceeded",
    ],
    ErrorCategory.DISK: [
        "disk",
        "i/o error",
        "no space left",
        "write failed",
        "scratch full",
    ],
    ErrorCategory.GEOMETRY: [
        "invalid geometry",
        "atoms too close",
        "bond length",
        "linear molecule",
        "invalid z-matrix",
        "geometry invalid",
    ],
    ErrorCategory.BASIS_SET: [
        "basis set not found",
        "unknown basis",
        "basis unavailable",
        "no basis for element",
    ],
    ErrorCategory.METHOD: [
        "unknown method",
        "method not available",
        "invalid method",
        "method not implemented",
    ],
    ErrorCategory.LINEAR_DEPENDENCY: [
        "linear dependency",
        "linearly dependent",
        "overlap eigenvalue",
        "s_min_eigenvalue",
        "basis nearly singular",
    ],
    ErrorCategory.SYMMETRY: [
        "symmetry",
        "point group",
        "irrep",
        "symmetry operation",
    ],
    ErrorCategory.NUMERICAL: [
        "nan",
        "inf",
        "numerical instability",
        "divide by zero",
        "overflow",
    ],
}


def categorize_error(error_message: str) -> ErrorCategory:
    """
    Categorize an error message.
    
    Args:
        error_message: Error message to categorize
        
    Returns:
        ErrorCategory for the error
    """
    message_lower = error_message.lower()
    
    for category, patterns in _CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if pattern in message_lower:
                return category
    
    return ErrorCategory.UNKNOWN


def get_error_category(
    error_message: str,
    error_type: Optional[str] = None,
) -> ErrorInfo:
    """
    Get detailed error category information.
    
    Args:
        error_message: Error message
        error_type: Type of error (e.g., exception type)
        
    Returns:
        ErrorInfo with categorization
    """
    category = categorize_error(error_message)
    
    # Determine severity
    severity = _get_severity(category, error_message)
    
    # Determine if recoverable
    recoverable = _is_recoverable(category)
    
    # Get basic suggestions
    suggestions = _get_basic_suggestions(category)
    
    return ErrorInfo(
        category=category,
        severity=severity,
        message=_get_category_description(category),
        original_error=error_message,
        recoverable=recoverable,
        suggestions=suggestions,
    )


def _get_severity(category: ErrorCategory, message: str) -> ErrorSeverity:
    """Determine error severity."""
    # Critical errors
    critical_categories = {
        ErrorCategory.MEMORY,
        ErrorCategory.DISK,
        ErrorCategory.INSTALLATION,
    }
    
    if category in critical_categories:
        return ErrorSeverity.CRITICAL
    
    # Check for warning indicators
    message_lower = message.lower()
    if "warning" in message_lower:
        return ErrorSeverity.WARNING
    
    # Convergence issues are typically recoverable
    convergence_categories = {
        ErrorCategory.CONVERGENCE,
        ErrorCategory.SCF_CONVERGENCE,
        ErrorCategory.GEOMETRY_CONVERGENCE,
        ErrorCategory.TDDFT_CONVERGENCE,
        ErrorCategory.CC_CONVERGENCE,
    }
    
    if category in convergence_categories:
        return ErrorSeverity.ERROR
    
    return ErrorSeverity.ERROR


def _is_recoverable(category: ErrorCategory) -> bool:
    """Check if error category is recoverable."""
    recoverable_categories = {
        ErrorCategory.CONVERGENCE,
        ErrorCategory.SCF_CONVERGENCE,
        ErrorCategory.GEOMETRY_CONVERGENCE,
        ErrorCategory.TDDFT_CONVERGENCE,
        ErrorCategory.CC_CONVERGENCE,
        ErrorCategory.LINEAR_DEPENDENCY,
        ErrorCategory.OPTIONS,
    }
    
    return category in recoverable_categories


def _get_category_description(category: ErrorCategory) -> str:
    """Get human-readable description for category."""
    descriptions = {
        ErrorCategory.CONVERGENCE: "Calculation did not converge",
        ErrorCategory.SCF_CONVERGENCE: "SCF wavefunction did not converge",
        ErrorCategory.GEOMETRY_CONVERGENCE: "Geometry optimization did not converge",
        ErrorCategory.TDDFT_CONVERGENCE: "TDDFT excited states did not converge",
        ErrorCategory.CC_CONVERGENCE: "Coupled cluster amplitudes did not converge",
        ErrorCategory.MEMORY: "Insufficient memory for calculation",
        ErrorCategory.DISK: "Disk space or I/O error",
        ErrorCategory.TIMEOUT: "Calculation exceeded time limit",
        ErrorCategory.GEOMETRY: "Invalid molecular geometry",
        ErrorCategory.BASIS_SET: "Basis set error",
        ErrorCategory.METHOD: "Invalid or unavailable method",
        ErrorCategory.OPTIONS: "Invalid calculation options",
        ErrorCategory.SYMMETRY: "Symmetry handling error",
        ErrorCategory.LINEAR_DEPENDENCY: "Linear dependency in basis set",
        ErrorCategory.SINGULARITY: "Singular matrix encountered",
        ErrorCategory.NUMERICAL: "Numerical instability",
        ErrorCategory.ENVIRONMENT: "Environment configuration error",
        ErrorCategory.INSTALLATION: "Psi4 installation issue",
        ErrorCategory.UNKNOWN: "Unknown error",
    }
    
    return descriptions.get(category, "Unknown error")


def _get_basic_suggestions(category: ErrorCategory) -> List[str]:
    """Get basic suggestions for error category."""
    suggestions: Dict[ErrorCategory, List[str]] = {
        ErrorCategory.SCF_CONVERGENCE: [
            "Try SOSCF algorithm",
            "Increase damping percentage",
            "Try level shift",
            "Check initial guess",
        ],
        ErrorCategory.GEOMETRY_CONVERGENCE: [
            "Check initial geometry",
            "Try smaller step size",
            "Use different coordinate system",
            "Increase max iterations",
        ],
        ErrorCategory.MEMORY: [
            "Reduce basis set size",
            "Use density fitting",
            "Increase available memory",
            "Try smaller system",
        ],
        ErrorCategory.GEOMETRY: [
            "Check atom coordinates",
            "Ensure atoms not too close",
            "Verify charge and multiplicity",
        ],
        ErrorCategory.BASIS_SET: [
            "Verify basis set name",
            "Check element coverage",
            "Try smaller basis set",
        ],
        ErrorCategory.LINEAR_DEPENDENCY: [
            "Use smaller basis set",
            "Adjust S_MIN_EIGENVALUE",
            "Try def2 basis sets",
        ],
    }
    
    return suggestions.get(category, ["Check calculation input"])


def is_convergence_error(category: ErrorCategory) -> bool:
    """Check if category is a convergence error."""
    convergence_categories = {
        ErrorCategory.CONVERGENCE,
        ErrorCategory.SCF_CONVERGENCE,
        ErrorCategory.GEOMETRY_CONVERGENCE,
        ErrorCategory.TDDFT_CONVERGENCE,
        ErrorCategory.CC_CONVERGENCE,
    }
    return category in convergence_categories


def is_resource_error(category: ErrorCategory) -> bool:
    """Check if category is a resource error."""
    resource_categories = {
        ErrorCategory.MEMORY,
        ErrorCategory.DISK,
        ErrorCategory.TIMEOUT,
    }
    return category in resource_categories


def is_input_error(category: ErrorCategory) -> bool:
    """Check if category is an input error."""
    input_categories = {
        ErrorCategory.GEOMETRY,
        ErrorCategory.BASIS_SET,
        ErrorCategory.METHOD,
        ErrorCategory.OPTIONS,
        ErrorCategory.SYMMETRY,
    }
    return category in input_categories
