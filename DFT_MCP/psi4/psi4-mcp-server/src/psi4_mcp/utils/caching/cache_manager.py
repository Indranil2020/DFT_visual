"""
Cache Manager for Psi4 MCP Server.

Provides a general-purpose caching system with configurable
size limits, TTL, and eviction policies.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, List
import hashlib
import json
import threading
from functools import wraps


T = TypeVar('T')


class EvictionPolicy(str, Enum):
    """Cache eviction policies."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live based


@dataclass
class CacheConfig:
    """Configuration for cache behavior."""
    max_entries: int = 1000
    default_ttl_seconds: Optional[int] = 3600  # 1 hour
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    enable_stats: bool = True
    thread_safe: bool = True


@dataclass
class CacheEntry(Generic[T]):
    """A single cache entry with metadata."""
    key: str
    value: T
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0
    
    @property
    def is_expired(self) -> bool:
        """Check if entry has expired based on TTL."""
        if self.ttl_seconds is None:
            return False
        expiry_time = self.created_at + timedelta(seconds=self.ttl_seconds)
        return datetime.now() > expiry_time
    
    @property
    def age_seconds(self) -> float:
        """Get age of entry in seconds."""
        delta = datetime.now() - self.created_at
        return delta.total_seconds()
    
    def touch(self) -> None:
        """Update last accessed time and increment count."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class CacheStats:
    """Cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    current_entries: int = 0
    total_size_bytes: int = 0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total
    
    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1
    
    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1
    
    def record_eviction(self) -> None:
        """Record an eviction."""
        self.evictions += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "current_entries": self.current_entries,
            "total_size_bytes": self.total_size_bytes,
            "hit_rate": self.hit_rate,
        }


class CacheManager:
    """
    Thread-safe cache manager with configurable policies.
    
    Provides get/set/delete operations with automatic eviction
    based on size limits and TTL.
    """
    
    _instance: Optional['CacheManager'] = None
    _lock = threading.Lock()
    
    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize cache manager.
        
        Args:
            config: Cache configuration
        """
        self.config = config or CacheConfig()
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = CacheStats()
        self._cache_lock = threading.RLock() if self.config.thread_safe else None
    
    @classmethod
    def get_instance(cls, config: Optional[CacheConfig] = None) -> 'CacheManager':
        """Get singleton cache manager instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(config)
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)."""
        with cls._lock:
            cls._instance = None
    
    def _acquire_lock(self) -> None:
        """Acquire lock if thread safety is enabled."""
        if self._cache_lock is not None:
            self._cache_lock.acquire()
    
    def _release_lock(self) -> None:
        """Release lock if thread safety is enabled."""
        if self._cache_lock is not None:
            self._cache_lock.release()
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        self._acquire_lock()
        
        entry = self._cache.get(key)
        
        if entry is None:
            if self.config.enable_stats:
                self._stats.record_miss()
            self._release_lock()
            return default
        
        if entry.is_expired:
            del self._cache[key]
            self._stats.current_entries = len(self._cache)
            if self.config.enable_stats:
                self._stats.record_miss()
            self._release_lock()
            return default
        
        entry.touch()
        if self.config.enable_stats:
            self._stats.record_hit()
        
        result = entry.value
        self._release_lock()
        return result
    
    def set(
        self,
        key: str,
        value: T,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override
        """
        self._acquire_lock()
        
        # Check if we need to evict entries
        if len(self._cache) >= self.config.max_entries:
            self._evict()
        
        # Estimate size
        size_bytes = _estimate_size(value)
        
        # Create entry
        now = datetime.now()
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            last_accessed=now,
            ttl_seconds=ttl_seconds or self.config.default_ttl_seconds,
            size_bytes=size_bytes,
        )
        
        self._cache[key] = entry
        self._stats.current_entries = len(self._cache)
        self._stats.total_size_bytes += size_bytes
        
        self._release_lock()
    
    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was deleted, False if not found
        """
        self._acquire_lock()
        
        if key in self._cache:
            entry = self._cache[key]
            self._stats.total_size_bytes -= entry.size_bytes
            del self._cache[key]
            self._stats.current_entries = len(self._cache)
            self._release_lock()
            return True
        
        self._release_lock()
        return False
    
    def clear(self) -> None:
        """Clear all entries from cache."""
        self._acquire_lock()
        self._cache.clear()
        self._stats.current_entries = 0
        self._stats.total_size_bytes = 0
        self._release_lock()
    
    def contains(self, key: str) -> bool:
        """Check if key exists in cache (and is not expired)."""
        self._acquire_lock()
        
        entry = self._cache.get(key)
        if entry is None:
            self._release_lock()
            return False
        
        if entry.is_expired:
            del self._cache[key]
            self._stats.current_entries = len(self._cache)
            self._release_lock()
            return False
        
        self._release_lock()
        return True
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats
    
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        self._acquire_lock()
        keys = list(self._cache.keys())
        self._release_lock()
        return keys
    
    def _evict(self) -> None:
        """Evict entries based on policy."""
        if not self._cache:
            return
        
        policy = self.config.eviction_policy
        
        if policy == EvictionPolicy.LRU:
            # Find least recently used
            oldest_key = None
            oldest_time = None
            for key, entry in self._cache.items():
                if oldest_time is None or entry.last_accessed < oldest_time:
                    oldest_key = key
                    oldest_time = entry.last_accessed
            if oldest_key:
                self._remove_entry(oldest_key)
        
        elif policy == EvictionPolicy.LFU:
            # Find least frequently used
            min_key = None
            min_count = None
            for key, entry in self._cache.items():
                if min_count is None or entry.access_count < min_count:
                    min_key = key
                    min_count = entry.access_count
            if min_key:
                self._remove_entry(min_key)
        
        elif policy == EvictionPolicy.FIFO:
            # Find oldest entry
            oldest_key = None
            oldest_time = None
            for key, entry in self._cache.items():
                if oldest_time is None or entry.created_at < oldest_time:
                    oldest_key = key
                    oldest_time = entry.created_at
            if oldest_key:
                self._remove_entry(oldest_key)
        
        elif policy == EvictionPolicy.TTL:
            # Remove expired entries first
            expired = [k for k, v in self._cache.items() if v.is_expired]
            if expired:
                self._remove_entry(expired[0])
            else:
                # Fall back to LRU
                oldest_key = None
                oldest_time = None
                for key, entry in self._cache.items():
                    if oldest_time is None or entry.last_accessed < oldest_time:
                        oldest_key = key
                        oldest_time = entry.last_accessed
                if oldest_key:
                    self._remove_entry(oldest_key)
        
        if self.config.enable_stats:
            self._stats.record_eviction()
    
    def _remove_entry(self, key: str) -> None:
        """Remove an entry by key."""
        if key in self._cache:
            entry = self._cache[key]
            self._stats.total_size_bytes -= entry.size_bytes
            del self._cache[key]
            self._stats.current_entries = len(self._cache)


def _estimate_size(value: Any) -> int:
    """Estimate size of a value in bytes."""
    if value is None:
        return 0
    
    if isinstance(value, (str, bytes)):
        return len(value)
    
    if isinstance(value, (int, float)):
        return 8
    
    if isinstance(value, (list, tuple)):
        return sum(_estimate_size(v) for v in value)
    
    if isinstance(value, dict):
        return sum(_estimate_size(k) + _estimate_size(v) for k, v in value.items())
    
    # Default estimate
    return 100


def cache_result(
    ttl_seconds: Optional[int] = None,
    key_func: Optional[Callable[..., str]] = None,
) -> Callable:
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: TTL for cached results
        key_func: Function to generate cache key from arguments
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = _default_key_func(func.__name__, args, kwargs)
            
            # Check cache
            cache = CacheManager.get_instance()
            cached = cache.get(key)
            if cached is not None:
                return cached
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def _default_key_func(func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate default cache key from function arguments."""
    # Create a hashable representation
    key_parts = [func_name]
    
    for arg in args:
        key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    
    key_string = ":".join(key_parts)
    
    # Hash long keys
    if len(key_string) > 100:
        return hashlib.md5(key_string.encode()).hexdigest()
    
    return key_string


def get_cache() -> CacheManager:
    """Get the global cache manager instance."""
    return CacheManager.get_instance()


def clear_cache() -> None:
    """Clear all cached data."""
    CacheManager.get_instance().clear()
