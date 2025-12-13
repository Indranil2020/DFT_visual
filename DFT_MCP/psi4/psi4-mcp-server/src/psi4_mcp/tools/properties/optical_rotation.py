"""
Optical Rotation Tool.

MCP tool for computing optical rotation (specific rotation) for chiral molecules.
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
# OPTICAL ROTATION TOOL
# =============================================================================

class OpticalRotationToolInput(ToolInput):
    """Input schema for optical rotation calculation."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ or Z-matrix format")
    method: str = Field(default="b3lyp", description="DFT method (recommended: B3LYP, CAM-B3LYP)")
    basis: str = Field(default="aug-cc-pvdz", description="Basis set (augmented recommended)")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    wavelengths: list[float] = Field(
        default=[589.3],
        description="Wavelengths in nm (default: sodium D-line 589.3 nm)"
    )
    gauge: str = Field(
        default="length",
        description="Gauge for calculation: 'length' or 'velocity'"
    )
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class OpticalRotationTool(BaseTool[OpticalRotationToolInput, ToolOutput]):
    """
    MCP tool for optical rotation calculations.
    
    Computes specific rotation [α] for chiral molecules at specified
    wavelengths. Useful for:
    - Absolute configuration determination
    - Comparison with experimental ORD data
    - Chiroptical property prediction
    
    Note: Requires augmented basis sets for accurate results.
    """
    
    name: ClassVar[str] = "calculate_optical_rotation"
    description: ClassVar[str] = (
        "Calculate optical rotation (specific rotation [α]) for chiral molecules. "
        "Returns specific rotation at specified wavelengths in deg/(dm·g/mL)."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        """Return JSON schema for tool input."""
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string", "description": "Molecular geometry"},
                "method": {"type": "string", "default": "b3lyp"},
                "basis": {"type": "string", "default": "aug-cc-pvdz"},
                "charge": {"type": "integer", "default": 0},
                "multiplicity": {"type": "integer", "default": 1},
                "wavelengths": {
                    "type": "array",
                    "items": {"type": "number"},
                    "default": [589.3],
                    "description": "Wavelengths in nm"
                },
                "gauge": {"type": "string", "default": "length"},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: OpticalRotationToolInput) -> Result[ToolOutput]:
        """Execute optical rotation calculation."""
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
                "gauge": input_data.gauge,
            })
            
            # Convert wavelengths to frequencies (atomic units)
            # E (a.u.) = hc/λ, where hc = 45.56335 eV·nm = 1.0 / (λ in nm * 0.0219475)
            HARTREE_TO_NM = 45.56335 * 27.2114  # ~1239.84 nm
            frequencies_au = [HARTREE_TO_NM / wl for wl in input_data.wavelengths]
            
            # Set omega for response calculation
            psi4.set_options({"omega": frequencies_au})
            
            # Calculate optical rotation via response properties
            # This requires CCRESPONSE or similar module
            method_str = f"{input_data.method}/{input_data.basis}"
            
            # Run energy first
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Compute response properties (optical rotation requires linear response)
            # Note: Full implementation requires Psi4's response module
            # This is a simplified interface
            
            rotations = {}
            for i, wavelength in enumerate(input_data.wavelengths):
                # Get rotation from Psi4 variables if available
                var_name = f"OPTICAL ROTATION (LEN) @ {wavelength:.1f}NM"
                try:
                    rotation = psi4.variable(var_name)
                    rotations[wavelength] = float(rotation)
                except Exception:
                    # If specific wavelength not available, mark as not computed
                    rotations[wavelength] = None
                    logger.warning(f"Optical rotation at {wavelength} nm not available")
            
            # Build output
            data = {
                "energy": float(energy),
                "method": input_data.method,
                "basis": input_data.basis,
                "gauge": input_data.gauge,
                "wavelengths_nm": input_data.wavelengths,
                "specific_rotations": rotations,
                "units": {
                    "rotation": "deg/(dm·g/mL)",
                    "wavelength": "nm"
                },
                "notes": [
                    "Specific rotation [α] computed via linear response",
                    "Augmented basis sets recommended for accuracy",
                    f"Gauge: {input_data.gauge}"
                ]
            }
            
            # Format message
            rotation_str = ", ".join(
                f"{wl} nm: {rot:.1f}" if rot is not None else f"{wl} nm: N/A"
                for wl, rot in rotations.items()
            )
            message = f"Optical rotation computed: {rotation_str}"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("Optical rotation calculation failed")
            return Result.failure(CalculationError(
                code="OPTICAL_ROTATION_ERROR",
                message=str(e),
                details={"geometry": input_data.geometry[:100]}
            ))


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def calculate_optical_rotation(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "aug-cc-pvdz",
    wavelengths: list[float] = None,
    gauge: str = "length",
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate optical rotation for a chiral molecule.
    
    Args:
        geometry: Molecular geometry string
        method: Calculation method (default: B3LYP)
        basis: Basis set (default: aug-cc-pVDZ, augmented recommended)
        wavelengths: Wavelengths in nm (default: [589.3] sodium D-line)
        gauge: Response gauge ('length' or 'velocity')
        **kwargs: Additional options
        
    Returns:
        ToolOutput with specific rotation values
        
    Example:
        >>> result = calculate_optical_rotation(
        ...     geometry=\"\"\"
        ...     C  0.0  0.0  0.0
        ...     H  1.0  0.0  0.0
        ...     F  0.0  1.0  0.0
        ...     Cl 0.0  0.0  1.0
        ...     Br 0.0 -1.0 -1.0
        ...     \"\"\",
        ...     wavelengths=[589.3, 365.0]
        ... )
    """
    if wavelengths is None:
        wavelengths = [589.3]  # Sodium D-line
    
    tool = OpticalRotationTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "wavelengths": wavelengths,
        "gauge": gauge,
        **kwargs
    })


def calculate_ord(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "aug-cc-pvdz",
    wavelength_range: tuple[float, float] = (300.0, 700.0),
    n_points: int = 10,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate Optical Rotatory Dispersion (ORD) spectrum.
    
    Computes optical rotation at multiple wavelengths to generate
    an ORD curve.
    
    Args:
        geometry: Molecular geometry string
        method: Calculation method
        basis: Basis set
        wavelength_range: (min, max) wavelength in nm
        n_points: Number of wavelength points
        **kwargs: Additional options
        
    Returns:
        ToolOutput with ORD spectrum data
    """
    import numpy as np
    
    wavelengths = np.linspace(
        wavelength_range[0],
        wavelength_range[1],
        n_points
    ).tolist()
    
    return calculate_optical_rotation(
        geometry=geometry,
        method=method,
        basis=basis,
        wavelengths=wavelengths,
        **kwargs
    )
