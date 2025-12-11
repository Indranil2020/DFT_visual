"""
Error and Result Types for Psi4 MCP Server.

This module defines structured error types and result containers for
quantum chemistry calculations. Instead of using exceptions, we use
explicit result types that carry either success data or error information.

Key Design Principles:
    - Explicit error handling through result types
    - Detailed error categorization
    - Recovery suggestions
    - Full error context preservation
"""

from typing import Generic, TypeVar, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# Type variable for generic result type
T = TypeVar("T")


# =============================================================================
# ERROR CATEGORIES
# =============================================================================

class ErrorCategory(str, Enum):
    """
    High-level categorization of errors.
    
    Attributes:
        INPUT: Invalid input parameters or data
        VALIDATION: Validation failure
        CALCULATION: Error during calculation
        CONVERGENCE: Convergence failure
        RESOURCE: Resource limitation (memory, time, etc.)
        CONFIGURATION: Configuration or setup error
        INTERNAL: Internal/unexpected error
        EXTERNAL: External dependency error
    """
    INPUT = "input"
    VALIDATION = "validation"
    CALCULATION = "calculation"
    CONVERGENCE = "convergence"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    INTERNAL = "internal"
    EXTERNAL = "external"


class ErrorSeverity(str, Enum):
    """
    Error severity levels.
    
    Attributes:
        WARNING: Non-fatal issue, calculation may proceed
        ERROR: Fatal error, calculation cannot proceed
        CRITICAL: Critical error, may affect system stability
    """
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ConvergenceType(str, Enum):
    """
    Types of convergence failures.
    
    Attributes:
        SCF: SCF convergence failure
        GEOMETRY: Geometry optimization convergence failure
        CORRELATION: Correlation method convergence failure
        TDDFT: TDDFT/response convergence failure
        CASSCF: CASSCF convergence failure
    """
    SCF = "scf"
    GEOMETRY = "geometry"
    CORRELATION = "correlation"
    TDDFT = "tddft"
    CASSCF = "casscf"


# =============================================================================
# ERROR DATA CLASSES
# =============================================================================

@dataclass
class ErrorContext:
    """
    Context information for an error.
    
    Attributes:
        method: Calculation method being used
        basis_set: Basis set being used
        molecule: Molecule identifier or formula
        step: Current step/iteration
        file: File where error occurred
        line: Line number in file
        function: Function where error occurred
        timestamp: When the error occurred
        additional: Additional context information
    """
    method: Optional[str] = None
    basis_set: Optional[str] = None
    molecule: Optional[str] = None
    step: Optional[int] = None
    file: Optional[str] = None
    line: Optional[int] = None
    function: Optional[str] = None
    timestamp: Optional[datetime] = None
    additional: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        if self.method:
            result["method"] = self.method
        if self.basis_set:
            result["basis_set"] = self.basis_set
        if self.molecule:
            result["molecule"] = self.molecule
        if self.step is not None:
            result["step"] = self.step
        if self.file:
            result["file"] = self.file
        if self.line is not None:
            result["line"] = self.line
        if self.function:
            result["function"] = self.function
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        if self.additional:
            result["additional"] = self.additional
        return result


@dataclass
class RecoverySuggestion:
    """
    A suggestion for recovering from an error.
    
    Attributes:
        description: Human-readable description of the suggestion
        action: Specific action to take
        parameter: Parameter to modify
        suggested_value: Suggested new value
        confidence: Confidence that this will help (0-1)
    """
    description: str
    action: Optional[str] = None
    parameter: Optional[str] = None
    suggested_value: Optional[Any] = None
    confidence: float = 0.5
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {"description": self.description, "confidence": self.confidence}
        if self.action:
            result["action"] = self.action
        if self.parameter:
            result["parameter"] = self.parameter
        if self.suggested_value is not None:
            result["suggested_value"] = self.suggested_value
        return result


@dataclass
class CalculationError:
    """
    Detailed error information for a calculation failure.
    
    Attributes:
        code: Error code (for programmatic handling)
        message: Human-readable error message
        category: Error category
        severity: Error severity
        context: Error context information
        suggestions: Recovery suggestions
        details: Additional error details
        cause: Underlying cause (if known)
    """
    code: str
    message: str
    category: ErrorCategory = ErrorCategory.CALCULATION
    severity: ErrorSeverity = ErrorSeverity.ERROR
    context: Optional[ErrorContext] = None
    suggestions: list[RecoverySuggestion] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    cause: Optional[str] = None
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
    
    def __repr__(self) -> str:
        return f"CalculationError(code='{self.code}', message='{self.message}')"
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "code": self.code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
        }
        if self.context:
            result["context"] = self.context.to_dict()
        if self.suggestions:
            result["suggestions"] = [s.to_dict() for s in self.suggestions]
        if self.details:
            result["details"] = self.details
        if self.cause:
            result["cause"] = self.cause
        return result
    
    def with_context(self, **kwargs: Any) -> "CalculationError":
        """Return a new error with additional context."""
        if self.context is None:
            new_context = ErrorContext(**kwargs)
        else:
            context_dict = self.context.to_dict()
            context_dict.update(kwargs)
            # Remove timestamp as it's auto-generated
            context_dict.pop("timestamp", None)
            new_context = ErrorContext(**context_dict)
        
        return CalculationError(
            code=self.code,
            message=self.message,
            category=self.category,
            severity=self.severity,
            context=new_context,
            suggestions=self.suggestions.copy(),
            details=self.details.copy(),
            cause=self.cause,
        )
    
    def with_suggestion(
        self,
        description: str,
        action: Optional[str] = None,
        parameter: Optional[str] = None,
        suggested_value: Optional[Any] = None,
        confidence: float = 0.5
    ) -> "CalculationError":
        """Return a new error with an additional suggestion."""
        new_suggestions = self.suggestions.copy()
        new_suggestions.append(RecoverySuggestion(
            description=description,
            action=action,
            parameter=parameter,
            suggested_value=suggested_value,
            confidence=confidence,
        ))
        
        return CalculationError(
            code=self.code,
            message=self.message,
            category=self.category,
            severity=self.severity,
            context=self.context,
            suggestions=new_suggestions,
            details=self.details.copy(),
            cause=self.cause,
        )


# =============================================================================
# RESULT TYPES
# =============================================================================

@dataclass
class Result(Generic[T]):
    """
    A result type that holds either a success value or an error.
    
    This is similar to Rust's Result type or Haskell's Either.
    
    Attributes:
        value: The success value (if successful)
        error: The error (if failed)
        warnings: Non-fatal warnings
    """
    value: Optional[T] = None
    error: Optional[CalculationError] = None
    warnings: list[CalculationError] = field(default_factory=list)
    
    @property
    def is_success(self) -> bool:
        """Check if the result is successful."""
        return self.error is None
    
    @property
    def is_failure(self) -> bool:
        """Check if the result is a failure."""
        return self.error is not None
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0
    
    def unwrap(self) -> T:
        """
        Get the success value, or raise ValueError if failed.
        
        Returns:
            The success value.
        """
        if self.error is not None:
            raise ValueError(f"Cannot unwrap failed result: {self.error}")
        if self.value is None:
            raise ValueError("Cannot unwrap None value")
        return self.value
    
    def unwrap_or(self, default: T) -> T:
        """
        Get the success value, or return a default if failed.
        
        Args:
            default: Default value to return on failure.
            
        Returns:
            The success value or default.
        """
        if self.error is not None or self.value is None:
            return default
        return self.value
    
    def map(self, func: Any) -> "Result[Any]":
        """
        Apply a function to the success value.
        
        Args:
            func: Function to apply.
            
        Returns:
            New Result with transformed value.
        """
        if self.error is not None:
            return Result(error=self.error, warnings=self.warnings)
        if self.value is None:
            return Result(warnings=self.warnings)
        return Result(value=func(self.value), warnings=self.warnings)
    
    @classmethod
    def success(cls, value: T, warnings: Optional[list[CalculationError]] = None) -> "Result[T]":
        """Create a successful result."""
        return cls(value=value, warnings=warnings or [])
    
    @classmethod
    def failure(
        cls,
        error: CalculationError,
        warnings: Optional[list[CalculationError]] = None
    ) -> "Result[T]":
        """Create a failed result."""
        return cls(error=error, warnings=warnings or [])
    
    @classmethod
    def from_error_code(
        cls,
        code: str,
        message: str,
        category: ErrorCategory = ErrorCategory.CALCULATION,
        **kwargs: Any
    ) -> "Result[T]":
        """Create a failed result from error details."""
        error = CalculationError(code=code, message=message, category=category, **kwargs)
        return cls(error=error)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result: dict[str, Any] = {
            "success": self.is_success,
        }
        if self.value is not None:
            if hasattr(self.value, 'to_dict'):
                result["value"] = self.value.to_dict()  # type: ignore
            else:
                result["value"] = self.value
        if self.error is not None:
            result["error"] = self.error.to_dict()
        if self.warnings:
            result["warnings"] = [w.to_dict() for w in self.warnings]
        return result


# =============================================================================
# COMMON ERROR FACTORIES
# =============================================================================

def input_error(
    message: str,
    parameter: Optional[str] = None,
    value: Optional[Any] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create an input validation error.
    
    Args:
        message: Error message.
        parameter: Name of the invalid parameter.
        value: The invalid value.
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for input validation.
    """
    details: dict[str, Any] = kwargs
    if parameter:
        details["parameter"] = parameter
    if value is not None:
        details["value"] = value
    
    return CalculationError(
        code="INPUT_ERROR",
        message=message,
        category=ErrorCategory.INPUT,
        severity=ErrorSeverity.ERROR,
        details=details,
    )


def validation_error(
    message: str,
    field: Optional[str] = None,
    constraint: Optional[str] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create a validation error.
    
    Args:
        message: Error message.
        field: Field that failed validation.
        constraint: Constraint that was violated.
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for validation.
    """
    details: dict[str, Any] = kwargs
    if field:
        details["field"] = field
    if constraint:
        details["constraint"] = constraint
    
    return CalculationError(
        code="VALIDATION_ERROR",
        message=message,
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.ERROR,
        details=details,
    )


def convergence_error(
    convergence_type: ConvergenceType,
    message: str,
    iterations: Optional[int] = None,
    final_error: Optional[float] = None,
    threshold: Optional[float] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create a convergence failure error.
    
    Args:
        convergence_type: Type of convergence failure.
        message: Error message.
        iterations: Number of iterations attempted.
        final_error: Final error value.
        threshold: Convergence threshold.
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for convergence failure.
    """
    details: dict[str, Any] = {"convergence_type": convergence_type.value}
    details.update(kwargs)
    
    if iterations is not None:
        details["iterations"] = iterations
    if final_error is not None:
        details["final_error"] = final_error
    if threshold is not None:
        details["threshold"] = threshold
    
    error = CalculationError(
        code=f"CONVERGENCE_{convergence_type.value.upper()}",
        message=message,
        category=ErrorCategory.CONVERGENCE,
        severity=ErrorSeverity.ERROR,
        details=details,
    )
    
    # Add common suggestions based on type
    if convergence_type == ConvergenceType.SCF:
        error = error.with_suggestion(
            "Increase maximum SCF iterations",
            parameter="maxiter",
            suggested_value=200,
            confidence=0.6,
        ).with_suggestion(
            "Use a different SCF algorithm (e.g., DIIS, SOSCF)",
            parameter="scf_type",
            confidence=0.5,
        ).with_suggestion(
            "Try level shifting for difficult cases",
            parameter="level_shift",
            suggested_value=0.5,
            confidence=0.4,
        )
    elif convergence_type == ConvergenceType.GEOMETRY:
        error = error.with_suggestion(
            "Increase maximum geometry optimization steps",
            parameter="geom_maxiter",
            suggested_value=200,
            confidence=0.5,
        ).with_suggestion(
            "Use a different optimization algorithm",
            parameter="opt_type",
            confidence=0.4,
        )
    
    return error


def resource_error(
    message: str,
    resource_type: str,
    requested: Optional[Any] = None,
    available: Optional[Any] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create a resource limitation error.
    
    Args:
        message: Error message.
        resource_type: Type of resource (memory, disk, time, etc.).
        requested: Requested amount.
        available: Available amount.
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for resource limitation.
    """
    details: dict[str, Any] = {"resource_type": resource_type}
    details.update(kwargs)
    
    if requested is not None:
        details["requested"] = requested
    if available is not None:
        details["available"] = available
    
    return CalculationError(
        code=f"RESOURCE_{resource_type.upper()}",
        message=message,
        category=ErrorCategory.RESOURCE,
        severity=ErrorSeverity.ERROR,
        details=details,
    )


def method_error(
    message: str,
    method: str,
    reason: Optional[str] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create an error for unsupported or invalid method.
    
    Args:
        message: Error message.
        method: The method that caused the error.
        reason: Reason for the error.
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for method issues.
    """
    details: dict[str, Any] = {"method": method}
    details.update(kwargs)
    
    if reason:
        details["reason"] = reason
    
    return CalculationError(
        code="METHOD_ERROR",
        message=message,
        category=ErrorCategory.CALCULATION,
        severity=ErrorSeverity.ERROR,
        details=details,
    )


def basis_set_error(
    message: str,
    basis_set: str,
    element: Optional[str] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create an error for basis set issues.
    
    Args:
        message: Error message.
        basis_set: The basis set that caused the error.
        element: Element with the issue (if applicable).
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for basis set issues.
    """
    details: dict[str, Any] = {"basis_set": basis_set}
    details.update(kwargs)
    
    if element:
        details["element"] = element
    
    return CalculationError(
        code="BASIS_SET_ERROR",
        message=message,
        category=ErrorCategory.INPUT,
        severity=ErrorSeverity.ERROR,
        details=details,
    )


def geometry_error(
    message: str,
    atom_indices: Optional[list[int]] = None,
    **kwargs: Any
) -> CalculationError:
    """
    Create an error for geometry issues.
    
    Args:
        message: Error message.
        atom_indices: Indices of atoms involved.
        **kwargs: Additional error details.
        
    Returns:
        CalculationError for geometry issues.
    """
    details: dict[str, Any] = kwargs
    if atom_indices:
        details["atom_indices"] = atom_indices
    
    return CalculationError(
        code="GEOMETRY_ERROR",
        message=message,
        category=ErrorCategory.INPUT,
        severity=ErrorSeverity.ERROR,
        details=details,
    )


def warning(
    message: str,
    code: str = "WARNING",
    category: ErrorCategory = ErrorCategory.CALCULATION,
    **kwargs: Any
) -> CalculationError:
    """
    Create a warning (non-fatal).
    
    Args:
        message: Warning message.
        code: Warning code.
        category: Warning category.
        **kwargs: Additional details.
        
    Returns:
        CalculationError with warning severity.
    """
    return CalculationError(
        code=code,
        message=message,
        category=category,
        severity=ErrorSeverity.WARNING,
        details=kwargs,
    )
