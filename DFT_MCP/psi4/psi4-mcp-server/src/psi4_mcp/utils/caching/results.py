"""
Calculation Results Caching for Psi4 MCP Server.

Provides specialized caching for quantum chemistry calculation
results, with support for method/basis/geometry-based lookup.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import hashlib


class CalculationType(str, Enum):
    """Types of calculations that can be cached."""
    ENERGY = "energy"
    OPTIMIZATION = "optimization"
    FREQUENCIES = "frequencies"
    PROPERTIES = "properties"
    TDDFT = "tddft"
    SAPT = "sapt"
    GRADIENT = "gradient"
    HESSIAN = "hessian"


@dataclass
class CalculationKey:
    """Key for uniquely identifying a calculation."""
    calculation_type: CalculationType
    molecule_hash: str
    method: str
    basis: str
    reference: str = "rhf"
    options_hash: str = ""
    
    def to_hash(self) -> str:
        """Generate hash from key components."""
        key_string = (
            f"{self.calculation_type.value}|"
            f"{self.molecule_hash}|"
            f"{self.method}|"
            f"{self.basis}|"
            f"{self.reference}|"
            f"{self.options_hash}"
        )
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @classmethod
    def create(
        cls,
        calculation_type: CalculationType,
        geometry: List[Tuple[str, float, float, float]],
        charge: int,
        multiplicity: int,
        method: str,
        basis: str,
        reference: str = "rhf",
        options: Optional[Dict[str, Any]] = None,
    ) -> 'CalculationKey':
        """
        Create a calculation key.
        
        Args:
            calculation_type: Type of calculation
            geometry: Molecular geometry
            charge: Molecular charge
            multiplicity: Spin multiplicity
            method: Computational method
            basis: Basis set
            reference: Reference type (rhf, uhf, rohf)
            options: Additional options
            
        Returns:
            CalculationKey instance
        """
        from psi4_mcp.utils.caching.molecular import compute_molecule_hash
        
        mol_hash = compute_molecule_hash(geometry, charge, multiplicity)
        
        # Hash options if provided
        options_hash = ""
        if options:
            # Sort for deterministic hashing
            sorted_opts = sorted(options.items())
            opts_string = str(sorted_opts)
            options_hash = hashlib.md5(opts_string.encode()).hexdigest()[:8]
        
        return cls(
            calculation_type=calculation_type,
            molecule_hash=mol_hash,
            method=method.lower(),
            basis=basis.lower(),
            reference=reference.lower(),
            options_hash=options_hash,
        )


@dataclass
class ResultsCacheEntry:
    """Cache entry for calculation results."""
    key: CalculationKey
    key_hash: str
    result: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    computation_time_seconds: float = 0.0
    psi4_version: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        delta = datetime.now() - self.created_at
        return delta.total_seconds()


class ResultsCache:
    """
    Specialized cache for calculation results.
    
    Provides lookup by calculation key with support for
    partial matching and result validation.
    """
    
    def __init__(self, max_entries: int = 500):
        """
        Initialize results cache.
        
        Args:
            max_entries: Maximum number of results to cache
        """
        self.max_entries = max_entries
        self._cache: Dict[str, ResultsCacheEntry] = {}
        self._method_index: Dict[str, List[str]] = {}  # method -> [key_hashes]
        self._type_index: Dict[CalculationType, List[str]] = {}  # type -> [key_hashes]
    
    def get(self, key: CalculationKey) -> Optional[ResultsCacheEntry]:
        """
        Get cached result by key.
        
        Args:
            key: Calculation key
            
        Returns:
            Cached result or None
        """
        key_hash = key.to_hash()
        return self._cache.get(key_hash)
    
    def get_by_hash(self, key_hash: str) -> Optional[ResultsCacheEntry]:
        """
        Get cached result by hash.
        
        Args:
            key_hash: Key hash
            
        Returns:
            Cached result or None
        """
        return self._cache.get(key_hash)
    
    def set(
        self,
        key: CalculationKey,
        result: Dict[str, Any],
        computation_time: float = 0.0,
        psi4_version: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ResultsCacheEntry:
        """
        Cache a calculation result.
        
        Args:
            key: Calculation key
            result: Result dictionary
            computation_time: Time taken for calculation
            psi4_version: Psi4 version used
            metadata: Additional metadata
            
        Returns:
            Created cache entry
        """
        # Evict if necessary
        if len(self._cache) >= self.max_entries:
            self._evict_oldest()
        
        key_hash = key.to_hash()
        
        entry = ResultsCacheEntry(
            key=key,
            key_hash=key_hash,
            result=dict(result),
            computation_time_seconds=computation_time,
            psi4_version=psi4_version,
            metadata=metadata or {},
        )
        
        self._cache[key_hash] = entry
        
        # Update indices
        method = key.method
        if method not in self._method_index:
            self._method_index[method] = []
        if key_hash not in self._method_index[method]:
            self._method_index[method].append(key_hash)
        
        calc_type = key.calculation_type
        if calc_type not in self._type_index:
            self._type_index[calc_type] = []
        if key_hash not in self._type_index[calc_type]:
            self._type_index[calc_type].append(key_hash)
        
        return entry
    
    def delete(self, key: CalculationKey) -> bool:
        """
        Delete cached result.
        
        Args:
            key: Calculation key
            
        Returns:
            True if deleted, False if not found
        """
        key_hash = key.to_hash()
        return self._delete_by_hash(key_hash)
    
    def _delete_by_hash(self, key_hash: str) -> bool:
        """Delete by hash."""
        entry = self._cache.get(key_hash)
        if entry is None:
            return False
        
        # Remove from indices
        method = entry.key.method
        if method in self._method_index:
            self._method_index[method] = [
                h for h in self._method_index[method] if h != key_hash
            ]
        
        calc_type = entry.key.calculation_type
        if calc_type in self._type_index:
            self._type_index[calc_type] = [
                h for h in self._type_index[calc_type] if h != key_hash
            ]
        
        del self._cache[key_hash]
        return True
    
    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._method_index.clear()
        self._type_index.clear()
    
    def invalidate_by_molecule(self, molecule_hash: str) -> int:
        """
        Invalidate all results for a molecule.
        
        Args:
            molecule_hash: Molecule hash
            
        Returns:
            Number of entries invalidated
        """
        to_delete = [
            key_hash for key_hash, entry in self._cache.items()
            if entry.key.molecule_hash == molecule_hash
        ]
        
        for key_hash in to_delete:
            self._delete_by_hash(key_hash)
        
        return len(to_delete)
    
    def invalidate_by_method(self, method: str) -> int:
        """
        Invalidate all results for a method.
        
        Args:
            method: Method name
            
        Returns:
            Number of entries invalidated
        """
        method_lower = method.lower()
        to_delete = list(self._method_index.get(method_lower, []))
        
        for key_hash in to_delete:
            self._delete_by_hash(key_hash)
        
        return len(to_delete)
    
    def invalidate_by_type(self, calc_type: CalculationType) -> int:
        """
        Invalidate all results of a type.
        
        Args:
            calc_type: Calculation type
            
        Returns:
            Number of entries invalidated
        """
        to_delete = list(self._type_index.get(calc_type, []))
        
        for key_hash in to_delete:
            self._delete_by_hash(key_hash)
        
        return len(to_delete)
    
    def get_by_method(self, method: str) -> List[ResultsCacheEntry]:
        """Get all cached results for a method."""
        method_lower = method.lower()
        hashes = self._method_index.get(method_lower, [])
        return [self._cache[h] for h in hashes if h in self._cache]
    
    def get_by_type(self, calc_type: CalculationType) -> List[ResultsCacheEntry]:
        """Get all cached results of a type."""
        hashes = self._type_index.get(calc_type, [])
        return [self._cache[h] for h in hashes if h in self._cache]
    
    def _evict_oldest(self) -> None:
        """Evict the oldest entry."""
        if not self._cache:
            return
        
        oldest_hash = None
        oldest_time = None
        
        for key_hash, entry in self._cache.items():
            if oldest_time is None or entry.created_at < oldest_time:
                oldest_hash = key_hash
                oldest_time = entry.created_at
        
        if oldest_hash:
            self._delete_by_hash(oldest_hash)
    
    @property
    def size(self) -> int:
        """Get number of cached results."""
        return len(self._cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        type_counts = {
            t.value: len(self._type_index.get(t, []))
            for t in CalculationType
        }
        
        return {
            "n_results": len(self._cache),
            "n_methods": len(self._method_index),
            "max_entries": self.max_entries,
            "by_type": type_counts,
        }


# Global results cache instance
_results_cache: Optional[ResultsCache] = None


def get_results_cache() -> ResultsCache:
    """Get the global results cache instance."""
    global _results_cache
    if _results_cache is None:
        _results_cache = ResultsCache()
    return _results_cache


def cache_calculation_result(
    calculation_type: CalculationType,
    geometry: List[Tuple[str, float, float, float]],
    charge: int,
    multiplicity: int,
    method: str,
    basis: str,
    result: Dict[str, Any],
    reference: str = "rhf",
    options: Optional[Dict[str, Any]] = None,
    computation_time: float = 0.0,
) -> ResultsCacheEntry:
    """
    Cache a calculation result.
    
    Args:
        calculation_type: Type of calculation
        geometry: Molecular geometry
        charge: Molecular charge
        multiplicity: Spin multiplicity
        method: Computational method
        basis: Basis set
        result: Result dictionary
        reference: Reference type
        options: Calculation options
        computation_time: Time taken
        
    Returns:
        Cache entry
    """
    cache = get_results_cache()
    key = CalculationKey.create(
        calculation_type=calculation_type,
        geometry=geometry,
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        basis=basis,
        reference=reference,
        options=options,
    )
    return cache.set(key, result, computation_time)


def get_cached_result(
    calculation_type: CalculationType,
    geometry: List[Tuple[str, float, float, float]],
    charge: int,
    multiplicity: int,
    method: str,
    basis: str,
    reference: str = "rhf",
    options: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get a cached calculation result.
    
    Args:
        calculation_type: Type of calculation
        geometry: Molecular geometry
        charge: Molecular charge
        multiplicity: Spin multiplicity
        method: Computational method
        basis: Basis set
        reference: Reference type
        options: Calculation options
        
    Returns:
        Cached result dictionary or None
    """
    cache = get_results_cache()
    key = CalculationKey.create(
        calculation_type=calculation_type,
        geometry=geometry,
        charge=charge,
        multiplicity=multiplicity,
        method=method,
        basis=basis,
        reference=reference,
        options=options,
    )
    entry = cache.get(key)
    if entry:
        return entry.result
    return None


def invalidate_results(
    molecule_hash: Optional[str] = None,
    method: Optional[str] = None,
    calc_type: Optional[CalculationType] = None,
) -> int:
    """
    Invalidate cached results.
    
    Args:
        molecule_hash: Invalidate by molecule
        method: Invalidate by method
        calc_type: Invalidate by calculation type
        
    Returns:
        Number of entries invalidated
    """
    cache = get_results_cache()
    total = 0
    
    if molecule_hash:
        total += cache.invalidate_by_molecule(molecule_hash)
    
    if method:
        total += cache.invalidate_by_method(method)
    
    if calc_type:
        total += cache.invalidate_by_type(calc_type)
    
    return total
