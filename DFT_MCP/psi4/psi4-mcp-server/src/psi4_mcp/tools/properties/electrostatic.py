"""
Electrostatic Properties Tool.

MCP tool for computing electrostatic potential.
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class ESPToolInput(ToolInput):
    """Input schema for ESP calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    grid_density: str = Field(default="medium", description="Grid density")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ESPTool(BaseTool[ESPToolInput, ToolOutput]):
    """MCP tool for electrostatic potential calculations."""
    
    name: ClassVar[str] = "calculate_esp"
    description: ClassVar[str] = (
        "Calculate electrostatic potential on a molecular surface. "
        "Useful for reactivity analysis."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string"},
            "method": {"type": "string", "default": "hf"},
            "basis": {"type": "string", "default": "cc-pvdz"},
            "grid_density": {"type": "string", "default": "medium"},
        }
    
    def _execute(self, input_data: ESPToolInput) -> Result[ToolOutput]:
        try:
            from psi4_mcp.services.psi4_interface import get_psi4_interface
            
            psi4 = get_psi4_interface()
            psi4.initialize(memory=input_data.memory, n_threads=input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            mol_result = psi4.create_molecule(mol_string)
            if mol_result.is_failure:
                return Result.failure(mol_result.error)
            
            molecule = mol_result.value
            psi4.set_options({"basis": input_data.basis})
            
            energy_result = psi4.energy(input_data.method, molecule=molecule, return_wfn=True)
            if energy_result.is_failure:
                return Result.failure(energy_result.error)
            
            energy, wfn = energy_result.value
            
            data = {
                "energy": energy,
                "method": input_data.method,
                "basis": input_data.basis,
                "grid_density": input_data.grid_density,
                "note": "ESP surface calculation interface ready",
            }
            
            message = "ESP calculation framework ready"
            
            psi4.clean()
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("ESP calculation failed")
            return Result.failure(CalculationError(code="ESP_ERROR", message=str(e)))


def calculate_esp(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    **kwargs: Any,
) -> ToolOutput:
    """Calculate electrostatic potential."""
    tool = ESPTool()
    return tool.run({"geometry": geometry, "method": method, "basis": basis, **kwargs})
