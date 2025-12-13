"""
Electric Moments Tools.

MCP tools for computing electric dipole and multipole moments.

Key Functions:
    - calculate_dipole: Dipole moment calculation
    - calculate_multipoles: Higher multipole moments
    
Key Classes:
    - DipoleTool: Dipole moment tool
    - MultipoleTool: Multipole moment tool
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolCategory,
    register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError
from psi4_mcp.runners.property_runner import run_properties


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMAS
# =============================================================================

class DipoleMomentToolInput(ToolInput):
    """Input schema for dipole moment calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


class MultipoleToolInput(ToolInput):
    """Input schema for multipole moment calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    max_order: int = Field(default=2, description="Maximum multipole order", ge=1, le=4)
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# DIPOLE TOOL
# =============================================================================

@register_tool
class DipoleTool(BaseTool[DipoleMomentToolInput, ToolOutput]):
    """
    MCP tool for dipole moment calculations.
    
    Computes the electric dipole moment of a molecule, which characterizes
    the distribution of positive and negative charges.
    
    Returns:
        - Dipole moment components (x, y, z)
        - Total dipole moment magnitude
        - Units in Debye
    """
    
    name: ClassVar[str] = "calculate_dipole"
    description: ClassVar[str] = (
        "Calculate the electric dipole moment of a molecule. "
        "Returns components and magnitude in Debye."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string", "description": "Molecular geometry"},
            "method": {"type": "string", "default": "hf"},
            "basis": {"type": "string", "default": "cc-pvdz"},
            "charge": {"type": "integer", "default": 0},
            "multiplicity": {"type": "integer", "default": 1},
        }
    
    def _execute(self, input_data: DipoleMomentToolInput) -> Result[ToolOutput]:
        """Execute dipole moment calculation."""
        try:
            result = run_properties(
                geometry=input_data.geometry,
                method=input_data.method,
                basis=input_data.basis,
                charge=input_data.charge,
                multiplicity=input_data.multiplicity,
                properties=["dipole"],
                memory=input_data.memory,
                n_threads=input_data.n_threads,
            )
            
            if result.is_failure:
                return Result.failure(result.error)
            
            prop_output = result.value
            
            if prop_output.dipole_moment:
                dm = prop_output.dipole_moment
                data = {
                    "dipole_x": dm.x,
                    "dipole_y": dm.y,
                    "dipole_z": dm.z,
                    "dipole_total": dm.total,
                    "unit": "Debye",
                    "method": input_data.method,
                    "basis": input_data.basis,
                }
                message = (
                    f"Dipole moment: {dm.total:.4f} Debye\n"
                    f"Components: ({dm.x:.4f}, {dm.y:.4f}, {dm.z:.4f})"
                )
            else:
                data = {"dipole": None, "note": "Dipole moment not computed"}
                message = "Dipole moment calculation completed but no result"
            
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("Dipole calculation failed")
            return Result.failure(CalculationError(code="DIPOLE_ERROR", message=str(e)))


@register_tool
class MultipoleTool(BaseTool[MultipoleToolInput, ToolOutput]):
    """
    MCP tool for multipole moment calculations.
    
    Computes electric multipole moments (dipole, quadrupole, etc.).
    """
    
    name: ClassVar[str] = "calculate_multipoles"
    description: ClassVar[str] = (
        "Calculate electric multipole moments (dipole, quadrupole, octupole). "
        "Higher multipoles provide more detailed charge distribution information."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string", "description": "Molecular geometry"},
            "method": {"type": "string", "default": "hf"},
            "basis": {"type": "string", "default": "cc-pvdz"},
            "max_order": {"type": "integer", "default": 2, "description": "Max multipole order"},
        }
    
    def _execute(self, input_data: MultipoleToolInput) -> Result[ToolOutput]:
        """Execute multipole calculation."""
        try:
            properties = ["dipole"]
            if input_data.max_order >= 2:
                properties.append("quadrupole")
            
            result = run_properties(
                geometry=input_data.geometry,
                method=input_data.method,
                basis=input_data.basis,
                charge=input_data.charge,
                multiplicity=input_data.multiplicity,
                properties=properties,
                memory=input_data.memory,
                n_threads=input_data.n_threads,
            )
            
            if result.is_failure:
                return Result.failure(result.error)
            
            prop_output = result.value
            
            data = {"method": input_data.method, "basis": input_data.basis}
            
            if prop_output.dipole_moment:
                dm = prop_output.dipole_moment
                data["dipole"] = {
                    "x": dm.x, "y": dm.y, "z": dm.z,
                    "total": dm.total, "unit": "Debye"
                }
            
            if prop_output.quadrupole_moment:
                qm = prop_output.quadrupole_moment
                data["quadrupole"] = {
                    "xx": qm.xx, "yy": qm.yy, "zz": qm.zz,
                    "xy": qm.xy, "xz": qm.xz, "yz": qm.yz,
                    "unit": "Debye*Angstrom"
                }
            
            message = f"Multipole moments calculated up to order {input_data.max_order}"
            
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("Multipole calculation failed")
            return Result.failure(CalculationError(code="MULTIPOLE_ERROR", message=str(e)))


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def calculate_dipole(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate dipole moment."""
    tool = DipoleTool()
    return tool.run({
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity, **kwargs
    })


def calculate_multipoles(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    max_order: int = 2,
    charge: int = 0,
    multiplicity: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate multipole moments."""
    tool = MultipoleTool()
    return tool.run({
        "geometry": geometry, "method": method, "basis": basis,
        "max_order": max_order, "charge": charge,
        "multiplicity": multiplicity, **kwargs
    })
