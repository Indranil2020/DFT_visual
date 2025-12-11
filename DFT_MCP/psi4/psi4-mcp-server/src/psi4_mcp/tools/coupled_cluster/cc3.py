"""CC3 Tool - Iterative approximate triples."""

from typing import Any, ClassVar
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class CC3ToolInput(ToolInput):
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


@register_tool
class CC3Tool(BaseTool[CC3ToolInput, ToolOutput]):
    """CC3 includes iterative approximate triples. O(N^7) scaling."""
    name: ClassVar[str] = "calculate_cc3"
    description: ClassVar[str] = "Calculate CC3 energy with iterative triples."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CC3ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            
            energy = psi4.energy(f"cc3/{input_data.basis}", molecule=molecule)
            
            data = {"total_energy": float(energy), "basis": input_data.basis, "method": "CC3"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CC3: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CC3_ERROR", message=str(e)))


def calculate_cc3(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return CC3Tool().run({"geometry": geometry, "basis": basis, **kwargs})
