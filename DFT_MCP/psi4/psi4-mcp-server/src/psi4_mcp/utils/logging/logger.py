"""
Logger Implementation for Psi4 MCP Server.

Provides configured loggers for the MCP server.
IMPORTANT: MCP stdio transport requires logging to stderr only!
"""

import logging
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional


# Default log format
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Global configuration
_configured = False
_loggers: Dict[str, logging.Logger] = {}


def get_logger(name: str = "psi4_mcp") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    if name in _loggers:
        return _loggers[name]
    
    logger = logging.getLogger(name)
    
    # Configure if not already done
    if not _configured:
        configure_logging()
    
    _loggers[name] = logger
    return logger


def configure_logging(
    level: int = logging.INFO,
    format_string: str = DEFAULT_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    log_to_file: Optional[str] = None,
) -> None:
    """
    Configure logging for the MCP server.
    
    CRITICAL: MCP stdio transport requires all logging to stderr.
    Never log to stdout as it interferes with the protocol.
    
    Args:
        level: Logging level
        format_string: Log message format
        date_format: Date format string
        log_to_file: Optional file path for logging
    """
    global _configured
    
    # Get root logger for psi4_mcp
    root_logger = logging.getLogger("psi4_mcp")
    root_logger.setLevel(level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(format_string, date_format)
    
    # CRITICAL: Use stderr only for MCP compatibility
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(level)
    stderr_handler.setFormatter(formatter)
    root_logger.addHandler(stderr_handler)
    
    # Optional file handler
    if log_to_file:
        file_handler = logging.FileHandler(log_to_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    _configured = True


def set_log_level(level: int, logger_name: str = "psi4_mcp") -> None:
    """
    Set logging level.
    
    Args:
        level: Logging level (e.g., logging.DEBUG)
        logger_name: Logger name
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    for handler in logger.handlers:
        handler.setLevel(level)


def add_file_handler(
    filepath: str,
    level: int = logging.DEBUG,
    format_string: str = DEFAULT_FORMAT,
    logger_name: str = "psi4_mcp",
) -> logging.Handler:
    """
    Add a file handler to the logger.
    
    Args:
        filepath: Path to log file
        level: Logging level for file
        format_string: Log format
        logger_name: Logger name
        
    Returns:
        The created handler
    """
    logger = logging.getLogger(logger_name)
    
    handler = logging.FileHandler(filepath)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(format_string, DEFAULT_DATE_FORMAT))
    
    logger.addHandler(handler)
    return handler


@dataclass
class LogContext:
    """Context for structured logging."""
    calculation_id: Optional[str] = None
    molecule_name: Optional[str] = None
    method: Optional[str] = None
    basis: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.calculation_id:
            result["calculation_id"] = self.calculation_id
        if self.molecule_name:
            result["molecule"] = self.molecule_name
        if self.method:
            result["method"] = self.method
        if self.basis:
            result["basis"] = self.basis
        result.update(self.extra)
        return result
    
    def format_prefix(self) -> str:
        """Format as log prefix."""
        parts = []
        if self.calculation_id:
            parts.append(f"[{self.calculation_id}]")
        if self.molecule_name:
            parts.append(f"[{self.molecule_name}]")
        if self.method and self.basis:
            parts.append(f"[{self.method}/{self.basis}]")
        return " ".join(parts)


class CalculationLogger:
    """
    Logger for calculation progress and results.
    
    Provides structured logging for quantum chemistry calculations.
    """
    
    def __init__(
        self,
        name: str = "psi4_mcp.calculation",
        context: Optional[LogContext] = None,
    ):
        """
        Initialize calculation logger.
        
        Args:
            name: Logger name
            context: Optional logging context
        """
        self.logger = get_logger(name)
        self.context = context or LogContext()
        self._start_time: Optional[float] = None
        self._step_times: List[float] = []
    
    def _format_message(self, message: str) -> str:
        """Format message with context prefix."""
        prefix = self.context.format_prefix()
        if prefix:
            return f"{prefix} {message}"
        return message
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message."""
        self.logger.debug(self._format_message(message), **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message."""
        self.logger.info(self._format_message(message), **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message."""
        self.logger.warning(self._format_message(message), **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message."""
        self.logger.error(self._format_message(message), **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message."""
        self.logger.critical(self._format_message(message), **kwargs)
    
    def start_calculation(self, description: str = "Starting calculation") -> None:
        """Log start of calculation."""
        self._start_time = time.time()
        self._step_times = [self._start_time]
        self.info(description)
    
    def log_step(self, step_name: str, details: Optional[str] = None) -> None:
        """Log a calculation step."""
        current_time = time.time()
        self._step_times.append(current_time)
        
        if len(self._step_times) > 1:
            step_duration = current_time - self._step_times[-2]
            msg = f"{step_name} (took {step_duration:.2f}s)"
        else:
            msg = step_name
        
        if details:
            msg = f"{msg}: {details}"
        
        self.info(msg)
    
    def log_progress(
        self,
        current: int,
        total: int,
        message: str = "Progress",
    ) -> None:
        """Log progress update."""
        percent = (current / total * 100) if total > 0 else 0
        self.info(f"{message}: {current}/{total} ({percent:.1f}%)")
    
    def log_convergence(
        self,
        iteration: int,
        energy: float,
        delta_e: Optional[float] = None,
        rms_d: Optional[float] = None,
    ) -> None:
        """Log SCF convergence iteration."""
        parts = [f"Iteration {iteration}", f"E = {energy:.10f}"]
        
        if delta_e is not None:
            parts.append(f"ΔE = {delta_e:.2e}")
        if rms_d is not None:
            parts.append(f"RMS(D) = {rms_d:.2e}")
        
        self.debug(" | ".join(parts))
    
    def log_result(
        self,
        result_type: str,
        value: Any,
        unit: Optional[str] = None,
    ) -> None:
        """Log a calculation result."""
        if unit:
            self.info(f"{result_type}: {value} {unit}")
        else:
            self.info(f"{result_type}: {value}")
    
    def end_calculation(
        self,
        success: bool = True,
        message: Optional[str] = None,
    ) -> float:
        """
        Log end of calculation.
        
        Args:
            success: Whether calculation succeeded
            message: Optional message
            
        Returns:
            Total calculation time in seconds
        """
        end_time = time.time()
        total_time = end_time - self._start_time if self._start_time else 0.0
        
        status = "completed successfully" if success else "failed"
        msg = message or f"Calculation {status}"
        msg = f"{msg} (total time: {total_time:.2f}s)"
        
        if success:
            self.info(msg)
        else:
            self.error(msg)
        
        return total_time
    
    @contextmanager
    def calculation_context(
        self,
        description: str = "Calculation",
    ) -> Generator["CalculationLogger", None, None]:
        """
        Context manager for logging calculation.
        
        Args:
            description: Calculation description
            
        Yields:
            Self for logging within context
        """
        self.start_calculation(f"Starting {description}")
        success = True
        
        try:
            yield self
        except Exception as e:
            success = False
            self.error(f"Exception during {description}: {e}")
            raise
        finally:
            self.end_calculation(success, f"{description} finished")
    
    def with_context(self, **kwargs: Any) -> "CalculationLogger":
        """
        Create logger with updated context.
        
        Args:
            **kwargs: Context fields to update
            
        Returns:
            New CalculationLogger with updated context
        """
        new_context = LogContext(
            calculation_id=kwargs.get("calculation_id", self.context.calculation_id),
            molecule_name=kwargs.get("molecule_name", self.context.molecule_name),
            method=kwargs.get("method", self.context.method),
            basis=kwargs.get("basis", self.context.basis),
            extra={**self.context.extra, **kwargs.get("extra", {})},
        )
        return CalculationLogger(self.logger.name, new_context)


# Convenience function for quick logging
def log_calculation_start(
    method: str,
    basis: str,
    molecule_name: Optional[str] = None,
) -> CalculationLogger:
    """
    Start logging a calculation.
    
    Args:
        method: Calculation method
        basis: Basis set
        molecule_name: Optional molecule name
        
    Returns:
        Configured CalculationLogger
    """
    context = LogContext(
        method=method,
        basis=basis,
        molecule_name=molecule_name,
    )
    logger = CalculationLogger(context=context)
    logger.start_calculation()
    return logger
