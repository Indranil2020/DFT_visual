"""
String Utility Functions for Psi4 MCP Server.

This module provides string manipulation utilities for parsing,
formatting, and processing text data commonly encountered in
quantum chemistry workflows.

Functions cover:
    - Element symbol normalization
    - Coordinate parsing
    - Output formatting
    - Name/identifier manipulation
"""

import re
from typing import Sequence, Optional


# =============================================================================
# ELEMENT SYMBOL HANDLING
# =============================================================================

def normalize_element_symbol(symbol: str) -> str:
    """
    Normalize an element symbol to standard form (first letter uppercase, rest lowercase).
    
    Args:
        symbol: Element symbol string (e.g., "h", "HE", "fe").
        
    Returns:
        Normalized symbol (e.g., "H", "He", "Fe").
    """
    cleaned = symbol.strip()
    if not cleaned:
        return ""
    
    # Remove any ghost atom prefix (e.g., "@H", "Gh(H)")
    if cleaned.startswith("@"):
        cleaned = cleaned[1:]
    elif cleaned.lower().startswith("gh(") and cleaned.endswith(")"):
        cleaned = cleaned[3:-1]
    
    # Handle isotope prefixes (e.g., "2H" for deuterium)
    match = re.match(r'^(\d+)?([A-Za-z]+)$', cleaned)
    if match:
        isotope, element = match.groups()
        normalized_element = element.capitalize()
        if isotope:
            return f"{isotope}{normalized_element}"
        return normalized_element
    
    return cleaned.capitalize()


def is_valid_element_symbol(symbol: str) -> bool:
    """
    Check if a string could be a valid element symbol.
    
    Args:
        symbol: String to check.
        
    Returns:
        True if it matches element symbol pattern.
    """
    # Pattern: optional isotope number, then 1-2 letters
    pattern = r'^(\d+)?[A-Za-z]{1,2}$'
    return bool(re.match(pattern, symbol.strip()))


def parse_element_and_isotope(symbol: str) -> tuple[str, Optional[int]]:
    """
    Parse an element symbol into element and isotope number.
    
    Args:
        symbol: Element symbol, possibly with isotope (e.g., "2H", "13C").
        
    Returns:
        Tuple of (element_symbol, isotope_number or None).
    """
    cleaned = symbol.strip()
    match = re.match(r'^(\d+)?([A-Za-z]+)$', cleaned)
    
    if not match:
        return (cleaned.capitalize(), None)
    
    isotope_str, element = match.groups()
    isotope = int(isotope_str) if isotope_str else None
    
    return (element.capitalize(), isotope)


# =============================================================================
# COORDINATE STRING PARSING
# =============================================================================

def parse_xyz_line(line: str) -> Optional[tuple[str, float, float, float]]:
    """
    Parse a line from XYZ format into element and coordinates.
    
    Args:
        line: Line in format "Element  X  Y  Z".
        
    Returns:
        Tuple of (element, x, y, z) or None if parsing fails.
    """
    parts = line.split()
    
    if len(parts) < 4:
        return None
    
    element = normalize_element_symbol(parts[0])
    
    # Handle possible failure in float conversion
    x_str = parts[1].replace('D', 'E').replace('d', 'e')
    y_str = parts[2].replace('D', 'E').replace('d', 'e')
    z_str = parts[3].replace('D', 'E').replace('d', 'e')
    
    # Validate that these can be converted to floats
    x_valid = is_numeric_string(x_str)
    y_valid = is_numeric_string(y_str)
    z_valid = is_numeric_string(z_str)
    
    if not (x_valid and y_valid and z_valid):
        return None
    
    return (element, float(x_str), float(y_str), float(z_str))


def format_xyz_line(
    element: str, 
    x: float, 
    y: float, 
    z: float, 
    precision: int = 10
) -> str:
    """
    Format an XYZ coordinate line.
    
    Args:
        element: Element symbol.
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        precision: Number of decimal places.
        
    Returns:
        Formatted XYZ line.
    """
    width = precision + 6  # Account for sign, integer part, decimal point
    return f"{element:>2s}  {x:>{width}.{precision}f}  {y:>{width}.{precision}f}  {z:>{width}.{precision}f}"


def parse_geometry_string(geometry: str) -> list[tuple[str, float, float, float]]:
    """
    Parse a multi-line geometry string into a list of atoms.
    
    Handles various formats including XYZ block and Psi4 molecule strings.
    
    Args:
        geometry: Multi-line geometry string.
        
    Returns:
        List of (element, x, y, z) tuples.
    """
    atoms = []
    lines = geometry.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines, comments, and special directives
        if not line:
            continue
        if line.startswith('#') or line.startswith('!'):
            continue
        if line.startswith('--'):  # Fragment separator
            continue
        if '=' in line:  # Psi4 options like "units angstrom"
            continue
        if line.lower() in ('units', 'angstrom', 'bohr', 'symmetry', 'noreorient', 'nocom'):
            continue
        
        result = parse_xyz_line(line)
        if result:
            atoms.append(result)
    
    return atoms


# =============================================================================
# NUMBER FORMATTING AND PARSING
# =============================================================================

def is_numeric_string(s: str) -> bool:
    """
    Check if a string represents a valid number.
    
    Args:
        s: String to check.
        
    Returns:
        True if the string can be converted to a float.
    """
    # Replace Fortran-style exponent notation
    cleaned = s.strip().replace('D', 'E').replace('d', 'e')
    
    if not cleaned:
        return False
    
    # Check for valid float pattern
    pattern = r'^[+-]?(\d+\.?\d*|\d*\.?\d+)([eE][+-]?\d+)?$'
    return bool(re.match(pattern, cleaned))


def parse_float_safe(s: str, default: float = 0.0) -> float:
    """
    Safely parse a string to float, returning default on failure.
    
    Args:
        s: String to parse.
        default: Value to return on failure.
        
    Returns:
        Parsed float or default value.
    """
    cleaned = s.strip().replace('D', 'E').replace('d', 'e')
    
    if not is_numeric_string(cleaned):
        return default
    
    return float(cleaned)


def format_scientific(value: float, precision: int = 6) -> str:
    """
    Format a number in scientific notation.
    
    Args:
        value: Number to format.
        precision: Number of significant digits.
        
    Returns:
        Formatted string (e.g., "1.234567E+02").
    """
    return f"{value:.{precision}E}"


def format_fixed(value: float, precision: int = 6, width: int = 0) -> str:
    """
    Format a number in fixed-point notation.
    
    Args:
        value: Number to format.
        precision: Number of decimal places.
        width: Minimum field width (0 for no padding).
        
    Returns:
        Formatted string.
    """
    if width > 0:
        return f"{value:>{width}.{precision}f}"
    return f"{value:.{precision}f}"


def format_energy(
    value: float, 
    unit: str = "Hartree", 
    precision: int = 10
) -> str:
    """
    Format an energy value with unit.
    
    Args:
        value: Energy value.
        unit: Unit string.
        precision: Number of decimal places.
        
    Returns:
        Formatted energy string.
    """
    return f"{value:.{precision}f} {unit}"


# =============================================================================
# TEXT PROCESSING
# =============================================================================

def clean_whitespace(s: str) -> str:
    """
    Clean up whitespace in a string (collapse multiple spaces, strip).
    
    Args:
        s: Input string.
        
    Returns:
        Cleaned string.
    """
    return ' '.join(s.split())


def remove_comments(text: str, comment_chars: str = "#!") -> str:
    """
    Remove comments from text.
    
    Args:
        text: Input text.
        comment_chars: Characters that start comments.
        
    Returns:
        Text with comments removed.
    """
    lines = []
    for line in text.split('\n'):
        # Find first comment character
        min_pos = len(line)
        for char in comment_chars:
            pos = line.find(char)
            if pos >= 0 and pos < min_pos:
                min_pos = pos
        
        cleaned_line = line[:min_pos].rstrip()
        lines.append(cleaned_line)
    
    return '\n'.join(lines)


def indent_text(text: str, spaces: int = 4) -> str:
    """
    Indent each line of text by a specified number of spaces.
    
    Args:
        text: Input text.
        spaces: Number of spaces to indent.
        
    Returns:
        Indented text.
    """
    prefix = ' ' * spaces
    return '\n'.join(prefix + line for line in text.split('\n'))


def wrap_text(text: str, width: int = 80) -> str:
    """
    Wrap text to a specified line width.
    
    Args:
        text: Input text.
        width: Maximum line width.
        
    Returns:
        Wrapped text.
    """
    words = text.split()
    lines = []
    current_line: list[str] = []
    current_length = 0
    
    for word in words:
        word_len = len(word)
        
        if current_length + word_len + (1 if current_line else 0) <= width:
            current_line.append(word)
            current_length += word_len + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = word_len
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


# =============================================================================
# IDENTIFIER MANIPULATION
# =============================================================================

def to_snake_case(name: str) -> str:
    """
    Convert a string to snake_case.
    
    Args:
        name: Input string (camelCase, PascalCase, or other).
        
    Returns:
        snake_case version.
    """
    # Insert underscore before uppercase letters, then lowercase all
    s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower().replace(' ', '_').replace('-', '_')


def to_camel_case(name: str) -> str:
    """
    Convert a string to camelCase.
    
    Args:
        name: Input string (snake_case or other).
        
    Returns:
        camelCase version.
    """
    components = re.split(r'[_\-\s]+', name)
    if not components:
        return name
    
    return components[0].lower() + ''.join(x.title() for x in components[1:])


def to_pascal_case(name: str) -> str:
    """
    Convert a string to PascalCase.
    
    Args:
        name: Input string.
        
    Returns:
        PascalCase version.
    """
    components = re.split(r'[_\-\s]+', name)
    return ''.join(x.title() for x in components)


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Sanitize a string for use as a filename.
    
    Args:
        name: Input string.
        replacement: Character to replace invalid characters with.
        
    Returns:
        Sanitized filename.
    """
    # Remove or replace invalid filename characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, replacement, name)
    
    # Remove leading/trailing periods and spaces
    sanitized = sanitized.strip('. ')
    
    # Collapse multiple replacements
    sanitized = re.sub(f'{re.escape(replacement)}+', replacement, sanitized)
    
    return sanitized if sanitized else "unnamed"


def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        s: Input string.
        max_length: Maximum length including suffix.
        suffix: String to append if truncated.
        
    Returns:
        Truncated string.
    """
    if len(s) <= max_length:
        return s
    
    truncate_at = max_length - len(suffix)
    if truncate_at < 0:
        truncate_at = 0
    
    return s[:truncate_at] + suffix


# =============================================================================
# TABLE FORMATTING
# =============================================================================

def format_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    separator: str = " | ",
    align: str = "left"
) -> str:
    """
    Format data as a text table.
    
    Args:
        headers: Column headers.
        rows: Row data (list of lists).
        separator: Column separator string.
        align: Alignment ("left", "right", or "center").
        
    Returns:
        Formatted table string.
    """
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
            else:
                widths.append(len(str(cell)))
    
    # Format alignment function
    def align_cell(text: str, width: int) -> str:
        if align == "right":
            return text.rjust(width)
        elif align == "center":
            return text.center(width)
        return text.ljust(width)
    
    # Build table
    lines = []
    
    # Header
    header_line = separator.join(align_cell(h, widths[i]) for i, h in enumerate(headers))
    lines.append(header_line)
    
    # Separator
    sep_line = separator.join('-' * w for w in widths)
    lines.append(sep_line)
    
    # Rows
    for row in rows:
        row_line = separator.join(
            align_cell(str(cell) if i < len(row) else "", widths[i]) 
            for i, cell in enumerate(row)
        )
        lines.append(row_line)
    
    return '\n'.join(lines)


def format_key_value_pairs(
    pairs: dict[str, str],
    separator: str = ": ",
    key_width: int = 0
) -> str:
    """
    Format key-value pairs as aligned text.
    
    Args:
        pairs: Dictionary of key-value pairs.
        separator: String between key and value.
        key_width: Minimum key width (0 to auto-calculate).
        
    Returns:
        Formatted text.
    """
    if not pairs:
        return ""
    
    if key_width == 0:
        key_width = max(len(k) for k in pairs.keys())
    
    lines = []
    for key, value in pairs.items():
        lines.append(f"{key:<{key_width}}{separator}{value}")
    
    return '\n'.join(lines)


# =============================================================================
# MOLECULAR FORMULA PARSING
# =============================================================================

def parse_molecular_formula(formula: str) -> dict[str, int]:
    """
    Parse a molecular formula into element counts.
    
    Args:
        formula: Molecular formula (e.g., "H2O", "C6H12O6", "Ca(OH)2").
        
    Returns:
        Dictionary mapping elements to counts.
    """
    elements: dict[str, int] = {}
    
    # Simple parser for formulas without parentheses
    pattern = r'([A-Z][a-z]?)(\d*)'
    matches = re.findall(pattern, formula)
    
    for element, count in matches:
        if element:
            n = int(count) if count else 1
            elements[element] = elements.get(element, 0) + n
    
    return elements


def format_molecular_formula(elements: dict[str, int], hill_order: bool = True) -> str:
    """
    Format element counts as a molecular formula.
    
    Args:
        elements: Dictionary mapping elements to counts.
        hill_order: Use Hill system ordering (C first, then H, then alphabetical).
        
    Returns:
        Molecular formula string.
    """
    if not elements:
        return ""
    
    def format_element(symbol: str, count: int) -> str:
        if count == 1:
            return symbol
        return f"{symbol}{count}"
    
    if hill_order:
        # Hill system: C first, then H, then alphabetical
        result_parts = []
        
        if "C" in elements:
            result_parts.append(format_element("C", elements["C"]))
            if "H" in elements:
                result_parts.append(format_element("H", elements["H"]))
        
        # Remaining elements alphabetically
        for element in sorted(elements.keys()):
            if element not in ("C", "H") or "C" not in elements:
                if element == "H" and "C" in elements:
                    continue
                result_parts.append(format_element(element, elements[element]))
        
        return "".join(result_parts)
    else:
        # Simple alphabetical order
        return "".join(
            format_element(e, elements[e]) 
            for e in sorted(elements.keys())
        )
