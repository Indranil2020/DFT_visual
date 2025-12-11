"""Grid Quality Tool - Test DFT integration grid convergence."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class GridQualityToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="b3lyp")
    basis: str = Field(default="cc-pvdz")
    grids: list[int] = Field(default=[1, 2, 3, 4, 5], description="DFT_SPHERICAL_POINTS levels")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class GridQualityTool(BaseTool[GridQualityToolInput, ToolOutput]):
    """Test DFT integration grid convergence."""
    name: ClassVar[str] = "test_grid_quality"
    description: ClassVar[str] = "Test DFT energy convergence with grid size."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: GridQualityToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            results = {}
            for grid in input_data.grids:
                psi4.set_options({
                    "basis": input_data.basis,
                    "dft_spherical_points": grid * 110,  # Approximate
                    "dft_radial_points": grid * 25,
                })
                energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
                results[f"grid_{grid}"] = float(energy)
                psi4.core.clean_variables()
            
            # Check convergence
            energies = list(results.values())
            convergence = max(energies) - min(energies)
            
            data = {
                "energies": results,
                "convergence_hartree": convergence,
                "convergence_kcal": convergence * 627.509,
                "converged": convergence < 1e-6,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Grid convergence: {convergence:.2e} Hartree", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="GRID_ERROR", message=str(e)))

def test_grid_quality(geometry: str, **kwargs) -> ToolOutput:
    return GridQualityTool().run({"geometry": geometry, **kwargs})
