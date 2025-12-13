"""Structure Builder Tool."""
from typing import Any, ClassVar
from pydantic import Field
from psi4_mcp.tools.core.base_tool import BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool
from psi4_mcp.models.errors import Result, CalculationError

COMMON_MOLECULES = {
    "water": "O 0.0 0.0 0.0\nH 0.96 0.0 0.0\nH -0.24 0.93 0.0",
    "methane": "C 0.0 0.0 0.0\nH 0.63 0.63 0.63\nH -0.63 -0.63 0.63\nH -0.63 0.63 -0.63\nH 0.63 -0.63 -0.63",
    "ethane": "C 0.0 0.0 0.76\nC 0.0 0.0 -0.76\nH 1.02 0.0 1.16\nH -0.51 0.88 1.16\nH -0.51 -0.88 1.16\nH -1.02 0.0 -1.16\nH 0.51 0.88 -1.16\nH 0.51 -0.88 -1.16",
    "benzene": "C 1.39 0.0 0.0\nC 0.69 1.20 0.0\nC -0.69 1.20 0.0\nC -1.39 0.0 0.0\nC -0.69 -1.20 0.0\nC 0.69 -1.20 0.0\nH 2.47 0.0 0.0\nH 1.24 2.14 0.0\nH -1.24 2.14 0.0\nH -2.47 0.0 0.0\nH -1.24 -2.14 0.0\nH 1.24 -2.14 0.0",
}

class StructureBuilderToolInput(ToolInput):
    molecule_name: str = Field(default=None, description="Common molecule name")
    smiles: str = Field(default=None, description="SMILES string")

@register_tool
class StructureBuilderTool(BaseTool[StructureBuilderToolInput, ToolOutput]):
    """Build molecular structures from names or SMILES."""
    name: ClassVar[str] = "build_structure"
    description: ClassVar[str] = "Build molecular geometry from name or SMILES."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITY
    version: ClassVar[str] = "1.0.0"
    
    def _execute(self, input_data: StructureBuilderToolInput) -> Result[ToolOutput]:
        if input_data.molecule_name and input_data.molecule_name.lower() in COMMON_MOLECULES:
            geom = COMMON_MOLECULES[input_data.molecule_name.lower()]
            data = {"geometry": geom, "source": "library", "molecule": input_data.molecule_name}
            return Result.success(ToolOutput(success=True, message=f"Built {input_data.molecule_name}", data=data))
        elif input_data.smiles:
            data = {"smiles": input_data.smiles, "note": "SMILES conversion requires RDKit"}
            return Result.success(ToolOutput(success=True, message="SMILES provided", data=data))
        else:
            return Result.failure(CalculationError(code="BUILD_ERROR", message="Provide molecule_name or smiles"))

def build_structure(molecule_name: str = None, smiles: str = None) -> ToolOutput:
    return StructureBuilderTool().run({"molecule_name": molecule_name, "smiles": smiles})
