"""
Excited State Geometry Optimization Tool.

MCP tool for optimizing molecular geometry on excited state surfaces.
"""

from typing import Any, ClassVar, Literal
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class ExcitedOptToolInput(ToolInput):
    """Input schema for excited state optimization."""
    
    geometry: str = Field(..., description="Initial molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional or method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    target_state: int = Field(default=1, description="Target excited state (1 = S1)")
    excited_method: Literal["tddft", "tda", "eom-ccsd"] = Field(
        default="tddft",
        description="Method for excited states"
    )
    convergence: str = Field(default="gau", description="Convergence criteria")
    max_iterations: int = Field(default=50, description="Maximum optimization steps")
    track_root: bool = Field(default=True, description="Track root during optimization")
    memory: int = Field(default=4000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ExcitedOptTool(BaseTool[ExcitedOptToolInput, ToolOutput]):
    """
    MCP tool for excited state geometry optimization.
    
    Optimizes molecular geometry on an excited state potential energy surface.
    Useful for:
    - Finding S1 minimum (fluorescence geometry)
    - Locating conical intersections
    - Studying photochemical reaction pathways
    
    Methods available:
    - TD-DFT / TDA gradient
    - EOM-CCSD gradient
    
    Note: Excited state optimizations require analytical or numerical gradients
    for the excited state, which can be computationally demanding.
    """
    
    name: ClassVar[str] = "optimize_excited_state"
    description: ClassVar[str] = (
        "Optimize molecular geometry on excited state surface. "
        "Finds minimum on specified excited state PES."
    )
    category: ClassVar[ToolCategory] = ToolCategory.EXCITED_STATES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "method": {"type": "string", "default": "b3lyp"},
                "basis": {"type": "string", "default": "cc-pvdz"},
                "target_state": {"type": "integer", "default": 1},
                "excited_method": {"type": "string", "default": "tddft"},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: ExcitedOptToolInput) -> Result[ToolOutput]:
        """Execute excited state optimization."""
        try:
            import psi4
            
            # Configure Psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            # Build molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            initial_geom = molecule.save_string_xyz()
            
            # Set options
            n_states = input_data.target_state + 2  # Extra states for stability
            psi4.set_options({
                "basis": input_data.basis,
                "roots_per_irrep": [n_states],
                "g_convergence": input_data.convergence,
                "geom_maxiter": input_data.max_iterations,
            })
            
            if input_data.excited_method in ["tddft", "tda"]:
                psi4.set_options({"tda": input_data.excited_method == "tda"})
                method_str = f"td-{input_data.method}/{input_data.basis}"
            else:
                method_str = f"eom-ccsd/{input_data.basis}"
            
            # Note: Excited state optimization requires setting the target root
            psi4.set_options({"follow_root": input_data.target_state})
            
            # Run optimization
            try:
                final_energy = psi4.optimize(method_str, molecule=molecule)
                converged = True
            except Exception as opt_error:
                logger.warning(f"Optimization may not have converged: {opt_error}")
                final_energy = psi4.variable("CURRENT ENERGY")
                converged = False
            
            # Get final geometry
            final_geom = molecule.save_string_xyz()
            
            # Get excitation energy at optimized geometry
            HARTREE_TO_EV = 27.2114
            HARTREE_TO_NM = 45.56335 * 27.2114
            
            try:
                if input_data.excited_method in ["tddft", "tda"]:
                    var_prefix = f"TD-{input_data.method.upper()}"
                else:
                    var_prefix = "EOM-CCSD"
                
                exc_energy = psi4.variable(f"{var_prefix} ROOT 0 -> ROOT {input_data.target_state} EXCITATION ENERGY")
                ground_energy = psi4.variable("CURRENT ENERGY") - float(exc_energy)
            except Exception:
                exc_energy = None
                ground_energy = None
            
            # Build output
            data = {
                "converged": converged,
                "target_state": input_data.target_state,
                "method": input_data.excited_method.upper(),
                "functional": input_data.method if input_data.excited_method != "eom-ccsd" else None,
                "basis": input_data.basis,
                "initial_geometry": initial_geom,
                "final_geometry": final_geom,
                "final_total_energy": float(final_energy),
                "excitation_energy_ev": float(exc_energy) * HARTREE_TO_EV if exc_energy else None,
                "emission_wavelength_nm": HARTREE_TO_NM / float(exc_energy) if exc_energy else None,
                "ground_state_energy": float(ground_energy) if ground_energy else None,
                "n_iterations": psi4.variable("CURRENT GEOMETRY ITERATION") if converged else None,
                "units": {
                    "energy": "hartree",
                    "excitation": "eV",
                    "wavelength": "nm"
                },
                "notes": [
                    f"Optimized on S{input_data.target_state} surface",
                    "Emission wavelength corresponds to vertical transition from S1 minimum"
                ]
            }
            
            # Calculate Stokes shift if we have absorption data
            # (would need initial TD-DFT at ground state geometry)
            
            if converged:
                message = f"S{input_data.target_state} optimization converged"
                if data["emission_wavelength_nm"]:
                    message += f", emission: {data['emission_wavelength_nm']:.1f} nm"
            else:
                message = "Optimization did not converge"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=converged,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("Excited state optimization failed")
            return Result.failure(CalculationError(
                code="EXCITED_OPT_ERROR",
                message=str(e)
            ))


def optimize_excited_state(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "cc-pvdz",
    target_state: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """Optimize geometry on excited state surface."""
    tool = ExcitedOptTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "target_state": target_state,
        **kwargs
    })
