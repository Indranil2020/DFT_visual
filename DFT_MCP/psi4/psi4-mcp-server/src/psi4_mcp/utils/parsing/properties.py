"""
Property Output Parser for Psi4 MCP Server.

Parses molecular property results.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from psi4_mcp.utils.parsing.generic import GenericParser, ParseResult


@dataclass
class DipoleResult:
    """Dipole moment result."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    total: float = 0.0
    unit: str = "debye"


@dataclass
class ChargesResult:
    """Atomic charges result."""
    method: str
    charges: List[float]
    atom_labels: List[str] = field(default_factory=list)


@dataclass
class OrbitalGap:
    """HOMO-LUMO gap result."""
    homo: float
    lumo: float
    gap: float
    unit: str = "hartree"


@dataclass
class PropertyResult:
    """Parsed property result."""
    dipole: Optional[DipoleResult] = None
    quadrupole: Optional[Dict[str, float]] = None
    mulliken_charges: Optional[ChargesResult] = None
    lowdin_charges: Optional[ChargesResult] = None
    orbital_gap: Optional[OrbitalGap] = None
    polarizability: Optional[float] = None


class PropertyParser(GenericParser):
    """Parser for molecular property outputs."""
    
    DIPOLE_PATTERN = r"Dipole Moment.*?X:\s*([-+]?\d+\.\d+).*?Y:\s*([-+]?\d+\.\d+).*?Z:\s*([-+]?\d+\.\d+)"
    TOTAL_DIPOLE_PATTERN = r"Total:\s*([-+]?\d+\.\d+)"
    MULLIKEN_PATTERN = r"Mulliken Charges"
    
    def parse(self, text: str) -> ParseResult:
        """Parse property output."""
        result = PropertyResult()
        
        # Parse dipole
        dipole_match = re.search(self.DIPOLE_PATTERN, text, re.DOTALL)
        if dipole_match:
            x, y, z = float(dipole_match.group(1)), float(dipole_match.group(2)), float(dipole_match.group(3))
            total = (x**2 + y**2 + z**2) ** 0.5
            result.dipole = DipoleResult(x=x, y=y, z=z, total=total)
        
        return ParseResult(success=True, data={"property_result": result})
    
    def parse_from_wavefunction(self, wfn: Any, props: List[str]) -> PropertyResult:
        """Parse properties from Psi4 wavefunction."""
        result = PropertyResult()
        
        # Orbital gap from epsilon arrays
        if hasattr(wfn, "epsilon_a"):
            eps_a = wfn.epsilon_a()
            if hasattr(eps_a, "np"):
                eps = eps_a.np
                n_occ = wfn.nalpha()
                if n_occ > 0 and n_occ < len(eps):
                    homo = float(eps[n_occ - 1])
                    lumo = float(eps[n_occ])
                    result.orbital_gap = OrbitalGap(homo=homo, lumo=lumo, gap=lumo - homo)
        
        return result


def parse_property_output(text: str) -> Optional[PropertyResult]:
    """Convenience function to parse property output."""
    parser = PropertyParser()
    result = parser.parse(text)
    return result.data.get("property_result")
