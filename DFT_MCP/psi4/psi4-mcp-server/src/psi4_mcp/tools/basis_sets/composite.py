"""Composite Basis Set Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

class CompositeBasisToolInput(ToolInput):
    geometry: str = Field(...)
    method: str = Field(default="hf")
    basis_by_element: dict[str, str] = Field(..., description="Element -> basis mapping")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)

@register_tool
class CompositeBasisTool(BaseTool[CompositeBasisToolInput, ToolOutput]):
    """Use different basis sets for different elements."""
    name: ClassVar[str] = "calculate_composite_basis"
    description: ClassVar[str] = "Calculate with mixed basis sets per element."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: CompositeBasisToolInput) -> Result[ToolOutput]:
        try:
            import psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            mol = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}")
            
            # Build basis string
            basis_str = "\nassign cc-pvdz\n"  # default
            for element, basis in input_data.basis_by_element.items():
                basis_str += f"assign {element} {basis}\n"
            
            psi4.basis_helper(basis_str)
            energy = psi4.energy(input_data.method, molecule=mol)
            
            data = {
                "total_energy": float(energy),
                "basis_assignment": input_data.basis_by_element,
                "method": input_data.method,
            }
            psi4.core.clean()
            return Result.success(ToolOutput(success=True, message=f"Composite basis: E = {energy:.10f}", data=data))
        except Exception as e:
            return Result.failure(CalculationError(code="COMPOSITE_BASIS_ERROR", message=str(e)))

def calculate_composite_basis(geometry: str, basis_by_element: dict, **kwargs) -> ToolOutput:
    return CompositeBasisTool().run({"geometry": geometry, "basis_by_element": basis_by_element, **kwargs})
