"""
IR and Raman Spectroscopy Tools.

MCP tools for computing vibrational spectra:
    - Infrared (IR) absorption spectra
    - Raman scattering spectra
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
# IR/RAMAN TOOL
# =============================================================================

class IRRamanToolInput(ToolInput):
    """Input schema for IR/Raman calculation."""
    
    geometry: str = Field(..., description="Molecular geometry (should be optimized)")
    method: str = Field(default="b3lyp", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    compute_ir: bool = Field(default=True, description="Compute IR intensities")
    compute_raman: bool = Field(default=False, description="Compute Raman activities")
    scale_factor: float = Field(default=1.0, description="Frequency scaling factor")
    broadening: float = Field(default=10.0, description="Gaussian broadening FWHM (cm^-1)")
    spectrum_range: tuple[float, float] = Field(
        default=(0.0, 4000.0),
        description="Frequency range for spectrum (cm^-1)"
    )
    n_points: int = Field(default=1000, description="Number of spectrum points")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class IRRamanTool(BaseTool[IRRamanToolInput, ToolOutput]):
    """
    MCP tool for IR and Raman spectroscopy calculations.
    
    Computes vibrational frequencies with IR intensities and optionally
    Raman activities. Generates simulated spectra with Gaussian broadening.
    
    Important: Input geometry should be at a stationary point (optimized).
    """
    
    name: ClassVar[str] = "calculate_ir_raman"
    description: ClassVar[str] = (
        "Calculate IR absorption and/or Raman scattering spectra from "
        "vibrational frequencies. Returns frequencies, intensities, and "
        "simulated spectra."
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
                "compute_ir": {"type": "boolean", "default": True},
                "compute_raman": {"type": "boolean", "default": False},
                "scale_factor": {"type": "number", "default": 1.0},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: IRRamanToolInput) -> Result[ToolOutput]:
        """Execute IR/Raman calculation."""
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
            })
            
            # Run frequency calculation
            method_str = f"{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.frequency(method_str, return_wfn=True, molecule=molecule)
            
            # Extract frequencies and intensities
            vibinfo = wfn.frequency_analysis
            frequencies = vibinfo['omega'].to_array()  # cm^-1
            
            # Apply scaling factor
            scaled_frequencies = frequencies * input_data.scale_factor
            
            # Extract IR intensities
            ir_intensities = None
            if input_data.compute_ir and 'IR_intensity' in vibinfo:
                ir_intensities = vibinfo['IR_intensity'].to_array()  # km/mol
            
            # Extract Raman activities (if available)
            raman_activities = None
            if input_data.compute_raman:
                # Raman requires additional calculation
                try:
                    raman_activities = vibinfo.get('Raman_activity', None)
                    if raman_activities is not None:
                        raman_activities = raman_activities.to_array()
                except Exception:
                    logger.warning("Raman activities not available")
            
            # Generate simulated spectra
            freq_axis = np.linspace(
                input_data.spectrum_range[0],
                input_data.spectrum_range[1],
                input_data.n_points
            )
            
            # Gaussian broadening function
            def gaussian(x, x0, intensity, fwhm):
                sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
                return intensity * np.exp(-0.5 * ((x - x0) / sigma) ** 2)
            
            # Generate IR spectrum
            ir_spectrum = None
            if ir_intensities is not None:
                ir_spectrum = np.zeros_like(freq_axis)
                for freq, intensity in zip(scaled_frequencies, ir_intensities):
                    if freq > 0:  # Skip imaginary frequencies
                        ir_spectrum += gaussian(freq_axis, freq, intensity, input_data.broadening)
            
            # Generate Raman spectrum
            raman_spectrum = None
            if raman_activities is not None:
                raman_spectrum = np.zeros_like(freq_axis)
                for freq, activity in zip(scaled_frequencies, raman_activities):
                    if freq > 0:
                        raman_spectrum += gaussian(freq_axis, freq, activity, input_data.broadening)
            
            # Build output
            data = {
                "energy": float(energy),
                "method": input_data.method,
                "basis": input_data.basis,
                "scale_factor": input_data.scale_factor,
                "frequencies_cm1": scaled_frequencies.tolist(),
                "n_frequencies": len(frequencies),
                "n_imaginary": int(np.sum(frequencies < 0)),
            }
            
            if ir_intensities is not None:
                data["ir_intensities_km_mol"] = ir_intensities.tolist()
                data["ir_spectrum"] = {
                    "frequency_axis": freq_axis.tolist(),
                    "intensity": ir_spectrum.tolist(),
                }
            
            if raman_activities is not None:
                data["raman_activities"] = raman_activities.tolist()
                data["raman_spectrum"] = {
                    "frequency_axis": freq_axis.tolist(),
                    "intensity": raman_spectrum.tolist(),
                }
            
            data["units"] = {
                "frequency": "cm^-1",
                "ir_intensity": "km/mol",
                "raman_activity": "Å^4/amu"
            }
            
            message = f"IR/Raman spectra computed: {len(frequencies)} modes"
            if data["n_imaginary"] > 0:
                message += f" ({data['n_imaginary']} imaginary)"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("IR/Raman calculation failed")
            return Result.failure(CalculationError(
                code="IR_RAMAN_ERROR",
                message=str(e)
            ))


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def calculate_ir_spectrum(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "cc-pvdz",
    scale_factor: float = 0.97,  # Common scaling for B3LYP
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate IR absorption spectrum.
    
    Args:
        geometry: Optimized molecular geometry
        method: Calculation method
        basis: Basis set
        scale_factor: Frequency scaling factor (default 0.97 for B3LYP)
        **kwargs: Additional options
        
    Returns:
        ToolOutput with IR spectrum
    """
    tool = IRRamanTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "compute_ir": True,
        "compute_raman": False,
        "scale_factor": scale_factor,
        **kwargs
    })


def calculate_raman_spectrum(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "cc-pvdz",
    scale_factor: float = 0.97,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Raman scattering spectrum.
    
    Args:
        geometry: Optimized molecular geometry
        method: Calculation method
        basis: Basis set
        scale_factor: Frequency scaling factor
        **kwargs: Additional options
        
    Returns:
        ToolOutput with Raman spectrum
    """
    tool = IRRamanTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "compute_ir": False,
        "compute_raman": True,
        "scale_factor": scale_factor,
        **kwargs
    })
