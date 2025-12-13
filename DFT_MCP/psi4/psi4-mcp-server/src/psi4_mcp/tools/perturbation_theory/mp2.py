"""MP2 (Second-Order Møller-Plesset) Tool."""

from typing import Any, ClassVar
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class MP2ToolInput(ToolInput):
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True, description="Freeze core orbitals")
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)


@register_tool
class MP2Tool(BaseTool[MP2ToolInput, ToolOutput]):
    """
    MP2 - Second-Order Møller-Plesset Perturbation Theory.
    
    O(N^5) scaling, recovers ~80-90% of correlation energy.
    Good for: weak interactions, geometry optimization, relative energies.
    """
    name: ClassVar[str] = "calculate_mp2"
    description: ClassVar[str] = "Calculate MP2 energy. O(N^5), ~80-90% correlation recovery."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {"type": "object", "properties": {"geometry": {"type": "string"}, "basis": {"type": "string"}}, "required": ["geometry"]}
    
    def _execute(self, input_data: MP2ToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            psi4.set_options({"basis": input_data.basis, "freeze_core": input_data.freeze_core})
            
            energy = psi4.energy(f"mp2/{input_data.basis}", molecule=molecule)
            
            hf = psi4.variable("HF TOTAL ENERGY")
            mp2_corr = psi4.variable("MP2 CORRELATION ENERGY")
            same_spin = psi4.variable("MP2 SAME-SPIN CORRELATION ENERGY")
            opp_spin = psi4.variable("MP2 OPPOSITE-SPIN CORRELATION ENERGY")
            
            data = {
                "mp2_total_energy": float(energy),
                "hf_energy": float(hf),
                "mp2_correlation_energy": float(mp2_corr),
                "same_spin_correlation": float(same_spin),
                "opposite_spin_correlation": float(opp_spin),
                "basis": input_data.basis,
                "method": "MP2",
                "units": {"energy": "hartree"}
            }
            
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"MP2: E = {energy:.10f} Hartree", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="MP2_ERROR", message=str(e)))


def calculate_mp2(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return MP2Tool().run({"geometry": geometry, "basis": basis, **kwargs})
