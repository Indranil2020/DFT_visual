"""
Orbital Output Parser for Psi4 MCP Server.

Parses molecular orbital results.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from psi4_mcp.utils.parsing.generic import GenericParser, ParseResult


@dataclass
class OrbitalInfo:
    """Information about a molecular orbital."""
    index: int
    energy: float  # hartree
    occupation: float
    symmetry: str = ""
    is_occupied: bool = True
    is_alpha: bool = True


@dataclass
class OrbitalResult:
    """Parsed orbital result."""
    alpha_orbitals: List[OrbitalInfo] = field(default_factory=list)
    beta_orbitals: List[OrbitalInfo] = field(default_factory=list)
    n_alpha: int = 0
    n_beta: int = 0
    homo_index: int = 0
    lumo_index: int = 0
    homo_energy: float = 0.0
    lumo_energy: float = 0.0
    gap: float = 0.0


class OrbitalParser(GenericParser):
    """Parser for orbital outputs."""
    
    def parse(self, text: str) -> ParseResult:
        """Parse orbital output."""
        return ParseResult(success=True, data={"orbital_result": OrbitalResult()})
    
    def parse_from_wavefunction(self, wfn: Any) -> OrbitalResult:
        """Parse orbital info from Psi4 wavefunction."""
        result = OrbitalResult()
        
        # Get occupation numbers
        n_alpha = wfn.nalpha() if hasattr(wfn, "nalpha") else 0
        n_beta = wfn.nbeta() if hasattr(wfn, "nbeta") else 0
        result.n_alpha = n_alpha
        result.n_beta = n_beta
        
        # Get orbital energies
        if hasattr(wfn, "epsilon_a"):
            eps_a = wfn.epsilon_a()
            if hasattr(eps_a, "np"):
                energies = eps_a.np
                for i, e in enumerate(energies):
                    orb = OrbitalInfo(
                        index=i + 1,
                        energy=float(e),
                        occupation=1.0 if i < n_alpha else 0.0,
                        is_occupied=i < n_alpha,
                        is_alpha=True,
                    )
                    result.alpha_orbitals.append(orb)
                
                if n_alpha > 0 and n_alpha < len(energies):
                    result.homo_index = n_alpha
                    result.lumo_index = n_alpha + 1
                    result.homo_energy = float(energies[n_alpha - 1])
                    result.lumo_energy = float(energies[n_alpha])
                    result.gap = result.lumo_energy - result.homo_energy
        
        return result


def parse_orbital_energies(wfn: Any) -> List[float]:
    """Extract orbital energies from wavefunction."""
    parser = OrbitalParser()
    result = parser.parse_from_wavefunction(wfn)
    return [orb.energy for orb in result.alpha_orbitals]
