"""
Logging Utilities for Psi4 MCP Server.

This module provides utilities for logging:
- Configured loggers
- Custom formatters
- File and stream handlers

Example Usage:
    from psi4_mcp.utils.logging import (
        get_logger,
        configure_logging,
        CalculationLogger,
    )
    
    # Get a logger
    logger = get_logger("psi4_mcp.tools")
    logger.info("Starting calculation")
"""

from psi4_mcp.utils.logging.logger import (
    get_logger,
    configure_logging,
    set_log_level,
    add_file_handler,
    CalculationLogger,
    LogContext,
)

from psi4_mcp.utils.logging.formatters import (
    Psi4Formatter,
    ColoredFormatter,
    JSONFormatter,
    get_formatter,
)

from psi4_mcp.utils.logging.handlers import (
    StderrHandler,
    RotatingFileHandler,
    CalculationFileHandler,
    get_handler,
)

__all__ = [
    # Logger
    "get_logger",
    "configure_logging",
    "set_log_level",
    "add_file_handler",
    "CalculationLogger",
    "LogContext",
    
    # Formatters
    "Psi4Formatter",
    "ColoredFormatter",
    "JSONFormatter",
    "get_formatter",
    
    # Handlers
    "StderrHandler",
    "RotatingFileHandler",
    "CalculationFileHandler",
    "get_handler",
]
