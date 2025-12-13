"""Complete Basis Set Extrapolation Tool."""
from typing import Any, ClassVar, Literal
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class ExtrapolationToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="mp2")
    basis_family: Literal["cc-pv", "aug-cc-pv"] = Field(default="cc-pv")
    zeta_pair: tuple[int, int] = Field(default=(2, 3), description="(X, Y) for X/Y extrapolation")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)

@register_tool
class ExtrapolationTool(BaseTool[ExtrapolationToolInput, ToolOutput]):
    """CBS extrapolation to estimate complete basis set limit."""
    name: ClassVar[str] = "extrapolate_cbs"
    description: ClassVar[str] = "Extrapolate energy to complete basis set limit."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: ExtrapolationToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            x, y = input_data.zeta_pair
            zeta_map = {2: "dz", 3: "tz", 4: "qz", 5: "5z"}
            
            basis_x = f"{input_data.basis_family}{zeta_map[x]}"
            basis_y = f"{input_data.basis_family}{zeta_map[y]}"
            
            # Calculate at both basis sets
            psi4.set_options({"basis": basis_x})
            e_x = psi4.energy(input_data.method, molecule=mol)
            
            psi4.set_options({"basis": basis_y})
            e_y = psi4.energy(input_data.method, molecule=mol)
            
            # CBS extrapolation (Helgaker formula for correlation)
            # E_CBS = E_Y + (E_Y - E_X) * Y^3 / (Y^3 - X^3)
            cbs_energy = float(e_y) + (float(e_y) - float(e_x)) * (y**3) / (y**3 - x**3)
            
            data = {
                "cbs_energy": cbs_energy,
                f"energy_{zeta_map[x]}": float(e_x),
                f"energy_{zeta_map[y]}": float(e_y),
                "extrapolation": f"{x}/{y}",
                "method": input_data.method,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"CBS({x}/{y}): E = {cbs_energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CBS_ERROR", message=str(e)))

def extrapolate_cbs(geometry: str, method: str = "mp2", **kwargs) -> ToolOutput:
    return ExtrapolationTool().run({"geometry": geometry, "method": method, **kwargs})
