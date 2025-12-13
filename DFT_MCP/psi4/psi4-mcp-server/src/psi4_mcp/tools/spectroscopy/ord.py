"""
Optical Rotatory Dispersion (ORD) Tool.

MCP tool for computing ORD spectra showing wavelength-dependent optical rotation.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class ORDToolInput(ToolInput):
    """Input schema for ORD calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="aug-cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    wavelengths: list[float] = Field(
        default=[589.3, 546.1, 436.0, 365.0],
        description="Wavelengths for ORD calculation (nm)"
    )
    gauge: str = Field(default="length", description="Gauge: 'length' or 'velocity'")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ORDTool(BaseTool[ORDToolInput, ToolOutput]):
    """
    MCP tool for Optical Rotatory Dispersion spectroscopy.
    
    Computes specific rotation at multiple wavelengths to generate
    an ORD curve. Useful for:
    - Absolute configuration assignment
    - Cotton effect analysis
    - Comparison with experimental ORD
    """
    
    name: ClassVar[str] = "calculate_ord"
    description: ClassVar[str] = (
        "Calculate Optical Rotatory Dispersion (ORD) spectrum. "
        "Returns specific rotation [α] at multiple wavelengths."
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
                "wavelengths": {"type": "array", "items": {"type": "number"}},
                "gauge": {"type": "string", "default": "length"},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: ORDToolInput) -> Result[ToolOutput]:
        """Execute ORD calculation."""
        try:
            import psi4
            
            # Configure Psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            # Build molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            
            # Convert wavelengths to frequencies (a.u.)
            HARTREE_TO_NM = 45.56335 * 27.2114
            frequencies_au = [HARTREE_TO_NM / wl for wl in input_data.wavelengths]
            
            # Set options
            psi4.set_options({
                "basis": input_data.basis,
                "gauge": input_data.gauge,
                "omega": frequencies_au,
            })
            
            # Run calculation
            method_str = f"{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Extract optical rotations at each wavelength
            rotations = {}
            for wl in input_data.wavelengths:
                try:
                    var_name = f"OPTICAL ROTATION ({input_data.gauge.upper()}) @ {wl:.1f}NM"
                    rot = psi4.variable(var_name)
                    rotations[wl] = float(rot)
                except Exception:
                    rotations[wl] = None
            
            # Build output
            ord_data = [
                {"wavelength_nm": wl, "rotation": rot}
                for wl, rot in rotations.items()
            ]
            
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "gauge": input_data.gauge,
                "ord_curve": ord_data,
                "rotations": rotations,
                "units": {
                    "rotation": "deg/(dm·g/mL)",
                    "wavelength": "nm"
                }
            }
            
            # Identify any Cotton effects (sign changes)
            sorted_rots = sorted(
                [(wl, rot) for wl, rot in rotations.items() if rot is not None],
                key=lambda x: x[0]
            )
            
            sign_changes = []
            for i in range(1, len(sorted_rots)):
                if sorted_rots[i-1][1] * sorted_rots[i][1] < 0:
                    sign_changes.append({
                        "between": [sorted_rots[i-1][0], sorted_rots[i][0]],
                        "type": "positive to negative" if sorted_rots[i-1][1] > 0 else "negative to positive"
                    })
            
            if sign_changes:
                data["cotton_effects"] = sign_changes
            
            message = f"ORD computed at {len([r for r in rotations.values() if r is not None])} wavelengths"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("ORD calculation failed")
            return Result.failure(CalculationError(
                code="ORD_ERROR",
                message=str(e)
            ))


def calculate_ord_spectrum(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "aug-cc-pvdz",
    wavelengths: list[float] = None,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate ORD spectrum.
    
    Args:
        geometry: Molecular geometry
        method: DFT functional
        basis: Basis set (augmented recommended)
        wavelengths: Wavelengths in nm
        **kwargs: Additional options
        
    Returns:
        ToolOutput with ORD curve
    """
    if wavelengths is None:
        wavelengths = [589.3, 546.1, 436.0, 365.0]
    
    tool = ORDTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "wavelengths": wavelengths,
        **kwargs
    })
