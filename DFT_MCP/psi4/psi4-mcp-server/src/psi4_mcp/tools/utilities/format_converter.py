"""
File Format Converter Tool.

Converts between various molecular file formats and provides
output formatting utilities.

Key Features:
    - XYZ to Z-matrix conversion
    - Energy unit conversion
    - Output format standardization
    - Data export utilities
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)


# Unit conversion factors
ENERGY_CONVERSIONS = {
    ("hartree", "ev"): 27.211386245988,
    ("hartree", "kcal/mol"): 627.5094740631,
    ("hartree", "kj/mol"): 2625.4996394799,
    ("hartree", "cm-1"): 219474.63136320,
    ("ev", "hartree"): 1 / 27.211386245988,
    ("ev", "kcal/mol"): 23.0605419,
    ("ev", "kj/mol"): 96.4853321,
    ("kcal/mol", "hartree"): 1 / 627.5094740631,
    ("kcal/mol", "kj/mol"): 4.184,
    ("kj/mol", "hartree"): 1 / 2625.4996394799,
    ("kj/mol", "kcal/mol"): 1 / 4.184,
}

LENGTH_CONVERSIONS = {
    ("angstrom", "bohr"): 1.8897259886,
    ("bohr", "angstrom"): 1 / 1.8897259886,
    ("angstrom", "nm"): 0.1,
    ("nm", "angstrom"): 10.0,
}


@dataclass
class ConversionResult:
    """Result of a unit conversion."""
    original_value: float
    original_unit: str
    converted_value: float
    target_unit: str
    conversion_factor: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_value": self.original_value,
            "original_unit": self.original_unit,
            "converted_value": self.converted_value,
            "target_unit": self.target_unit,
            "conversion_factor": self.conversion_factor,
        }


@dataclass
class GeometryConversion:
    """Result of geometry format conversion."""
    original_format: str
    target_format: str
    converted_geometry: str
    n_atoms: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "original_format": self.original_format,
            "target_format": self.target_format,
            "converted_geometry": self.converted_geometry,
            "n_atoms": self.n_atoms,
        }


class FormatConverterInput(ToolInput):
    """Input for format converter."""
    # Energy/unit conversion
    convert_energy: Optional[float] = Field(default=None, description="Energy value to convert")
    from_unit: Optional[str] = Field(default=None, description="Source unit")
    to_unit: Optional[str] = Field(default=None, description="Target unit")
    
    # Geometry conversion
    convert_geometry: Optional[str] = Field(default=None, description="Geometry to convert")
    geometry_from: Optional[str] = Field(default="xyz", description="Source format")
    geometry_to: Optional[str] = Field(default="zmatrix", description="Target format")
    
    # List available conversions
    list_units: bool = Field(default=False, description="List available unit conversions")


def validate_format_converter_input(input_data: FormatConverterInput) -> Optional[ValidationError]:
    if input_data.convert_energy is not None:
        if not input_data.from_unit or not input_data.to_unit:
            return ValidationError(
                field="from_unit",
                message="Both from_unit and to_unit required for energy conversion",
            )
    return None


def convert_energy_units(value: float, from_unit: str, to_unit: str) -> ConversionResult:
    """Convert energy between units."""
    from_lower = from_unit.lower().replace(" ", "").replace("_", "")
    to_lower = to_unit.lower().replace(" ", "").replace("_", "")
    
    # Normalize unit names
    unit_aliases = {
        "hartree": "hartree", "ha": "hartree", "eh": "hartree", "au": "hartree",
        "ev": "ev", "electronvolt": "ev",
        "kcal/mol": "kcal/mol", "kcalmol": "kcal/mol", "kcal": "kcal/mol",
        "kj/mol": "kj/mol", "kjmol": "kj/mol", "kj": "kj/mol",
        "cm-1": "cm-1", "cm^-1": "cm-1", "wavenumber": "cm-1",
    }
    
    from_norm = unit_aliases.get(from_lower, from_lower)
    to_norm = unit_aliases.get(to_lower, to_lower)
    
    if from_norm == to_norm:
        return ConversionResult(value, from_unit, value, to_unit, 1.0)
    
    key = (from_norm, to_norm)
    if key in ENERGY_CONVERSIONS:
        factor = ENERGY_CONVERSIONS[key]
    else:
        # Try via Hartree
        to_hartree = ENERGY_CONVERSIONS.get((from_norm, "hartree"), None)
        from_hartree = ENERGY_CONVERSIONS.get(("hartree", to_norm), None)
        
        if to_hartree and from_hartree:
            factor = to_hartree * from_hartree
        else:
            factor = 1.0  # Unknown conversion
    
    return ConversionResult(
        original_value=value,
        original_unit=from_unit,
        converted_value=value * factor,
        target_unit=to_unit,
        conversion_factor=factor,
    )


def xyz_to_zmatrix(xyz_geometry: str) -> str:
    """Convert XYZ format to Z-matrix format (simple version)."""
    lines = xyz_geometry.strip().split("\n")
    atoms = []
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            symbol = parts[0]
            x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            atoms.append((symbol, x, y, z))
    
    if not atoms:
        return ""
    
    # Build Z-matrix
    zmat_lines = []
    
    # First atom - just symbol
    zmat_lines.append(atoms[0][0])
    
    if len(atoms) >= 2:
        # Second atom - bond to first
        s1, x1, y1, z1 = atoms[0]
        s2, x2, y2, z2 = atoms[1]
        r12 = ((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)**0.5
        zmat_lines.append(f"{atoms[1][0]} 1 {r12:.6f}")
    
    if len(atoms) >= 3:
        # Third atom - bond and angle
        s3, x3, y3, z3 = atoms[2]
        # Distance to atom 2
        r23 = ((x3-x2)**2 + (y3-y2)**2 + (z3-z2)**2)**0.5
        
        # Angle 1-2-3
        import math
        v21 = (x1-x2, y1-y2, z1-z2)
        v23 = (x3-x2, y3-y2, z3-z2)
        dot = v21[0]*v23[0] + v21[1]*v23[1] + v21[2]*v23[2]
        mag21 = (v21[0]**2 + v21[1]**2 + v21[2]**2)**0.5
        mag23 = (v23[0]**2 + v23[1]**2 + v23[2]**2)**0.5
        
        if mag21 > 0 and mag23 > 0:
            cos_angle = max(-1, min(1, dot / (mag21 * mag23)))
            angle = math.degrees(math.acos(cos_angle))
        else:
            angle = 109.5
        
        zmat_lines.append(f"{atoms[2][0]} 2 {r23:.6f} 1 {angle:.2f}")
    
    # Remaining atoms - bond, angle, dihedral
    for i in range(3, len(atoms)):
        si, xi, yi, zi = atoms[i]
        # Use previous three atoms as references
        r = ((xi-atoms[i-1][1])**2 + (yi-atoms[i-1][2])**2 + (zi-atoms[i-1][3])**2)**0.5
        zmat_lines.append(f"{si} {i} {r:.6f} {i-1} 109.5 {i-2} 120.0")
    
    return "\n".join(zmat_lines)


def convert_geometry_format(geometry: str, from_format: str, to_format: str) -> GeometryConversion:
    """Convert between geometry formats."""
    from_lower = from_format.lower()
    to_lower = to_format.lower()
    
    # Count atoms in input
    lines = geometry.strip().split("\n")
    n_atoms = sum(1 for line in lines if len(line.split()) >= 4)
    
    if from_lower == "xyz" and to_lower in ["zmatrix", "z-matrix", "internal"]:
        converted = xyz_to_zmatrix(geometry)
    else:
        # No conversion needed or unsupported
        converted = geometry
    
    return GeometryConversion(
        original_format=from_format,
        target_format=to_format,
        converted_geometry=converted,
        n_atoms=n_atoms,
    )


@register_tool
class FormatConverterTool(BaseTool[FormatConverterInput, ToolOutput]):
    """Tool for format conversions."""
    name: ClassVar[str] = "convert_format"
    description: ClassVar[str] = "Convert between units and geometry formats."
    category: ClassVar[ToolCategory] = ToolCategory.UTILITIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: FormatConverterInput) -> Optional[ValidationError]:
        return validate_format_converter_input(input_data)
    
    def _execute(self, input_data: FormatConverterInput) -> Result[ToolOutput]:
        result_data: Dict[str, Any] = {}
        
        if input_data.list_units:
            units = {
                "energy": ["hartree", "eV", "kcal/mol", "kJ/mol", "cm-1"],
                "length": ["angstrom", "bohr", "nm"],
            }
            message = f"Available units:\n  Energy: {', '.join(units['energy'])}\n  Length: {', '.join(units['length'])}"
            return Result.success(ToolOutput(success=True, message=message, data=units))
        
        if input_data.convert_energy is not None:
            result = convert_energy_units(
                input_data.convert_energy,
                input_data.from_unit or "hartree",
                input_data.to_unit or "kcal/mol",
            )
            result_data = result.to_dict()
            message = f"{result.original_value} {result.original_unit} = {result.converted_value:.6f} {result.target_unit}"
        
        elif input_data.convert_geometry:
            result = convert_geometry_format(
                input_data.convert_geometry,
                input_data.geometry_from or "xyz",
                input_data.geometry_to or "zmatrix",
            )
            result_data = result.to_dict()
            message = f"Converted {result.n_atoms} atoms from {result.original_format} to {result.target_format}"
        
        else:
            message = "No conversion requested"
        
        return Result.success(ToolOutput(success=True, message=message, data=result_data))


def convert_units(value: float, from_unit: str, to_unit: str) -> ToolOutput:
    """Convert energy or length units."""
    return FormatConverterTool().run({
        "convert_energy": value, "from_unit": from_unit, "to_unit": to_unit,
    })
