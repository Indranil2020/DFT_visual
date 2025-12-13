"""Batch Runner Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class BatchToolInput(ToolInput):
    geometries: list[str] = Field(..., description="List of geometries")
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    calculation_type: str = Field(default="energy")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class BatchTool(BaseTool[BatchToolInput, ToolOutput]):
    """Run calculations on multiple geometries."""
    name: ClassVar[str] = "run_batch"
    description: ClassVar[str] = "Run batch calculations on multiple molecules."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITY
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: BatchToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_options({"basis": input_data.basis})
            
            results = []
            for i, geom in enumerate(input_data.geometries):
                try:
                    mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{geom}")
                    energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
                    results.append({"index": i, "energy": float(energy), "status": "success"})
                except Exception as e:
                    results.append({"index": i, "energy": None, "status": f"error: {str(e)}"})
                psi4.core.clean_variables()
            
            data = {"results": results, "n_total": len(input_data.geometries),
                    "n_success": sum(1 for r in results if r["status"] == "success")}
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Batch: {data['n_success']}/{data['n_total']} succeeded", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="BATCH_ERROR", message=str(e)))

def run_batch(geometries: list, **kwargs) -> ToolOutput:
    return BatchTool().run({"geometries": geometries, **kwargs})
