"""Basis Set Information Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

BASIS_INFO = {
    "sto-3g": {"type": "minimal", "quality": "poor", "use": "testing only"},
    "3-21g": {"type": "split-valence", "quality": "low", "use": "quick estimates"},
    "6-31g": {"type": "split-valence", "quality": "low", "use": "quick estimates"},
    "6-31g*": {"type": "polarized", "quality": "medium", "use": "geometry optimization"},
    "6-311g**": {"type": "triple-zeta", "quality": "medium", "use": "general purpose"},
    "cc-pvdz": {"type": "correlation-consistent DZ", "quality": "medium", "use": "correlation"},
    "cc-pvtz": {"type": "correlation-consistent TZ", "quality": "high", "use": "accurate correlation"},
    "cc-pvqz": {"type": "correlation-consistent QZ", "quality": "very high", "use": "benchmark"},
    "aug-cc-pvdz": {"type": "augmented DZ", "quality": "medium", "use": "anions, polarizability"},
    "aug-cc-pvtz": {"type": "augmented TZ", "quality": "high", "use": "accurate properties"},
    "def2-svp": {"type": "Karlsruhe DZ", "quality": "medium", "use": "efficient DFT"},
    "def2-tzvp": {"type": "Karlsruhe TZ", "quality": "high", "use": "production DFT"},
    "def2-qzvp": {"type": "Karlsruhe QZ", "quality": "very high", "use": "benchmark DFT"},
}

class BasisInfoToolInput(ToolInput):
    basis: str = Field(..., description="Basis set name")

@register_tool
class BasisInfoTool(BaseTool[BasisInfoToolInput, ToolOutput]):
    """Get information about a basis set."""
    name: ClassVar[str] = "get_basis_info"
    description: ClassVar[str] = "Get information about a basis set."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: BasisInfoToolInput) -> Result[ToolOutput]:
        basis_lower = input_data.basis.lower()
        if basis_lower in BASIS_INFO:
            info = BASIS_INFO[basis_lower]
            data = {"basis": input_data.basis, **info}
            return Result.success(ToolOutput(success=True, message=f"{input_data.basis}: {info['quality']}", data=data))
        else:
            return Result.success(ToolOutput(success=True, 
                message=f"Unknown basis {input_data.basis}", 
                data={"basis": input_data.basis, "note": "Check Psi4 documentation"}))

def get_basis_info(basis: str) -> ToolOutput:
    return BasisInfoTool().run({"basis": basis})
