"""
EOM-CC (Equation of Motion Coupled Cluster) Tool.

MCP tool for computing excited states using EOM-CCSD and variants.
"""

from typing import Any, ClassVar, Literal
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class EOMCCToolInput(ToolInput):
    """Input schema for EOM-CC calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    eom_type: Literal["ee", "ip", "ea"] = Field(
        default="ee",
        description="EOM type: ee (excitations), ip (ionization), ea (electron attachment)"
    )
    n_states: int = Field(default=5, description="Number of target states")
    cc_convergence: float = Field(default=1e-7, description="CC amplitude convergence")
    eom_convergence: float = Field(default=1e-6, description="EOM convergence")
    freeze_core: bool = Field(default=True, description="Freeze core orbitals")
    memory: int = Field(default=4000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class EOMCCTool(BaseTool[EOMCCToolInput, ToolOutput]):
    """
    MCP tool for EOM-CC (Equation of Motion Coupled Cluster) calculations.
    
    EOM-CC is a high-accuracy method for excited states built on top of
    coupled cluster theory.
    
    Available variants:
    - EOM-CCSD-EE: Electronic excitations (standard excited states)
    - EOM-CCSD-IP: Ionization potentials (cation states)
    - EOM-CCSD-EA: Electron affinities (anion states)
    
    Properties:
    - High accuracy (~0.1-0.3 eV for valence states)
    - Size-extensive
    - O(N^6) scaling
    - Good for all types of excited states
    """
    
    name: ClassVar[str] = "calculate_eom_cc"
    description: ClassVar[str] = (
        "Calculate excited states using EOM-CCSD. "
        "High-accuracy method for excitations, ionizations, and electron attachments."
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
                "eom_type": {"type": "string", "default": "ee", "enum": ["ee", "ip", "ea"]},
                "n_states": {"type": "integer", "default": 5},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: EOMCCToolInput) -> Result[ToolOutput]:
        """Execute EOM-CC calculation."""
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
                "freeze_core": input_data.freeze_core,
                "r_convergence": input_data.cc_convergence,
                "roots_per_irrep": [input_data.n_states],
            })
            
            # Determine method
            method_map = {
                "ee": "eom-ccsd",
                "ip": "eom-ccsd-ip",
                "ea": "eom-ccsd-ea"
            }
            method_str = f"{method_map[input_data.eom_type]}/{input_data.basis}"
            
            # Run EOM-CCSD
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract ground state info
            ccsd_energy = psi4.variable("CCSD TOTAL ENERGY")
            ccsd_corr = psi4.variable("CCSD CORRELATION ENERGY")
            
            # Extract excited/ionized states
            HARTREE_TO_EV = 27.2114
            states = []
            
            type_labels = {
                "ee": "EXCITATION",
                "ip": "IONIZATION",
                "ea": "ELECTRON ATTACHMENT"
            }
            
            for i in range(input_data.n_states):
                try:
                    if input_data.eom_type == "ee":
                        var_name = f"EOM-CCSD ROOT 0 -> ROOT {i+1} EXCITATION ENERGY"
                    else:
                        var_name = f"EOM-CCSD ROOT {i+1} TOTAL ENERGY"
                    
                    state_energy = psi4.variable(var_name)
                    
                    if input_data.eom_type == "ee":
                        exc_ev = float(state_energy) * HARTREE_TO_EV
                    else:
                        exc_ev = (float(state_energy) - float(ccsd_energy)) * HARTREE_TO_EV
                    
                    try:
                        osc = psi4.variable(f"EOM-CCSD ROOT 0 -> ROOT {i+1} OSCILLATOR STRENGTH")
                    except Exception:
                        osc = None
                    
                    states.append({
                        "state": i + 1,
                        "energy_ev": abs(exc_ev),
                        "total_energy_hartree": float(state_energy) if input_data.eom_type != "ee" else None,
                        "oscillator_strength": float(osc) if osc else None,
                    })
                except Exception:
                    break
            
            # Build output
            data = {
                "ccsd_total_energy": float(ccsd_energy),
                "ccsd_correlation_energy": float(ccsd_corr),
                "basis": input_data.basis,
                "method": f"EOM-CCSD-{input_data.eom_type.upper()}",
                "eom_type": input_data.eom_type,
                "eom_type_description": type_labels[input_data.eom_type],
                "n_states_computed": len(states),
                "states": states,
                "freeze_core": input_data.freeze_core,
                "units": {"energy": "eV"}
            }
            
            message = f"EOM-CCSD-{input_data.eom_type.upper()}: {len(states)} states"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("EOM-CC calculation failed")
            return Result.failure(CalculationError(
                code="EOM_CC_ERROR",
                message=str(e)
            ))


def calculate_eom_cc(
    geometry: str,
    basis: str = "cc-pvdz",
    eom_type: str = "ee",
    n_states: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate excited states using EOM-CCSD."""
    tool = EOMCCTool()
    return tool.run({
        "geometry": geometry,
        "basis": basis,
        "eom_type": eom_type,
        "n_states": n_states,
        **kwargs
    })
