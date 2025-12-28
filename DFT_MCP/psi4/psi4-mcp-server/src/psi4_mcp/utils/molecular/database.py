"""
Molecule Database for Psi4 MCP Server.

Provides storage and retrieval of molecular structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import json
from pathlib import Path


@dataclass
class MoleculeRecord:
    """Record of a molecule in the database."""
    name: str
    elements: List[str]
    coordinates: List[Tuple[float, float, float]]
    charge: int = 0
    multiplicity: int = 1
    formula: str = ""
    smiles: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def n_atoms(self) -> int:
        return len(self.elements)
    
    def to_xyz_string(self) -> str:
        lines = [str(self.n_atoms), self.name or ""]
        for elem, (x, y, z) in zip(self.elements, self.coordinates):
            lines.append(f"{elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        return "\n".join(lines)
    
    def to_psi4_string(self) -> str:
        lines = [f"{self.charge} {self.multiplicity}"]
        for elem, (x, y, z) in zip(self.elements, self.coordinates):
            lines.append(f"{elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name, "elements": self.elements,
            "coordinates": [list(c) for c in self.coordinates],
            "charge": self.charge, "multiplicity": self.multiplicity,
            "formula": self.formula, "smiles": self.smiles,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MoleculeRecord":
        coords = [tuple(c) for c in data.get("coordinates", [])]
        return cls(
            name=data.get("name", ""), elements=data.get("elements", []),
            coordinates=coords, charge=data.get("charge", 0),
            multiplicity=data.get("multiplicity", 1),
            formula=data.get("formula", ""), smiles=data.get("smiles", ""),
            metadata=data.get("metadata", {}),
        )


class MoleculeDatabase:
    """Database for storing and retrieving molecules."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path
        self._molecules: Dict[str, MoleculeRecord] = {}
        self._load_common_molecules()
    
    def _load_common_molecules(self) -> None:
        """Load common test molecules."""
        common = {
            "water": (["O", "H", "H"], [(0.0, 0.0, 0.117), (-0.757, 0.0, -0.470), (0.757, 0.0, -0.470)]),
            "methane": (["C", "H", "H", "H", "H"], [(0.0, 0.0, 0.0), (0.629, 0.629, 0.629), 
                       (-0.629, -0.629, 0.629), (-0.629, 0.629, -0.629), (0.629, -0.629, -0.629)]),
            "ammonia": (["N", "H", "H", "H"], [(0.0, 0.0, 0.116), (0.0, 0.939, -0.272),
                       (0.813, -0.470, -0.272), (-0.813, -0.470, -0.272)]),
            "hydrogen": (["H", "H"], [(0.0, 0.0, 0.0), (0.74, 0.0, 0.0)]),
            "helium": (["He"], [(0.0, 0.0, 0.0)]),
        }
        for name, (elements, coords) in common.items():
            self._molecules[name] = MoleculeRecord(name=name, elements=elements, coordinates=coords)
    
    def add(self, molecule: MoleculeRecord) -> str:
        key = molecule.name or f"mol_{len(self._molecules)}"
        self._molecules[key] = molecule
        return key
    
    def get(self, name: str) -> Optional[MoleculeRecord]:
        return self._molecules.get(name)
    
    def remove(self, name: str) -> bool:
        if name in self._molecules:
            del self._molecules[name]
            return True
        return False
    
    def list_all(self) -> List[str]:
        return list(self._molecules.keys())
    
    def search(self, query: str) -> List[MoleculeRecord]:
        results = []
        query_lower = query.lower()
        for name, mol in self._molecules.items():
            if query_lower in name.lower() or query_lower in mol.formula.lower():
                results.append(mol)
        return results
    
    def save(self, filepath: Optional[Path] = None) -> None:
        path = filepath or self.storage_path
        if path is None:
            return
        data = {name: mol.to_dict() for name, mol in self._molecules.items()}
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def load(self, filepath: Optional[Path] = None) -> None:
        path = filepath or self.storage_path
        if path is None or not path.exists():
            return
        with open(path, "r") as f:
            data = json.load(f)
        for name, mol_data in data.items():
            self._molecules[name] = MoleculeRecord.from_dict(mol_data)


_database: Optional[MoleculeDatabase] = None

def get_molecule_database() -> MoleculeDatabase:
    global _database
    if _database is None:
        _database = MoleculeDatabase()
    return _database
