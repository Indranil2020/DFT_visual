"""
Molecular Visualization for Psi4 MCP Server.

Generates visualization data for molecular structures.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Element colors (CPK coloring scheme)
ELEMENT_COLORS = {
    "H": "#FFFFFF", "He": "#D9FFFF", "Li": "#CC80FF", "Be": "#C2FF00",
    "B": "#FFB5B5", "C": "#909090", "N": "#3050F8", "O": "#FF0D0D",
    "F": "#90E050", "Ne": "#B3E3F5", "Na": "#AB5CF2", "Mg": "#8AFF00",
    "Al": "#BFA6A6", "Si": "#F0C8A0", "P": "#FF8000", "S": "#FFFF30",
    "Cl": "#1FF01F", "Ar": "#80D1E3", "K": "#8F40D4", "Ca": "#3DFF00",
    "Fe": "#E06633", "Cu": "#C88033", "Zn": "#7D80B0", "Br": "#A62929",
    "I": "#940094",
}

# Element radii for visualization (Angstrom)
ELEMENT_RADII = {
    "H": 0.31, "He": 0.28, "Li": 1.28, "Be": 0.96, "B": 0.84, "C": 0.76,
    "N": 0.71, "O": 0.66, "F": 0.57, "Ne": 0.58, "Na": 1.66, "Mg": 1.41,
    "Al": 1.21, "Si": 1.11, "P": 1.07, "S": 1.05, "Cl": 1.02, "Ar": 1.06,
}


@dataclass
class AtomData:
    """Atom visualization data."""
    index: int
    element: str
    x: float
    y: float
    z: float
    color: str
    radius: float
    label: str = ""


@dataclass
class BondData:
    """Bond visualization data."""
    atom1: int
    atom2: int
    order: int = 1
    color: str = "#808080"


@dataclass
class MoleculeVisualization:
    """Complete molecule visualization data."""
    atoms: List[AtomData]
    bonds: List[BondData]
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    bounding_box: Tuple[float, float, float, float, float, float] = (0, 0, 0, 0, 0, 0)


class MoleculeVisualizer:
    """Generates molecule visualization data."""
    
    BOND_DISTANCE_FACTOR = 1.3
    
    def __init__(self):
        self.colors = ELEMENT_COLORS
        self.radii = ELEMENT_RADII
    
    def generate(
        self,
        elements: List[str],
        coordinates: List[Tuple[float, float, float]],
        bonds: Optional[List[Tuple[int, int]]] = None,
    ) -> MoleculeVisualization:
        """Generate visualization data for molecule."""
        n_atoms = len(elements)
        
        # Generate atom data
        atoms = []
        for i, (elem, (x, y, z)) in enumerate(zip(elements, coordinates)):
            atom = AtomData(
                index=i,
                element=elem,
                x=x, y=y, z=z,
                color=self.colors.get(elem, "#808080"),
                radius=self.radii.get(elem, 1.0) * 0.5,
                label=f"{elem}{i+1}",
            )
            atoms.append(atom)
        
        # Generate bonds if not provided
        if bonds is None:
            bonds = self._detect_bonds(elements, coordinates)
        
        bond_data = []
        for a1, a2 in bonds:
            bond = BondData(atom1=a1, atom2=a2, order=1)
            bond_data.append(bond)
        
        # Calculate center and bounding box
        if coordinates:
            xs = [c[0] for c in coordinates]
            ys = [c[1] for c in coordinates]
            zs = [c[2] for c in coordinates]
            center = (sum(xs)/n_atoms, sum(ys)/n_atoms, sum(zs)/n_atoms)
            bbox = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
        else:
            center = (0.0, 0.0, 0.0)
            bbox = (0, 0, 0, 0, 0, 0)
        
        return MoleculeVisualization(
            atoms=atoms,
            bonds=bond_data,
            center=center,
            bounding_box=bbox,
        )
    
    def _detect_bonds(
        self,
        elements: List[str],
        coordinates: List[Tuple[float, float, float]],
    ) -> List[Tuple[int, int]]:
        """Detect bonds based on distances."""
        bonds = []
        n = len(elements)
        
        for i in range(n):
            ri = self.radii.get(elements[i], 1.5)
            for j in range(i + 1, n):
                rj = self.radii.get(elements[j], 1.5)
                
                dx = coordinates[i][0] - coordinates[j][0]
                dy = coordinates[i][1] - coordinates[j][1]
                dz = coordinates[i][2] - coordinates[j][2]
                dist = (dx*dx + dy*dy + dz*dz) ** 0.5
                
                max_bond = (ri + rj) * self.BOND_DISTANCE_FACTOR
                if dist < max_bond:
                    bonds.append((i, j))
        
        return bonds
    
    def to_xyz_string(
        self,
        elements: List[str],
        coordinates: List[Tuple[float, float, float]],
        title: str = "",
    ) -> str:
        """Generate XYZ format string."""
        lines = [str(len(elements)), title]
        for elem, (x, y, z) in zip(elements, coordinates):
            lines.append(f"{elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        return "\n".join(lines)
    
    def to_json(self, vis: MoleculeVisualization) -> Dict[str, Any]:
        """Convert visualization to JSON-serializable dict."""
        return {
            "atoms": [
                {"index": a.index, "element": a.element, "x": a.x, "y": a.y, "z": a.z,
                 "color": a.color, "radius": a.radius, "label": a.label}
                for a in vis.atoms
            ],
            "bonds": [
                {"atom1": b.atom1, "atom2": b.atom2, "order": b.order}
                for b in vis.bonds
            ],
            "center": vis.center,
            "bounding_box": vis.bounding_box,
        }


def generate_xyz_viewer_data(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
) -> Dict[str, Any]:
    """Generate data for XYZ viewer."""
    visualizer = MoleculeVisualizer()
    vis = visualizer.generate(elements, coordinates)
    return visualizer.to_json(vis)
