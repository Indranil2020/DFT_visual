"""
Custom Log Formatters for Psi4 MCP Server.

Provides various formatting options for log messages.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional


class Psi4Formatter(logging.Formatter):
    """
    Custom formatter for Psi4 calculations.
    
    Provides clean, readable output for calculation logs.
    """
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        include_level: bool = True,
        include_name: bool = False,
    ):
        """
        Initialize formatter.
        
        Args:
            fmt: Format string (uses default if None)
            datefmt: Date format string
            include_level: Include log level in output
            include_name: Include logger name in output
        """
        if fmt is None:
            parts = ["%(asctime)s"]
            if include_level:
                parts.append("%(levelname)s")
            if include_name:
                parts.append("%(name)s")
            parts.append("%(message)s")
            fmt = " - ".join(parts)
        
        super().__init__(fmt, datefmt or "%H:%M:%S")
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        # Add custom formatting for specific message types
        if hasattr(record, "energy"):
            record.msg = f"{record.msg} [E = {record.energy:.10f}]"
        
        if hasattr(record, "convergence"):
            conv = record.convergence
            record.msg = f"{record.msg} [ΔE = {conv:.2e}]"
        
        return super().format(record)


class ColoredFormatter(logging.Formatter):
    """
    Colored formatter for terminal output.
    
    Adds ANSI color codes based on log level.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
    }
    RESET = "\033[0m"
    
    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        use_colors: bool = True,
    ):
        """
        Initialize colored formatter.
        
        Args:
            fmt: Format string
            datefmt: Date format string
            use_colors: Whether to use colors
        """
        super().__init__(
            fmt or "%(asctime)s - %(levelname)s - %(message)s",
            datefmt or "%Y-%m-%d %H:%M:%S",
        )
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """Format with colors."""
        formatted = super().format(record)
        
        if self.use_colors and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            formatted = f"{color}{formatted}{self.RESET}"
        
        return formatted


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Outputs log messages as JSON objects for machine parsing.
    """
    
    def __init__(
        self,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_name: bool = True,
        include_extra: bool = True,
    ):
        """
        Initialize JSON formatter.
        
        Args:
            include_timestamp: Include timestamp in output
            include_level: Include log level
            include_name: Include logger name
            include_extra: Include extra fields
        """
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_name = include_name
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        """Format as JSON."""
        data: Dict[str, Any] = {
            "message": record.getMessage(),
        }
        
        if self.include_timestamp:
            data["timestamp"] = datetime.fromtimestamp(record.created).isoformat()
        
        if self.include_level:
            data["level"] = record.levelname
        
        if self.include_name:
            data["logger"] = record.name
        
        # Add exception info if present
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if self.include_extra:
            standard_attrs = {
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "asctime",
            }
            
            for key, value in record.__dict__.items():
                if key not in standard_attrs:
                    data[key] = value
        
        return json.dumps(data)


class CalculationFormatter(logging.Formatter):
    """
    Formatter specifically for calculation progress.
    
    Provides compact, informative output for long-running calculations.
    """
    
    def __init__(self):
        """Initialize calculation formatter."""
        super().__init__()
        self._iteration_count = 0
    
    def format(self, record: logging.LogRecord) -> str:
        """Format calculation log."""
        # Time prefix
        time_str = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        
        # Level indicator
        level_chars = {
            "DEBUG": ".",
            "INFO": "*",
            "WARNING": "!",
            "ERROR": "X",
            "CRITICAL": "!!!",
        }
        indicator = level_chars.get(record.levelname, " ")
        
        # Message
        message = record.getMessage()
        
        # Check for special formatting
        if hasattr(record, "iteration"):
            self._iteration_count = record.iteration
            message = f"[Iter {record.iteration:4d}] {message}"
        
        if hasattr(record, "energy"):
            message = f"{message} E={record.energy:.8f}"
        
        if hasattr(record, "progress"):
            progress = record.progress
            bar_width = 20
            filled = int(bar_width * progress / 100)
            bar = "█" * filled + "░" * (bar_width - filled)
            message = f"{message} [{bar}] {progress:.1f}%"
        
        return f"{time_str} {indicator} {message}"


def get_formatter(
    format_type: str = "default",
    **kwargs: Any,
) -> logging.Formatter:
    """
    Get a formatter by type.
    
    Args:
        format_type: Type of formatter
            - "default": Standard formatter
            - "psi4": Psi4-specific formatter
            - "colored": Colored terminal formatter
            - "json": JSON formatter
            - "calculation": Calculation progress formatter
        **kwargs: Additional arguments for formatter
        
    Returns:
        Configured formatter
    """
    formatters = {
        "default": logging.Formatter,
        "psi4": Psi4Formatter,
        "colored": ColoredFormatter,
        "json": JSONFormatter,
        "calculation": CalculationFormatter,
    }
    
    formatter_class = formatters.get(format_type, logging.Formatter)
    return formatter_class(**kwargs)
