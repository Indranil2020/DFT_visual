"""
Error Handling Utilities for Psi4 MCP Server.

This module provides comprehensive error detection, categorization,
logging, recovery, and suggestion capabilities.

Example Usage:
    from psi4_mcp.utils.error_handling import (
        ErrorDetector,
        ErrorCategory,
        detect_error,
        get_error_suggestions,
        attempt_recovery,
    )
    
    # Detect and categorize errors
    error_info = detect_error(error_message)
    if error_info.category == ErrorCategory.CONVERGENCE:
        suggestions = get_error_suggestions(error_info)
"""

from psi4_mcp.utils.error_handling.categorization import (
    ErrorCategory,
    ErrorSeverity,
    ErrorInfo,
    categorize_error,
    get_error_category,
)

from psi4_mcp.utils.error_handling.detection import (
    ErrorDetector,
    ErrorPattern,
    detect_error,
    detect_psi4_error,
    parse_error_message,
)

from psi4_mcp.utils.error_handling.logging import (
    ErrorLogger,
    LogLevel,
    log_error,
    get_error_logger,
    configure_error_logging,
)

from psi4_mcp.utils.error_handling.recovery import (
    RecoveryStrategy,
    RecoveryResult,
    attempt_recovery,
    get_recovery_strategies,
    RecoveryManager,
)

from psi4_mcp.utils.error_handling.suggestions import (
    ErrorSuggestion,
    SuggestionPriority,
    get_error_suggestions,
    get_suggestion_for_category,
    SuggestionEngine,
)

__all__ = [
    # Categorization
    "ErrorCategory",
    "ErrorSeverity",
    "ErrorInfo",
    "categorize_error",
    "get_error_category",
    
    # Detection
    "ErrorDetector",
    "ErrorPattern",
    "detect_error",
    "detect_psi4_error",
    "parse_error_message",
    
    # Logging
    "ErrorLogger",
    "LogLevel",
    "log_error",
    "get_error_logger",
    "configure_error_logging",
    
    # Recovery
    "RecoveryStrategy",
    "RecoveryResult",
    "attempt_recovery",
    "get_recovery_strategies",
    "RecoveryManager",
    
    # Suggestions
    "ErrorSuggestion",
    "SuggestionPriority",
    "get_error_suggestions",
    "get_suggestion_for_category",
    "SuggestionEngine",
]
