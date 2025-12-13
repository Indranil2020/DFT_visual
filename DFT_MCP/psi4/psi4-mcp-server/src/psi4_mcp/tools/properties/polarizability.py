"""
Polarizability Tool.

MCP tool for computing molecular polarizability.
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError
from psi4_mcp.runners.property_runner import run_properties

logger = logging.getLogger(__name__)


class PolarizabilityToolInput(ToolInput):
    """Input schema for polarizability calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="aug-cc-pvdz", description="Basis set (augmented recommended)")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class PolarizabilityTool(BaseTool[PolarizabilityToolInput, ToolOutput]):
    """MCP tool for polarizability calculations."""
    
    name: ClassVar[str] = "calculate_polarizability"
    description: ClassVar[str] = (
        "Calculate molecular polarizability tensor. "
        "Returns isotropic and anisotropic components."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string", "description": "Molecular geometry"},
            "method": {"type": "string", "default": "hf"},
            "basis": {"type": "string", "default": "aug-cc-pvdz"},
        }
    
    def _execute(self, input_data: PolarizabilityToolInput) -> Result[ToolOutput]:
        try:
            result = run_properties(
                geometry=input_data.geometry,
                method=input_data.method,
                basis=input_data.basis,
                charge=input_data.charge,
                multiplicity=input_data.multiplicity,
                properties=["polarizability"],
                memory=input_data.memory,
                n_threads=input_data.n_threads,
            )
            
            if result.is_failure:
                return Result.failure(result.error)
            
            prop_output = result.value
            
            if prop_output.polarizability:
                pol = prop_output.polarizability
                data = {
                    "isotropic": pol.isotropic,
                    "anisotropy": pol.anisotropy,
                    "tensor": {
                        "xx": pol.xx, "yy": pol.yy, "zz": pol.zz,
                        "xy": pol.xy, "xz": pol.xz, "yz": pol.yz,
                    },
                    "unit": "Angstrom^3",
                }
                message = f"Isotropic polarizability: {pol.isotropic:.4f} Å³"
            else:
                data = {"polarizability": None}
                message = "Polarizability not computed"
            
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("Polarizability calculation failed")
            return Result.failure(CalculationError(code="POLARIZABILITY_ERROR", message=str(e)))


def calculate_polarizability(
    geometry: str,
    method: str = "hf",
    basis: str = "aug-cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate polarizability."""
    tool = PolarizabilityTool()
    return tool.run({
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity, **kwargs
    })
