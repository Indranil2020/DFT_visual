"""
Energy Output Parser for Psi4 MCP Server.

Parses energy calculation results.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from psi4_mcp.utils.parsing.generic import GenericParser, ParseResult


@dataclass
class EnergyResult:
    """Parsed energy calculation result."""
    total_energy: float
    method: str = ""
    basis: str = ""
    scf_energy: Optional[float] = None
    correlation_energy: Optional[float] = None
    mp2_energy: Optional[float] = None
    ccsd_energy: Optional[float] = None
    components: Dict[str, float] = field(default_factory=dict)
    n_iterations: int = 0
    converged: bool = True


class EnergyParser(GenericParser):
    """Parser for energy calculation outputs."""
    
    ENERGY_PATTERNS = {
        "total_scf": r"Total Energy\s*=\s*([-+]?\d+\.\d+)",
        "scf_energy": r"@(?:R|U)?(?:HF|KS)\s+Final Energy:\s*([-+]?\d+\.\d+)",
        "mp2_total": r"MP2 Total Energy\s*=\s*([-+]?\d+\.\d+)",
        "mp2_correlation": r"MP2 Correlation Energy\s*=\s*([-+]?\d+\.\d+)",
        "ccsd_total": r"CCSD Total Energy\s*=\s*([-+]?\d+\.\d+)",
        "ccsd_correlation": r"CCSD Correlation Energy\s*=\s*([-+]?\d+\.\d+)",
        "ccsd_t_total": r"CCSD\(T\) Total Energy\s*=\s*([-+]?\d+\.\d+)",
        "iterations": r"(\d+)\s+iterations",
    }
    
    def parse(self, text: str) -> ParseResult:
        """Parse energy output."""
        result = EnergyResult(total_energy=0.0)
        errors = []
        
        # Try to find total energy
        for pattern_name in ["total_scf", "scf_energy", "mp2_total", "ccsd_total", "ccsd_t_total"]:
            energy = self.extract_float(text, self.ENERGY_PATTERNS[pattern_name])
            if energy is not None:
                result.total_energy = energy
                break
        
        if result.total_energy == 0.0:
            errors.append("Could not find total energy")
        
        # Parse SCF energy
        scf_energy = self.extract_float(text, self.ENERGY_PATTERNS["scf_energy"])
        if scf_energy is not None:
            result.scf_energy = scf_energy
            result.components["scf"] = scf_energy
        
        # Parse correlation energies
        mp2_corr = self.extract_float(text, self.ENERGY_PATTERNS["mp2_correlation"])
        if mp2_corr is not None:
            result.correlation_energy = mp2_corr
            result.components["mp2_correlation"] = mp2_corr
        
        ccsd_corr = self.extract_float(text, self.ENERGY_PATTERNS["ccsd_correlation"])
        if ccsd_corr is not None:
            result.correlation_energy = ccsd_corr
            result.components["ccsd_correlation"] = ccsd_corr
        
        # Parse iterations
        iters = self.extract_int(text, self.ENERGY_PATTERNS["iterations"])
        if iters is not None:
            result.n_iterations = iters
        
        # Check convergence
        if "not converged" in text.lower() or "failed to converge" in text.lower():
            result.converged = False
            errors.append("SCF did not converge")
        
        return ParseResult(
            success=len(errors) == 0,
            data={"energy_result": result},
            errors=errors,
        )
    
    def parse_from_wavefunction(self, wfn: Any) -> EnergyResult:
        """Parse energy from Psi4 wavefunction object."""
        result = EnergyResult(
            total_energy=float(wfn.energy()),
            method=str(wfn.name()) if hasattr(wfn, "name") else "",
            converged=True,
        )
        return result


def parse_energy_output(text: str) -> Optional[EnergyResult]:
    """Convenience function to parse energy output."""
    parser = EnergyParser()
    result = parser.parse(text)
    return result.data.get("energy_result") if result.success else None
