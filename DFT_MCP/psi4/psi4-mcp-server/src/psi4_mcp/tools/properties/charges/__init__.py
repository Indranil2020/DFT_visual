"""
Charges Tools Subpackage.

Tools for computing atomic charges using various methods:
    - Mulliken charges
    - Löwdin charges
    - ESP charges
    - NPA (Natural Population Analysis)
    - Hirshfeld charges
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


# =============================================================================
# COMBINED CHARGES TOOL
# =============================================================================

class ChargesToolInput(ToolInput):
    """Input schema for charges calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    charge_types: list[str] = Field(
        default=["mulliken"],
        description="Types of charges to compute"
    )
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ChargesTool(BaseTool[ChargesToolInput, ToolOutput]):
    """MCP tool for atomic charge calculations."""
    
    name: ClassVar[str] = "calculate_charges"
    description: ClassVar[str] = (
        "Calculate atomic charges using various methods. "
        "Supports Mulliken, Löwdin, ESP, and NPA."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string"},
            "method": {"type": "string", "default": "hf"},
            "basis": {"type": "string", "default": "cc-pvdz"},
            "charge_types": {"type": "array", "items": {"type": "string"}},
        }
    
    def _execute(self, input_data: ChargesToolInput) -> Result[ToolOutput]:
        try:
            from psi4_mcp.runners.property_runner import run_properties
            
            prop_map = {
                "mulliken": "mulliken_charges",
                "lowdin": "lowdin_charges",
                "esp": "grid_esp",
                "npa": "no_occupations",
            }
            
            properties = [prop_map.get(ct, ct) for ct in input_data.charge_types]
            
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
            
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "charge_types": input_data.charge_types,
            }
            
            if prop_output.charges:
                for charge_data in prop_output.charges:
                    data[charge_data.method.lower()] = [
                        {"atom": c.atom_index, "symbol": c.symbol, "charge": c.charge}
                        for c in [charge_data]
                    ]
            
            message = f"Computed charges: {', '.join(input_data.charge_types)}"
            
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("Charges calculation failed")
            return Result.failure(CalculationError(code="CHARGES_ERROR", message=str(e)))


def calculate_charges(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge_types: list[str] = None,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate atomic charges."""
    if charge_types is None:
        charge_types = ["mulliken"]
    tool = ChargesTool()
    return tool.run({
        "geometry": geometry, "method": method, "basis": basis,
        "charge_types": charge_types, **kwargs
    })


# =============================================================================
# SPECIALIZED CHARGE FUNCTIONS
# =============================================================================

def calculate_mulliken_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate Mulliken charges."""
    return calculate_charges(geometry, method, basis, charge_types=["mulliken"], **kwargs)


def calculate_lowdin_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate Löwdin charges."""
    return calculate_charges(geometry, method, basis, charge_types=["lowdin"], **kwargs)


def calculate_esp_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate ESP charges."""
    return calculate_charges(geometry, method, basis, charge_types=["esp"], **kwargs)


def calculate_npa_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate NPA charges."""
    return calculate_charges(geometry, method, basis, charge_types=["npa"], **kwargs)


__all__ = [
    "ChargesTool",
    "ChargesToolInput",
    "calculate_charges",
    "calculate_mulliken_charges",
    "calculate_lowdin_charges",
    "calculate_esp_charges",
    "calculate_npa_charges",
]
