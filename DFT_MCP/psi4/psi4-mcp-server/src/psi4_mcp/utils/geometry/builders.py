"""
Geometry Building Utilities for Psi4 MCP Server.

Provides tools for building molecular geometries.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ZMatrixEntry:
    """Entry in a Z-matrix."""
    element: str
    ref1: Optional[int] = None  # Bond to this atom
    distance: Optional[float] = None
    ref2: Optional[int] = None  # Angle reference
    angle: Optional[float] = None
    ref3: Optional[int] = None  # Dihedral reference
    dihedral: Optional[float] = None


class GeometryBuilder:
    """
    Builder for molecular geometries.
    
    Provides methods to construct geometries from various
    specifications.
    """
    
    def __init__(self):
        """Initialize geometry builder."""
        self.elements: List[str] = []
        self.coordinates: List[Tuple[float, float, float]] = []
    
    def add_atom(
        self,
        element: str,
        x: float,
        y: float,
        z: float,
    ) -> int:
        """
        Add atom with Cartesian coordinates.
        
        Args:
            element: Element symbol
            x, y, z: Cartesian coordinates
            
        Returns:
            Index of added atom
        """
        self.elements.append(element)
        self.coordinates.append((x, y, z))
        return len(self.elements) - 1
    
    def add_atom_zmatrix(
        self,
        element: str,
        ref1: Optional[int] = None,
        distance: Optional[float] = None,
        ref2: Optional[int] = None,
        angle: Optional[float] = None,
        ref3: Optional[int] = None,
        dihedral: Optional[float] = None,
    ) -> int:
        """
        Add atom using Z-matrix style specification.
        
        Args:
            element: Element symbol
            ref1: Atom index for distance reference
            distance: Distance to ref1 in Angstroms
            ref2: Atom index for angle reference
            angle: Angle in degrees
            ref3: Atom index for dihedral reference
            dihedral: Dihedral angle in degrees
            
        Returns:
            Index of added atom
        """
        n = len(self.elements)
        
        if n == 0:
            # First atom at origin
            self.elements.append(element)
            self.coordinates.append((0.0, 0.0, 0.0))
            return 0
        
        if n == 1:
            # Second atom along x-axis
            if distance is None:
                distance = 1.5  # Default bond length
            self.elements.append(element)
            self.coordinates.append((distance, 0.0, 0.0))
            return 1
        
        if n == 2:
            # Third atom in xy-plane
            if ref1 is None:
                ref1 = 1
            if distance is None:
                distance = 1.5
            if ref2 is None:
                ref2 = 0
            if angle is None:
                angle = 109.5
            
            coords = self._compute_third_atom(ref1, distance, ref2, angle)
            self.elements.append(element)
            self.coordinates.append(coords)
            return 2
        
        # General case (4+ atoms)
        if ref1 is None or distance is None or ref2 is None or angle is None:
            raise ValueError("Must specify ref1, distance, ref2, angle for 4+ atoms")
        if ref3 is None:
            ref3 = 0
        if dihedral is None:
            dihedral = 0.0
        
        coords = self._compute_coords_from_zmatrix(
            ref1, distance, ref2, angle, ref3, dihedral
        )
        self.elements.append(element)
        self.coordinates.append(coords)
        return n
    
    def _compute_third_atom(
        self,
        ref1: int,
        distance: float,
        ref2: int,
        angle: float,
    ) -> Tuple[float, float, float]:
        """Compute coordinates for third atom (in xy-plane)."""
        c1 = self.coordinates[ref1]
        c2 = self.coordinates[ref2]
        
        # Vector from ref1 to ref2
        v = (c2[0] - c1[0], c2[1] - c1[1], c2[2] - c1[2])
        v_len = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
        
        if v_len < 1e-10:
            v = (1.0, 0.0, 0.0)
            v_len = 1.0
        
        # Normalize
        v = (v[0]/v_len, v[1]/v_len, v[2]/v_len)
        
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Build perpendicular vector in xy-plane
        if abs(v[2]) < 0.999:
            perp = (0.0, 0.0, 1.0)
        else:
            perp = (1.0, 0.0, 0.0)
        
        # Cross product to get perpendicular
        perp = (
            v[1]*perp[2] - v[2]*perp[1],
            v[2]*perp[0] - v[0]*perp[2],
            v[0]*perp[1] - v[1]*perp[0],
        )
        p_len = math.sqrt(perp[0]**2 + perp[1]**2 + perp[2]**2)
        if p_len > 1e-10:
            perp = (perp[0]/p_len, perp[1]/p_len, perp[2]/p_len)
        
        # New position
        x = c1[0] + distance * (math.cos(angle_rad) * (-v[0]) + math.sin(angle_rad) * perp[0])
        y = c1[1] + distance * (math.cos(angle_rad) * (-v[1]) + math.sin(angle_rad) * perp[1])
        z = c1[2] + distance * (math.cos(angle_rad) * (-v[2]) + math.sin(angle_rad) * perp[2])
        
        return (x, y, z)
    
    def _compute_coords_from_zmatrix(
        self,
        ref1: int,
        distance: float,
        ref2: int,
        angle: float,
        ref3: int,
        dihedral: float,
    ) -> Tuple[float, float, float]:
        """Compute coordinates from Z-matrix parameters."""
        # Get reference coordinates
        c1 = self.coordinates[ref1]
        c2 = self.coordinates[ref2]
        c3 = self.coordinates[ref3]
        
        # Convert angles to radians
        angle_rad = math.radians(180.0 - angle)  # Supplement for internal angle
        dihedral_rad = math.radians(dihedral)
        
        # Build local coordinate system
        # v1: ref2 -> ref1
        v1 = (c1[0] - c2[0], c1[1] - c2[1], c1[2] - c2[2])
        v1_len = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        if v1_len < 1e-10:
            v1 = (1.0, 0.0, 0.0)
            v1_len = 1.0
        v1 = (v1[0]/v1_len, v1[1]/v1_len, v1[2]/v1_len)
        
        # v2: ref3 -> ref2
        v2 = (c2[0] - c3[0], c2[1] - c3[1], c2[2] - c3[2])
        v2_len = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        if v2_len < 1e-10:
            v2 = (0.0, 1.0, 0.0)
            v2_len = 1.0
        v2 = (v2[0]/v2_len, v2[1]/v2_len, v2[2]/v2_len)
        
        # n: normal to plane (v1 x v2)
        n = (
            v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0],
        )
        n_len = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
        if n_len < 1e-10:
            n = (0.0, 0.0, 1.0)
        else:
            n = (n[0]/n_len, n[1]/n_len, n[2]/n_len)
        
        # m: perpendicular in plane (n x v1)
        m = (
            n[1]*v1[2] - n[2]*v1[1],
            n[2]*v1[0] - n[0]*v1[2],
            n[0]*v1[1] - n[1]*v1[0],
        )
        
        # Position relative to ref1
        dx = distance * math.cos(angle_rad)
        dy = distance * math.sin(angle_rad) * math.cos(dihedral_rad)
        dz = distance * math.sin(angle_rad) * math.sin(dihedral_rad)
        
        # Transform to global coordinates
        x = c1[0] + dx * v1[0] + dy * m[0] + dz * n[0]
        y = c1[1] + dx * v1[1] + dy * m[1] + dz * n[1]
        z = c1[2] + dx * v1[2] + dy * m[2] + dz * n[2]
        
        return (x, y, z)
    
    def get_geometry(self) -> Tuple[List[str], List[Tuple[float, float, float]]]:
        """
        Get current geometry.
        
        Returns:
            Tuple of (elements, coordinates)
        """
        return list(self.elements), list(self.coordinates)
    
    def to_xyz_string(self) -> str:
        """
        Convert to XYZ format string.
        
        Returns:
            XYZ format string
        """
        lines = [str(len(self.elements)), ""]
        
        for elem, (x, y, z) in zip(self.elements, self.coordinates):
            lines.append(f"{elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        
        return "\n".join(lines)
    
    def to_psi4_string(self, charge: int = 0, multiplicity: int = 1) -> str:
        """
        Convert to Psi4 geometry string.
        
        Args:
            charge: Molecular charge
            multiplicity: Spin multiplicity
            
        Returns:
            Psi4 format string
        """
        lines = [f"{charge} {multiplicity}"]
        
        for elem, (x, y, z) in zip(self.elements, self.coordinates):
            lines.append(f"{elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        
        return "\n".join(lines)
    
    def clear(self) -> None:
        """Clear the builder."""
        self.elements.clear()
        self.coordinates.clear()


def build_from_zmatrix(zmatrix: List[ZMatrixEntry]) -> GeometryBuilder:
    """
    Build geometry from Z-matrix entries.
    
    Args:
        zmatrix: List of Z-matrix entries
        
    Returns:
        GeometryBuilder with constructed geometry
    """
    builder = GeometryBuilder()
    
    for entry in zmatrix:
        builder.add_atom_zmatrix(
            element=entry.element,
            ref1=entry.ref1,
            distance=entry.distance,
            ref2=entry.ref2,
            angle=entry.angle,
            ref3=entry.ref3,
            dihedral=entry.dihedral,
        )
    
    return builder


def build_molecule_from_smiles(smiles: str) -> Optional[GeometryBuilder]:
    """
    Build geometry from SMILES string.
    
    Note: This is a placeholder. Full implementation would require
    RDKit or similar library.
    
    Args:
        smiles: SMILES string
        
    Returns:
        GeometryBuilder or None if not available
    """
    # Simple molecules only
    simple_molecules: Dict[str, List[Tuple[str, float, float, float]]] = {
        "O": [("O", 0.0, 0.0, 0.0), ("H", 0.96, 0.0, 0.0), 
              ("H", -0.24, 0.93, 0.0)],  # Water
        "C": [("C", 0.0, 0.0, 0.0)],  # Methane would need Hs
        "[He]": [("He", 0.0, 0.0, 0.0)],
        "[Ne]": [("Ne", 0.0, 0.0, 0.0)],
        "[Ar]": [("Ar", 0.0, 0.0, 0.0)],
    }
    
    if smiles in simple_molecules:
        builder = GeometryBuilder()
        for elem, x, y, z in simple_molecules[smiles]:
            builder.add_atom(elem, x, y, z)
        return builder
    
    return None


def add_hydrogens(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
) -> Tuple[List[str], List[Tuple[float, float, float]]]:
    """
    Add missing hydrogens to a structure.
    
    Note: Simplified implementation. Full version would use
    valence rules and geometry optimization.
    
    Args:
        elements: Current elements
        coordinates: Current coordinates
        
    Returns:
        Tuple of (new_elements, new_coordinates)
    """
    # Standard valences
    valences = {"C": 4, "N": 3, "O": 2, "S": 2, "P": 3}
    
    from psi4_mcp.utils.geometry.analysis import GeometryAnalyzer
    
    analyzer = GeometryAnalyzer(elements, coordinates)
    connectivity = analyzer.get_connectivity()
    
    new_elements = list(elements)
    new_coords = list(coordinates)
    
    for i, elem in enumerate(elements):
        if elem not in valences:
            continue
        
        expected_bonds = valences[elem]
        current_bonds = len(connectivity[i])
        missing_h = expected_bonds - current_bonds
        
        if missing_h <= 0:
            continue
        
        # Add hydrogens (simplified placement)
        base_coord = coordinates[i]
        
        for j in range(missing_h):
            # Simple radial placement
            angle = 2 * math.pi * j / missing_h
            h_x = base_coord[0] + 1.09 * math.cos(angle)
            h_y = base_coord[1] + 1.09 * math.sin(angle)
            h_z = base_coord[2]
            
            new_elements.append("H")
            new_coords.append((h_x, h_y, h_z))
    
    return new_elements, new_coords


def generate_conformer(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    rotatable_bonds: List[Tuple[int, int]],
    angles: List[float],
) -> List[Tuple[float, float, float]]:
    """
    Generate conformer by rotating around specified bonds.
    
    Args:
        elements: Element symbols
        coordinates: Initial coordinates
        rotatable_bonds: List of (atom1, atom2) defining rotation axes
        angles: Rotation angles in degrees
        
    Returns:
        New coordinates
    """
    from psi4_mcp.utils.geometry.transformations import rotate_around_axis
    
    coords = list(coordinates)
    
    for (a1, a2), angle in zip(rotatable_bonds, angles):
        # Get atoms to rotate (all atoms bonded to a2 that aren't a1)
        from psi4_mcp.utils.geometry.analysis import GeometryAnalyzer
        analyzer = GeometryAnalyzer(elements, coords)
        connectivity = analyzer.get_connectivity()
        
        # Find atoms to rotate (simple BFS from a2 excluding a1)
        to_rotate = set()
        queue = [i for i in connectivity[a2] if i != a1]
        visited = {a1, a2}
        
        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)
            to_rotate.add(curr)
            queue.extend(connectivity[curr])
        
        if to_rotate:
            # Rotation axis
            axis = (
                coords[a2][0] - coords[a1][0],
                coords[a2][1] - coords[a1][1],
                coords[a2][2] - coords[a1][2],
            )
            
            # Rotate selected atoms
            new_coords = rotate_around_axis(
                [coords[i] for i in sorted(to_rotate)],
                axis,
                coords[a1],
                angle,
            )
            
            for i, idx in enumerate(sorted(to_rotate)):
                coords[idx] = new_coords[i]
    
    return coords


# Common molecule templates
MOLECULE_TEMPLATES: Dict[str, Tuple[List[str], List[Tuple[float, float, float]]]] = {
    "water": (
        ["O", "H", "H"],
        [(0.0, 0.0, 0.117), (-0.757, 0.0, -0.470), (0.757, 0.0, -0.470)]
    ),
    "methane": (
        ["C", "H", "H", "H", "H"],
        [(0.0, 0.0, 0.0), (0.629, 0.629, 0.629), (-0.629, -0.629, 0.629),
         (-0.629, 0.629, -0.629), (0.629, -0.629, -0.629)]
    ),
    "ammonia": (
        ["N", "H", "H", "H"],
        [(0.0, 0.0, 0.116), (0.0, 0.939, -0.272),
         (0.813, -0.470, -0.272), (-0.813, -0.470, -0.272)]
    ),
    "carbon_dioxide": (
        ["C", "O", "O"],
        [(0.0, 0.0, 0.0), (1.16, 0.0, 0.0), (-1.16, 0.0, 0.0)]
    ),
}


def get_template_molecule(name: str) -> Optional[GeometryBuilder]:
    """
    Get a template molecule by name.
    
    Args:
        name: Molecule name (water, methane, etc.)
        
    Returns:
        GeometryBuilder or None
    """
    template = MOLECULE_TEMPLATES.get(name.lower())
    if template is None:
        return None
    
    elements, coords = template
    builder = GeometryBuilder()
    for elem, (x, y, z) in zip(elements, coords):
        builder.add_atom(elem, x, y, z)
    
    return builder
