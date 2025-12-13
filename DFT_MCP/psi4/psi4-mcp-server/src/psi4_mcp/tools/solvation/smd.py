"""SMD Solvation Model Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class SMDToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    solvent: str = Field(default="water")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class SMDTool(BaseTool[SMDToolInput, ToolOutput]):
    """SMD solvation model (universal, includes nonelectrostatic)."""
    name: ClassVar[str] = "calculate_smd"
    description: ClassVar[str] = "Calculate solvation energy with SMD model."
    category: ClassVar[ToolCategory] = ToolCategory.SOLVATION
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: SMDToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            psi4.set_options({
                "basis": input_data.basis,
                "pcm": True,
                "pcm__input": f'''
                    Units = Angstrom
                    Cavity {{Type = GePol}}
                    Medium {{Solvent = {input_data.solvent}}}
                '''
            })
            energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
            
            data = {"total_energy": float(energy), "solvent": input_data.solvent, "model": "SMD"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"SMD: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SMD_ERROR", message=str(e)))

def calculate_smd(geometry: str, solvent: str = "water", **kwargs) -> ToolOutput:
    return SMDTool().run({"geometry": geometry, "solvent": solvent, **kwargs})
