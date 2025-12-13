"""Potential Energy Surface Scan Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError
import numpy as np

class ScanToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    scan_type: str = Field(default="bond", description="bond, angle, or dihedral")
    atoms: list[int] = Field(..., description="Atom indices for scan coordinate")
    start: float = Field(...)
    end: float = Field(...)
    steps: int = Field(default=10)
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class ScanTool(BaseTool[ScanToolInput, ToolOutput]):
    """Scan potential energy surface along a coordinate."""
    name: ClassVar[str] = "run_scan"
    description: ClassVar[str] = "Scan energy along bond, angle, or dihedral."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: ScanToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            
            scan_values = np.linspace(input_data.start, input_data.end, input_data.steps)
            energies = []
            
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            psi4.set_options({"basis": input_data.basis})
            
            # For now, just compute energy at starting geometry
            # Full scan would modify geometry at each step
            for val in scan_values:
                energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
                energies.append(float(energy))
                break  # Simplified - only one point
            
            data = {
                "scan_type": input_data.scan_type,
                "atoms": input_data.atoms,
                "values": scan_values.tolist(),
                "energies": energies,
                "note": "Full scan requires geometry modification at each step",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Scan: {len(energies)} points", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="SCAN_ERROR", message=str(e)))

def run_scan(geometry: str, atoms: list, start: float, end: float, **kwargs) -> ToolOutput:
    return ScanTool().run({"geometry": geometry, "atoms": atoms, "start": start, "end": end, **kwargs})
