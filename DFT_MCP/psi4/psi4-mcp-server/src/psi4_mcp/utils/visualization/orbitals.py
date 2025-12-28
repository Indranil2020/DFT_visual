"""
Orbital Visualization for Psi4 MCP Server.

Generates visualization data for molecular orbitals.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class OrbitalInfo:
    """Information about a molecular orbital."""
    index: int
    energy: float
    occupation: float
    symmetry: str = ""
    is_homo: bool = False
    is_lumo: bool = False


@dataclass
class OrbitalVisualization:
    """Orbital visualization data."""
    orbitals: List[OrbitalInfo]
    homo_index: int
    lumo_index: int
    gap: float
    n_occupied: int
    n_virtual: int


class OrbitalVisualizer:
    """Generates orbital visualization data."""
    
    def __init__(self):
        pass
    
    def generate(
        self,
        energies: List[float],
        occupations: Optional[List[float]] = None,
        n_electrons: int = 0,
    ) -> OrbitalVisualization:
        """Generate orbital visualization data."""
        n_orb = len(energies)
        
        # Determine occupations if not provided
        if occupations is None:
            n_occ = n_electrons // 2
            occupations = [2.0 if i < n_occ else 0.0 for i in range(n_orb)]
        
        # Find HOMO and LUMO
        homo_idx = -1
        lumo_idx = -1
        for i, occ in enumerate(occupations):
            if occ > 0:
                homo_idx = i
            elif lumo_idx < 0:
                lumo_idx = i
        
        if lumo_idx < 0:
            lumo_idx = homo_idx + 1 if homo_idx + 1 < n_orb else homo_idx
        
        # Calculate gap
        gap = 0.0
        if homo_idx >= 0 and lumo_idx < n_orb:
            gap = energies[lumo_idx] - energies[homo_idx]
        
        # Build orbital list
        orbitals = []
        for i, (e, occ) in enumerate(zip(energies, occupations)):
            orb = OrbitalInfo(
                index=i + 1,
                energy=e,
                occupation=occ,
                is_homo=(i == homo_idx),
                is_lumo=(i == lumo_idx),
            )
            orbitals.append(orb)
        
        n_occupied = sum(1 for occ in occupations if occ > 0)
        n_virtual = n_orb - n_occupied
        
        return OrbitalVisualization(
            orbitals=orbitals,
            homo_index=homo_idx + 1,
            lumo_index=lumo_idx + 1,
            gap=gap,
            n_occupied=n_occupied,
            n_virtual=n_virtual,
        )
    
    def to_energy_diagram(
        self,
        vis: OrbitalVisualization,
        n_show_occupied: int = 5,
        n_show_virtual: int = 5,
    ) -> Dict[str, Any]:
        """Generate energy level diagram data."""
        # Filter orbitals to show
        shown = []
        for orb in vis.orbitals:
            if orb.occupation > 0:
                if vis.homo_index - orb.index < n_show_occupied:
                    shown.append(orb)
            else:
                if orb.index - vis.lumo_index < n_show_virtual:
                    shown.append(orb)
        
        return {
            "levels": [
                {
                    "index": o.index,
                    "energy": o.energy,
                    "occupation": o.occupation,
                    "label": "HOMO" if o.is_homo else ("LUMO" if o.is_lumo else ""),
                }
                for o in shown
            ],
            "homo_index": vis.homo_index,
            "lumo_index": vis.lumo_index,
            "gap": vis.gap,
            "gap_ev": vis.gap * 27.2114,  # Convert to eV
        }


def generate_orbital_data(
    energies: List[float],
    n_electrons: int,
) -> Dict[str, Any]:
    """Generate orbital visualization data."""
    visualizer = OrbitalVisualizer()
    vis = visualizer.generate(energies, n_electrons=n_electrons)
    return visualizer.to_energy_diagram(vis)
