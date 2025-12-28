"""
Caching Utilities for Psi4 MCP Server.

This module provides caching systems for:
- Calculation results
- Molecular structures and fingerprints
- Basis set data
- General-purpose caching

Example Usage:
    from psi4_mcp.utils.caching import (
        CacheManager,
        MolecularCache,
        ResultsCache,
        cache_result,
    )
    
    # Use the global cache manager
    cache = CacheManager.get_instance()
    cache.set("key", value)
    value = cache.get("key")
"""

from psi4_mcp.utils.caching.cache_manager import (
    CacheManager,
    CacheConfig,
    CacheEntry,
    CacheStats,
    cache_result,
    get_cache,
    clear_cache,
)

from psi4_mcp.utils.caching.molecular import (
    MolecularCache,
    MolecularCacheEntry,
    cache_molecule,
    get_cached_molecule,
    compute_molecule_hash,
)

from psi4_mcp.utils.caching.results import (
    ResultsCache,
    ResultsCacheEntry,
    CalculationKey,
    cache_calculation_result,
    get_cached_result,
    invalidate_results,
)

__all__ = [
    # Cache Manager
    "CacheManager",
    "CacheConfig",
    "CacheEntry",
    "CacheStats",
    "cache_result",
    "get_cache",
    "clear_cache",
    
    # Molecular Cache
    "MolecularCache",
    "MolecularCacheEntry",
    "cache_molecule",
    "get_cached_molecule",
    "compute_molecule_hash",
    
    # Results Cache
    "ResultsCache",
    "ResultsCacheEntry",
    "CalculationKey",
    "cache_calculation_result",
    "get_cached_result",
    "invalidate_results",
]
