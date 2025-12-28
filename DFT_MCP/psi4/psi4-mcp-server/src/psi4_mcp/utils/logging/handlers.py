"""
Custom Log Handlers for Psi4 MCP Server.

Provides specialized handlers for different logging needs.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class StderrHandler(logging.StreamHandler):
    """
    Handler that always writes to stderr.
    
    CRITICAL for MCP servers using stdio transport.
    """
    
    def __init__(self, level: int = logging.NOTSET):
        """
        Initialize stderr handler.
        
        Args:
            level: Logging level
        """
        super().__init__(sys.stderr)
        self.setLevel(level)
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to stderr."""
        # Ensure we're writing to stderr even if sys.stderr changed
        self.stream = sys.stderr
        super().emit(record)


class RotatingFileHandler(logging.Handler):
    """
    Rotating file handler with size-based rotation.
    
    Creates new log files when size limit is reached.
    """
    
    def __init__(
        self,
        filename: str,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB default
        backup_count: int = 5,
        level: int = logging.NOTSET,
    ):
        """
        Initialize rotating file handler.
        
        Args:
            filename: Base log file path
            max_bytes: Maximum bytes per file
            backup_count: Number of backup files to keep
            level: Logging level
        """
        super().__init__(level)
        
        self.base_filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self._stream: Optional[Any] = None
        self._current_size = 0
        
        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Open initial file
        self._open_file()
    
    def _open_file(self) -> None:
        """Open the log file."""
        if self._stream is not None:
            self._stream.close()
        
        self._stream = open(self.base_filename, "a", encoding="utf-8")
        self._current_size = self._stream.tell()
    
    def _rotate(self) -> None:
        """Rotate log files."""
        if self._stream is not None:
            self._stream.close()
        
        # Rotate existing backups
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.base_filename}.{i}"
            dst = f"{self.base_filename}.{i + 1}"
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
        
        # Rename current file to .1
        if os.path.exists(self.base_filename):
            dst = f"{self.base_filename}.1"
            if os.path.exists(dst):
                os.remove(dst)
            os.rename(self.base_filename, dst)
        
        # Open new file
        self._open_file()
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        if self._stream is None:
            return
        
        msg = self.format(record) + "\n"
        msg_bytes = msg.encode("utf-8")
        
        # Check if rotation needed
        if self._current_size + len(msg_bytes) > self.max_bytes:
            self._rotate()
        
        self._stream.write(msg)
        self._stream.flush()
        self._current_size += len(msg_bytes)
    
    def close(self) -> None:
        """Close the handler."""
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        super().close()


class CalculationFileHandler(logging.Handler):
    """
    Handler that writes calculation logs to individual files.
    
    Creates separate log files for each calculation.
    """
    
    def __init__(
        self,
        log_dir: str,
        level: int = logging.NOTSET,
        filename_pattern: str = "calc_{timestamp}_{calc_id}.log",
    ):
        """
        Initialize calculation file handler.
        
        Args:
            log_dir: Directory for log files
            level: Logging level
            filename_pattern: Pattern for log filenames
        """
        super().__init__(level)
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.filename_pattern = filename_pattern
        self._current_file: Optional[Any] = None
        self._current_calc_id: Optional[str] = None
    
    def _get_filename(self, calc_id: str) -> Path:
        """Get filename for calculation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.filename_pattern.format(
            timestamp=timestamp,
            calc_id=calc_id,
        )
        return self.log_dir / filename
    
    def set_calculation(self, calc_id: str) -> None:
        """
        Start logging to new calculation file.
        
        Args:
            calc_id: Calculation identifier
        """
        # Close previous file
        if self._current_file is not None:
            self._current_file.close()
        
        # Open new file
        filepath = self._get_filename(calc_id)
        self._current_file = open(filepath, "w", encoding="utf-8")
        self._current_calc_id = calc_id
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        # Check if we need to switch files
        calc_id = getattr(record, "calculation_id", None)
        if calc_id is not None and calc_id != self._current_calc_id:
            self.set_calculation(calc_id)
        
        if self._current_file is None:
            return
        
        msg = self.format(record) + "\n"
        self._current_file.write(msg)
        self._current_file.flush()
    
    def close(self) -> None:
        """Close the handler."""
        if self._current_file is not None:
            self._current_file.close()
            self._current_file = None
        super().close()


class BufferingHandler(logging.Handler):
    """
    Handler that buffers messages before writing.
    
    Useful for batch processing of logs.
    """
    
    def __init__(
        self,
        capacity: int = 1000,
        flush_level: int = logging.ERROR,
        target: Optional[logging.Handler] = None,
    ):
        """
        Initialize buffering handler.
        
        Args:
            capacity: Maximum buffer size
            flush_level: Level at which to auto-flush
            target: Target handler to flush to
        """
        super().__init__()
        
        self.capacity = capacity
        self.flush_level = flush_level
        self.target = target
        self.buffer: list = []
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record."""
        self.buffer.append(record)
        
        # Auto-flush on high-priority messages
        if record.levelno >= self.flush_level:
            self.flush()
        # Flush when buffer full
        elif len(self.buffer) >= self.capacity:
            self.flush()
    
    def flush(self) -> None:
        """Flush buffer to target."""
        if self.target is None:
            self.buffer.clear()
            return
        
        for record in self.buffer:
            self.target.emit(record)
        
        self.buffer.clear()
        self.target.flush()
    
    def close(self) -> None:
        """Close the handler."""
        self.flush()
        if self.target is not None:
            self.target.close()
        super().close()


class FilteredHandler(logging.Handler):
    """
    Handler that filters messages based on criteria.
    
    Only passes messages matching specified criteria.
    """
    
    def __init__(
        self,
        target: logging.Handler,
        include_names: Optional[list] = None,
        exclude_names: Optional[list] = None,
        min_level: int = logging.NOTSET,
        max_level: int = logging.CRITICAL,
    ):
        """
        Initialize filtered handler.
        
        Args:
            target: Target handler
            include_names: Logger names to include (None = all)
            exclude_names: Logger names to exclude
            min_level: Minimum level to pass
            max_level: Maximum level to pass
        """
        super().__init__()
        
        self.target = target
        self.include_names = include_names
        self.exclude_names = exclude_names or []
        self.min_level = min_level
        self.max_level = max_level
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit if record passes filters."""
        # Check level
        if not (self.min_level <= record.levelno <= self.max_level):
            return
        
        # Check name filters
        if self.include_names is not None:
            if not any(record.name.startswith(n) for n in self.include_names):
                return
        
        if any(record.name.startswith(n) for n in self.exclude_names):
            return
        
        # Pass to target
        self.target.emit(record)
    
    def close(self) -> None:
        """Close the handler."""
        self.target.close()
        super().close()


def get_handler(
    handler_type: str,
    **kwargs: Any,
) -> logging.Handler:
    """
    Get a handler by type.
    
    Args:
        handler_type: Type of handler
            - "stderr": StderrHandler
            - "file": Standard FileHandler
            - "rotating": RotatingFileHandler
            - "calculation": CalculationFileHandler
            - "buffering": BufferingHandler
        **kwargs: Additional arguments for handler
        
    Returns:
        Configured handler
    """
    handlers = {
        "stderr": StderrHandler,
        "file": logging.FileHandler,
        "rotating": RotatingFileHandler,
        "calculation": CalculationFileHandler,
        "buffering": BufferingHandler,
    }
    
    handler_class = handlers.get(handler_type)
    if handler_class is None:
        raise ValueError(f"Unknown handler type: {handler_type}")
    
    return handler_class(**kwargs)
