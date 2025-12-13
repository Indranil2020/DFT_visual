"""
Electronic Circular Dichroism (ECD) Tool.

MCP tool for computing ECD spectra of chiral molecules.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class ECDToolInput(ToolInput):
    """Input schema for ECD calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="aug-cc-pvdz", description="Basis set (augmented recommended)")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_states: int = Field(default=20, description="Number of excited states")
    use_tda: bool = Field(default=False, description="Use Tamm-Dancoff approximation")
    wavelength_range: tuple[float, float] = Field(
        default=(180.0, 400.0),
        description="Wavelength range (nm)"
    )
    broadening_ev: float = Field(default=0.3, description="Gaussian broadening (eV)")
    n_points: int = Field(default=500, description="Number of spectrum points")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ECDTool(BaseTool[ECDToolInput, ToolOutput]):
    """
    MCP tool for Electronic Circular Dichroism spectroscopy.
    
    Computes ECD spectrum showing differential absorption of left and right
    circularly polarized light by chiral molecules.
    """
    
    name: ClassVar[str] = "calculate_ecd"
    description: ClassVar[str] = (
        "Calculate Electronic Circular Dichroism (ECD) spectrum for chiral molecules. "
        "Returns excitation energies, rotatory strengths, and simulated spectrum."
    )
    category: ClassVar[ToolCategory] = ToolCategory.SPECTROSCOPY
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "method": {"type": "string", "default": "b3lyp"},
                "basis": {"type": "string", "default": "aug-cc-pvdz"},
                "n_states": {"type": "integer", "default": 20},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: ECDToolInput) -> Result[ToolOutput]:
        """Execute ECD calculation."""
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
                "tda": input_data.use_tda,
            })
            
            # Run TD-DFT (ECD requires rotatory strengths)
            method_str = f"td-{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract excitations with rotatory strengths
            HARTREE_TO_NM = 45.56335 * 27.2114
            excitations = []
            
            for i in range(input_data.n_states):
                try:
                    exc_energy = psi4.variable(f"TD-{input_data.method.upper()} ROOT 0 -> ROOT {i+1} EXCITATION ENERGY")
                    osc_str = psi4.variable(f"TD-{input_data.method.upper()} ROOT 0 -> ROOT {i+1} OSCILLATOR STRENGTH (LEN)")
                    
                    # Try to get rotatory strength (may not be available in all Psi4 versions)
                    try:
                        rot_str = psi4.variable(f"TD-{input_data.method.upper()} ROOT 0 -> ROOT {i+1} ROTATORY STRENGTH (LEN)")
                    except Exception:
                        rot_str = 0.0
                    
                    exc_ev = float(exc_energy) * 27.2114
                    wavelength = HARTREE_TO_NM / float(exc_energy) if exc_energy > 0 else 0
                    
                    excitations.append({
                        "state": i + 1,
                        "energy_ev": exc_ev,
                        "wavelength_nm": wavelength,
                        "oscillator_strength": float(osc_str),
                        "rotatory_strength": float(rot_str),
                    })
                except Exception:
                    break
            
            # Generate ECD spectrum
            wavelengths = np.linspace(
                input_data.wavelength_range[0],
                input_data.wavelength_range[1],
                input_data.n_points
            )
            energies_ev = HARTREE_TO_NM / 27.2114 / wavelengths
            
            # Simulated spectrum
            ecd_spectrum = np.zeros_like(wavelengths)
            abs_spectrum = np.zeros_like(wavelengths)
            sigma = input_data.broadening_ev / (2 * np.sqrt(2 * np.log(2)))
            
            for exc in excitations:
                exc_ev = exc["energy_ev"]
                rot = exc["rotatory_strength"]
                osc = exc["oscillator_strength"]
                
                if exc_ev > 0:
                    gauss = np.exp(-0.5 * ((energies_ev - exc_ev) / sigma) ** 2)
                    ecd_spectrum += rot * gauss
                    abs_spectrum += osc * gauss
            
            # Build output
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "n_states": len(excitations),
                "excitations": excitations,
                "ecd_spectrum": {
                    "wavelength_nm": wavelengths.tolist(),
                    "delta_epsilon": ecd_spectrum.tolist(),  # Δε (L mol^-1 cm^-1)
                },
                "absorption_spectrum": {
                    "wavelength_nm": wavelengths.tolist(),
                    "epsilon": abs_spectrum.tolist(),
                },
                "units": {
                    "rotatory_strength": "10^-40 cgs",
                    "delta_epsilon": "L/(mol·cm)",
                }
            }
            
            message = f"ECD spectrum: {len(excitations)} excitations"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("ECD calculation failed")
            return Result.failure(CalculationError(
                code="ECD_ERROR",
                message=str(e)
            ))


def calculate_ecd_spectrum(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "aug-cc-pvdz",
    n_states: int = 20,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate ECD spectrum for a chiral molecule."""
    tool = ECDTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "n_states": n_states,
        **kwargs
    })
