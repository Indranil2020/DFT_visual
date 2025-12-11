"""EOM-CCSD Tool in Coupled Cluster package."""

from typing import Any, ClassVar, Literal
import logging
from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class EOMCCSDToolInput(ToolInput):
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    eom_type: Literal["ee", "ip", "ea", "sf"] = Field(default="ee")
    n_states: int = Field(default=5)
    freeze_core: bool = Field(default=True)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


@register_tool
class EOMCCSDTool(BaseTool[EOMCCSDToolInput, ToolOutput]):
    """
    EOM-CCSD for excited states, ionization potentials, and electron affinities.
    ee=excitations, ip=ionization, ea=attachment, sf=spin-flip.
    """
    name: ClassVar[str] = "calculate_eom_ccsd"
    description: ClassVar[str] = "Calculate EOM-CCSD excited states or IP/EA."
    category: ClassVar[ToolCategory] = ToolCategory.EXCITED_STATES
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: EOMCCSDToolInput) -> Result[ToolOutput]:
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
                "roots_per_irrep": [input_data.n_states],
            })
            
            method_map = {"ee": "eom-ccsd", "ip": "eom-ccsd-ip", "ea": "eom-ccsd-ea", "sf": "eom-sf-ccsd"}
            energy = psi4.energy(f"{method_map[input_data.eom_type]}/{input_data.basis}", molecule=molecule)
            
            states = []
            HARTREE_TO_EV = 27.2114
            for i in range(input_data.n_states):
                try:
                    exc = psi4.variable(f"EOM-CCSD ROOT 0 -> ROOT {i+1} EXCITATION ENERGY")
                    states.append({"state": i+1, "energy_ev": float(exc) * HARTREE_TO_EV})
                except:
                    break
            
            data = {
                "ccsd_energy": float(energy),
                "eom_type": input_data.eom_type,
                "states": states,
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"EOM-CCSD: {len(states)} states", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="EOM_CCSD_ERROR", message=str(e)))


def calculate_eom_ccsd(geometry: str, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return EOMCCSDTool().run({"geometry": geometry, "basis": basis, **kwargs})
