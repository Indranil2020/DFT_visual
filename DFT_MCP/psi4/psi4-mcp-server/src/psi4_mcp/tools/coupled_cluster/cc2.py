"""
CC2 (Approximate Coupled Cluster) Tool.

MCP tool for CC2 calculations.
"""

from typing import Any, ClassVar
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class CC2ToolInput(ToolInput):
    """Input schema for CC2 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    n_states: int = Field(default=0, description="Excited states (0 = ground only)")
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


@register_tool
class CC2Tool(BaseTool[CC2ToolInput, ToolOutput]):
    """
    MCP tool for CC2 calculations.
    
    CC2 is an approximation to CCSD with O(N^5) scaling. Good for excited states.
    Accuracy similar to ADC(2).
    """
    name: ClassVar[str] = "calculate_cc2"
    description: ClassVar[str] = "Calculate CC2 energy. O(N^5), good for excited states."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CC2ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            
            psi4.set_options({
                "basis": input_data.basis,
                "freeze_core": input_data.freeze_core,
            })
            
            if input_data.n_states > 0:
                psi4.set_options({"roots_per_irrep": [input_data.n_states]})
            
            energy, wfn = psi4.energy(f"cc2/{input_data.basis}", return_wfn=True, molecule=molecule)
            
            data = {
                "total_energy": float(energy),
                "correlation_energy": float(psi4.variable("CC2 CORRELATION ENERGY")),
                "basis": input_data.basis,
                "method": "CC2",
            }
            
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CC2: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CC2_ERROR", message=str(e)))


def calculate_cc2(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return CC2Tool().run({"geometry": geometry, "basis": basis, **kwargs})
