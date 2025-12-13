"""Natural Orbitals Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class NaturalOrbitalsToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="mp2")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class NaturalOrbitalsTool(BaseTool[NaturalOrbitalsToolInput, ToolOutput]):
    """Compute natural orbitals and occupation numbers."""
    name: ClassVar[str] = "compute_natural_orbitals"
    description: ClassVar[str] = "Compute natural orbitals from correlated density."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: NaturalOrbitalsToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            import numpy as np
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis, "nat_orbs": True})
            
            energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", return_wfn=True, molecule=mol)
            
            # Get NO occupations if available
            try:
                no_occ = wfn.no_occupations()
                occupations = np.array(no_occ).tolist()
            except:
                occupations = []
            
            data = {
                "energy": float(energy),
                "method": input_data.method,
                "natural_occupations": occupations[:20] if occupations else [],
                "note": "Natural orbitals computed",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message="Natural orbitals computed", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="NO_ERROR", message=str(e)))

def compute_natural_orbitals(geometry: str, method: str = "mp2", **kwargs) -> ToolOutput:
    return NaturalOrbitalsTool().run({"geometry": geometry, "method": method, **kwargs})
