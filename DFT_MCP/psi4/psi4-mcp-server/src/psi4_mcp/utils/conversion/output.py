"""
Output Format Conversion Utilities.

This module provides functions for converting quantum chemistry calculation
results between different output formats, including:

- JSON serialization
- Human-readable text reports
- CSV/tabular data
- QCSchema format
- Structured logging output

Key Features:
    - Consistent formatting across all output types
    - Configurable precision and units
    - Support for nested data structures
"""

from typing import Any, Optional, Sequence, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json

from psi4_mcp.utils.helpers.units import (
    EnergyUnit,
    LengthUnit,
    convert_energy,
    convert_length,
    get_energy_unit_label,
    get_length_unit_label,
)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    TEXT = "text"
    CSV = "csv"
    MARKDOWN = "markdown"
    QCSCHEMA = "qcschema"
    YAML = "yaml"


class ReportStyle(str, Enum):
    """Report formatting styles."""
    COMPACT = "compact"
    DETAILED = "detailed"
    VERBOSE = "verbose"
    MINIMAL = "minimal"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class OutputConfig:
    """
    Configuration for output formatting.
    
    Attributes:
        energy_unit: Unit for energy values.
        length_unit: Unit for length values.
        energy_precision: Decimal places for energies.
        length_precision: Decimal places for lengths.
        angle_precision: Decimal places for angles.
        include_metadata: Include calculation metadata.
        include_timings: Include timing information.
        indent: JSON indentation level.
    """
    energy_unit: EnergyUnit = EnergyUnit.HARTREE
    length_unit: LengthUnit = LengthUnit.ANGSTROM
    energy_precision: int = 10
    length_precision: int = 6
    angle_precision: int = 4
    include_metadata: bool = True
    include_timings: bool = True
    indent: int = 2


@dataclass
class CalculationMetadata:
    """
    Metadata for a quantum chemistry calculation.
    
    Attributes:
        method: Calculation method.
        basis_set: Basis set used.
        reference: Reference type (RHF, UHF, etc.).
        n_atoms: Number of atoms.
        n_electrons: Number of electrons.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        timestamp: Calculation timestamp.
        hostname: Machine hostname.
        version: Software version.
        wall_time: Wall clock time in seconds.
        cpu_time: CPU time in seconds.
    """
    method: str = ""
    basis_set: str = ""
    reference: str = ""
    n_atoms: int = 0
    n_electrons: int = 0
    charge: int = 0
    multiplicity: int = 1
    timestamp: Optional[str] = None
    hostname: Optional[str] = None
    version: Optional[str] = None
    wall_time: Optional[float] = None
    cpu_time: Optional[float] = None
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {}
        for key, value in asdict(self).items():
            if value is not None and value != "" and value != 0:
                result[key] = value
        return result


@dataclass
class EnergyResult:
    """
    Energy calculation result.
    
    Attributes:
        total_energy: Total energy in Hartree.
        nuclear_repulsion: Nuclear repulsion energy.
        electronic_energy: Electronic energy.
        correlation_energy: Correlation energy (for post-HF).
        scf_energy: SCF energy.
        dispersion_energy: Dispersion correction.
        solvation_energy: Solvation energy.
    """
    total_energy: float = 0.0
    nuclear_repulsion: Optional[float] = None
    electronic_energy: Optional[float] = None
    correlation_energy: Optional[float] = None
    scf_energy: Optional[float] = None
    dispersion_energy: Optional[float] = None
    solvation_energy: Optional[float] = None
    
    def to_dict(self, config: Optional[OutputConfig] = None) -> dict[str, Any]:
        """Convert to dictionary with unit conversion."""
        cfg = config or OutputConfig()
        result: dict[str, Any] = {}
        
        def convert_and_format(value: Optional[float]) -> Optional[str]:
            if value is None:
                return None
            converted = convert_energy(value, EnergyUnit.HARTREE, cfg.energy_unit)
            return f"{converted:.{cfg.energy_precision}f}"
        
        result["total_energy"] = convert_and_format(self.total_energy)
        result["unit"] = get_energy_unit_label(cfg.energy_unit)
        
        if self.nuclear_repulsion is not None:
            result["nuclear_repulsion"] = convert_and_format(self.nuclear_repulsion)
        if self.electronic_energy is not None:
            result["electronic_energy"] = convert_and_format(self.electronic_energy)
        if self.correlation_energy is not None:
            result["correlation_energy"] = convert_and_format(self.correlation_energy)
        if self.scf_energy is not None:
            result["scf_energy"] = convert_and_format(self.scf_energy)
        if self.dispersion_energy is not None:
            result["dispersion_energy"] = convert_and_format(self.dispersion_energy)
        if self.solvation_energy is not None:
            result["solvation_energy"] = convert_and_format(self.solvation_energy)
        
        return result


# =============================================================================
# JSON FORMATTING
# =============================================================================

class ResultEncoder(json.JSONEncoder):
    """Custom JSON encoder for calculation results."""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return super().default(obj)


def to_json(
    data: Any,
    config: Optional[OutputConfig] = None,
    pretty: bool = True
) -> str:
    """
    Convert data to JSON string.
    
    Args:
        data: Data to convert.
        config: Output configuration.
        pretty: Use pretty printing with indentation.
        
    Returns:
        JSON string.
    """
    cfg = config or OutputConfig()
    indent = cfg.indent if pretty else None
    return json.dumps(data, cls=ResultEncoder, indent=indent)


def from_json(json_string: str) -> Any:
    """
    Parse JSON string to Python object.
    
    Args:
        json_string: JSON string to parse.
        
    Returns:
        Parsed Python object.
    """
    return json.loads(json_string)


# =============================================================================
# TEXT REPORT FORMATTING
# =============================================================================

def format_energy_report(
    result: EnergyResult,
    metadata: Optional[CalculationMetadata] = None,
    config: Optional[OutputConfig] = None,
    style: ReportStyle = ReportStyle.DETAILED
) -> str:
    """
    Format an energy result as a text report.
    
    Args:
        result: Energy result to format.
        metadata: Optional calculation metadata.
        config: Output configuration.
        style: Report formatting style.
        
    Returns:
        Formatted text report.
    """
    cfg = config or OutputConfig()
    lines = []
    
    # Header
    lines.append("=" * 70)
    lines.append("ENERGY CALCULATION RESULTS")
    lines.append("=" * 70)
    lines.append("")
    
    # Metadata section
    if metadata and cfg.include_metadata:
        lines.append("-" * 40)
        lines.append("Calculation Details")
        lines.append("-" * 40)
        if metadata.method:
            lines.append(f"  Method:        {metadata.method.upper()}")
        if metadata.basis_set:
            lines.append(f"  Basis Set:     {metadata.basis_set}")
        if metadata.reference:
            lines.append(f"  Reference:     {metadata.reference}")
        if metadata.n_atoms:
            lines.append(f"  Atoms:         {metadata.n_atoms}")
        if metadata.n_electrons:
            lines.append(f"  Electrons:     {metadata.n_electrons}")
        if metadata.charge != 0 or metadata.multiplicity != 1:
            lines.append(f"  Charge/Mult:   {metadata.charge} / {metadata.multiplicity}")
        lines.append("")
    
    # Energy section
    unit_label = get_energy_unit_label(cfg.energy_unit)
    precision = cfg.energy_precision
    
    def format_energy(value: Optional[float], label: str) -> Optional[str]:
        if value is None:
            return None
        converted = convert_energy(value, EnergyUnit.HARTREE, cfg.energy_unit)
        return f"  {label:<25} {converted:>{precision + 8}.{precision}f} {unit_label}"
    
    lines.append("-" * 40)
    lines.append("Energies")
    lines.append("-" * 40)
    
    # Always show total energy
    line = format_energy(result.total_energy, "Total Energy:")
    if line:
        lines.append(line)
    
    # Show components based on style
    if style in (ReportStyle.DETAILED, ReportStyle.VERBOSE):
        if result.scf_energy is not None:
            line = format_energy(result.scf_energy, "SCF Energy:")
            if line:
                lines.append(line)
        
        if result.correlation_energy is not None:
            line = format_energy(result.correlation_energy, "Correlation Energy:")
            if line:
                lines.append(line)
        
        if result.nuclear_repulsion is not None:
            line = format_energy(result.nuclear_repulsion, "Nuclear Repulsion:")
            if line:
                lines.append(line)
        
        if result.electronic_energy is not None:
            line = format_energy(result.electronic_energy, "Electronic Energy:")
            if line:
                lines.append(line)
        
        if result.dispersion_energy is not None:
            line = format_energy(result.dispersion_energy, "Dispersion Correction:")
            if line:
                lines.append(line)
        
        if result.solvation_energy is not None:
            line = format_energy(result.solvation_energy, "Solvation Energy:")
            if line:
                lines.append(line)
    
    lines.append("")
    
    # Timing section
    if metadata and cfg.include_timings and (metadata.wall_time or metadata.cpu_time):
        lines.append("-" * 40)
        lines.append("Timings")
        lines.append("-" * 40)
        if metadata.wall_time:
            lines.append(f"  Wall Time:     {format_time(metadata.wall_time)}")
        if metadata.cpu_time:
            lines.append(f"  CPU Time:      {format_time(metadata.cpu_time)}")
        lines.append("")
    
    lines.append("=" * 70)
    
    return "\n".join(lines)


def format_time(seconds: float) -> str:
    """
    Format time duration in human-readable form.
    
    Args:
        seconds: Time in seconds.
        
    Returns:
        Formatted time string.
    """
    if seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes} min {secs:.1f} s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours} h {minutes} min {secs:.0f} s"


# =============================================================================
# TABLE FORMATTING
# =============================================================================

def format_data_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    title: Optional[str] = None,
    alignment: Optional[Sequence[str]] = None
) -> str:
    """
    Format data as an aligned text table.
    
    Args:
        headers: Column headers.
        rows: Row data.
        title: Optional table title.
        alignment: Column alignments ('l', 'r', 'c' for each column).
        
    Returns:
        Formatted table string.
    """
    # Convert all cells to strings
    str_headers = [str(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]
    
    # Calculate column widths
    n_cols = len(headers)
    widths = [len(h) for h in str_headers]
    
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < n_cols:
                widths[i] = max(widths[i], len(cell))
    
    # Default alignment (left for text, right for numbers)
    if alignment is None:
        alignment = ['l'] * n_cols
    
    def align_cell(text: str, width: int, align: str) -> str:
        if align == 'r':
            return text.rjust(width)
        elif align == 'c':
            return text.center(width)
        return text.ljust(width)
    
    lines = []
    
    # Title
    if title:
        total_width = sum(widths) + 3 * (n_cols - 1)
        lines.append(title.center(total_width))
        lines.append("")
    
    # Header
    header_line = " | ".join(
        align_cell(str_headers[i], widths[i], 'c')
        for i in range(n_cols)
    )
    lines.append(header_line)
    
    # Separator
    sep_line = "-+-".join("-" * w for w in widths)
    lines.append(sep_line)
    
    # Rows
    for row in str_rows:
        row_line = " | ".join(
            align_cell(row[i] if i < len(row) else "", widths[i], alignment[i])
            for i in range(n_cols)
        )
        lines.append(row_line)
    
    return "\n".join(lines)


def format_csv(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    delimiter: str = ",",
    quote_strings: bool = True
) -> str:
    """
    Format data as CSV.
    
    Args:
        headers: Column headers.
        rows: Row data.
        delimiter: Field delimiter.
        quote_strings: Quote string values.
        
    Returns:
        CSV string.
    """
    def format_cell(value: Any) -> str:
        if value is None:
            return ""
        s = str(value)
        if quote_strings and isinstance(value, str):
            if delimiter in s or '"' in s or '\n' in s:
                s = '"' + s.replace('"', '""') + '"'
        return s
    
    lines = []
    
    # Header
    lines.append(delimiter.join(format_cell(h) for h in headers))
    
    # Rows
    for row in rows:
        lines.append(delimiter.join(format_cell(cell) for cell in row))
    
    return "\n".join(lines)


def format_markdown_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    alignment: Optional[Sequence[str]] = None
) -> str:
    """
    Format data as a Markdown table.
    
    Args:
        headers: Column headers.
        rows: Row data.
        alignment: Column alignments ('l', 'r', 'c').
        
    Returns:
        Markdown table string.
    """
    n_cols = len(headers)
    
    # Convert to strings
    str_headers = [str(h) for h in headers]
    str_rows = [[str(cell) for cell in row] for row in rows]
    
    # Calculate widths
    widths = [len(h) for h in str_headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            if i < n_cols:
                widths[i] = max(widths[i], len(cell))
    
    # Default alignment
    if alignment is None:
        alignment = ['l'] * n_cols
    
    lines = []
    
    # Header
    header_line = "| " + " | ".join(
        str_headers[i].ljust(widths[i]) for i in range(n_cols)
    ) + " |"
    lines.append(header_line)
    
    # Separator with alignment
    sep_parts = []
    for i in range(n_cols):
        if alignment[i] == 'c':
            sep_parts.append(":" + "-" * (widths[i] - 2) + ":")
        elif alignment[i] == 'r':
            sep_parts.append("-" * (widths[i] - 1) + ":")
        else:
            sep_parts.append("-" * widths[i])
    sep_line = "| " + " | ".join(sep_parts) + " |"
    lines.append(sep_line)
    
    # Rows
    for row in str_rows:
        row_cells = []
        for i in range(n_cols):
            cell = row[i] if i < len(row) else ""
            if alignment[i] == 'r':
                row_cells.append(cell.rjust(widths[i]))
            elif alignment[i] == 'c':
                row_cells.append(cell.center(widths[i]))
            else:
                row_cells.append(cell.ljust(widths[i]))
        row_line = "| " + " | ".join(row_cells) + " |"
        lines.append(row_line)
    
    return "\n".join(lines)


# =============================================================================
# QCSCHEMA CONVERSION
# =============================================================================

def to_qcschema_result(
    energy: float,
    method: str,
    basis: str,
    molecule: dict[str, Any],
    properties: Optional[dict[str, Any]] = None,
    return_result: bool = True,
    extras: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """
    Convert results to QCSchema AtomicResult format.
    
    Args:
        energy: Total energy in Hartree.
        method: Calculation method.
        basis: Basis set.
        molecule: Molecule specification (QCSchema Molecule).
        properties: Additional calculated properties.
        return_result: Energy or gradient/hessian.
        extras: Additional information.
        
    Returns:
        QCSchema AtomicResult dictionary.
    """
    result: dict[str, Any] = {
        "schema_name": "qcschema_output",
        "schema_version": 1,
        "success": True,
        "molecule": molecule,
        "driver": "energy",
        "model": {
            "method": method,
            "basis": basis,
        },
        "keywords": {},
        "return_result": energy if return_result else None,
        "properties": {
            "return_energy": energy,
            "calcinfo_natom": molecule.get("natom", len(molecule.get("symbols", []))),
        },
    }
    
    if properties:
        result["properties"].update(properties)
    
    if extras:
        result["extras"] = extras
    
    return result


def from_qcschema_result(qcschema: dict[str, Any]) -> tuple[float, dict[str, Any]]:
    """
    Extract results from QCSchema AtomicResult.
    
    Args:
        qcschema: QCSchema result dictionary.
        
    Returns:
        Tuple of (energy, properties_dict).
    """
    energy = qcschema.get("return_result", 0.0)
    if energy is None:
        energy = qcschema.get("properties", {}).get("return_energy", 0.0)
    
    properties = qcschema.get("properties", {})
    
    return (energy, properties)


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def truncate_float(value: float, precision: int) -> float:
    """
    Truncate a float to specified precision.
    
    Args:
        value: Float value.
        precision: Number of decimal places.
        
    Returns:
        Truncated value.
    """
    multiplier = 10 ** precision
    return int(value * multiplier) / multiplier


def format_scientific(value: float, precision: int = 6) -> str:
    """
    Format a number in scientific notation.
    
    Args:
        value: Number to format.
        precision: Significant figures.
        
    Returns:
        Formatted string.
    """
    return f"{value:.{precision}E}"


def format_fixed(value: float, precision: int = 6) -> str:
    """
    Format a number in fixed-point notation.
    
    Args:
        value: Number to format.
        precision: Decimal places.
        
    Returns:
        Formatted string.
    """
    return f"{value:.{precision}f}"


def format_with_uncertainty(
    value: float,
    uncertainty: float,
    precision: Optional[int] = None
) -> str:
    """
    Format a value with uncertainty.
    
    Args:
        value: Central value.
        uncertainty: Uncertainty (standard deviation).
        precision: Decimal places (auto if None).
        
    Returns:
        Formatted string like "1.234 ± 0.005".
    """
    import math
    
    if precision is None:
        # Determine precision from uncertainty magnitude
        if uncertainty > 0:
            precision = max(0, -int(math.floor(math.log10(uncertainty))) + 1)
        else:
            precision = 6
    
    return f"{value:.{precision}f} ± {uncertainty:.{precision}f}"
