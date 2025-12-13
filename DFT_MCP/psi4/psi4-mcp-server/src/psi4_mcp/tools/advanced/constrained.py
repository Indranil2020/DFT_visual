"""Constrained Optimization Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class ConstrainedOptToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    frozen_atoms: list[int] = Field(default=[], description="Atom indices to freeze (1-based)")
    fixed_distances: list[tuple[int, int, float]] = Field(default=[], description="(i, j, distance) tuples")
    fixed_angles: list[tuple[int, int, int, float]] = Field(default=[], description="(i, j, k, angle) tuples")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class ConstrainedOptTool(BaseTool[ConstrainedOptToolInput, ToolOutput]):
    """Geometry optimization with constraints."""
    name: ClassVar[str] = "optimize_constrained"
    description: ClassVar[str] = "Optimize geometry with frozen atoms or fixed coordinates."
    category: ClassVar[ToolCategory] = ToolCategory.OPTIMIZATION
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: ConstrainedOptToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            # Set frozen atoms
            freeze_str = ""
            if input_data.frozen_atoms:
                freeze_str = "frozen_cartesian = (" + " ".join(str(i) for i in input_data.frozen_atoms) + ")"
            
            psi4.set_options({"basis": input_data.basis, "geom_maxiter": 50})
            if freeze_str:
                psi4.set_options({"optking__frozen_cartesian": freeze_str})
            
            energy = psi4.optimize(f"{input_data.method}/{input_data.basis}", molecule=mol)
            final_geom = mol.save_string_xyz()
            
            data = {
                "final_energy": float(energy),
                "final_geometry": final_geom,
                "frozen_atoms": input_data.frozen_atoms,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Constrained opt: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="CONSTRAINED_ERROR", message=str(e)))

def optimize_constrained(geometry: str, **kwargs) -> ToolOutput:
    return ConstrainedOptTool().run({"geometry": geometry, **kwargs})
