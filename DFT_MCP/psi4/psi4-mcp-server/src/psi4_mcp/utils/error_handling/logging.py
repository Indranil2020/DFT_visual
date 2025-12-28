"""
Error Logging for Psi4 MCP Server.

Provides structured logging for errors with context preservation.
"""

import sys
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

from psi4_mcp.utils.error_handling.categorization import ErrorCategory, ErrorInfo, ErrorSeverity


class LogLevel(str, Enum):
    """Log levels for error logging."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def to_logging_level(self) -> int:
        """Convert to standard logging level."""
        mapping = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping[self]


@dataclass
class ErrorLogEntry:
    """Entry for error log."""
    timestamp: datetime
    error_info: ErrorInfo
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    calculation_id: Optional[str] = None
    recovery_attempted: bool = False
    recovery_successful: Optional[bool] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "error": self.error_info.to_dict(),
            "context": self.context,
            "stack_trace": self.stack_trace,
            "calculation_id": self.calculation_id,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ErrorLogger:
    """
    Structured error logging for Psi4 calculations.
    
    Logs errors with context, categorization, and recovery information.
    All output goes to stderr for MCP compatibility.
    """
    
    def __init__(
        self,
        name: str = "psi4_mcp",
        level: LogLevel = LogLevel.INFO,
        log_file: Optional[Path] = None,
        max_entries: int = 1000,
    ):
        """
        Initialize error logger.
        
        Args:
            name: Logger name
            level: Minimum log level
            log_file: Optional file path for logging
            max_entries: Maximum entries to keep in memory
        """
        self.name = name
        self.level = level
        self.log_file = log_file
        self.max_entries = max_entries
        
        self._entries: List[ErrorLogEntry] = []
        self._logger = self._setup_logger()
        self._file_handler: Optional[TextIO] = None
        
        if log_file:
            self._file_handler = open(log_file, "a")
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the underlying logger."""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level.to_logging_level())
        
        # Remove existing handlers
        logger.handlers = []
        
        # Add stderr handler (required for MCP)
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(self.level.to_logging_level())
        
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def log(
        self,
        error_info: ErrorInfo,
        context: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
        calculation_id: Optional[str] = None,
    ) -> ErrorLogEntry:
        """
        Log an error.
        
        Args:
            error_info: Error information
            context: Additional context
            stack_trace: Stack trace if available
            calculation_id: ID of the calculation
            
        Returns:
            Created log entry
        """
        entry = ErrorLogEntry(
            timestamp=datetime.now(),
            error_info=error_info,
            context=context or {},
            stack_trace=stack_trace,
            calculation_id=calculation_id,
        )
        
        # Add to in-memory list
        self._entries.append(entry)
        
        # Trim if needed
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries:]
        
        # Log to logger
        log_level = self._severity_to_level(error_info.severity)
        message = self._format_message(entry)
        self._logger.log(log_level, message)
        
        # Log to file if configured
        if self._file_handler:
            self._file_handler.write(entry.to_json() + "\n")
            self._file_handler.flush()
        
        return entry
    
    def log_recovery(
        self,
        entry: ErrorLogEntry,
        successful: bool,
        recovery_details: Optional[str] = None,
    ) -> None:
        """
        Log recovery attempt for an error.
        
        Args:
            entry: Original error log entry
            successful: Whether recovery was successful
            recovery_details: Additional details
        """
        entry.recovery_attempted = True
        entry.recovery_successful = successful
        
        status = "successful" if successful else "failed"
        message = f"Recovery {status} for {entry.error_info.category.value}"
        if recovery_details:
            message += f": {recovery_details}"
        
        level = logging.INFO if successful else logging.WARNING
        self._logger.log(level, message)
    
    def _severity_to_level(self, severity: ErrorSeverity) -> int:
        """Convert severity to logging level."""
        mapping = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.INFO: logging.INFO,
        }
        return mapping.get(severity, logging.ERROR)
    
    def _format_message(self, entry: ErrorLogEntry) -> str:
        """Format log entry message."""
        parts = [
            f"[{entry.error_info.category.value}]",
            entry.error_info.message,
        ]
        
        if entry.calculation_id:
            parts.insert(0, f"({entry.calculation_id})")
        
        if entry.error_info.original_error:
            parts.append(f"- {entry.error_info.original_error[:100]}")
        
        return " ".join(parts)
    
    def get_entries(
        self,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[ErrorLogEntry]:
        """
        Get logged entries with filtering.
        
        Args:
            category: Filter by category
            severity: Filter by severity
            since: Filter by timestamp
            limit: Maximum entries to return
            
        Returns:
            Filtered log entries
        """
        entries = self._entries.copy()
        
        if category:
            entries = [e for e in entries if e.error_info.category == category]
        
        if severity:
            entries = [e for e in entries if e.error_info.severity == severity]
        
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        
        return entries[-limit:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        stats: Dict[str, Any] = {
            "total_errors": len(self._entries),
            "by_category": {},
            "by_severity": {},
            "recovery_rate": 0.0,
        }
        
        # Count by category
        for category in ErrorCategory:
            count = sum(1 for e in self._entries if e.error_info.category == category)
            if count > 0:
                stats["by_category"][category.value] = count
        
        # Count by severity
        for severity in ErrorSeverity:
            count = sum(1 for e in self._entries if e.error_info.severity == severity)
            if count > 0:
                stats["by_severity"][severity.value] = count
        
        # Calculate recovery rate
        recovery_attempted = [e for e in self._entries if e.recovery_attempted]
        if recovery_attempted:
            successful = sum(1 for e in recovery_attempted if e.recovery_successful)
            stats["recovery_rate"] = successful / len(recovery_attempted)
        
        return stats
    
    def clear(self) -> None:
        """Clear all logged entries."""
        self._entries.clear()
    
    def close(self) -> None:
        """Close the logger and release resources."""
        if self._file_handler:
            self._file_handler.close()
            self._file_handler = None


# Global logger instance
_error_logger: Optional[ErrorLogger] = None


def get_error_logger() -> ErrorLogger:
    """Get the global error logger instance."""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger


def configure_error_logging(
    level: LogLevel = LogLevel.INFO,
    log_file: Optional[Path] = None,
) -> ErrorLogger:
    """
    Configure the global error logger.
    
    Args:
        level: Log level
        log_file: Optional log file path
        
    Returns:
        Configured logger
    """
    global _error_logger
    _error_logger = ErrorLogger(level=level, log_file=log_file)
    return _error_logger


def log_error(
    error_info: ErrorInfo,
    context: Optional[Dict[str, Any]] = None,
    calculation_id: Optional[str] = None,
) -> ErrorLogEntry:
    """
    Log an error.
    
    Convenience function using global logger.
    
    Args:
        error_info: Error information
        context: Additional context
        calculation_id: Calculation ID
        
    Returns:
        Log entry
    """
    logger = get_error_logger()
    return logger.log(error_info, context, calculation_id=calculation_id)


def log_calculation_error(
    message: str,
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    context: Optional[Dict[str, Any]] = None,
    calculation_id: Optional[str] = None,
) -> ErrorLogEntry:
    """
    Log a calculation error with minimal setup.
    
    Args:
        message: Error message
        category: Error category
        severity: Error severity
        context: Additional context
        calculation_id: Calculation ID
        
    Returns:
        Log entry
    """
    error_info = ErrorInfo(
        category=category,
        severity=severity,
        message=message,
    )
    return log_error(error_info, context, calculation_id)
