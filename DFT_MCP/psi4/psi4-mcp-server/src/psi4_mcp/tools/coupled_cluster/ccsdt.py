"""CCSDT Tool - Full iterative triples."""

from typing import Any, ClassVar
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class CCSDTFullToolInput(ToolInput):
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=16000, description="Large memory required")
    n_threads: int = Field(default=1)


@register_tool
class CCSDTFullTool(BaseTool[CCSDTFullToolInput, ToolOutput]):
    """CCSDT with full iterative triples. O(N^8) scaling - very expensive."""
    name: ClassVar[str] = "calculate_ccsdt"
    description: ClassVar[str] = "Calculate CCSDT energy. O(N^8), very expensive."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CCSDTFullToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            
            energy = psi4.energy(f"ccsdt/{input_data.basis}", molecule=molecule)
            
            data = {"total_energy": float(energy), "basis": input_data.basis, "method": "CCSDT"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CCSDT: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CCSDT_ERROR", message=str(e)))


def calculate_ccsdt(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return CCSDTFullTool().run({"geometry": geometry, "basis": basis, **kwargs})
