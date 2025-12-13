"""CASSCF Tool - Complete Active Space SCF."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class CASSCFToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    active_electrons: int = Field(..., description="Number of active electrons")
    active_orbitals: int = Field(..., description="Number of active orbitals")
    num_roots: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class CASSCFTool(BaseTool[CASSCFToolInput, ToolOutput]):
    """CASSCF - Complete Active Space SCF for multireference systems."""
    name: ClassVar[str] = "calculate_casscf"
    description: ClassVar[str] = "Calculate CASSCF energy for multireference systems."
    category: ClassVar[ToolCategory] = ToolCategory.MULTIREFERENCE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CASSCFToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({
                "basis": input_data.basis,
                "active": [input_data.active_orbitals],
                "restricted_docc": [],  # Will be auto-determined
                "mcscf_maxiter": 100,
                "num_roots": input_data.num_roots,
            })
            energy = psi4.energy(f"casscf/{input_data.basis}", molecule=mol)
            data = {
                "casscf_energy": float(energy),
                "active_space": f"({input_data.active_electrons},{input_data.active_orbitals})",
                "basis": input_data.basis,
                "method": "CASSCF",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CASSCF: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CASSCF_ERROR", message=str(e)))

def calculate_casscf(geometry: str, active_electrons: int, active_orbitals: int, 
                     basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return CASSCFTool().run({"geometry": geometry, "basis": basis,
                            "active_electrons": active_electrons, "active_orbitals": active_orbitals, **kwargs})
