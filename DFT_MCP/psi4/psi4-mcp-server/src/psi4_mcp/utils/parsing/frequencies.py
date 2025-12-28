"""
Frequency Output Parser for Psi4 MCP Server.

Parses vibrational frequency results.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from psi4_mcp.utils.parsing.generic import GenericParser, ParseResult


@dataclass
class VibrationalMode:
    """Single vibrational mode."""
    frequency: float  # cm^-1
    intensity: float = 0.0  # km/mol
    symmetry: str = ""
    reduced_mass: float = 0.0
    force_constant: float = 0.0
    is_imaginary: bool = False


@dataclass
class ThermochemistryResult:
    """Thermochemistry data."""
    temperature: float = 298.15
    pressure: float = 101325.0
    zero_point_energy: float = 0.0  # hartree
    thermal_energy: float = 0.0
    enthalpy: float = 0.0
    entropy: float = 0.0  # cal/(mol·K)
    gibbs_energy: float = 0.0


@dataclass
class FrequencyResult:
    """Parsed frequency result."""
    frequencies: List[float]
    modes: List[VibrationalMode] = field(default_factory=list)
    n_imaginary: int = 0
    thermochemistry: Optional[ThermochemistryResult] = None
    is_minimum: bool = True
    is_transition_state: bool = False


class FrequencyParser(GenericParser):
    """Parser for frequency calculation outputs."""
    
    FREQ_PATTERN = r"Freq\s*\[cm\^-1\]\s*:\s*([-+]?\d+\.?\d*)"
    ZPE_PATTERN = r"Zero-point correction\s*=?\s*([-+]?\d+\.\d+)"
    THERMAL_PATTERN = r"Thermal correction to Energy\s*=?\s*([-+]?\d+\.\d+)"
    ENTHALPY_PATTERN = r"Thermal correction to Enthalpy\s*=?\s*([-+]?\d+\.\d+)"
    
    def parse(self, text: str) -> ParseResult:
        """Parse frequency output."""
        frequencies: List[float] = []
        modes: List[VibrationalMode] = []
        
        # Extract frequencies
        freq_matches = re.findall(self.FREQ_PATTERN, text)
        for freq_str in freq_matches:
            freq = float(freq_str)
            frequencies.append(freq)
            modes.append(VibrationalMode(
                frequency=freq,
                is_imaginary=freq < 0,
            ))
        
        # Count imaginary frequencies
        n_imaginary = sum(1 for f in frequencies if f < 0)
        
        # Parse thermochemistry
        thermo = ThermochemistryResult()
        zpe = self.extract_float(text, self.ZPE_PATTERN)
        if zpe is not None:
            thermo.zero_point_energy = zpe
        
        result = FrequencyResult(
            frequencies=frequencies,
            modes=modes,
            n_imaginary=n_imaginary,
            thermochemistry=thermo,
            is_minimum=n_imaginary == 0,
            is_transition_state=n_imaginary == 1,
        )
        
        return ParseResult(
            success=True,
            data={"frequency_result": result},
        )
    
    def parse_from_vibinfo(self, vibinfo: Dict[str, Any]) -> FrequencyResult:
        """Parse from Psi4 vibrational analysis dict."""
        frequencies = []
        modes = []
        
        if "omega" in vibinfo:
            freq_array = vibinfo["omega"]
            if hasattr(freq_array, "to_array"):
                freq_array = freq_array.to_array()
            frequencies = [float(f) for f in freq_array]
            modes = [VibrationalMode(frequency=f, is_imaginary=f < 0) for f in frequencies]
        
        n_imaginary = sum(1 for f in frequencies if f < 0)
        
        thermo = ThermochemistryResult()
        if "ZPE" in vibinfo:
            thermo.zero_point_energy = float(vibinfo["ZPE"])
        
        return FrequencyResult(
            frequencies=frequencies,
            modes=modes,
            n_imaginary=n_imaginary,
            thermochemistry=thermo,
            is_minimum=n_imaginary == 0,
            is_transition_state=n_imaginary == 1,
        )


def parse_frequency_output(text: str) -> Optional[FrequencyResult]:
    """Convenience function to parse frequency output."""
    parser = FrequencyParser()
    result = parser.parse(text)
    return result.data.get("frequency_result")
