"""
Optimization Output Parser for Psi4 MCP Server.

Parses geometry optimization results.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from psi4_mcp.utils.parsing.generic import GenericParser, ParseResult


@dataclass
class OptimizationStep:
    """Single optimization step."""
    step_number: int
    energy: float
    max_force: Optional[float] = None
    rms_force: Optional[float] = None
    max_disp: Optional[float] = None
    rms_disp: Optional[float] = None
    converged: bool = False


@dataclass
class OptimizationResult:
    """Parsed optimization result."""
    converged: bool
    n_steps: int
    final_energy: float
    initial_energy: Optional[float] = None
    trajectory: List[OptimizationStep] = field(default_factory=list)
    final_geometry: Optional[str] = None
    convergence_criteria: Dict[str, float] = field(default_factory=dict)


class OptimizationParser(GenericParser):
    """Parser for optimization outputs."""
    
    STEP_PATTERN = r"Step\s+(\d+)\s+Energy\s+([-+]?\d+\.\d+)"
    FORCE_PATTERN = r"MAX Force\s+([-+]?\d+\.\d+)"
    RMS_FORCE_PATTERN = r"RMS Force\s+([-+]?\d+\.\d+)"
    CONVERGED_PATTERN = r"Optimization is complete"
    
    def parse(self, text: str) -> ParseResult:
        """Parse optimization output."""
        trajectory = []
        errors = []
        
        # Find all steps
        step_matches = re.findall(self.STEP_PATTERN, text)
        for step_num, energy in step_matches:
            step = OptimizationStep(
                step_number=int(step_num),
                energy=float(energy),
            )
            trajectory.append(step)
        
        # Check convergence
        converged = bool(re.search(self.CONVERGED_PATTERN, text))
        
        # Build result
        result = OptimizationResult(
            converged=converged,
            n_steps=len(trajectory),
            final_energy=trajectory[-1].energy if trajectory else 0.0,
            initial_energy=trajectory[0].energy if trajectory else None,
            trajectory=trajectory,
        )
        
        return ParseResult(
            success=True,
            data={"optimization_result": result},
            errors=errors,
        )
    
    def parse_trajectory_from_wfn(self, trajectory: List[Dict[str, Any]]) -> List[OptimizationStep]:
        """Parse trajectory from Psi4 optimization history."""
        steps = []
        for i, step_data in enumerate(trajectory):
            step = OptimizationStep(
                step_number=i + 1,
                energy=float(step_data.get("energy", 0.0)),
                max_force=step_data.get("max_force"),
                rms_force=step_data.get("rms_force"),
                max_disp=step_data.get("max_disp"),
                rms_disp=step_data.get("rms_disp"),
            )
            steps.append(step)
        return steps


def parse_optimization_trajectory(text: str) -> List[OptimizationStep]:
    """Parse optimization trajectory from output."""
    parser = OptimizationParser()
    result = parser.parse(text)
    opt_result = result.data.get("optimization_result")
    return opt_result.trajectory if opt_result else []
