"""RASSCF Tool - Restricted Active Space SCF."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class RASSCFToolInput(ToolInput):
    geometry: str = Field(...)
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    ras1: int = Field(default=0, description="RAS1 orbitals (limited holes)")
    ras2: int = Field(..., description="RAS2 orbitals (full CI)")
    ras3: int = Field(default=0, description="RAS3 orbitals (limited particles)")
    max_holes: int = Field(default=2, description="Max holes in RAS1")
    max_particles: int = Field(default=2, description="Max particles in RAS3")
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class RASSCFTool(BaseTool[RASSCFToolInput, ToolOutput]):
    """RASSCF - Restricted Active Space SCF with limited excitations."""
    name: ClassVar[str] = "calculate_rasscf"
    description: ClassVar[str] = "Calculate RASSCF with restricted excitations."
    category: ClassVar[ToolCategory] = ToolCategory.MULTIREFERENCE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: RASSCFToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({
                "basis": input_data.basis,
                "ras1": [input_data.ras1],
                "ras2": [input_data.ras2],
                "ras3": [input_data.ras3],
                "ex_level": input_data.max_holes,
            })
            energy = psi4.energy(f"rasscf/{input_data.basis}", molecule=mol)
            data = {
                "rasscf_energy": float(energy),
                "ras_space": f"RAS1={input_data.ras1}, RAS2={input_data.ras2}, RAS3={input_data.ras3}",
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"RASSCF: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="RASSCF_ERROR", message=str(e)))

def calculate_rasscf(geometry: str, ras2: int, basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    return RASSCFTool().run({"geometry": geometry, "basis": basis, "ras2": ras2, **kwargs})
