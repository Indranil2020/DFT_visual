"""
Geometry Validation for Psi4 MCP Server.

Validates molecular geometry inputs.
"""

import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple


VALID_ELEMENTS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr",
    "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",
    "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",
    "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",
    "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",
    "Tl", "Pb", "Bi", "Po", "At", "Rn",
}

COVALENT_RADII = {
    "H": 0.31, "He": 0.28, "Li": 1.28, "Be": 0.96, "B": 0.84, "C": 0.76,
    "N": 0.71, "O": 0.66, "F": 0.57, "Ne": 0.58, "Na": 1.66, "Mg": 1.41,
    "Al": 1.21, "Si": 1.11, "P": 1.07, "S": 1.05, "Cl": 1.02, "Ar": 1.06,
}


@dataclass
class ValidationResult:
    """Result of validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class GeometryValidator:
    """Validates molecular geometry."""
    
    MIN_DISTANCE = 0.4  # Angstrom
    MAX_DISTANCE = 100.0  # Angstrom
    LINEARITY_THRESHOLD = 0.01  # degrees
    
    def __init__(self):
        self.valid_elements = VALID_ELEMENTS
    
    def validate(self, geometry: str, charge: int = 0, multiplicity: int = 1) -> ValidationResult:
        """Validate geometry string."""
        errors = []
        warnings = []
        
        if not geometry or not geometry.strip():
            return ValidationResult(valid=False, errors=["Geometry cannot be empty"])
        
        lines = geometry.strip().split("\n")
        elements = []
        coordinates = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            parts = line.split()
            if len(parts) < 1:
                continue
            
            elem = parts[0].capitalize()
            if elem not in self.valid_elements:
                errors.append(f"Line {i+1}: Unknown element '{parts[0]}'")
                continue
            
            elements.append(elem)
            
            # Cartesian coordinates
            if len(parts) >= 4:
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    coordinates.append((x, y, z))
                except ValueError:
                    errors.append(f"Line {i+1}: Invalid coordinates")
        
        if len(elements) == 0:
            errors.append("No valid atoms found")
            return ValidationResult(valid=False, errors=errors)
        
        # Check distances if we have coordinates
        if len(coordinates) == len(elements):
            dist_result = self._check_distances(elements, coordinates)
            errors.extend(dist_result.errors)
            warnings.extend(dist_result.warnings)
        
        # Check charge/multiplicity consistency
        n_electrons = self._count_electrons(elements) - charge
        if n_electrons < 0:
            errors.append(f"Invalid charge: would result in negative electrons")
        
        expected_mult_parity = (n_electrons % 2) + 1
        if (multiplicity - 1) % 2 != (n_electrons % 2):
            warnings.append(f"Multiplicity {multiplicity} may be inconsistent with {n_electrons} electrons")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _check_distances(self, elements: List[str], coords: List[Tuple[float, float, float]]) -> ValidationResult:
        """Check interatomic distances."""
        errors = []
        warnings = []
        n = len(elements)
        
        for i in range(n):
            for j in range(i + 1, n):
                dx = coords[i][0] - coords[j][0]
                dy = coords[i][1] - coords[j][1]
                dz = coords[i][2] - coords[j][2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < self.MIN_DISTANCE:
                    errors.append(f"Atoms {i+1} ({elements[i]}) and {j+1} ({elements[j]}) too close: {dist:.3f} Å")
                elif dist > self.MAX_DISTANCE:
                    warnings.append(f"Atoms {i+1} and {j+1} very far apart: {dist:.1f} Å")
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def _count_electrons(self, elements: List[str]) -> int:
        """Count total electrons."""
        atomic_numbers = {
            "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8,
            "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15,
            "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20,
        }
        return sum(atomic_numbers.get(e, 6) for e in elements)


def validate_geometry(geometry: str, charge: int = 0, multiplicity: int = 1) -> Tuple[bool, List[str]]:
    """Validate geometry string."""
    validator = GeometryValidator()
    result = validator.validate(geometry, charge, multiplicity)
    return result.valid, result.errors


def validate_coordinates(coords: List[Tuple[float, float, float]]) -> Tuple[bool, List[str]]:
    """Validate coordinate list."""
    errors = []
    for i, (x, y, z) in enumerate(coords):
        if not all(isinstance(v, (int, float)) for v in (x, y, z)):
            errors.append(f"Atom {i+1}: Invalid coordinate type")
        if any(abs(v) > 1000 for v in (x, y, z)):
            errors.append(f"Atom {i+1}: Coordinates too large")
    return len(errors) == 0, errors


def check_atom_distances(elements: List[str], coords: List[Tuple[float, float, float]]) -> List[Tuple[int, int, float]]:
    """Return list of atom pairs that are too close."""
    close_pairs = []
    n = len(elements)
    for i in range(n):
        for j in range(i + 1, n):
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            dz = coords[i][2] - coords[j][2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            if dist < 0.4:
                close_pairs.append((i, j, dist))
    return close_pairs


def check_linear_molecule(coords: List[Tuple[float, float, float]], threshold: float = 0.01) -> bool:
    """Check if molecule is linear."""
    if len(coords) <= 2:
        return True
    
    # Check if all atoms are collinear
    v1 = (coords[1][0] - coords[0][0], coords[1][1] - coords[0][1], coords[1][2] - coords[0][2])
    v1_mag = math.sqrt(sum(x*x for x in v1))
    if v1_mag < 1e-10:
        return True
    v1 = tuple(x / v1_mag for x in v1)
    
    for i in range(2, len(coords)):
        v2 = (coords[i][0] - coords[0][0], coords[i][1] - coords[0][1], coords[i][2] - coords[0][2])
        v2_mag = math.sqrt(sum(x*x for x in v2))
        if v2_mag < 1e-10:
            continue
        v2 = tuple(x / v2_mag for x in v2)
        
        # Cross product magnitude
        cross = (
            v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0],
        )
        cross_mag = math.sqrt(sum(x*x for x in cross))
        if cross_mag > threshold:
            return False
    
    return True
