"""
ADC (Algebraic Diagrammatic Construction) Tool.

MCP tool for computing excited states using ADC methods.
"""

from typing import Any, ClassVar, Literal
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class ADCToolInput(ToolInput):
    """Input schema for ADC calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    adc_order: Literal[1, 2, 3] = Field(default=2, description="ADC order (1, 2, or 3)")
    n_states: int = Field(default=5, description="Number of excited states")
    triplets: bool = Field(default=False, description="Compute triplet states")
    convergence: float = Field(default=1e-6, description="Convergence threshold")
    memory: int = Field(default=4000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ADCTool(BaseTool[ADCToolInput, ToolOutput]):
    """
    MCP tool for ADC (Algebraic Diagrammatic Construction) calculations.
    
    ADC is a size-consistent excited state method derived from propagator theory.
    
    Available orders:
    - ADC(1): Equivalent to CIS
    - ADC(2): Includes 2nd-order correlation, similar to CC2
    - ADC(3): 3rd-order, similar to CC3 accuracy
    
    Properties:
    - Size-consistent
    - Systematically improvable
    - ADC(2) is cost-effective for medium-sized molecules
    - Better for Rydberg/charge-transfer than TD-DFT
    """
    
    name: ClassVar[str] = "calculate_adc"
    description: ClassVar[str] = (
        "Calculate excited states using ADC (Algebraic Diagrammatic Construction). "
        "Size-consistent wavefunction method with systematic improvement."
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
                "adc_order": {"type": "integer", "default": 2, "enum": [1, 2, 3]},
                "n_states": {"type": "integer", "default": 5},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: ADCToolInput) -> Result[ToolOutput]:
        """Execute ADC calculation."""
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
                "adc__r_convergence": input_data.convergence,
            })
            
            # Determine method string
            method_map = {1: "adc(1)", 2: "adc(2)", 3: "adc(3)"}
            method_str = f"{method_map[input_data.adc_order]}/{input_data.basis}"
            
            # Run ADC
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract excited states
            HARTREE_TO_EV = 27.2114
            HARTREE_TO_NM = 45.56335 * 27.2114
            
            excitations = []
            method_upper = f"ADC({input_data.adc_order})"
            
            for i in range(input_data.n_states):
                try:
                    var_prefix = f"{method_upper} ROOT 0 -> ROOT {i+1}"
                    exc_energy = psi4.variable(f"{var_prefix} EXCITATION ENERGY")
                    
                    try:
                        osc_str = psi4.variable(f"{var_prefix} OSCILLATOR STRENGTH (LEN)")
                    except Exception:
                        osc_str = 0.0
                    
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
            
            # Get MP2 correlation energy
            try:
                mp2_corr = psi4.variable("MP2 CORRELATION ENERGY")
            except Exception:
                mp2_corr = None
            
            # Build output
            data = {
                "ground_state_energy": float(energy),
                "mp2_correlation_energy": float(mp2_corr) if mp2_corr else None,
                "basis": input_data.basis,
                "method": f"ADC({input_data.adc_order})",
                "adc_order": input_data.adc_order,
                "n_states_computed": len(excitations),
                "excitations": excitations,
                "scaling": {
                    1: "O(N^4)",
                    2: "O(N^5)",
                    3: "O(N^6)"
                }[input_data.adc_order],
                "units": {"energy": "eV", "wavelength": "nm"}
            }
            
            message = f"ADC({input_data.adc_order}): {len(excitations)} excited states"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("ADC calculation failed")
            return Result.failure(CalculationError(
                code="ADC_ERROR",
                message=str(e)
            ))


def calculate_adc(
    geometry: str,
    basis: str = "cc-pvdz",
    adc_order: int = 2,
    n_states: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate excited states using ADC."""
    tool = ADCTool()
    return tool.run({
        "geometry": geometry,
        "basis": basis,
        "adc_order": adc_order,
        "n_states": n_states,
        **kwargs
    })
