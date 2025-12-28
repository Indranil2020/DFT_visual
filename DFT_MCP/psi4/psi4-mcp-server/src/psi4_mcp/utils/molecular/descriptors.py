"""
Molecular Descriptors for Psi4 MCP Server.

Calculates molecular descriptors from structure.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# Atomic properties
ATOMIC_MASSES = {"H": 1.008, "He": 4.003, "Li": 6.941, "Be": 9.012, "B": 10.81, "C": 12.01,
                 "N": 14.01, "O": 16.00, "F": 19.00, "Ne": 20.18, "Na": 22.99, "Mg": 24.31,
                 "Al": 26.98, "Si": 28.09, "P": 30.97, "S": 32.07, "Cl": 35.45, "Ar": 39.95}

COVALENT_RADII = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "S": 1.05, "P": 1.07, "Cl": 1.02}


@dataclass
class MolecularDescriptors:
    """Collection of molecular descriptors."""
    molecular_weight: float = 0.0
    n_atoms: int = 0
    n_heavy_atoms: int = 0
    n_electrons: int = 0
    formula: str = ""
    center_of_mass: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    principal_moments: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    radius_of_gyration: float = 0.0
    max_distance: float = 0.0
    surface_area_estimate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "molecular_weight": self.molecular_weight,
            "n_atoms": self.n_atoms,
            "n_heavy_atoms": self.n_heavy_atoms,
            "n_electrons": self.n_electrons,
            "formula": self.formula,
            "center_of_mass": self.center_of_mass,
            "radius_of_gyration": self.radius_of_gyration,
            "max_distance": self.max_distance,
        }


def calculate_descriptors(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
) -> MolecularDescriptors:
    """Calculate molecular descriptors from structure."""
    n_atoms = len(elements)
    if n_atoms == 0:
        return MolecularDescriptors()
    
    # Count elements and calculate mass
    element_counts: Dict[str, int] = {}
    total_mass = 0.0
    n_electrons = 0
    n_heavy = 0
    
    atomic_numbers = {"H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8,
                     "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15,
                     "S": 16, "Cl": 17, "Ar": 18}
    
    for elem in elements:
        element_counts[elem] = element_counts.get(elem, 0) + 1
        total_mass += ATOMIC_MASSES.get(elem, 12.0)
        n_electrons += atomic_numbers.get(elem, 6)
        if elem != "H":
            n_heavy += 1
    
    # Build formula
    formula_parts = []
    for elem in ["C", "H", "N", "O", "F", "S", "P", "Cl"]:
        if elem in element_counts:
            count = element_counts[elem]
            formula_parts.append(f"{elem}{count}" if count > 1 else elem)
    for elem, count in sorted(element_counts.items()):
        if elem not in ["C", "H", "N", "O", "F", "S", "P", "Cl"]:
            formula_parts.append(f"{elem}{count}" if count > 1 else elem)
    formula = "".join(formula_parts)
    
    # Center of mass
    cx, cy, cz = 0.0, 0.0, 0.0
    for elem, (x, y, z) in zip(elements, coordinates):
        mass = ATOMIC_MASSES.get(elem, 12.0)
        cx += mass * x
        cy += mass * y
        cz += mass * z
    if total_mass > 0:
        cx, cy, cz = cx/total_mass, cy/total_mass, cz/total_mass
    
    # Radius of gyration
    rg_sum = 0.0
    for elem, (x, y, z) in zip(elements, coordinates):
        mass = ATOMIC_MASSES.get(elem, 12.0)
        rg_sum += mass * ((x-cx)**2 + (y-cy)**2 + (z-cz)**2)
    radius_of_gyration = math.sqrt(rg_sum / total_mass) if total_mass > 0 else 0.0
    
    # Maximum interatomic distance
    max_dist = 0.0
    for i in range(n_atoms):
        for j in range(i + 1, n_atoms):
            dx = coordinates[i][0] - coordinates[j][0]
            dy = coordinates[i][1] - coordinates[j][1]
            dz = coordinates[i][2] - coordinates[j][2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            max_dist = max(max_dist, dist)
    
    # Simple surface area estimate (sum of atomic spheres)
    surface_area = sum(4 * math.pi * COVALENT_RADII.get(e, 1.5)**2 for e in elements)
    
    return MolecularDescriptors(
        molecular_weight=total_mass,
        n_atoms=n_atoms,
        n_heavy_atoms=n_heavy,
        n_electrons=n_electrons,
        formula=formula,
        center_of_mass=(cx, cy, cz),
        radius_of_gyration=radius_of_gyration,
        max_distance=max_dist,
        surface_area_estimate=surface_area,
    )
