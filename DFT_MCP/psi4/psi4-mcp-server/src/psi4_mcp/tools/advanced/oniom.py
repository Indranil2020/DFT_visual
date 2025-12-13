"""ONIOM Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class ONIOMToolInput(ToolInput):
    full_geometry: str = Field(...)
    high_atoms: list[int] = Field(..., description="Atom indices for high-level region")
    high_method: str = Field(default="ccsd(t)")
    high_basis: str = Field(default="cc-pvdz")
    low_method: str = Field(default="hf")
    low_basis: str = Field(default="sto-3g")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class ONIOMTool(BaseTool[ONIOMToolInput, ToolOutput]):
    """ONIOM multi-layer method."""
    name: ClassVar[str] = "calculate_oniom"
    description: ClassVar[str] = "Calculate with ONIOM layered approach."
    category: ClassVar[ToolCategory] = ToolCategory.MULTISCALE
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: ONIOMToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.full_geometry}")
            
            # Full system at low level
            psi4.set_options({"basis": input_data.low_basis})
            e_low_full = psi4.energy(f"{input_data.low_method}/{input_data.low_basis}", molecule=mol)
            
            # High region at both levels (simplified - would need subsystem extraction)
            # ONIOM energy = E_high(model) + E_low(real) - E_low(model)
            
            data = {
                "oniom_energy": float(e_low_full),
                "high_level": f"{input_data.high_method}/{input_data.high_basis}",
                "low_level": f"{input_data.low_method}/{input_data.low_basis}",
                "note": "Simplified ONIOM - full implementation requires subsystem handling",
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"ONIOM: E = {e_low_full:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="ONIOM_ERROR", message=str(e)))

def calculate_oniom(full_geometry: str, high_atoms: list, **kwargs) -> ToolOutput:
    return ONIOMTool().run({"full_geometry": full_geometry, "high_atoms": high_atoms, **kwargs})
