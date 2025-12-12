"""
CIS (Configuration Interaction Singles) Tool.

MCP tool for computing excited states using CIS.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class CISToolInput(ToolInput):
    """Input schema for CIS calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_states: int = Field(default=5, description="Number of excited states")
    triplets: bool = Field(default=False, description="Compute triplet states")
    convergence: float = Field(default=1e-6, description="Convergence threshold")
    max_iterations: int = Field(default=100, description="Maximum iterations")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class CISTool(BaseTool[CISToolInput, ToolOutput]):
    """
    MCP tool for CIS (Configuration Interaction Singles) calculations.
    
    CIS is the simplest wavefunction method for excited states. It includes
    only single excitations from the HF reference, making it equivalent to
    TDA with HF (no correlation).
    
    Properties:
    - Size-consistent
    - Variational for excitation energies
    - Fast but limited accuracy
    - Typical error: 1-2 eV for valence states
    
    Best for:
    - Quick screening
    - Qualitative excited state ordering
    - Large molecules where higher methods are too expensive
    """
    
    name: ClassVar[str] = "calculate_cis"
    description: ClassVar[str] = (
        "Calculate excited states using CIS (Configuration Interaction Singles). "
        "Simplest wavefunction method for excited states."
    )
    category: ClassVar[ToolCategory] = ToolCategory.EXCITED_STATES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "basis": {"type": "string", "default": "cc-pvdz"},
                "n_states": {"type": "integer", "default": 5},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: CISToolInput) -> Result[ToolOutput]:
        """Execute CIS calculation."""
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
            psi4.set_options({
                "basis": input_data.basis,
                "roots_per_irrep": [input_data.n_states],
                "tda": True,  # CIS is TDA with HF
            })
            
            # Run CIS (TD-HF with TDA = CIS)
            method_str = f"td-hf/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract excited states
            HARTREE_TO_EV = 27.2114
            HARTREE_TO_NM = 45.56335 * 27.2114
            
            excitations = []
            for i in range(input_data.n_states):
                try:
                    var_prefix = f"TD-HF ROOT 0 -> ROOT {i+1}"
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
                "hf_energy": float(energy),
                "basis": input_data.basis,
                "method": "CIS",
                "n_states_computed": len(excitations),
                "excitations": excitations,
                "notes": [
                    "CIS typically overestimates excitation energies by 1-2 eV",
                    "No dynamical correlation included",
                    "Size-consistent and variational"
                ],
                "units": {"energy": "eV", "wavelength": "nm"}
            }
            
            message = f"CIS: {len(excitations)} excited states"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("CIS calculation failed")
            return Result.failure(CalculationError(
                code="CIS_ERROR",
                message=str(e)
            ))


def calculate_cis(
    geometry: str,
    basis: str = "cc-pvdz",
    n_states: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate excited states using CIS."""
    tool = CISTool()
    return tool.run({
        "geometry": geometry,
        "basis": basis,
        "n_states": n_states,
        **kwargs
    })
