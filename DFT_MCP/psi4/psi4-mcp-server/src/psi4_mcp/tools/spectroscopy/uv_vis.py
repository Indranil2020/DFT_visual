"""
UV-Vis Absorption Spectroscopy Tool.

MCP tool for computing electronic absorption spectra using TD-DFT or other
excited state methods.
"""

from typing import Any, ClassVar, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


# =============================================================================
# UV-VIS TOOL
# =============================================================================

class UVVisToolInput(ToolInput):
    """Input schema for UV-Vis calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_states: int = Field(default=10, description="Number of excited states")
    use_tda: bool = Field(default=False, description="Use Tamm-Dancoff approximation")
    wavelength_range: tuple[float, float] = Field(
        default=(200.0, 800.0),
        description="Wavelength range for spectrum (nm)"
    )
    broadening_ev: float = Field(default=0.4, description="Gaussian broadening (eV)")
    n_points: int = Field(default=500, description="Number of spectrum points")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class UVVisTool(BaseTool[UVVisToolInput, ToolOutput]):
    """
    MCP tool for UV-Vis absorption spectroscopy.
    
    Computes electronic excitation energies and oscillator strengths using
    TD-DFT (or TDA), and generates a simulated absorption spectrum.
    """
    
    name: ClassVar[str] = "calculate_uv_vis"
    description: ClassVar[str] = (
        "Calculate UV-Vis electronic absorption spectrum using TD-DFT. "
        "Returns excitation energies, oscillator strengths, and simulated spectrum."
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
                "basis": {"type": "string", "default": "cc-pvdz"},
                "n_states": {"type": "integer", "default": 10},
                "use_tda": {"type": "boolean", "default": False},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: UVVisToolInput) -> Result[ToolOutput]:
        """Execute UV-Vis calculation."""
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
            
            # Set options for TD-DFT
            psi4.set_options({
                "basis": input_data.basis,
                "roots_per_irrep": [input_data.n_states],
                "tda": input_data.use_tda,
            })
            
            # Run TD-DFT
            method_str = f"td-{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract excited state information
            excitations = []
            EV_TO_HARTREE = 0.0367493  # Conversion factor
            HARTREE_TO_NM = 45.56335 * 27.2114  # ~1239.84
            
            for i in range(input_data.n_states):
                try:
                    exc_energy = psi4.variable(f"TD-{input_data.method.upper()} ROOT 0 -> ROOT {i+1} EXCITATION ENERGY")
                    osc_str = psi4.variable(f"TD-{input_data.method.upper()} ROOT 0 -> ROOT {i+1} OSCILLATOR STRENGTH (LEN)")
                    
                    exc_ev = float(exc_energy) * 27.2114  # Hartree to eV
                    wavelength = HARTREE_TO_NM / float(exc_energy) if exc_energy > 0 else 0
                    
                    excitations.append({
                        "state": i + 1,
                        "energy_hartree": float(exc_energy),
                        "energy_ev": exc_ev,
                        "wavelength_nm": wavelength,
                        "oscillator_strength": float(osc_str),
                    })
                except Exception:
                    break  # No more states available
            
            # Generate simulated spectrum
            wavelengths = np.linspace(
                input_data.wavelength_range[0],
                input_data.wavelength_range[1],
                input_data.n_points
            )
            
            # Convert wavelengths to eV for Gaussian convolution
            energies_ev = HARTREE_TO_NM / 27.2114 / wavelengths  # nm to eV
            
            # Generate spectrum with Gaussian broadening
            spectrum = np.zeros_like(wavelengths)
            sigma = input_data.broadening_ev / (2 * np.sqrt(2 * np.log(2)))
            
            for exc in excitations:
                exc_ev = exc["energy_ev"]
                osc = exc["oscillator_strength"]
                if osc > 0 and exc_ev > 0:
                    # Add Gaussian peak
                    spectrum += osc * np.exp(-0.5 * ((energies_ev - exc_ev) / sigma) ** 2)
            
            # Build output
            data = {
                "ground_state_energy": float(energy),
                "method": input_data.method,
                "basis": input_data.basis,
                "approximation": "TDA" if input_data.use_tda else "Full TD-DFT",
                "n_states_computed": len(excitations),
                "excitations": excitations,
                "spectrum": {
                    "wavelength_nm": wavelengths.tolist(),
                    "intensity": spectrum.tolist(),
                    "broadening_ev": input_data.broadening_ev,
                },
                "lambda_max": None,
                "units": {
                    "energy": "eV",
                    "wavelength": "nm",
                }
            }
            
            # Find lambda_max
            if len(excitations) > 0 and max(e["oscillator_strength"] for e in excitations) > 0:
                max_exc = max(excitations, key=lambda x: x["oscillator_strength"])
                data["lambda_max"] = {
                    "wavelength_nm": max_exc["wavelength_nm"],
                    "energy_ev": max_exc["energy_ev"],
                    "oscillator_strength": max_exc["oscillator_strength"],
                }
            
            message = f"UV-Vis spectrum: {len(excitations)} excitations computed"
            if data["lambda_max"]:
                message += f", λmax = {data['lambda_max']['wavelength_nm']:.1f} nm"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("UV-Vis calculation failed")
            return Result.failure(CalculationError(
                code="UV_VIS_ERROR",
                message=str(e)
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_uv_vis_spectrum(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "cc-pvdz",
    n_states: int = 10,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate UV-Vis absorption spectrum.
    
    Args:
        geometry: Molecular geometry
        method: DFT functional (e.g., B3LYP, CAM-B3LYP, wB97X-D)
        basis: Basis set
        n_states: Number of excited states to compute
        **kwargs: Additional options
        
    Returns:
        ToolOutput with excitation data and simulated spectrum
    """
    tool = UVVisTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "n_states": n_states,
        **kwargs
    })
