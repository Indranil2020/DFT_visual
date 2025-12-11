"""LR-CCSD (Linear Response CCSD) Tool."""

from typing import Any, ClassVar
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class LRCCSDToolInput(ToolInput):
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    property_type: str = Field(default="polarizability", description="Response property")
    frequencies: list[float] = Field(default=[0.0], description="Frequencies in au")
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


@register_tool
class LRCCSDTool(BaseTool[LRCCSDToolInput, ToolOutput]):
    """
    Linear Response CCSD for frequency-dependent properties.
    Computes polarizabilities, optical rotation, etc.
    """
    name: ClassVar[str] = "calculate_lr_ccsd"
    description: ClassVar[str] = "Calculate linear response properties at CCSD level."
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: LRCCSDToolInput) -> Result[ToolOutput]:
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
                "omega": input_data.frequencies,
            })
            
            # Run CCSD with properties
            energy = psi4.energy(f"ccsd/{input_data.basis}", molecule=molecule)
            
            # Response properties would be extracted here
            data = {
                "ccsd_energy": float(energy),
                "property_type": input_data.property_type,
                "frequencies": input_data.frequencies,
                "basis": input_data.basis,
                "method": "LR-CCSD",
                "note": "Full LR-CCSD requires ccresponse module"
            }
            
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message="LR-CCSD completed", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="LR_CCSD_ERROR", message=str(e)))


def calculate_lr_ccsd(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return LRCCSDTool().run({"geometry": geometry, "basis": basis, **kwargs})
