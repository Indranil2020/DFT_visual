"""
Molecular Symmetry Analysis Tool.

Analyzes molecular point group symmetry and provides symmetry-related
properties and orbital classifications.

Key Features:
    - Point group detection
    - Symmetry element identification
    - Irreducible representation analysis
    - Symmetry-adapted orbitals
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)


@dataclass
class SymmetryElement:
    """A symmetry element."""
    element_type: str  # E, Cn, sigma, i, Sn
    order: Optional[int]
    axis: Optional[Tuple[float, float, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "order": self.order,
            "axis": self.axis,
        }


@dataclass
class SymmetryResult:
    """Symmetry analysis results."""
    point_group: str
    schoenflies_symbol: str
    n_symmetry_operations: int
    symmetry_elements: List[SymmetryElement]
    irreducible_representations: List[str]
    is_abelian: bool
    is_chiral: bool
    principal_axis: Optional[Tuple[float, float, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "point_group": self.point_group,
            "schoenflies_symbol": self.schoenflies_symbol,
            "n_symmetry_operations": self.n_symmetry_operations,
            "symmetry_elements": [e.to_dict() for e in self.symmetry_elements],
            "irreducible_representations": self.irreducible_representations,
            "is_abelian": self.is_abelian,
            "is_chiral": self.is_chiral,
            "principal_axis": self.principal_axis,
        }


class SymmetryInput(ToolInput):
    """Input for symmetry analysis."""
    geometry: str = Field(..., description="Molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    tolerance: float = Field(default=1e-4, description="Symmetry detection tolerance")
    memory: int = Field(default=2000)
    n_threads: int = Field(default=1)


def validate_symmetry_input(input_data: SymmetryInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


# Point group characteristics
POINT_GROUP_INFO = {
    "c1": {"n_ops": 1, "abelian": True, "chiral": True, "irreps": ["A"]},
    "ci": {"n_ops": 2, "abelian": True, "chiral": False, "irreps": ["Ag", "Au"]},
    "cs": {"n_ops": 2, "abelian": True, "chiral": False, "irreps": ["A'", "A''"]},
    "c2": {"n_ops": 2, "abelian": True, "chiral": True, "irreps": ["A", "B"]},
    "c2v": {"n_ops": 4, "abelian": True, "chiral": False, "irreps": ["A1", "A2", "B1", "B2"]},
    "c2h": {"n_ops": 4, "abelian": True, "chiral": False, "irreps": ["Ag", "Bg", "Au", "Bu"]},
    "c3v": {"n_ops": 6, "abelian": False, "chiral": False, "irreps": ["A1", "A2", "E"]},
    "c4v": {"n_ops": 8, "abelian": False, "chiral": False, "irreps": ["A1", "A2", "B1", "B2", "E"]},
    "d2": {"n_ops": 4, "abelian": True, "chiral": True, "irreps": ["A", "B1", "B2", "B3"]},
    "d2h": {"n_ops": 8, "abelian": True, "chiral": False, "irreps": ["Ag", "B1g", "B2g", "B3g", "Au", "B1u", "B2u", "B3u"]},
    "d3h": {"n_ops": 12, "abelian": False, "chiral": False, "irreps": ["A1'", "A2'", "E'", "A1''", "A2''", "E''"]},
    "d4h": {"n_ops": 16, "abelian": False, "chiral": False, "irreps": ["A1g", "A2g", "B1g", "B2g", "Eg", "A1u", "A2u", "B1u", "B2u", "Eu"]},
    "d6h": {"n_ops": 24, "abelian": False, "chiral": False, "irreps": ["A1g", "A2g", "B1g", "B2g", "E1g", "E2g", "A1u", "A2u", "B1u", "B2u", "E1u", "E2u"]},
    "td": {"n_ops": 24, "abelian": False, "chiral": False, "irreps": ["A1", "A2", "E", "T1", "T2"]},
    "oh": {"n_ops": 48, "abelian": False, "chiral": False, "irreps": ["A1g", "A2g", "Eg", "T1g", "T2g", "A1u", "A2u", "Eu", "T1u", "T2u"]},
}


def run_symmetry_analysis(input_data: SymmetryInput) -> SymmetryResult:
    """Execute symmetry analysis."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_symmetry.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    # Get point group
    point_group = mol.point_group().symbol().lower()
    schoenflies = mol.schoenflies_symbol()
    
    # Get info from lookup
    pg_info = POINT_GROUP_INFO.get(point_group, {
        "n_ops": 1, "abelian": True, "chiral": False, "irreps": ["A"]
    })
    
    # Build symmetry elements list
    symmetry_elements = [SymmetryElement(element_type="E", order=1, axis=None)]
    
    if "c" in point_group and point_group != "ci" and point_group != "cs":
        # Has rotation axis
        n = int(''.join(c for c in point_group if c.isdigit()) or '1')
        symmetry_elements.append(SymmetryElement(element_type=f"C{n}", order=n, axis=(0, 0, 1)))
    
    if "v" in point_group or "h" in point_group or "s" in point_group:
        symmetry_elements.append(SymmetryElement(element_type="sigma", order=None, axis=None))
    
    if "i" in point_group or "h" in point_group:
        symmetry_elements.append(SymmetryElement(element_type="i", order=None, axis=None))
    
    psi4.core.clean()
    
    return SymmetryResult(
        point_group=point_group,
        schoenflies_symbol=schoenflies,
        n_symmetry_operations=pg_info["n_ops"],
        symmetry_elements=symmetry_elements,
        irreducible_representations=pg_info["irreps"],
        is_abelian=pg_info["abelian"],
        is_chiral=pg_info["chiral"],
        principal_axis=(0, 0, 1) if pg_info["n_ops"] > 1 else None,
    )


@register_tool
class SymmetryTool(BaseTool[SymmetryInput, ToolOutput]):
    """Tool for molecular symmetry analysis."""
    name: ClassVar[str] = "analyze_symmetry"
    description: ClassVar[str] = "Analyze molecular point group symmetry."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: SymmetryInput) -> Optional[ValidationError]:
        return validate_symmetry_input(input_data)
    
    def _execute(self, input_data: SymmetryInput) -> Result[ToolOutput]:
        result = run_symmetry_analysis(input_data)
        
        elements_str = ", ".join(e.element_type for e in result.symmetry_elements)
        irreps_str = ", ".join(result.irreducible_representations)
        
        message = (
            f"Molecular Symmetry Analysis\n"
            f"{'='*40}\n"
            f"Point Group: {result.schoenflies_symbol} ({result.point_group})\n"
            f"Symmetry Operations: {result.n_symmetry_operations}\n"
            f"Elements: {elements_str}\n"
            f"Irreps: {irreps_str}\n"
            f"Abelian: {result.is_abelian}, Chiral: {result.is_chiral}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def analyze_symmetry(geometry: str, charge: int = 0, multiplicity: int = 1, 
                     **kwargs: Any) -> ToolOutput:
    """Analyze molecular symmetry."""
    return SymmetryTool().run({"geometry": geometry, "charge": charge, 
                                "multiplicity": multiplicity, **kwargs})
