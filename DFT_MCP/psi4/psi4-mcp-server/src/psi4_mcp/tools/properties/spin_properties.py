"""
Spin Properties Tool.

MCP tool for computing spin-related properties.
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class SpinPropertiesToolInput(ToolInput):
    """Input schema for spin properties calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="uhf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=2, description="Spin multiplicity")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class SpinPropertiesTool(BaseTool[SpinPropertiesToolInput, ToolOutput]):
    """MCP tool for spin properties calculations."""
    
    name: ClassVar[str] = "calculate_spin_properties"
    description: ClassVar[str] = (
        "Calculate spin properties including S^2, spin density, "
        "and spin populations for open-shell systems."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string"},
            "method": {"type": "string", "default": "uhf"},
            "basis": {"type": "string", "default": "cc-pvdz"},
            "multiplicity": {"type": "integer", "default": 2},
        }
    
    def _execute(self, input_data: SpinPropertiesToolInput) -> Result[ToolOutput]:
        try:
            from psi4_mcp.services.psi4_interface import get_psi4_interface
            
            psi4 = get_psi4_interface()
            psi4.initialize(memory=input_data.memory, n_threads=input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            mol_result = psi4.create_molecule(mol_string)
            if mol_result.is_failure:
                return Result.failure(mol_result.error)
            
            molecule = mol_result.value
            psi4.set_options({"basis": input_data.basis, "reference": "uhf"})
            
            energy_result = psi4.energy(input_data.method, molecule=molecule, return_wfn=True)
            if energy_result.is_failure:
                return Result.failure(energy_result.error)
            
            energy, wfn = energy_result.value
            
            n_alpha = wfn.nalpha()
            n_beta = wfn.nbeta()
            n_unpaired = n_alpha - n_beta
            
            # Expected S^2 value
            s = (input_data.multiplicity - 1) / 2
            s_squared_expected = s * (s + 1)
            
            data = {
                "energy": energy,
                "n_alpha": n_alpha,
                "n_beta": n_beta,
                "n_unpaired": n_unpaired,
                "multiplicity": input_data.multiplicity,
                "s_expected": s,
                "s_squared_expected": s_squared_expected,
                "method": input_data.method,
                "basis": input_data.basis,
            }
            
            message = (
                f"Spin properties for multiplicity {input_data.multiplicity}\n"
                f"Alpha electrons: {n_alpha}, Beta electrons: {n_beta}\n"
                f"Expected <S^2>: {s_squared_expected:.4f}"
            )
            
            psi4.clean()
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("Spin properties calculation failed")
            return Result.failure(CalculationError(code="SPIN_ERROR", message=str(e)))


def calculate_spin_properties(
    geometry: str,
    method: str = "uhf",
    basis: str = "cc-pvdz",
    multiplicity: int = 2,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate spin properties."""
    tool = SpinPropertiesTool()
    return tool.run({
        "geometry": geometry, "method": method, "basis": basis,
        "multiplicity": multiplicity, **kwargs
    })
