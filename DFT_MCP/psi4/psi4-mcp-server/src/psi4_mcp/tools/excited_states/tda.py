"""
TDA (Tamm-Dancoff Approximation) Tool.

MCP tool for computing excited states using TDA.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class TDAToolInput(ToolInput):
    """Input schema for TDA calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    functional: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_states: int = Field(default=5, description="Number of excited states")
    triplets: bool = Field(default=False, description="Compute triplet states")
    convergence: float = Field(default=1e-5, description="Convergence threshold")
    max_iterations: int = Field(default=60, description="Maximum iterations")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class TDATool(BaseTool[TDAToolInput, ToolOutput]):
    """
    MCP tool for TDA (Tamm-Dancoff Approximation) calculations.
    
    TDA is a simplified TD-DFT approach that neglects de-excitation terms.
    It is faster and more numerically stable than full TD-DFT, while
    typically giving similar results for valence excitations.
    
    Advantages:
    - Faster than full TD-DFT
    - Better numerical stability
    - No triplet instability problems
    
    Limitations:
    - Less accurate for charge-transfer states
    - Sum rules not satisfied
    """
    
    name: ClassVar[str] = "calculate_tda"
    description: ClassVar[str] = (
        "Calculate excited states using TDA (Tamm-Dancoff Approximation). "
        "Faster than full TD-DFT with similar accuracy for most cases."
    )
    category: ClassVar[ToolCategory] = ToolCategory.EXCITED_STATES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "functional": {"type": "string", "default": "b3lyp"},
                "basis": {"type": "string", "default": "cc-pvdz"},
                "n_states": {"type": "integer", "default": 5},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: TDAToolInput) -> Result[ToolOutput]:
        """Execute TDA calculation."""
        try:
            import psi4
            
            # Configure Psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            # Build molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            
            # Set options - TDA enabled
            psi4.set_options({
                "basis": input_data.basis,
                "roots_per_irrep": [input_data.n_states],
                "tdscf_r_convergence": input_data.convergence,
                "tdscf_maxiter": input_data.max_iterations,
                "tda": True,  # Tamm-Dancoff Approximation
            })
            
            if input_data.triplets:
                psi4.set_options({"tdscf_triplets": True})
            
            # Run TDA
            method_str = f"td-{input_data.functional}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract excited states
            HARTREE_TO_EV = 27.2114
            HARTREE_TO_NM = 45.56335 * 27.2114
            
            excitations = []
            for i in range(input_data.n_states):
                try:
                    var_prefix = f"TD-{input_data.functional.upper()} ROOT 0 -> ROOT {i+1}"
                    exc_energy = psi4.variable(f"{var_prefix} EXCITATION ENERGY")
                    osc_str = psi4.variable(f"{var_prefix} OSCILLATOR STRENGTH (LEN)")
                    
                    exc_ev = float(exc_energy) * HARTREE_TO_EV
                    wavelength = HARTREE_TO_NM / float(exc_energy) if exc_energy > 0 else 0
                    
                    excitations.append({
                        "state": i + 1,
                        "energy_hartree": float(exc_energy),
                        "energy_ev": exc_ev,
                        "wavelength_nm": wavelength,
                        "oscillator_strength": float(osc_str),
                    })
                except Exception:
                    break
            
            # Build output
            data = {
                "ground_state_energy": float(energy),
                "functional": input_data.functional,
                "basis": input_data.basis,
                "method": "TDA (Tamm-Dancoff)",
                "n_states_computed": len(excitations),
                "excitations": excitations,
                "triplets": input_data.triplets,
                "units": {"energy": "eV", "wavelength": "nm"}
            }
            
            message = f"TDA: {len(excitations)} excited states"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("TDA calculation failed")
            return Result.failure(CalculationError(
                code="TDA_ERROR",
                message=str(e)
            ))


def calculate_tda(
    geometry: str,
    functional: str = "b3lyp",
    basis: str = "cc-pvdz",
    n_states: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate excited states using TDA."""
    tool = TDATool()
    return tool.run({
        "geometry": geometry,
        "functional": functional,
        "basis": basis,
        "n_states": n_states,
        **kwargs
    })
