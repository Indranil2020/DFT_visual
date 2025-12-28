"""
Error Suggestions for Psi4 MCP Server.

Provides intelligent suggestions for resolving errors.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from psi4_mcp.utils.error_handling.categorization import ErrorCategory, ErrorInfo, ErrorSeverity


class SuggestionPriority(int, Enum):
    """Priority levels for suggestions."""
    CRITICAL = 1    # Try this first
    HIGH = 2        # Very likely to help
    MEDIUM = 3      # Moderately likely
    LOW = 4         # Worth trying
    INFORMATIONAL = 5  # Background info


@dataclass
class ErrorSuggestion:
    """A suggestion for resolving an error."""
    text: str
    priority: SuggestionPriority
    category: ErrorCategory
    option_changes: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    requires_user_action: bool = False
    code_example: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "priority": self.priority.name,
            "category": self.category.value,
            "option_changes": self.option_changes,
            "explanation": self.explanation,
            "requires_user_action": self.requires_user_action,
            "code_example": self.code_example,
        }


class SuggestionEngine:
    """
    Engine for generating error suggestions.
    
    Provides context-aware suggestions based on error type,
    system characteristics, and calculation history.
    """
    
    def __init__(self):
        """Initialize suggestion engine."""
        self._suggestion_database = self._build_suggestion_database()
    
    def _build_suggestion_database(self) -> Dict[ErrorCategory, List[ErrorSuggestion]]:
        """Build the suggestion database."""
        database: Dict[ErrorCategory, List[ErrorSuggestion]] = {}
        
        # SCF Convergence suggestions
        database[ErrorCategory.SCF_CONVERGENCE] = [
            ErrorSuggestion(
                text="Enable SOSCF (Second-Order SCF) algorithm",
                priority=SuggestionPriority.CRITICAL,
                category=ErrorCategory.SCF_CONVERGENCE,
                option_changes={"soscf": True, "soscf_start_convergence": 1e-3},
                explanation="SOSCF provides quadratic convergence near the solution",
            ),
            ErrorSuggestion(
                text="Apply Fock matrix damping",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.SCF_CONVERGENCE,
                option_changes={"damping_percentage": 20.0},
                explanation="Damping reduces oscillations in SCF iterations",
            ),
            ErrorSuggestion(
                text="Apply level shift to virtual orbitals",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.SCF_CONVERGENCE,
                option_changes={"level_shift": 0.5},
                explanation="Level shift increases HOMO-LUMO gap for stability",
            ),
            ErrorSuggestion(
                text="Try SAD (Superposition of Atomic Densities) initial guess",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.SCF_CONVERGENCE,
                option_changes={"guess": "sad"},
                explanation="SAD often provides better starting point than core guess",
            ),
            ErrorSuggestion(
                text="Increase maximum SCF iterations",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.SCF_CONVERGENCE,
                option_changes={"maxiter": 200},
                explanation="Some systems simply need more iterations",
            ),
            ErrorSuggestion(
                text="Increase DIIS vector space",
                priority=SuggestionPriority.LOW,
                category=ErrorCategory.SCF_CONVERGENCE,
                option_changes={"diis_max_vecs": 12},
                explanation="More DIIS vectors can improve extrapolation",
            ),
        ]
        
        # Geometry optimization suggestions
        database[ErrorCategory.GEOMETRY_CONVERGENCE] = [
            ErrorSuggestion(
                text="Reduce optimization step size",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.GEOMETRY_CONVERGENCE,
                option_changes={"step_limit": 0.1},
                explanation="Smaller steps are more conservative but reliable",
            ),
            ErrorSuggestion(
                text="Increase maximum optimization steps",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.GEOMETRY_CONVERGENCE,
                option_changes={"geom_maxiter": 100},
                explanation="Complex systems may need more iterations",
            ),
            ErrorSuggestion(
                text="Use RFO (Rational Function Optimization) step",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.GEOMETRY_CONVERGENCE,
                option_changes={"step_type": "rfo"},
                explanation="RFO is often more robust than Newton-Raphson",
            ),
            ErrorSuggestion(
                text="Switch to internal coordinates",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.GEOMETRY_CONVERGENCE,
                option_changes={"opt_coordinates": "internal"},
                explanation="Internal coordinates often converge faster",
            ),
            ErrorSuggestion(
                text="Verify starting geometry is reasonable",
                priority=SuggestionPriority.LOW,
                category=ErrorCategory.GEOMETRY_CONVERGENCE,
                requires_user_action=True,
                explanation="Poor initial geometry can prevent convergence",
            ),
        ]
        
        # Memory suggestions
        database[ErrorCategory.MEMORY] = [
            ErrorSuggestion(
                text="Enable density fitting",
                priority=SuggestionPriority.CRITICAL,
                category=ErrorCategory.MEMORY,
                option_changes={"scf_type": "df"},
                explanation="DF reduces memory from O(N^4) to O(N^2)",
            ),
            ErrorSuggestion(
                text="Reduce DIIS vector storage",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.MEMORY,
                option_changes={"diis_max_vecs": 4},
                explanation="Fewer DIIS vectors reduce memory",
            ),
            ErrorSuggestion(
                text="Use smaller basis set",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.MEMORY,
                requires_user_action=True,
                explanation="Smaller basis means fewer integrals",
            ),
            ErrorSuggestion(
                text="Increase system memory allocation",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.MEMORY,
                requires_user_action=True,
                explanation="Set psi4.set_memory() to larger value",
                code_example="psi4.set_memory('8 GB')",
            ),
        ]
        
        # Basis set suggestions
        database[ErrorCategory.BASIS_SET] = [
            ErrorSuggestion(
                text="Check basis set name spelling",
                priority=SuggestionPriority.CRITICAL,
                category=ErrorCategory.BASIS_SET,
                requires_user_action=True,
                explanation="Common mistake: '6-31G*' vs '6-31g*'",
            ),
            ErrorSuggestion(
                text="Use def2 basis sets for better element coverage",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.BASIS_SET,
                requires_user_action=True,
                explanation="def2 series covers most elements",
            ),
            ErrorSuggestion(
                text="Check if basis set supports all elements",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.BASIS_SET,
                requires_user_action=True,
                explanation="Some basis sets don't include heavy elements",
            ),
        ]
        
        # Geometry suggestions
        database[ErrorCategory.GEOMETRY] = [
            ErrorSuggestion(
                text="Check for atoms too close together",
                priority=SuggestionPriority.CRITICAL,
                category=ErrorCategory.GEOMETRY,
                requires_user_action=True,
                explanation="Minimum distance should be > 0.5 angstrom",
            ),
            ErrorSuggestion(
                text="Verify charge and multiplicity",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.GEOMETRY,
                requires_user_action=True,
                explanation="Wrong charge/mult causes electron count errors",
            ),
            ErrorSuggestion(
                text="Check coordinate units",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.GEOMETRY,
                requires_user_action=True,
                explanation="Ensure using angstrom or bohr correctly",
            ),
        ]
        
        # Linear dependency suggestions
        database[ErrorCategory.LINEAR_DEPENDENCY] = [
            ErrorSuggestion(
                text="Use smaller basis set",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.LINEAR_DEPENDENCY,
                requires_user_action=True,
                explanation="Large basis sets can cause near-linear-dependence",
            ),
            ErrorSuggestion(
                text="Adjust S_MIN_EIGENVALUE threshold",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.LINEAR_DEPENDENCY,
                option_changes={"s_tolerance": 1e-5},
                explanation="Remove problematic overlap eigenvectors",
            ),
            ErrorSuggestion(
                text="Try def2 basis sets",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.LINEAR_DEPENDENCY,
                requires_user_action=True,
                explanation="def2 bases are well-conditioned",
            ),
        ]
        
        # TDDFT suggestions
        database[ErrorCategory.TDDFT_CONVERGENCE] = [
            ErrorSuggestion(
                text="Increase number of guess vectors",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.TDDFT_CONVERGENCE,
                option_changes={"tdscf_nguess": 30},
                explanation="More guess vectors help find roots",
            ),
            ErrorSuggestion(
                text="Increase maximum iterations",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.TDDFT_CONVERGENCE,
                option_changes={"tdscf_maxiter": 100},
                explanation="TDDFT can need many iterations",
            ),
            ErrorSuggestion(
                text="Try TDA (Tamm-Dancoff approximation)",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.TDDFT_CONVERGENCE,
                option_changes={"tda": True},
                explanation="TDA is more stable than full TDDFT",
            ),
            ErrorSuggestion(
                text="Loosen convergence threshold",
                priority=SuggestionPriority.LOW,
                category=ErrorCategory.TDDFT_CONVERGENCE,
                option_changes={"tdscf_r_convergence": 1e-4},
                explanation="May help for difficult systems",
            ),
        ]
        
        # CC convergence suggestions
        database[ErrorCategory.CC_CONVERGENCE] = [
            ErrorSuggestion(
                text="Increase CC iterations",
                priority=SuggestionPriority.HIGH,
                category=ErrorCategory.CC_CONVERGENCE,
                option_changes={"cc_maxiter": 150},
                explanation="CC may need many iterations",
            ),
            ErrorSuggestion(
                text="Try DIIS for CC",
                priority=SuggestionPriority.MEDIUM,
                category=ErrorCategory.CC_CONVERGENCE,
                option_changes={"cc_diis": True},
                explanation="DIIS can accelerate CC convergence",
            ),
        ]
        
        return database
    
    def get_suggestions(
        self,
        error_info: ErrorInfo,
        context: Optional[Dict[str, Any]] = None,
        max_suggestions: int = 5,
    ) -> List[ErrorSuggestion]:
        """
        Get suggestions for an error.
        
        Args:
            error_info: Error information
            context: Additional context
            max_suggestions: Maximum suggestions to return
            
        Returns:
            List of suggestions sorted by priority
        """
        category = error_info.category
        
        # Get base suggestions
        suggestions = list(self._suggestion_database.get(category, []))
        
        # Also check parent category
        if category in (ErrorCategory.SCF_CONVERGENCE, 
                       ErrorCategory.GEOMETRY_CONVERGENCE,
                       ErrorCategory.TDDFT_CONVERGENCE,
                       ErrorCategory.CC_CONVERGENCE):
            parent_suggestions = self._suggestion_database.get(
                ErrorCategory.CONVERGENCE, []
            )
            suggestions.extend(parent_suggestions)
        
        # Sort by priority and limit
        suggestions.sort(key=lambda s: s.priority.value)
        return suggestions[:max_suggestions]
    
    def get_automatic_fixes(
        self,
        error_info: ErrorInfo,
    ) -> List[Dict[str, Any]]:
        """
        Get automatic fixes (option changes) for an error.
        
        Args:
            error_info: Error information
            
        Returns:
            List of option change dictionaries
        """
        suggestions = self.get_suggestions(error_info)
        
        fixes = []
        for suggestion in suggestions:
            if suggestion.option_changes and not suggestion.requires_user_action:
                fixes.append(suggestion.option_changes)
        
        return fixes
    
    def add_suggestion(
        self,
        category: ErrorCategory,
        suggestion: ErrorSuggestion,
    ) -> None:
        """Add a custom suggestion."""
        if category not in self._suggestion_database:
            self._suggestion_database[category] = []
        self._suggestion_database[category].append(suggestion)


# Global suggestion engine
_suggestion_engine: Optional[SuggestionEngine] = None


def get_suggestion_engine() -> SuggestionEngine:
    """Get the global suggestion engine."""
    global _suggestion_engine
    if _suggestion_engine is None:
        _suggestion_engine = SuggestionEngine()
    return _suggestion_engine


def get_error_suggestions(
    error_info: ErrorInfo,
    max_suggestions: int = 5,
) -> List[ErrorSuggestion]:
    """
    Get suggestions for an error.
    
    Args:
        error_info: Error information
        max_suggestions: Maximum suggestions
        
    Returns:
        List of suggestions
    """
    engine = get_suggestion_engine()
    return engine.get_suggestions(error_info, max_suggestions=max_suggestions)


def get_suggestion_for_category(
    category: ErrorCategory,
    max_suggestions: int = 5,
) -> List[ErrorSuggestion]:
    """
    Get suggestions for an error category.
    
    Args:
        category: Error category
        max_suggestions: Maximum suggestions
        
    Returns:
        List of suggestions
    """
    error_info = ErrorInfo(
        category=category,
        severity=ErrorSeverity.ERROR,
        message="",
    )
    return get_error_suggestions(error_info, max_suggestions)


def format_suggestions(suggestions: List[ErrorSuggestion]) -> str:
    """
    Format suggestions as readable text.
    
    Args:
        suggestions: List of suggestions
        
    Returns:
        Formatted string
    """
    lines = ["Suggestions:"]
    
    for i, suggestion in enumerate(suggestions, 1):
        priority_marker = "!" * (5 - suggestion.priority.value + 1)
        lines.append(f"  {i}. [{priority_marker}] {suggestion.text}")
        
        if suggestion.explanation:
            lines.append(f"      {suggestion.explanation}")
        
        if suggestion.option_changes:
            options_str = ", ".join(
                f"{k}={v}" for k, v in suggestion.option_changes.items()
            )
            lines.append(f"      Options: {options_str}")
        
        if suggestion.code_example:
            lines.append(f"      Example: {suggestion.code_example}")
    
    return "\n".join(lines)
