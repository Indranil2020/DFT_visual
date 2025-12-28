"""
Generic Output Parser for Psi4 MCP Server.

Provides base parsing utilities.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Tuple


@dataclass
class ParseResult:
    """Result of parsing operation."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class GenericParser:
    """Base class for output parsers."""
    
    FLOAT_PATTERN = r"[-+]?\d*\.?\d+(?:[eEdD][-+]?\d+)?"
    INT_PATTERN = r"[-+]?\d+"
    
    def __init__(self):
        self._patterns: Dict[str, Pattern] = {}
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns."""
        self._patterns["float"] = re.compile(self.FLOAT_PATTERN)
        self._patterns["int"] = re.compile(self.INT_PATTERN)
    
    def extract_float(self, text: str, pattern: str) -> Optional[float]:
        """Extract a float value using pattern."""
        match = re.search(pattern, text)
        if match:
            try:
                value_str = match.group(1) if match.lastindex else match.group(0)
                return float(value_str.replace("D", "E").replace("d", "e"))
            except (ValueError, IndexError):
                return None
        return None
    
    def extract_int(self, text: str, pattern: str) -> Optional[int]:
        """Extract an integer value using pattern."""
        match = re.search(pattern, text)
        if match:
            try:
                value_str = match.group(1) if match.lastindex else match.group(0)
                return int(value_str)
            except (ValueError, IndexError):
                return None
        return None
    
    def extract_all_floats(self, text: str) -> List[float]:
        """Extract all float values from text."""
        matches = self._patterns["float"].findall(text)
        result = []
        for m in matches:
            try:
                result.append(float(m.replace("D", "E").replace("d", "e")))
            except ValueError:
                continue
        return result
    
    def find_section(self, text: str, start: str, end: str) -> Optional[str]:
        """Find section between markers."""
        start_idx = text.find(start)
        if start_idx == -1:
            return None
        end_idx = text.find(end, start_idx + len(start))
        if end_idx == -1:
            return text[start_idx:]
        return text[start_idx:end_idx]
    
    def parse_table(self, text: str, n_cols: int) -> List[List[str]]:
        """Parse space-separated table."""
        rows = []
        for line in text.strip().split("\n"):
            parts = line.split()
            if len(parts) >= n_cols:
                rows.append(parts[:n_cols])
        return rows
    
    def parse(self, text: str) -> ParseResult:
        """Parse output text. Override in subclasses."""
        return ParseResult(success=True)


def parse_output_section(
    text: str,
    section_name: str,
    patterns: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Parse a named section from output."""
    parser = GenericParser()
    result: Dict[str, Any] = {}
    
    if patterns:
        for key, pattern in patterns.items():
            value = parser.extract_float(text, pattern)
            if value is not None:
                result[key] = value
    
    return result
