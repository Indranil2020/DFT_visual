"""PCM (Polarizable Continuum Model) Tool."""
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

class PCMToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    solvent: str = Field(default="water")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class PCMTool(BaseTool[PCMToolInput, ToolOutput]):
    """PCM implicit solvation model."""
    name: ClassVar[str] = "calculate_pcm"
    description: ClassVar[str] = "Calculate energy with PCM implicit solvation."
    category: ClassVar[ToolCategory] = ToolCategory.SOLVATION
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: PCMToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            solvent_params = SOLVENTS.get(input_data.solvent.lower(), SOLVENTS["water"])
            psi4.set_options({
                "basis": input_data.basis,
                "pcm": True,
                "pcm_scf_type": "total",
                "pcm__input": f'''
                    Units = Angstrom
                    Solvent = Generic
                    SolverType = IEFPCM
                    Cavity {{Type = GePol}}
                    Medium {{SolverType = IEFPCM Solvent = Generic eps = {solvent_params["eps"]}}}
                '''
            })
            energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
            
            data = {
                "total_energy": float(energy),
                "solvent": input_data.solvent,
                "dielectric": solvent_params["eps"],
                "method": input_data.method,
                "basis": input_data.basis,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"PCM ({input_data.solvent}): E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="PCM_ERROR", message=str(e)))

def calculate_pcm(geometry: str, solvent: str = "water", method: str = "b3lyp", **kwargs) -> ToolOutput:
    return PCMTool().run({"geometry": geometry, "solvent": solvent, "method": method, **kwargs})
