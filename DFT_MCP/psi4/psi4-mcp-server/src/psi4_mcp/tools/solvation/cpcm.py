"""CPCM (Conductor-like PCM) Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

SOLVENTS = {
    "water": {"eps": 78.39, "eps_inf": 1.78},
    "methanol": {"eps": 32.70, "eps_inf": 1.76},
    "ethanol": {"eps": 24.55, "eps_inf": 1.85},
    "acetonitrile": {"eps": 36.64, "eps_inf": 1.81},
    "dmso": {"eps": 46.70, "eps_inf": 2.18},
    "chloroform": {"eps": 4.81, "eps_inf": 2.09},
    "toluene": {"eps": 2.38, "eps_inf": 2.23},
    "cyclohexane": {"eps": 2.02, "eps_inf": 2.03},
}

class CPCMToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    solvent: str = Field(default="water")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class CPCMTool(BaseTool[CPCMToolInput, ToolOutput]):
    """CPCM conductor-like solvation model."""
    name: ClassVar[str] = "calculate_cpcm"
    description: ClassVar[str] = "Calculate energy with CPCM solvation."
    category: ClassVar[ToolCategory] = ToolCategory.SOLVATION
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CPCMToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            solvent_params = SOLVENTS.get(input_data.solvent.lower(), SOLVENTS["water"])
            psi4.set_options({
                "basis": input_data.basis,
                "pcm": True,
                "pcm__input": f'''
                    Units = Angstrom
                    Medium {{SolverType = CPCM eps = {solvent_params["eps"]}}}
                '''
            })
            energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
            
            data = {"total_energy": float(energy), "solvent": input_data.solvent, "model": "CPCM"}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CPCM: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CPCM_ERROR", message=str(e)))

def calculate_cpcm(geometry: str, solvent: str = "water", **kwargs) -> ToolOutput:
    return CPCMTool().run({"geometry": geometry, "solvent": solvent, **kwargs})
