"""
NMR Spectrum Simulation Tool.

MCP tool for simulating NMR spectra from computed shieldings and couplings.
"""

from typing import Any, ClassVar, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class NMRSpectrumToolInput(ToolInput):
    """Input schema for NMR spectrum simulation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvtz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    nucleus: str = Field(default="1H", description="Nucleus type (1H, 13C, etc.)")
    field_strength_mhz: float = Field(default=400.0, description="Spectrometer frequency (MHz)")
    reference: str = Field(default="TMS", description="Reference compound")
    linewidth_hz: float = Field(default=1.0, description="Linewidth for broadening (Hz)")
    ppm_range: tuple[float, float] = Field(
        default=(-1.0, 12.0),
        description="Chemical shift range (ppm)"
    )
    n_points: int = Field(default=8192, description="Number of spectrum points")
    include_coupling: bool = Field(default=False, description="Include J-coupling splitting")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class NMRSpectrumTool(BaseTool[NMRSpectrumToolInput, ToolOutput]):
    """
    MCP tool for NMR spectrum simulation.
    
    Generates simulated NMR spectra from computed chemical shieldings,
    optionally including spin-spin coupling.
    """
    
    name: ClassVar[str] = "simulate_nmr_spectrum"
    description: ClassVar[str] = (
        "Simulate NMR spectrum from computed chemical shifts. "
        "Generates spectrum with Lorentzian line shapes."
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
                "basis": {"type": "string", "default": "cc-pvtz"},
                "nucleus": {"type": "string", "default": "1H"},
                "field_strength_mhz": {"type": "number", "default": 400.0},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: NMRSpectrumToolInput) -> Result[ToolOutput]:
        """Execute NMR spectrum simulation."""
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
            
            # Run shielding calculation
            psi4.set_options({"basis": input_data.basis})
            method_str = f"{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            psi4.oeprop(wfn, "NMR")
            
            # Reference shieldings
            REFERENCE_SHIELDINGS = {
                "1H": {"TMS": 31.7},
                "13C": {"TMS": 189.7},
                "19F": {"CFCl3": 188.7},
                "31P": {"H3PO4": 328.4},
            }
            
            # Determine target element
            element_map = {"1H": "H", "13C": "C", "19F": "F", "31P": "P", "15N": "N"}
            target_element = element_map.get(input_data.nucleus, input_data.nucleus)
            
            ref_shield = REFERENCE_SHIELDINGS.get(input_data.nucleus, {}).get(input_data.reference, 0)
            
            # Extract chemical shifts for target nucleus
            peaks = []
            n_atoms = molecule.natom()
            
            for i in range(n_atoms):
                element = molecule.symbol(i)
                if element != target_element:
                    continue
                
                try:
                    iso_shield = psi4.variable(f"NMR SHIELDING {i+1}")
                    chem_shift = ref_shield - float(iso_shield)
                    peaks.append({
                        "atom_index": i,
                        "chemical_shift_ppm": chem_shift,
                        "intensity": 1.0,  # Relative intensity
                    })
                except Exception:
                    pass
            
            # Generate spectrum
            ppm_axis = np.linspace(
                input_data.ppm_range[0],
                input_data.ppm_range[1],
                input_data.n_points
            )
            
            # Convert linewidth from Hz to ppm
            linewidth_ppm = input_data.linewidth_hz / input_data.field_strength_mhz
            
            # Lorentzian line shape
            def lorentzian(x, x0, intensity, gamma):
                return intensity * gamma**2 / ((x - x0)**2 + gamma**2)
            
            spectrum = np.zeros_like(ppm_axis)
            gamma = linewidth_ppm / 2
            
            for peak in peaks:
                spectrum += lorentzian(ppm_axis, peak["chemical_shift_ppm"], peak["intensity"], gamma)
            
            # Normalize
            if np.max(spectrum) > 0:
                spectrum = spectrum / np.max(spectrum)
            
            # Build output
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "nucleus": input_data.nucleus,
                "reference": input_data.reference,
                "field_strength_mhz": input_data.field_strength_mhz,
                "n_peaks": len(peaks),
                "peaks": peaks,
                "spectrum": {
                    "ppm": ppm_axis.tolist(),
                    "intensity": spectrum.tolist(),
                },
                "units": {
                    "chemical_shift": "ppm",
                    "intensity": "arbitrary (normalized)"
                }
            }
            
            message = f"{input_data.nucleus} NMR spectrum: {len(peaks)} peaks"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("NMR spectrum simulation failed")
            return Result.failure(CalculationError(
                code="NMR_SPECTRUM_ERROR",
                message=str(e)
            ))


def simulate_nmr_spectrum(
    geometry: str,
    nucleus: str = "1H",
    method: str = "b3lyp",
    basis: str = "cc-pvtz",
    field_strength_mhz: float = 400.0,
    **kwargs: Any,
) -> ToolOutput:
    """
    Simulate NMR spectrum.
    
    Args:
        geometry: Molecular geometry
        nucleus: Nucleus type (1H, 13C, etc.)
        method: DFT functional
        basis: Basis set
        field_strength_mhz: Spectrometer frequency
        **kwargs: Additional options
        
    Returns:
        ToolOutput with simulated spectrum
    """
    tool = NMRSpectrumTool()
    return tool.run({
        "geometry": geometry,
        "nucleus": nucleus,
        "method": method,
        "basis": basis,
        "field_strength_mhz": field_strength_mhz,
        **kwargs
    })
