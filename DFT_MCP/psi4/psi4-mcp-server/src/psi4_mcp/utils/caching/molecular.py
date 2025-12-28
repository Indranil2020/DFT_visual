"""
Molecular Structure Caching for Psi4 MCP Server.

Provides specialized caching for molecular structures,
including geometry hashing and fingerprint-based lookup.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import math


@dataclass
class MolecularCacheEntry:
    """Cache entry for molecular data."""
    molecule_hash: str
    geometry: List[Tuple[str, float, float, float]]
    charge: int
    multiplicity: int
    n_atoms: int
    molecular_formula: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def matches_geometry(
        self,
        other_geometry: List[Tuple[str, float, float, float]],
        tolerance: float = 1e-6,
    ) -> bool:
        """Check if another geometry matches this one."""
        if len(self.geometry) != len(other_geometry):
            return False
        
        for (elem1, x1, y1, z1), (elem2, x2, y2, z2) in zip(
            self.geometry, other_geometry
        ):
            if elem1 != elem2:
                return False
            
            dist_sq = (x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2
            if dist_sq > tolerance**2:
                return False
        
        return True


class MolecularCache:
    """
    Specialized cache for molecular structures.
    
    Provides fast lookup of molecules by geometry hash,
    with support for fuzzy matching based on coordinate tolerance.
    """
    
    def __init__(self, max_entries: int = 1000):
        """
        Initialize molecular cache.
        
        Args:
            max_entries: Maximum number of molecules to cache
        """
        self.max_entries = max_entries
        self._cache: Dict[str, MolecularCacheEntry] = {}
        self._formula_index: Dict[str, List[str]] = {}  # formula -> [hashes]
    
    def get(self, molecule_hash: str) -> Optional[MolecularCacheEntry]:
        """
        Get molecule by hash.
        
        Args:
            molecule_hash: Hash of the molecule
            
        Returns:
            Cached entry or None
        """
        return self._cache.get(molecule_hash)
    
    def get_by_geometry(
        self,
        geometry: List[Tuple[str, float, float, float]],
        charge: int = 0,
        multiplicity: int = 1,
        tolerance: float = 1e-6,
    ) -> Optional[MolecularCacheEntry]:
        """
        Get molecule by geometry with fuzzy matching.
        
        Args:
            geometry: List of (element, x, y, z) tuples
            charge: Molecular charge
            multiplicity: Spin multiplicity
            tolerance: Coordinate tolerance for matching
            
        Returns:
            Matching cached entry or None
        """
        # First try exact hash lookup
        mol_hash = compute_molecule_hash(geometry, charge, multiplicity)
        exact_match = self._cache.get(mol_hash)
        if exact_match:
            return exact_match
        
        # Try formula-based lookup with geometry comparison
        formula = _compute_molecular_formula(geometry)
        candidate_hashes = self._formula_index.get(formula, [])
        
        for candidate_hash in candidate_hashes:
            entry = self._cache.get(candidate_hash)
            if entry and entry.charge == charge and entry.multiplicity == multiplicity:
                if entry.matches_geometry(geometry, tolerance):
                    return entry
        
        return None
    
    def set(
        self,
        geometry: List[Tuple[str, float, float, float]],
        charge: int = 0,
        multiplicity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MolecularCacheEntry:
        """
        Add molecule to cache.
        
        Args:
            geometry: List of (element, x, y, z) tuples
            charge: Molecular charge
            multiplicity: Spin multiplicity
            metadata: Additional metadata to store
            
        Returns:
            Created cache entry
        """
        # Evict if necessary
        if len(self._cache) >= self.max_entries:
            self._evict_oldest()
        
        mol_hash = compute_molecule_hash(geometry, charge, multiplicity)
        formula = _compute_molecular_formula(geometry)
        
        entry = MolecularCacheEntry(
            molecule_hash=mol_hash,
            geometry=list(geometry),
            charge=charge,
            multiplicity=multiplicity,
            n_atoms=len(geometry),
            molecular_formula=formula,
            metadata=metadata or {},
        )
        
        self._cache[mol_hash] = entry
        
        # Update formula index
        if formula not in self._formula_index:
            self._formula_index[formula] = []
        if mol_hash not in self._formula_index[formula]:
            self._formula_index[formula].append(mol_hash)
        
        return entry
    
    def delete(self, molecule_hash: str) -> bool:
        """
        Delete molecule from cache.
        
        Args:
            molecule_hash: Hash of molecule to delete
            
        Returns:
            True if deleted, False if not found
        """
        entry = self._cache.get(molecule_hash)
        if entry is None:
            return False
        
        # Remove from formula index
        formula = entry.molecular_formula
        if formula in self._formula_index:
            self._formula_index[formula] = [
                h for h in self._formula_index[formula] if h != molecule_hash
            ]
            if not self._formula_index[formula]:
                del self._formula_index[formula]
        
        del self._cache[molecule_hash]
        return True
    
    def clear(self) -> None:
        """Clear all cached molecules."""
        self._cache.clear()
        self._formula_index.clear()
    
    def get_by_formula(self, formula: str) -> List[MolecularCacheEntry]:
        """
        Get all molecules with a given formula.
        
        Args:
            formula: Molecular formula
            
        Returns:
            List of matching cache entries
        """
        hashes = self._formula_index.get(formula, [])
        return [self._cache[h] for h in hashes if h in self._cache]
    
    def _evict_oldest(self) -> None:
        """Evict the oldest entry."""
        if not self._cache:
            return
        
        oldest_hash = None
        oldest_time = None
        
        for mol_hash, entry in self._cache.items():
            if oldest_time is None or entry.created_at < oldest_time:
                oldest_hash = mol_hash
                oldest_time = entry.created_at
        
        if oldest_hash:
            self.delete(oldest_hash)
    
    @property
    def size(self) -> int:
        """Get number of cached molecules."""
        return len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "n_molecules": len(self._cache),
            "n_formulas": len(self._formula_index),
            "max_entries": self.max_entries,
        }


# Global molecular cache instance
_molecular_cache: Optional[MolecularCache] = None


def get_molecular_cache() -> MolecularCache:
    """Get the global molecular cache instance."""
    global _molecular_cache
    if _molecular_cache is None:
        _molecular_cache = MolecularCache()
    return _molecular_cache


def cache_molecule(
    geometry: List[Tuple[str, float, float, float]],
    charge: int = 0,
    multiplicity: int = 1,
    metadata: Optional[Dict[str, Any]] = None,
) -> MolecularCacheEntry:
    """
    Cache a molecule in the global cache.
    
    Args:
        geometry: List of (element, x, y, z) tuples
        charge: Molecular charge
        multiplicity: Spin multiplicity
        metadata: Additional metadata
        
    Returns:
        Cache entry
    """
    cache = get_molecular_cache()
    return cache.set(geometry, charge, multiplicity, metadata)


def get_cached_molecule(
    geometry: List[Tuple[str, float, float, float]],
    charge: int = 0,
    multiplicity: int = 1,
    tolerance: float = 1e-6,
) -> Optional[MolecularCacheEntry]:
    """
    Get a cached molecule by geometry.
    
    Args:
        geometry: List of (element, x, y, z) tuples
        charge: Molecular charge
        multiplicity: Spin multiplicity
        tolerance: Coordinate tolerance
        
    Returns:
        Cached entry or None
    """
    cache = get_molecular_cache()
    return cache.get_by_geometry(geometry, charge, multiplicity, tolerance)


def compute_molecule_hash(
    geometry: List[Tuple[str, float, float, float]],
    charge: int = 0,
    multiplicity: int = 1,
    precision: int = 6,
) -> str:
    """
    Compute a hash for a molecular geometry.
    
    The hash is computed from the elements and coordinates,
    rounded to the specified precision.
    
    Args:
        geometry: List of (element, x, y, z) tuples
        charge: Molecular charge
        multiplicity: Spin multiplicity
        precision: Decimal places to use for coordinates
        
    Returns:
        MD5 hash of the molecule
    """
    # Sort atoms for consistent ordering
    # Use element then coordinates for deterministic sort
    sorted_geom = sorted(
        geometry,
        key=lambda a: (a[0], round(a[1], precision), round(a[2], precision), round(a[3], precision))
    )
    
    # Build hash string
    parts = [f"{charge}_{multiplicity}"]
    for elem, x, y, z in sorted_geom:
        parts.append(f"{elem}_{x:.{precision}f}_{y:.{precision}f}_{z:.{precision}f}")
    
    hash_string = "|".join(parts)
    return hashlib.md5(hash_string.encode()).hexdigest()


def _compute_molecular_formula(
    geometry: List[Tuple[str, float, float, float]],
) -> str:
    """Compute molecular formula from geometry."""
    element_counts: Dict[str, int] = {}
    
    for elem, _, _, _ in geometry:
        elem_upper = elem.capitalize()
        element_counts[elem_upper] = element_counts.get(elem_upper, 0) + 1
    
    # Sort by Hill notation (C first, then H, then alphabetical)
    sorted_elements = []
    
    if "C" in element_counts:
        sorted_elements.append(("C", element_counts.pop("C")))
        if "H" in element_counts:
            sorted_elements.append(("H", element_counts.pop("H")))
    
    for elem in sorted(element_counts.keys()):
        sorted_elements.append((elem, element_counts[elem]))
    
    # Build formula string
    formula_parts = []
    for elem, count in sorted_elements:
        if count == 1:
            formula_parts.append(elem)
        else:
            formula_parts.append(f"{elem}{count}")
    
    return "".join(formula_parts)


def compare_geometries(
    geom1: List[Tuple[str, float, float, float]],
    geom2: List[Tuple[str, float, float, float]],
) -> Dict[str, Any]:
    """
    Compare two geometries and return differences.
    
    Args:
        geom1: First geometry
        geom2: Second geometry
        
    Returns:
        Dictionary with comparison results
    """
    if len(geom1) != len(geom2):
        return {
            "same_size": False,
            "n_atoms_1": len(geom1),
            "n_atoms_2": len(geom2),
            "max_displacement": None,
            "rms_displacement": None,
        }
    
    # Compute displacements
    displacements = []
    element_match = True
    
    for (e1, x1, y1, z1), (e2, x2, y2, z2) in zip(geom1, geom2):
        if e1 != e2:
            element_match = False
        
        disp = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
        displacements.append(disp)
    
    max_disp = max(displacements) if displacements else 0.0
    rms_disp = math.sqrt(sum(d**2 for d in displacements) / len(displacements)) if displacements else 0.0
    
    return {
        "same_size": True,
        "elements_match": element_match,
        "n_atoms": len(geom1),
        "max_displacement": max_disp,
        "rms_displacement": rms_disp,
        "displacements": displacements,
    }
