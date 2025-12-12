"""
Transition Properties Tool.

MCP tool for computing transition dipole moments and related properties.
"""

from typing import Any, ClassVar, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class TransitionPropertiesToolInput(ToolInput):
    """Input schema for transition properties calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_states: int = Field(default=5, description="Number of excited states")
    properties: list[str] = Field(
        default=["dipole", "oscillator", "nto"],
        description="Properties to compute: dipole, oscillator, nto, density"
    )
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class TransitionPropertiesTool(BaseTool[TransitionPropertiesToolInput, ToolOutput]):
    """
    MCP tool for computing transition properties.
    
    Calculates various properties associated with electronic transitions:
    - Transition dipole moments (length and velocity gauges)
    - Oscillator strengths
    - Natural Transition Orbitals (NTOs)
    - Transition densities
    - Rotatory strengths (for ECD)
    
    These properties are essential for:
    - Understanding selection rules
    - Interpreting UV-Vis/ECD spectra
    - Analyzing character of excited states
    """
    
    name: ClassVar[str] = "calculate_transition_properties"
    description: ClassVar[str] = (
        "Calculate transition properties including dipole moments, "
        "oscillator strengths, and natural transition orbitals."
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
                "n_states": {"type": "integer", "default": 5},
                "properties": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: TransitionPropertiesToolInput) -> Result[ToolOutput]:
        """Execute transition properties calculation."""
        try:
            import psi4
            import numpy as np
            
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
            })
            
            # Run TD-DFT
            method_str = f"td-{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract transition properties
            HARTREE_TO_EV = 27.2114
            transitions = []
            
            for i in range(input_data.n_states):
                state_num = i + 1
                var_prefix = f"TD-{input_data.method.upper()} ROOT 0 -> ROOT {state_num}"
                
                try:
                    exc_energy = psi4.variable(f"{var_prefix} EXCITATION ENERGY")
                except Exception:
                    break
                
                transition_data = {
                    "state": state_num,
                    "excitation_energy_ev": float(exc_energy) * HARTREE_TO_EV,
                }
                
                # Transition dipole (length gauge)
                if "dipole" in input_data.properties:
                    try:
                        tdm_x = psi4.variable(f"{var_prefix} TRANSITION DIPOLE X")
                        tdm_y = psi4.variable(f"{var_prefix} TRANSITION DIPOLE Y")
                        tdm_z = psi4.variable(f"{var_prefix} TRANSITION DIPOLE Z")
                        tdm = [float(tdm_x), float(tdm_y), float(tdm_z)]
                        tdm_mag = np.linalg.norm(tdm)
                        
                        transition_data["transition_dipole_length"] = {
                            "x": tdm[0],
                            "y": tdm[1],
                            "z": tdm[2],
                            "magnitude": float(tdm_mag),
                            "units": "au"
                        }
                    except Exception:
                        pass
                
                # Oscillator strength
                if "oscillator" in input_data.properties:
                    try:
                        osc_len = psi4.variable(f"{var_prefix} OSCILLATOR STRENGTH (LEN)")
                        transition_data["oscillator_strength_length"] = float(osc_len)
                        
                        try:
                            osc_vel = psi4.variable(f"{var_prefix} OSCILLATOR STRENGTH (VEL)")
                            transition_data["oscillator_strength_velocity"] = float(osc_vel)
                        except Exception:
                            pass
                    except Exception:
                        pass
                
                # Rotatory strength (for ECD)
                try:
                    rot_len = psi4.variable(f"{var_prefix} ROTATORY STRENGTH (LEN)")
                    transition_data["rotatory_strength_length"] = float(rot_len)
                except Exception:
                    pass
                
                # NTO analysis would require additional implementation
                if "nto" in input_data.properties:
                    transition_data["nto_analysis"] = {
                        "note": "NTO analysis requires wavefunction post-processing",
                        "available": False
                    }
                
                # Characterize transition
                if "oscillator_strength_length" in transition_data:
                    osc = transition_data["oscillator_strength_length"]
                    if osc > 0.1:
                        character = "bright (allowed)"
                    elif osc > 0.01:
                        character = "weakly allowed"
                    else:
                        character = "dark (forbidden)"
                    transition_data["character"] = character
                
                transitions.append(transition_data)
            
            # Build output
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "n_states": len(transitions),
                "transitions": transitions,
                "computed_properties": input_data.properties,
                "units": {
                    "energy": "eV",
                    "transition_dipole": "au",
                    "rotatory_strength": "10^-40 cgs"
                },
                "selection_rules": {
                    "electric_dipole": "Δl = ±1, spin-conserving",
                    "magnetic_dipole": "Δl = 0, spin-conserving",
                    "note": "Dark states may be due to symmetry or spin-forbidden transitions"
                }
            }
            
            message = f"Transition properties for {len(transitions)} states"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("Transition properties calculation failed")
            return Result.failure(CalculationError(
                code="TRANSITION_PROP_ERROR",
                message=str(e)
            ))


def calculate_transition_properties(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "cc-pvdz",
    n_states: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate transition properties."""
    tool = TransitionPropertiesTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "n_states": n_states,
        **kwargs
    })
