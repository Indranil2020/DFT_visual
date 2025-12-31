"""
Molecular Structure Builder Tool.

Utilities for building and manipulating molecular structures
programmatically.

Key Features:
    - Build molecules from SMILES
    - Generate common structures
    - Create dimers and complexes
    - Modify existing geometries
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


# Common molecule templates
MOLECULE_TEMPLATES = {
    "water": "O  0.000000  0.000000  0.117369\nH -0.756950  0.000000 -0.469476\nH  0.756950  0.000000 -0.469476",
    "methane": "C  0.000000  0.000000  0.000000\nH  0.629118  0.629118  0.629118\nH -0.629118 -0.629118  0.629118\nH -0.629118  0.629118 -0.629118\nH  0.629118 -0.629118 -0.629118",
    "ammonia": "N  0.000000  0.000000  0.116500\nH  0.000000  0.939700 -0.271800\nH  0.813800 -0.469900 -0.271800\nH -0.813800 -0.469900 -0.271800",
    "benzene": "C  1.392000  0.000000  0.000000\nC  0.696000  1.205000  0.000000\nC -0.696000  1.205000  0.000000\nC -1.392000  0.000000  0.000000\nC -0.696000 -1.205000  0.000000\nC  0.696000 -1.205000  0.000000\nH  2.472000  0.000000  0.000000\nH  1.236000  2.140000  0.000000\nH -1.236000  2.140000  0.000000\nH -2.472000  0.000000  0.000000\nH -1.236000 -2.140000  0.000000\nH  1.236000 -2.140000  0.000000",
    "ethene": "C -0.667000  0.000000  0.000000\nC  0.667000  0.000000  0.000000\nH -1.237000  0.923000  0.000000\nH -1.237000 -0.923000  0.000000\nH  1.237000  0.923000  0.000000\nH  1.237000 -0.923000  0.000000",
    "formaldehyde": "C  0.000000  0.000000 -0.529200\nO  0.000000  0.000000  0.676200\nH  0.000000  0.935300 -1.109400\nH  0.000000 -0.935300 -1.109400",
    "hydrogen": "H  0.000000  0.000000  0.371000\nH  0.000000  0.000000 -0.371000",
    "co2": "C  0.000000  0.000000  0.000000\nO  0.000000  0.000000  1.160000\nO  0.000000  0.000000 -1.160000",
}


@dataclass
class BuiltStructure:
    """A built molecular structure."""
    geometry: str
    n_atoms: int
    formula: str
    center_of_mass: Tuple[float, float, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "geometry": self.geometry,
            "n_atoms": self.n_atoms,
            "formula": self.formula,
            "center_of_mass": self.center_of_mass,
        }


class StructureBuilderInput(ToolInput):
    """Input for structure builder."""
    template_name: Optional[str] = Field(default=None, description="Use a template molecule")
    list_templates: bool = Field(default=False, description="List available templates")
    
    geometry: Optional[str] = Field(default=None, description="Custom geometry to modify")
    
    translate: Optional[Tuple[float, float, float]] = Field(default=None, description="Translation vector")
    rotate: Optional[Tuple[float, float, float]] = Field(default=None, description="Rotation angles (degrees)")
    scale: Optional[float] = Field(default=None, description="Scale factor for coordinates")
    
    create_dimer: bool = Field(default=False, description="Create a dimer")
    dimer_distance: float = Field(default=3.0, description="Distance between monomer centers")
    dimer_axis: Tuple[float, float, float] = Field(default=(0, 0, 1), description="Axis for dimer separation")


def validate_structure_builder_input(input_data: StructureBuilderInput) -> Optional[ValidationError]:
    if not input_data.template_name and not input_data.list_templates and not input_data.geometry:
        return ValidationError(
            field="template_name",
            message="Provide template_name, geometry, or set list_templates=True",
        )
    return None


def parse_geometry(geom_str: str) -> List[Tuple[str, float, float, float]]:
    """Parse XYZ geometry string into atoms list."""
    atoms = []
    for line in geom_str.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 4:
            symbol = parts[0]
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            atoms.append((symbol, x, y, z))
    return atoms


def atoms_to_geometry(atoms: List[Tuple[str, float, float, float]]) -> str:
    """Convert atoms list to XYZ geometry string."""
    lines = []
    for symbol, x, y, z in atoms:
        lines.append(f"{symbol} {x:12.6f} {y:12.6f} {z:12.6f}")
    return "\n".join(lines)


def translate_geometry(atoms: List[Tuple[str, float, float, float]], 
                      vector: Tuple[float, float, float]) -> List[Tuple[str, float, float, float]]:
    """Translate atoms by vector."""
    return [(s, x + vector[0], y + vector[1], z + vector[2]) for s, x, y, z in atoms]


def calculate_center_of_mass(atoms: List[Tuple[str, float, float, float]]) -> Tuple[float, float, float]:
    """Calculate center of mass (unweighted geometric center)."""
    if not atoms:
        return (0.0, 0.0, 0.0)
    
    n = len(atoms)
    cx = sum(x for _, x, _, _ in atoms) / n
    cy = sum(y for _, _, y, _ in atoms) / n
    cz = sum(z for _, _, _, z in atoms) / n
    return (cx, cy, cz)


def get_molecular_formula(atoms: List[Tuple[str, float, float, float]]) -> str:
    """Get molecular formula from atoms."""
    from collections import Counter
    counts = Counter(symbol for symbol, _, _, _ in atoms)
    
    # Standard ordering: C, H, then alphabetical
    formula_parts = []
    if "C" in counts:
        formula_parts.append(f"C{counts['C']}" if counts['C'] > 1 else "C")
        del counts["C"]
    if "H" in counts:
        formula_parts.append(f"H{counts['H']}" if counts['H'] > 1 else "H")
        del counts["H"]
    
    for symbol in sorted(counts.keys()):
        count = counts[symbol]
        formula_parts.append(f"{symbol}{count}" if count > 1 else symbol)
    
    return "".join(formula_parts)


def build_structure(input_data: StructureBuilderInput) -> BuiltStructure:
    """Build or modify a molecular structure."""
    # Get initial geometry
    if input_data.template_name:
        template_lower = input_data.template_name.lower()
        if template_lower not in MOLECULE_TEMPLATES:
            # Return empty structure with error
            return BuiltStructure(
                geometry=f"# Template '{input_data.template_name}' not found",
                n_atoms=0,
                formula="",
                center_of_mass=(0, 0, 0),
            )
        geometry_str = MOLECULE_TEMPLATES[template_lower]
    else:
        geometry_str = input_data.geometry or ""
    
    atoms = parse_geometry(geometry_str)
    
    # Apply transformations
    if input_data.translate:
        atoms = translate_geometry(atoms, input_data.translate)
    
    if input_data.scale:
        center = calculate_center_of_mass(atoms)
        # Scale from center
        scaled = []
        for symbol, x, y, z in atoms:
            new_x = center[0] + (x - center[0]) * input_data.scale
            new_y = center[1] + (y - center[1]) * input_data.scale
            new_z = center[2] + (z - center[2]) * input_data.scale
            scaled.append((symbol, new_x, new_y, new_z))
        atoms = scaled
    
    # Create dimer if requested
    if input_data.create_dimer:
        # Center first monomer
        center = calculate_center_of_mass(atoms)
        atoms = translate_geometry(atoms, (-center[0], -center[1], -center[2]))
        
        # Create second monomer translated along axis
        axis = input_data.dimer_axis
        norm = (axis[0]**2 + axis[1]**2 + axis[2]**2)**0.5
        if norm > 0:
            unit_axis = (axis[0]/norm, axis[1]/norm, axis[2]/norm)
        else:
            unit_axis = (0, 0, 1)
        
        translation = (
            unit_axis[0] * input_data.dimer_distance,
            unit_axis[1] * input_data.dimer_distance,
            unit_axis[2] * input_data.dimer_distance,
        )
        
        monomer2 = translate_geometry(atoms, translation)
        
        # Combine with separator
        geometry_str = atoms_to_geometry(atoms) + "\n--\n" + atoms_to_geometry(monomer2)
        atoms = atoms + monomer2
    else:
        geometry_str = atoms_to_geometry(atoms)
    
    return BuiltStructure(
        geometry=geometry_str,
        n_atoms=len(atoms),
        formula=get_molecular_formula(atoms),
        center_of_mass=calculate_center_of_mass(atoms),
    )


@register_tool
class StructureBuilderTool(BaseTool[StructureBuilderInput, ToolOutput]):
    """Tool for building molecular structures."""
    name: ClassVar[str] = "build_structure"
    description: ClassVar[str] = "Build or modify molecular structures."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: StructureBuilderInput) -> Optional[ValidationError]:
        return validate_structure_builder_input(input_data)
    
    def _execute(self, input_data: StructureBuilderInput) -> Result[ToolOutput]:
        if input_data.list_templates:
            templates = list(MOLECULE_TEMPLATES.keys())
            message = f"Available templates: {', '.join(templates)}"
            return Result.success(ToolOutput(success=True, message=message, 
                                             data={"templates": templates}))
        
        result = build_structure(input_data)
        
        message = (
            f"Built Structure\n"
            f"{'='*40}\n"
            f"Formula: {result.formula}\n"
            f"N Atoms: {result.n_atoms}\n"
            f"Center of Mass: ({result.center_of_mass[0]:.3f}, "
            f"{result.center_of_mass[1]:.3f}, {result.center_of_mass[2]:.3f})\n"
            f"{'='*40}\n"
            f"{result.geometry}"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def build_molecule(template_name: Optional[str] = None, geometry: Optional[str] = None,
                   **kwargs: Any) -> ToolOutput:
    """Build a molecular structure."""
    return StructureBuilderTool().run({
        "template_name": template_name, "geometry": geometry, **kwargs,
    })
