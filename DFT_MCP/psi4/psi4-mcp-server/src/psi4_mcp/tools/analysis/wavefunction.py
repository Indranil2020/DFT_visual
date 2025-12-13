"""Wavefunction Analysis Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class WavefunctionToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class WavefunctionTool(BaseTool[WavefunctionToolInput, ToolOutput]):
    """Analyze wavefunction properties."""
    name: ClassVar[str] = "analyze_wavefunction"
    description: ClassVar[str] = "Analyze wavefunction (orbitals, density, etc.)."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: WavefunctionToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            import numpy as np
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", return_wfn=True, molecule=mol)
            
            # Extract wavefunction info
            n_alpha = wfn.nalpha()
            n_beta = wfn.nbeta()
            n_mo = wfn.nmo()
            
            # Orbital energies
            eps_a = np.array(wfn.epsilon_a()).tolist()
            homo = eps_a[n_alpha - 1] if n_alpha > 0 else None
            lumo = eps_a[n_alpha] if n_alpha < n_mo else None
            gap = lumo - homo if homo and lumo else None
            
            HARTREE_TO_EV = 27.2114
            data = {
                "energy": float(energy),
                "n_alpha": n_alpha,
                "n_beta": n_beta,
                "n_mo": n_mo,
                "homo_ev": homo * HARTREE_TO_EV if homo else None,
                "lumo_ev": lumo * HARTREE_TO_EV if lumo else None,
                "gap_ev": gap * HARTREE_TO_EV if gap else None,
                "orbital_energies_ev": [e * HARTREE_TO_EV for e in eps_a[:10]],
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"HOMO-LUMO gap: {gap*HARTREE_TO_EV:.2f} eV" if gap else "Analysis complete", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="WFN_ERROR", message=str(e)))

def analyze_wavefunction(geometry: str, **kwargs) -> ToolOutput:
    return WavefunctionTool().run({"geometry": geometry, **kwargs})
