"""
Error Detection for Psi4 MCP Server.

Provides error detection and pattern matching for Psi4 errors.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Tuple

from psi4_mcp.utils.error_handling.categorization import (
    ErrorCategory,
    ErrorInfo,
    ErrorSeverity,
    get_error_category,
)


@dataclass
class ErrorPattern:
    """Pattern for detecting specific errors."""
    name: str
    pattern: str
    category: ErrorCategory
    severity: ErrorSeverity
    message_template: str
    suggestions: List[str] = field(default_factory=list)
    extract_groups: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Compile the pattern."""
        self._compiled: Pattern = re.compile(self.pattern, re.IGNORECASE | re.MULTILINE)
    
    def match(self, text: str) -> Optional[re.Match]:
        """Match pattern against text."""
        return self._compiled.search(text)
    
    def extract_info(self, match: re.Match) -> Dict[str, str]:
        """Extract named groups from match."""
        result = {}
        for group in self.extract_groups:
            value = match.group(group) if group in match.groupdict() else None
            if value:
                result[group] = value
        return result


class ErrorDetector:
    """
    Detects and categorizes Psi4 errors.
    
    Uses pattern matching to identify specific error types
    and extract relevant information.
    """
    
    def __init__(self):
        """Initialize with default error patterns."""
        self._patterns: List[ErrorPattern] = []
        self._setup_default_patterns()
    
    def _setup_default_patterns(self) -> None:
        """Set up default error detection patterns."""
        # SCF convergence errors
        self._patterns.append(ErrorPattern(
            name="scf_not_converged",
            pattern=r"could not converge scf in (?P<iterations>\d+) iterations",
            category=ErrorCategory.SCF_CONVERGENCE,
            severity=ErrorSeverity.ERROR,
            message_template="SCF did not converge in {iterations} iterations",
            suggestions=["Try SOSCF", "Increase damping", "Try level shift"],
            extract_groups=["iterations"],
        ))
        
        self._patterns.append(ErrorPattern(
            name="scf_diis_error",
            pattern=r"diis error.*?(?P<error>[\d.e+-]+)",
            category=ErrorCategory.SCF_CONVERGENCE,
            severity=ErrorSeverity.ERROR,
            message_template="DIIS error: {error}",
            suggestions=["Increase DIIS vectors", "Try SOSCF"],
            extract_groups=["error"],
        ))
        
        # Geometry optimization errors
        self._patterns.append(ErrorPattern(
            name="geom_not_converged",
            pattern=r"geometry optimization did not converge in (?P<steps>\d+) steps",
            category=ErrorCategory.GEOMETRY_CONVERGENCE,
            severity=ErrorSeverity.ERROR,
            message_template="Optimization did not converge in {steps} steps",
            suggestions=["Increase max iterations", "Try smaller step size"],
            extract_groups=["steps"],
        ))
        
        self._patterns.append(ErrorPattern(
            name="geom_step_too_large",
            pattern=r"step.*too large.*(?P<size>[\d.e+-]+)",
            category=ErrorCategory.GEOMETRY_CONVERGENCE,
            severity=ErrorSeverity.WARNING,
            message_template="Step size too large: {size}",
            suggestions=["Reduce trust radius", "Use internal coordinates"],
            extract_groups=["size"],
        ))
        
        # Memory errors
        self._patterns.append(ErrorPattern(
            name="memory_insufficient",
            pattern=r"(?:insufficient|not enough) memory.*?(?P<needed>[\d.]+)\s*(?P<unit>MB|GB)?",
            category=ErrorCategory.MEMORY,
            severity=ErrorSeverity.CRITICAL,
            message_template="Insufficient memory: need {needed} {unit}",
            suggestions=["Increase memory allocation", "Use density fitting", "Reduce basis set"],
            extract_groups=["needed", "unit"],
        ))
        
        self._patterns.append(ErrorPattern(
            name="memory_allocation_failed",
            pattern=r"(?:malloc|allocation) failed",
            category=ErrorCategory.MEMORY,
            severity=ErrorSeverity.CRITICAL,
            message_template="Memory allocation failed",
            suggestions=["Increase system memory", "Reduce calculation size"],
            extract_groups=[],
        ))
        
        # Basis set errors
        self._patterns.append(ErrorPattern(
            name="basis_not_found",
            pattern=r"basis set ['\"]?(?P<basis>\S+)['\"]? not found",
            category=ErrorCategory.BASIS_SET,
            severity=ErrorSeverity.ERROR,
            message_template="Basis set '{basis}' not found",
            suggestions=["Check basis set name spelling", "Try alternative basis set"],
            extract_groups=["basis"],
        ))
        
        self._patterns.append(ErrorPattern(
            name="basis_element_missing",
            pattern=r"no basis.*for element (?P<element>\w+)",
            category=ErrorCategory.BASIS_SET,
            severity=ErrorSeverity.ERROR,
            message_template="No basis functions for element {element}",
            suggestions=["Use different basis set", "Check element symbol"],
            extract_groups=["element"],
        ))
        
        # Geometry errors
        self._patterns.append(ErrorPattern(
            name="atoms_too_close",
            pattern=r"atoms.*too close.*(?P<distance>[\d.]+)\s*(?P<unit>angstrom|bohr)?",
            category=ErrorCategory.GEOMETRY,
            severity=ErrorSeverity.ERROR,
            message_template="Atoms too close: {distance} {unit}",
            suggestions=["Check geometry", "Increase interatomic distances"],
            extract_groups=["distance", "unit"],
        ))
        
        self._patterns.append(ErrorPattern(
            name="linear_molecule",
            pattern=r"linear molecule.*(?:detected|problem)",
            category=ErrorCategory.GEOMETRY,
            severity=ErrorSeverity.WARNING,
            message_template="Linear molecule detected",
            suggestions=["Check symmetry settings", "Use C1 symmetry"],
            extract_groups=[],
        ))
        
        # Linear dependency
        self._patterns.append(ErrorPattern(
            name="linear_dependency",
            pattern=r"linear dependency.*eigenvalue.*(?P<eigenvalue>[\d.e+-]+)",
            category=ErrorCategory.LINEAR_DEPENDENCY,
            severity=ErrorSeverity.WARNING,
            message_template="Linear dependency: eigenvalue {eigenvalue}",
            suggestions=["Use smaller basis set", "Adjust S_MIN_EIGENVALUE"],
            extract_groups=["eigenvalue"],
        ))
        
        # TDDFT errors
        self._patterns.append(ErrorPattern(
            name="tddft_not_converged",
            pattern=r"(?:tddft|tdscf).*not converge.*(?P<root>\d+)?",
            category=ErrorCategory.TDDFT_CONVERGENCE,
            severity=ErrorSeverity.ERROR,
            message_template="TDDFT root {root} did not converge" if "{root}" else "TDDFT did not converge",
            suggestions=["Increase max iterations", "Try TDA", "Increase guess vectors"],
            extract_groups=["root"],
        ))
        
        # Numerical errors
        self._patterns.append(ErrorPattern(
            name="nan_detected",
            pattern=r"nan|not a number",
            category=ErrorCategory.NUMERICAL,
            severity=ErrorSeverity.CRITICAL,
            message_template="NaN detected in calculation",
            suggestions=["Check geometry", "Try different initial guess", "Use more stable algorithm"],
            extract_groups=[],
        ))
    
    def add_pattern(self, pattern: ErrorPattern) -> None:
        """Add a custom error pattern."""
        self._patterns.append(pattern)
    
    def detect(self, text: str) -> List[ErrorInfo]:
        """
        Detect all errors in text.
        
        Args:
            text: Text to search for errors
            
        Returns:
            List of detected ErrorInfo objects
        """
        detected = []
        
        for pattern in self._patterns:
            match = pattern.match(text)
            if match:
                # Extract information from match
                extracted = pattern.extract_info(match)
                
                # Format message with extracted info
                message = pattern.message_template
                for key, value in extracted.items():
                    message = message.replace(f"{{{key}}}", str(value))
                
                error_info = ErrorInfo(
                    category=pattern.category,
                    severity=pattern.severity,
                    message=message,
                    original_error=match.group(0),
                    recoverable=pattern.severity != ErrorSeverity.CRITICAL,
                    suggestions=list(pattern.suggestions),
                    context=extracted,
                )
                detected.append(error_info)
        
        return detected
    
    def detect_first(self, text: str) -> Optional[ErrorInfo]:
        """
        Detect first error in text.
        
        Args:
            text: Text to search
            
        Returns:
            First detected error or None
        """
        errors = self.detect(text)
        return errors[0] if errors else None
    
    def detect_by_category(
        self,
        text: str,
        categories: List[ErrorCategory],
    ) -> List[ErrorInfo]:
        """
        Detect errors of specific categories.
        
        Args:
            text: Text to search
            categories: Categories to filter by
            
        Returns:
            Errors matching specified categories
        """
        all_errors = self.detect(text)
        return [e for e in all_errors if e.category in categories]


# Global detector instance
_detector: Optional[ErrorDetector] = None


def get_error_detector() -> ErrorDetector:
    """Get the global error detector instance."""
    global _detector
    if _detector is None:
        _detector = ErrorDetector()
    return _detector


def detect_error(text: str) -> Optional[ErrorInfo]:
    """
    Detect error in text.
    
    Convenience function using global detector.
    
    Args:
        text: Text to search
        
    Returns:
        Detected error or None
    """
    detector = get_error_detector()
    return detector.detect_first(text)


def detect_psi4_error(
    output: str,
    error_message: Optional[str] = None,
) -> Optional[ErrorInfo]:
    """
    Detect Psi4-specific error from output.
    
    Args:
        output: Psi4 output text
        error_message: Optional error message from exception
        
    Returns:
        Detected error information
    """
    detector = get_error_detector()
    
    # First check the error message if provided
    if error_message:
        error = detector.detect_first(error_message)
        if error:
            return error
    
    # Then check the full output
    error = detector.detect_first(output)
    if error:
        return error
    
    # Fall back to basic categorization
    if error_message:
        return get_error_category(error_message)
    
    return None


def parse_error_message(message: str) -> Dict[str, Any]:
    """
    Parse error message and extract components.
    
    Args:
        message: Error message to parse
        
    Returns:
        Dictionary with parsed components
    """
    result: Dict[str, Any] = {
        "raw_message": message,
        "components": [],
        "numbers": [],
        "identifiers": [],
    }
    
    # Extract numbers
    numbers = re.findall(r'[\d.]+(?:e[+-]?\d+)?', message, re.IGNORECASE)
    result["numbers"] = [float(n) for n in numbers if n]
    
    # Extract potential identifiers (basis sets, methods, etc.)
    identifiers = re.findall(r'\b[a-z][\w\-]+(?:\([^)]*\))?\b', message, re.IGNORECASE)
    result["identifiers"] = identifiers
    
    # Split into components
    components = re.split(r'[;:,\n]', message)
    result["components"] = [c.strip() for c in components if c.strip()]
    
    return result


def detect_convergence_issue(
    energy_history: List[float],
    threshold: float = 1e-6,
) -> Tuple[bool, str]:
    """
    Detect convergence issues from energy history.
    
    Args:
        energy_history: List of energies per iteration
        threshold: Convergence threshold
        
    Returns:
        Tuple of (has_issue, issue_description)
    """
    if len(energy_history) < 2:
        return False, "Insufficient data"
    
    # Calculate changes
    changes = [abs(energy_history[i] - energy_history[i-1]) 
               for i in range(1, len(energy_history))]
    
    # Check if converged
    if changes[-1] < threshold:
        return False, "Converged"
    
    # Check for oscillation
    if len(changes) >= 6:
        increasing = sum(1 for i in range(1, len(changes)) 
                        if changes[i] > changes[i-1])
        if increasing > len(changes) * 0.4:
            return True, "Oscillating convergence"
    
    # Check for divergence
    if len(changes) >= 3:
        if all(changes[i] > changes[i-1] for i in range(-2, 0)):
            return True, "Diverging"
    
    # Check for slow convergence
    if len(changes) >= 10:
        recent_avg = sum(changes[-5:]) / 5
        early_avg = sum(changes[:5]) / 5
        if recent_avg > early_avg * 0.5:
            return True, "Slow convergence"
    
    return True, "Not converged"
