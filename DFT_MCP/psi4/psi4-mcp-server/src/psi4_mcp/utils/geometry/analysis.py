"""
Geometry Analysis Utilities for Psi4 MCP Server.

Provides tools for analyzing molecular geometries.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

# Covalent radii in Angstroms (approximate)
COVALENT_RADII: Dict[str, float] = {
    "H": 0.31, "He": 0.28,
    "Li": 1.28, "Be": 0.96, "B": 0.84, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "Ne": 0.58,
    "Na": 1.66, "Mg": 1.41, "Al": 1.21, "Si": 1.11, "P": 1.07, "S": 1.05, "Cl": 1.02, "Ar": 1.06,
    "K": 2.03, "Ca": 1.76, "Sc": 1.70, "Ti": 1.60, "V": 1.53, "Cr": 1.39, "Mn": 1.39,
    "Fe": 1.32, "Co": 1.26, "Ni": 1.24, "Cu": 1.32, "Zn": 1.22, "Ga": 1.22, "Ge": 1.20,
    "As": 1.19, "Se": 1.20, "Br": 1.20, "Kr": 1.16,
    "Rb": 2.20, "Sr": 1.95, "Y": 1.90, "Zr": 1.75, "Nb": 1.64, "Mo": 1.54, "Tc": 1.47,
    "Ru": 1.46, "Rh": 1.42, "Pd": 1.39, "Ag": 1.45, "Cd": 1.44, "In": 1.42, "Sn": 1.39,
    "Sb": 1.39, "Te": 1.38, "I": 1.39, "Xe": 1.40,
}


@dataclass
class Bond:
    """Represents a chemical bond."""
    atom1_idx: int
    atom2_idx: int
    distance: float
    bond_order: int = 1
    
    @property
    def indices(self) -> Tuple[int, int]:
        """Get bond indices as tuple."""
        return (self.atom1_idx, self.atom2_idx)


@dataclass
class Angle:
    """Represents a bond angle."""
    atom1_idx: int
    atom2_idx: int  # Central atom
    atom3_idx: int
    angle_degrees: float
    
    @property
    def indices(self) -> Tuple[int, int, int]:
        """Get angle indices as tuple."""
        return (self.atom1_idx, self.atom2_idx, self.atom3_idx)


@dataclass
class Dihedral:
    """Represents a dihedral angle."""
    atom1_idx: int
    atom2_idx: int
    atom3_idx: int
    atom4_idx: int
    angle_degrees: float
    
    @property
    def indices(self) -> Tuple[int, int, int, int]:
        """Get dihedral indices as tuple."""
        return (self.atom1_idx, self.atom2_idx, self.atom3_idx, self.atom4_idx)


class GeometryAnalyzer:
    """
    Analyzer for molecular geometries.
    
    Provides methods for calculating distances, angles, and
    other geometric properties.
    """
    
    def __init__(
        self,
        elements: List[str],
        coordinates: List[Tuple[float, float, float]],
        bond_tolerance: float = 1.3,
    ):
        """
        Initialize geometry analyzer.
        
        Args:
            elements: List of element symbols
            coordinates: List of (x, y, z) coordinates in Angstroms
            bond_tolerance: Multiplier for covalent radii in bond detection
        """
        if len(elements) != len(coordinates):
            raise ValueError("Elements and coordinates must have same length")
        
        self.elements = list(elements)
        self.coordinates = [tuple(c) for c in coordinates]
        self.bond_tolerance = bond_tolerance
        self.n_atoms = len(elements)
        
        self._bonds: Optional[List[Bond]] = None
        self._connectivity: Optional[Dict[int, Set[int]]] = None
    
    def calculate_distance(self, idx1: int, idx2: int) -> float:
        """
        Calculate distance between two atoms.
        
        Args:
            idx1: First atom index
            idx2: Second atom index
            
        Returns:
            Distance in Angstroms
        """
        if idx1 < 0 or idx1 >= self.n_atoms:
            raise IndexError(f"Atom index {idx1} out of range")
        if idx2 < 0 or idx2 >= self.n_atoms:
            raise IndexError(f"Atom index {idx2} out of range")
        
        c1 = self.coordinates[idx1]
        c2 = self.coordinates[idx2]
        
        return math.sqrt(
            (c2[0] - c1[0])**2 +
            (c2[1] - c1[1])**2 +
            (c2[2] - c1[2])**2
        )
    
    def calculate_angle(self, idx1: int, idx2: int, idx3: int) -> float:
        """
        Calculate angle between three atoms.
        
        Args:
            idx1: First atom index
            idx2: Central atom index
            idx3: Third atom index
            
        Returns:
            Angle in degrees
        """
        # Vectors from central atom
        c1 = self.coordinates[idx1]
        c2 = self.coordinates[idx2]
        c3 = self.coordinates[idx3]
        
        v1 = (c1[0] - c2[0], c1[1] - c2[1], c1[2] - c2[2])
        v2 = (c3[0] - c2[0], c3[1] - c2[1], c3[2] - c2[2])
        
        # Dot product and magnitudes
        dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        
        if mag1 < 1e-10 or mag2 < 1e-10:
            return 0.0
        
        cos_angle = dot / (mag1 * mag2)
        # Clamp to [-1, 1] to handle numerical errors
        cos_angle = max(-1.0, min(1.0, cos_angle))
        
        return math.degrees(math.acos(cos_angle))
    
    def calculate_dihedral(
        self,
        idx1: int,
        idx2: int,
        idx3: int,
        idx4: int,
    ) -> float:
        """
        Calculate dihedral angle between four atoms.
        
        Args:
            idx1: First atom index
            idx2: Second atom index
            idx3: Third atom index
            idx4: Fourth atom index
            
        Returns:
            Dihedral angle in degrees (-180 to 180)
        """
        c1 = self.coordinates[idx1]
        c2 = self.coordinates[idx2]
        c3 = self.coordinates[idx3]
        c4 = self.coordinates[idx4]
        
        # Vectors
        b1 = (c2[0] - c1[0], c2[1] - c1[1], c2[2] - c1[2])
        b2 = (c3[0] - c2[0], c3[1] - c2[1], c3[2] - c2[2])
        b3 = (c4[0] - c3[0], c4[1] - c3[1], c4[2] - c3[2])
        
        # Normal vectors
        n1 = self._cross(b1, b2)
        n2 = self._cross(b2, b3)
        
        # Normalize b2
        b2_norm = math.sqrt(b2[0]**2 + b2[1]**2 + b2[2]**2)
        if b2_norm < 1e-10:
            return 0.0
        
        b2_unit = (b2[0]/b2_norm, b2[1]/b2_norm, b2[2]/b2_norm)
        
        m1 = self._cross(n1, b2_unit)
        
        x = self._dot(n1, n2)
        y = self._dot(m1, n2)
        
        return math.degrees(math.atan2(y, x))
    
    def _cross(
        self,
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> Tuple[float, float, float]:
        """Cross product of two vectors."""
        return (
            v1[1]*v2[2] - v1[2]*v2[1],
            v1[2]*v2[0] - v1[0]*v2[2],
            v1[0]*v2[1] - v1[1]*v2[0],
        )
    
    def _dot(
        self,
        v1: Tuple[float, float, float],
        v2: Tuple[float, float, float],
    ) -> float:
        """Dot product of two vectors."""
        return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
    
    def find_bonds(self) -> List[Bond]:
        """
        Find all bonds in the molecule.
        
        Returns:
            List of Bond objects
        """
        if self._bonds is not None:
            return self._bonds
        
        bonds = []
        
        for i in range(self.n_atoms):
            elem_i = self.elements[i]
            r_i = COVALENT_RADII.get(elem_i, 1.5)
            
            for j in range(i + 1, self.n_atoms):
                elem_j = self.elements[j]
                r_j = COVALENT_RADII.get(elem_j, 1.5)
                
                # Bond threshold
                threshold = (r_i + r_j) * self.bond_tolerance
                
                distance = self.calculate_distance(i, j)
                
                if distance < threshold:
                    bonds.append(Bond(
                        atom1_idx=i,
                        atom2_idx=j,
                        distance=distance,
                    ))
        
        self._bonds = bonds
        return bonds
    
    def get_connectivity(self) -> Dict[int, Set[int]]:
        """
        Get connectivity map.
        
        Returns:
            Dictionary mapping atom index to set of bonded indices
        """
        if self._connectivity is not None:
            return self._connectivity
        
        connectivity: Dict[int, Set[int]] = {i: set() for i in range(self.n_atoms)}
        
        for bond in self.find_bonds():
            connectivity[bond.atom1_idx].add(bond.atom2_idx)
            connectivity[bond.atom2_idx].add(bond.atom1_idx)
        
        self._connectivity = connectivity
        return connectivity
    
    def find_angles(self) -> List[Angle]:
        """
        Find all bond angles.
        
        Returns:
            List of Angle objects
        """
        connectivity = self.get_connectivity()
        angles = []
        
        for central in range(self.n_atoms):
            neighbors = list(connectivity[central])
            
            for i, n1 in enumerate(neighbors):
                for n2 in neighbors[i + 1:]:
                    angle = self.calculate_angle(n1, central, n2)
                    angles.append(Angle(
                        atom1_idx=n1,
                        atom2_idx=central,
                        atom3_idx=n2,
                        angle_degrees=angle,
                    ))
        
        return angles
    
    def find_dihedrals(self) -> List[Dihedral]:
        """
        Find all dihedral angles.
        
        Returns:
            List of Dihedral objects
        """
        bonds = self.find_bonds()
        connectivity = self.get_connectivity()
        dihedrals = []
        seen: Set[Tuple[int, int, int, int]] = set()
        
        for bond in bonds:
            i, j = bond.atom1_idx, bond.atom2_idx
            
            for k in connectivity[i]:
                if k == j:
                    continue
                
                for l in connectivity[j]:
                    if l == i or l == k:
                        continue
                    
                    # Create canonical ordering
                    if k > l:
                        key = (l, j, i, k)
                    else:
                        key = (k, i, j, l)
                    
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    angle = self.calculate_dihedral(k, i, j, l)
                    dihedrals.append(Dihedral(
                        atom1_idx=k,
                        atom2_idx=i,
                        atom3_idx=j,
                        atom4_idx=l,
                        angle_degrees=angle,
                    ))
        
        return dihedrals
    
    def get_center_of_mass(self) -> Tuple[float, float, float]:
        """
        Calculate center of mass.
        
        Returns:
            (x, y, z) coordinates of center of mass
        """
        # Atomic masses
        masses = {
            "H": 1.008, "He": 4.003, "Li": 6.941, "Be": 9.012, "B": 10.81,
            "C": 12.01, "N": 14.01, "O": 16.00, "F": 19.00, "Ne": 20.18,
            "Na": 22.99, "Mg": 24.31, "Al": 26.98, "Si": 28.09, "P": 30.97,
            "S": 32.07, "Cl": 35.45, "Ar": 39.95, "K": 39.10, "Ca": 40.08,
        }
        
        total_mass = 0.0
        cx, cy, cz = 0.0, 0.0, 0.0
        
        for i, elem in enumerate(self.elements):
            mass = masses.get(elem, 12.0)  # Default to carbon mass
            total_mass += mass
            cx += mass * self.coordinates[i][0]
            cy += mass * self.coordinates[i][1]
            cz += mass * self.coordinates[i][2]
        
        if total_mass > 0:
            return (cx / total_mass, cy / total_mass, cz / total_mass)
        return (0.0, 0.0, 0.0)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get geometry summary."""
        bonds = self.find_bonds()
        angles = self.find_angles()
        
        return {
            "n_atoms": self.n_atoms,
            "n_bonds": len(bonds),
            "n_angles": len(angles),
            "elements": dict(zip(*[(e, self.elements.count(e)) 
                                   for e in set(self.elements)])),
            "center_of_mass": self.get_center_of_mass(),
            "bond_lengths_range": (
                min(b.distance for b in bonds) if bonds else 0.0,
                max(b.distance for b in bonds) if bonds else 0.0,
            ),
        }


# Convenience functions

def calculate_distance(
    coord1: Tuple[float, float, float],
    coord2: Tuple[float, float, float],
) -> float:
    """
    Calculate distance between two points.
    
    Args:
        coord1: First coordinate (x, y, z)
        coord2: Second coordinate (x, y, z)
        
    Returns:
        Distance
    """
    return math.sqrt(
        (coord2[0] - coord1[0])**2 +
        (coord2[1] - coord1[1])**2 +
        (coord2[2] - coord1[2])**2
    )


def calculate_angle(
    coord1: Tuple[float, float, float],
    coord2: Tuple[float, float, float],
    coord3: Tuple[float, float, float],
) -> float:
    """
    Calculate angle at coord2.
    
    Args:
        coord1: First coordinate
        coord2: Central coordinate
        coord3: Third coordinate
        
    Returns:
        Angle in degrees
    """
    analyzer = GeometryAnalyzer(["X", "X", "X"], [coord1, coord2, coord3])
    return analyzer.calculate_angle(0, 1, 2)


def calculate_dihedral(
    coord1: Tuple[float, float, float],
    coord2: Tuple[float, float, float],
    coord3: Tuple[float, float, float],
    coord4: Tuple[float, float, float],
) -> float:
    """
    Calculate dihedral angle.
    
    Args:
        coord1-4: Coordinates
        
    Returns:
        Dihedral angle in degrees
    """
    analyzer = GeometryAnalyzer(
        ["X", "X", "X", "X"],
        [coord1, coord2, coord3, coord4]
    )
    return analyzer.calculate_dihedral(0, 1, 2, 3)


def find_bonds(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    tolerance: float = 1.3,
) -> List[Bond]:
    """
    Find bonds in a geometry.
    
    Args:
        elements: Element symbols
        coordinates: Coordinates
        tolerance: Bond detection tolerance
        
    Returns:
        List of bonds
    """
    analyzer = GeometryAnalyzer(elements, coordinates, tolerance)
    return analyzer.find_bonds()


def find_angles(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
) -> List[Angle]:
    """Find all angles in a geometry."""
    analyzer = GeometryAnalyzer(elements, coordinates)
    return analyzer.find_angles()


def find_dihedrals(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
) -> List[Dihedral]:
    """Find all dihedrals in a geometry."""
    analyzer = GeometryAnalyzer(elements, coordinates)
    return analyzer.find_dihedrals()


def get_connectivity(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
) -> Dict[int, Set[int]]:
    """Get connectivity map for a geometry."""
    analyzer = GeometryAnalyzer(elements, coordinates)
    return analyzer.get_connectivity()
