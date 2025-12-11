"""
Geometry Optimization Tool.

MCP tool for optimizing molecular geometries to find minimum energy
structures or transition states.

Key Functions:
    - optimize_geometry: Convenience function for geometry optimization
    
Key Classes:
    - OptimizationTool: MCP tool class for geometry optimization
    - OptimizationToolInput: Input schema for optimization tool
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolCategory,
    register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError
from psi4_mcp.runners.optimization_runner import (
    OptimizationRunner,
    run_optimization,
)
from psi4_mcp.runners.base_runner import RunnerConfig


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class OptimizationToolInput(ToolInput):
    """
    Input schema for geometry optimization tool.
    
    Attributes:
        geometry: Initial molecular geometry (XYZ or Psi4 format).
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        opt_type: Optimization type (min, ts).
        geom_maxiter: Maximum optimization iterations.
        g_convergence: Gradient convergence criteria set.
        frozen_atoms: List of frozen atom indices.
        frozen_coordinates: List of frozen internal coordinates.
        constraints: Constraint specifications.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        options: Additional Psi4 options.
    """
    
    geometry: str = Field(
        ...,
        description="Initial molecular geometry in XYZ or Psi4 format",
    )
    
    method: str = Field(
        default="hf",
        description="Calculation method",
    )
    
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    
    charge: int = Field(
        default=0,
        description="Molecular charge",
    )
    
    multiplicity: int = Field(
        default=1,
        description="Spin multiplicity (2S+1)",
    )
    
    opt_type: str = Field(
        default="min",
        description="Optimization type: min (minimum) or ts (transition state)",
        pattern="^(min|ts)$",
    )
    
    geom_maxiter: int = Field(
        default=50,
        description="Maximum optimization iterations",
        ge=1,
        le=1000,
    )
    
    g_convergence: str = Field(
        default="gau_tight",
        description="Gradient convergence criteria set",
        examples=["gau_tight", "gau", "gau_loose", "interfrag_tight", "cfour"],
    )
    
    frozen_atoms: Optional[list[int]] = Field(
        default=None,
        description="List of frozen atom indices (1-indexed)",
    )
    
    frozen_coordinates: Optional[list[str]] = Field(
        default=None,
        description="List of frozen internal coordinates",
    )
    
    constraints: Optional[dict[str, Any]] = Field(
        default=None,
        description="Constraint specifications for constrained optimization",
    )
    
    memory: int = Field(
        default=2000,
        description="Memory limit in MB",
    )
    
    n_threads: int = Field(
        default=1,
        description="Number of threads",
    )
    
    options: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional Psi4 options",
    )


# =============================================================================
# OPTIMIZATION TOOL
# =============================================================================

@register_tool
class OptimizationTool(BaseTool[OptimizationToolInput, ToolOutput]):
    """
    MCP tool for geometry optimization.
    
    Optimizes molecular geometry to find minimum energy structures
    or transition states. Supports various convergence criteria
    and constraint options.
    
    Optimization Types:
        - min: Find minimum (stable structure)
        - ts: Find transition state (saddle point)
    
    Returns:
        Optimization output including:
        - Final optimized geometry
        - Final energy
        - Optimization trajectory
        - Convergence information
    """
    
    name: ClassVar[str] = "optimize_geometry"
    description: ClassVar[str] = (
        "Optimize molecular geometry to find minimum energy structures or "
        "transition states. Supports constraints and various convergence criteria."
    )
    category: ClassVar[ToolCategory] = ToolCategory.CORE
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        """Get JSON schema for input validation."""
        return {
            "geometry": {
                "type": "string",
                "description": "Initial molecular geometry in XYZ or Psi4 format",
            },
            "method": {
                "type": "string",
                "description": "Calculation method",
                "default": "hf",
            },
            "basis": {
                "type": "string",
                "description": "Basis set name",
                "default": "cc-pvdz",
            },
            "charge": {
                "type": "integer",
                "description": "Molecular charge",
                "default": 0,
            },
            "multiplicity": {
                "type": "integer",
                "description": "Spin multiplicity (2S+1)",
                "default": 1,
            },
            "opt_type": {
                "type": "string",
                "description": "Optimization type: min or ts",
                "default": "min",
                "enum": ["min", "ts"],
            },
            "geom_maxiter": {
                "type": "integer",
                "description": "Maximum optimization iterations",
                "default": 50,
            },
            "g_convergence": {
                "type": "string",
                "description": "Convergence criteria set",
                "default": "gau_tight",
            },
            "frozen_atoms": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Frozen atom indices",
            },
            "memory": {
                "type": "integer",
                "description": "Memory limit in MB",
                "default": 2000,
            },
            "n_threads": {
                "type": "integer",
                "description": "Number of threads",
                "default": 1,
            },
        }
    
    def _execute(self, input_data: OptimizationToolInput) -> Result[ToolOutput]:
        """Execute geometry optimization."""
        try:
            # Prepare options
            options = input_data.options or {}
            options["g_convergence"] = input_data.g_convergence
            
            if input_data.frozen_atoms:
                options["frozen_cartesian"] = input_data.frozen_atoms
            
            if input_data.frozen_coordinates:
                options["frozen_distance"] = input_data.frozen_coordinates
            
            # Run optimization
            result = run_optimization(
                geometry=input_data.geometry,
                method=input_data.method,
                basis=input_data.basis,
                charge=input_data.charge,
                multiplicity=input_data.multiplicity,
                maxiter=input_data.geom_maxiter,
                memory=input_data.memory,
                n_threads=input_data.n_threads,
                **options,
            )
            
            if result.is_failure:
                return Result.failure(result.error)
            
            opt_output = result.value
            
            # Build coordinates string
            coords_str = ""
            if opt_output.final_coordinates and opt_output.symbols:
                for i, (symbol, coords) in enumerate(
                    zip(opt_output.symbols, opt_output.final_coordinates)
                ):
                    coords_str += f"{symbol}  {coords[0]:.10f}  {coords[1]:.10f}  {coords[2]:.10f}\n"
            
            # Build response data
            data = {
                "final_energy": opt_output.final_energy,
                "energy_unit": "Hartree",
                "initial_energy": opt_output.initial_energy,
                "final_geometry": coords_str.strip(),
                "converged": opt_output.converged,
                "n_steps": opt_output.n_steps,
                "method": input_data.method,
                "basis": input_data.basis,
                "opt_type": input_data.opt_type,
            }
            
            # Add convergence details
            if opt_output.convergence_criteria:
                data["convergence_criteria"] = {
                    "max_force": opt_output.convergence_criteria.max_force,
                    "rms_force": opt_output.convergence_criteria.rms_force,
                    "max_displacement": opt_output.convergence_criteria.max_displacement,
                    "rms_displacement": opt_output.convergence_criteria.rms_displacement,
                }
            
            # Add trajectory summary
            if opt_output.trajectory:
                energies = [step.energy for step in opt_output.trajectory.steps]
                data["trajectory_summary"] = {
                    "n_steps": len(energies),
                    "initial_energy": energies[0] if energies else None,
                    "final_energy": energies[-1] if energies else None,
                    "energy_change": energies[-1] - energies[0] if len(energies) > 1 else 0,
                }
            
            # Create message
            status = "converged" if opt_output.converged else "did not converge"
            message = (
                f"Geometry optimization {status}: {input_data.method}/{input_data.basis}\n"
                f"Steps: {opt_output.n_steps}\n"
                f"Initial energy: {opt_output.initial_energy:.10f} Hartree\n"
                f"Final energy: {opt_output.final_energy:.10f} Hartree\n"
                f"Energy change: {opt_output.final_energy - opt_output.initial_energy:.10f} Hartree"
            )
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data,
            ))
            
        except Exception as e:
            logger.exception("Optimization failed")
            return Result.failure(CalculationError(
                code="OPTIMIZATION_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def optimize_geometry(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    opt_type: str = "min",
    geom_maxiter: int = 50,
    g_convergence: str = "gau_tight",
    frozen_atoms: Optional[list[int]] = None,
    memory: int = 2000,
    n_threads: int = 1,
    **options: Any,
) -> ToolOutput:
    """
    Optimize molecular geometry.
    
    Args:
        geometry: Initial molecular geometry string.
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        opt_type: Optimization type (min or ts).
        geom_maxiter: Maximum iterations.
        g_convergence: Convergence criteria set.
        frozen_atoms: List of frozen atom indices.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        **options: Additional Psi4 options.
        
    Returns:
        ToolOutput with optimization results.
        
    Examples:
        >>> # Basic optimization
        >>> result = optimize_geometry(
        ...     geometry="O 0 0 0\\nH 0 0 1.0\\nH 0 1.0 0",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        >>> print(result.data["final_geometry"])
        
        >>> # DFT optimization
        >>> result = optimize_geometry(
        ...     geometry="C 0 0 0\\nH 0.63 0.63 0.63\\nH -0.63 -0.63 0.63\\nH -0.63 0.63 -0.63\\nH 0.63 -0.63 -0.63",
        ...     method="b3lyp",
        ...     basis="def2-tzvp"
        ... )
    """
    tool = OptimizationTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "opt_type": opt_type,
        "geom_maxiter": geom_maxiter,
        "g_convergence": g_convergence,
        "memory": memory,
        "n_threads": n_threads,
    }
    
    if frozen_atoms:
        input_data["frozen_atoms"] = frozen_atoms
    
    if options:
        input_data["options"] = options
    
    return tool.run(input_data)


# =============================================================================
# SPECIALIZED FUNCTIONS
# =============================================================================

def find_minimum(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    **kwargs: Any,
) -> ToolOutput:
    """Find minimum energy structure."""
    return optimize_geometry(
        geometry=geometry,
        method=method,
        basis=basis,
        opt_type="min",
        **kwargs,
    )


def find_transition_state(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    **kwargs: Any,
) -> ToolOutput:
    """Find transition state structure."""
    return optimize_geometry(
        geometry=geometry,
        method=method,
        basis=basis,
        opt_type="ts",
        **kwargs,
    )


def constrained_optimization(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    frozen_atoms: Optional[list[int]] = None,
    frozen_distances: Optional[list[tuple[int, int]]] = None,
    frozen_angles: Optional[list[tuple[int, int, int]]] = None,
    **kwargs: Any,
) -> ToolOutput:
    """
    Run constrained geometry optimization.
    
    Args:
        geometry: Initial molecular geometry.
        method: Calculation method.
        basis: Basis set name.
        frozen_atoms: List of frozen atom indices (1-indexed).
        frozen_distances: List of frozen bond distance pairs.
        frozen_angles: List of frozen angle triplets.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with optimization results.
    """
    options = kwargs.pop("options", {}) or {}
    
    if frozen_atoms:
        options["frozen_cartesian"] = frozen_atoms
    
    if frozen_distances:
        options["frozen_distance"] = [
            f"{i}-{j}" for i, j in frozen_distances
        ]
    
    if frozen_angles:
        options["frozen_bend"] = [
            f"{i}-{j}-{k}" for i, j, k in frozen_angles
        ]
    
    return optimize_geometry(
        geometry=geometry,
        method=method,
        basis=basis,
        options=options,
        **kwargs,
    )
