"""
Molecular Fingerprints for Psi4 MCP Server.

Generates fingerprints for molecular comparison.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple


@dataclass
class MolecularFingerprint:
    """Fingerprint representation of a molecule."""
    bits: Set[int] = field(default_factory=set)
    n_bits: int = 1024
    
    def to_binary_string(self) -> str:
        return "".join("1" if i in self.bits else "0" for i in range(self.n_bits))
    
    def to_list(self) -> List[int]:
        return sorted(self.bits)
    
    def count_bits(self) -> int:
        return len(self.bits)
    
    def density(self) -> float:
        return len(self.bits) / self.n_bits if self.n_bits > 0 else 0.0


def calculate_fingerprint(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    n_bits: int = 1024,
    radius: float = 2.0,
) -> MolecularFingerprint:
    """
    Calculate structural fingerprint from geometry.
    
    Uses atom-centered environments within given radius.
    """
    bits: Set[int] = set()
    n_atoms = len(elements)
    
    # Element-based bits
    element_hash = {"H": 0, "C": 1, "N": 2, "O": 3, "F": 4, "S": 5, "P": 6, "Cl": 7}
    for elem in elements:
        bit = element_hash.get(elem, hash(elem)) % n_bits
        bits.add(bit)
    
    # Count-based bits
    element_counts: Dict[str, int] = {}
    for elem in elements:
        element_counts[elem] = element_counts.get(elem, 0) + 1
    
    for elem, count in element_counts.items():
        bit = (hash(f"{elem}_{count}") % n_bits + n_bits) % n_bits
        bits.add(bit)
    
    # Distance-based bits
    for i in range(n_atoms):
        neighbors = []
        for j in range(n_atoms):
            if i == j:
                continue
            dx = coordinates[i][0] - coordinates[j][0]
            dy = coordinates[i][1] - coordinates[j][1]
            dz = coordinates[i][2] - coordinates[j][2]
            dist = (dx*dx + dy*dy + dz*dz) ** 0.5
            if dist <= radius:
                neighbors.append((elements[j], dist))
        
        # Hash atom environment
        env_str = f"{elements[i]}:" + ",".join(sorted(n[0] for n in neighbors))
        bit = (hash(env_str) % n_bits + n_bits) % n_bits
        bits.add(bit)
    
    # Bond-based bits (approximate)
    covalent_radii = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57, "S": 1.05}
    for i in range(n_atoms):
        ri = covalent_radii.get(elements[i], 1.5)
        for j in range(i + 1, n_atoms):
            rj = covalent_radii.get(elements[j], 1.5)
            dx = coordinates[i][0] - coordinates[j][0]
            dy = coordinates[i][1] - coordinates[j][1]
            dz = coordinates[i][2] - coordinates[j][2]
            dist = (dx*dx + dy*dy + dz*dz) ** 0.5
            if dist < (ri + rj) * 1.3:  # Bonded
                bond_str = "-".join(sorted([elements[i], elements[j]]))
                bit = (hash(bond_str) % n_bits + n_bits) % n_bits
                bits.add(bit)
    
    return MolecularFingerprint(bits=bits, n_bits=n_bits)
