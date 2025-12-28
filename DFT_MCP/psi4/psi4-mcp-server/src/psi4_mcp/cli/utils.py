"""
CLI Utility Functions for Psi4 MCP Server.

Common utilities used by CLI commands.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO


def print_error(message: str, file: TextIO = sys.stderr) -> None:
    """Print an error message to stderr."""
    print(f"Error: {message}", file=file)


def print_warning(message: str, file: TextIO = sys.stderr) -> None:
    """Print a warning message to stderr."""
    print(f"Warning: {message}", file=file)


def print_success(message: str, file: TextIO = sys.stdout) -> None:
    """Print a success message."""
    print(f"✓ {message}", file=file)


def print_info(message: str, file: TextIO = sys.stdout) -> None:
    """Print an info message."""
    print(f"ℹ {message}", file=file)


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return Path(path).is_file()


def dir_exists(path: str) -> bool:
    """Check if a directory exists."""
    return Path(path).is_dir()


def ensure_dir(path: str) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_file_extension(path: str) -> str:
    """Get the file extension (without the dot)."""
    return Path(path).suffix.lstrip(".")


def detect_format_from_extension(path: str) -> Optional[str]:
    """Detect file format from extension."""
    ext = get_file_extension(path).lower()
    
    format_map = {
        "xyz": "xyz",
        "pdb": "pdb",
        "mol2": "mol2",
        "mol": "mol",
        "sdf": "sdf",
        "cif": "cif",
        "json": "json",
        "dat": "psi4",
        "in": "psi4",
    }
    
    return format_map.get(ext)


def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, "r") as f:
        return f.read()


def write_file(path: str, content: str) -> None:
    """Write content to file."""
    with open(path, "w") as f:
        f.write(content)


def format_table(
    headers: List[str],
    rows: List[List[str]],
    alignment: Optional[List[str]] = None,
) -> str:
    """Format data as a simple ASCII table."""
    if not rows:
        return ""
    
    # Calculate column widths
    n_cols = len(headers)
    widths = [len(h) for h in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < n_cols:
                widths[i] = max(widths[i], len(str(cell)))
    
    # Default alignment
    if alignment is None:
        alignment = ["<"] * n_cols
    
    # Build format string
    format_parts = []
    for i, (width, align) in enumerate(zip(widths, alignment)):
        format_parts.append(f"{{:{align}{width}}}")
    row_format = " | ".join(format_parts)
    
    # Build table
    lines = []
    lines.append(row_format.format(*headers))
    lines.append("-+-".join("-" * w for w in widths))
    
    for row in rows:
        padded_row = list(row) + [""] * (n_cols - len(row))
        lines.append(row_format.format(*padded_row[:n_cols]))
    
    return "\n".join(lines)


def format_dict(d: Dict[str, Any], indent: int = 2) -> str:
    """Format a dictionary for display."""
    lines = []
    prefix = " " * indent
    
    for key, value in d.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            lines.append(format_dict(value, indent + 2))
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"{prefix}- {item}")
        else:
            lines.append(f"{key}: {value}")
    
    return "\n".join(prefix + line for line in lines)


def parse_memory_string(memory: str) -> float:
    """Parse memory string and return value in MB."""
    memory = memory.strip().upper()
    
    # Extract number and unit
    import re
    match = re.match(r"^(\d+\.?\d*)\s*([A-Z]+)?$", memory)
    
    if not match:
        raise ValueError(f"Invalid memory format: {memory}")
    
    value = float(match.group(1))
    unit = match.group(2) or "MB"
    
    multipliers = {
        "B": 1e-6,
        "KB": 1e-3,
        "K": 1e-3,
        "MB": 1.0,
        "M": 1.0,
        "GB": 1024.0,
        "G": 1024.0,
        "TB": 1024 * 1024,
        "T": 1024 * 1024,
    }
    
    if unit not in multipliers:
        raise ValueError(f"Unknown memory unit: {unit}")
    
    return value * multipliers[unit]


def check_psi4_available() -> bool:
    """Check if Psi4 is available."""
    try:
        import psi4
        return True
    except ImportError:
        return False


def get_psi4_version() -> Optional[str]:
    """Get Psi4 version if available."""
    try:
        import psi4
        return psi4.__version__
    except ImportError:
        return None


def setup_psi4_environment(
    memory: str = "2 GB",
    threads: int = 1,
    scratch: Optional[str] = None,
) -> bool:
    """Set up Psi4 environment."""
    if not check_psi4_available():
        print_error("Psi4 is not installed")
        return False
    
    import psi4
    
    # Set memory
    psi4.set_memory(memory)
    
    # Set threads
    psi4.set_num_threads(threads)
    
    # Set scratch directory
    if scratch:
        os.environ["PSI_SCRATCH"] = scratch
    
    # Suppress output to stdout
    psi4.core.set_output_file("/dev/null", False)
    
    return True


def format_energy(energy: float, unit: str = "hartree") -> str:
    """Format energy value with units."""
    if unit == "hartree":
        return f"{energy:.10f} Eh"
    elif unit == "ev":
        return f"{energy * 27.2114:.6f} eV"
    elif unit == "kcal":
        return f"{energy * 627.509:.4f} kcal/mol"
    elif unit == "kj":
        return f"{energy * 2625.5:.4f} kJ/mol"
    return f"{energy} {unit}"


def spinner(message: str = "Processing"):
    """Create a simple spinner context manager."""
    import threading
    import time
    
    class Spinner:
        def __init__(self, msg: str):
            self.message = msg
            self.running = False
            self.thread: Optional[threading.Thread] = None
        
        def _spin(self) -> None:
            chars = "|/-\\"
            i = 0
            while self.running:
                sys.stderr.write(f"\r{self.message} {chars[i % len(chars)]}")
                sys.stderr.flush()
                time.sleep(0.1)
                i += 1
            sys.stderr.write(f"\r{self.message} done\n")
        
        def __enter__(self) -> "Spinner":
            self.running = True
            self.thread = threading.Thread(target=self._spin)
            self.thread.start()
            return self
        
        def __exit__(self, *args: Any) -> None:
            self.running = False
            if self.thread:
                self.thread.join()
    
    return Spinner(message)
