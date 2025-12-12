"""
TD-DFT (Time-Dependent DFT) Tool.

MCP tool for computing excited states using TD-DFT.
"""

from typing import Any, ClassVar, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class TDDFTToolInput(ToolInput):
    """Input schema for TD-DFT calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    functional: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_states: int = Field(default=5, description="Number of excited states")
    triplets: bool = Field(default=False, description="Compute triplet states")
    roots_per_irrep: Optional[list[int]] = Field(
        default=None,
        description="States per irreducible representation"
    )
    convergence: float = Field(default=1e-5, description="Convergence threshold")
    max_iterations: int = Field(default=60, description="Maximum iterations")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class TDDFTTool(BaseTool[TDDFTToolInput, ToolOutput]):
    """
    MCP tool for TD-DFT excited state calculations.
    
    Computes vertical excitation energies, oscillator strengths, and
    transition dipole moments using full linear response TD-DFT (RPA).
    
    For faster calculations, use TDA (Tamm-Dancoff Approximation).
    """
    
    name: ClassVar[str] = "calculate_tddft"
    description: ClassVar[str] = (
        "Calculate excited states using TD-DFT (full linear response). "
        "Returns excitation energies, oscillator strengths, and transitions."
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
                "triplets": {"type": "boolean", "default": False},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: TDDFTToolInput) -> Result[ToolOutput]:
        """Execute TD-DFT calculation."""
        try:
            import psi4
            
            # Configure Psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            # Build molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            
            # Set options
            roots = input_data.roots_per_irrep or [input_data.n_states]
            psi4.set_options({
                "basis": input_data.basis,
                "roots_per_irrep": roots,
                "tdscf_r_convergence": input_data.convergence,
                "tdscf_maxiter": input_data.max_iterations,
                "tda": False,  # Full TD-DFT
            })
            
            if input_data.triplets:
                psi4.set_options({"tdscf_triplets": True})
            
            # Run TD-DFT
            method_str = f"td-{input_data.functional}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract excited state information
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
                    
                    # Get transition dipole
                    try:
                        tdm_x = psi4.variable(f"{var_prefix} TRANSITION DIPOLE X")
                        tdm_y = psi4.variable(f"{var_prefix} TRANSITION DIPOLE Y")
                        tdm_z = psi4.variable(f"{var_prefix} TRANSITION DIPOLE Z")
                        transition_dipole = [float(tdm_x), float(tdm_y), float(tdm_z)]
                    except Exception:
                        transition_dipole = None
                    
                    excitations.append({
                        "state": i + 1,
                        "energy_hartree": float(exc_energy),
                        "energy_ev": exc_ev,
                        "wavelength_nm": wavelength,
                        "oscillator_strength": float(osc_str),
                        "transition_dipole": transition_dipole,
                        "spin_state": "triplet" if input_data.triplets else "singlet",
                    })
                except Exception:
                    break
            
            # Build output
            data = {
                "ground_state_energy": float(energy),
                "functional": input_data.functional,
                "basis": input_data.basis,
                "method": "TD-DFT (RPA)",
                "n_states_requested": input_data.n_states,
                "n_states_computed": len(excitations),
                "excitations": excitations,
                "triplets": input_data.triplets,
                "units": {
                    "energy": "eV",
                    "wavelength": "nm",
                    "oscillator_strength": "dimensionless"
                }
            }
            
            # Identify brightest state
            if excitations:
                brightest = max(excitations, key=lambda x: x["oscillator_strength"])
                data["brightest_state"] = brightest
            
            message = f"TD-DFT: {len(excitations)} excited states computed"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("TD-DFT calculation failed")
            return Result.failure(CalculationError(
                code="TDDFT_ERROR",
                message=str(e)
            ))


def calculate_tddft(
    geometry: str,
    functional: str = "b3lyp",
    basis: str = "cc-pvdz",
    n_states: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate excited states using TD-DFT.
    
    Args:
        geometry: Molecular geometry
        functional: DFT functional
        basis: Basis set
        n_states: Number of excited states
        **kwargs: Additional options
        
    Returns:
        ToolOutput with excited state data
    """
    tool = TDDFTTool()
    return tool.run({
        "geometry": geometry,
        "functional": functional,
        "basis": basis,
        "n_states": n_states,
        **kwargs
    })
