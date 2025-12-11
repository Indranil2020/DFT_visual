"""Brueckner Coupled Cluster Tool."""

from typing import Any, ClassVar
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class BruecknerCCToolInput(ToolInput):
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    with_triples: bool = Field(default=True, description="Include (T) correction")
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


@register_tool
class BruecknerCCTool(BaseTool[BruecknerCCToolInput, ToolOutput]):
    """
    Brueckner CC uses optimized orbitals where T1=0.
    Better for systems with large T1 amplitudes.
    """
    name: ClassVar[str] = "calculate_brueckner_cc"
    description: ClassVar[str] = "Calculate Brueckner CC energy with optimized orbitals."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: BruecknerCCToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            
            method = "bccd(t)" if input_data.with_triples else "bccd"
            energy = psi4.energy(f"{method}/{input_data.basis}", molecule=molecule)
            
            data = {
                "total_energy": float(energy),
                "basis": input_data.basis,
                "method": "BCCD(T)" if input_data.with_triples else "BCCD",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Brueckner CC: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="BCC_ERROR", message=str(e)))


def calculate_brueckner_cc(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return BruecknerCCTool().run({"geometry": geometry, "basis": basis, **kwargs})
