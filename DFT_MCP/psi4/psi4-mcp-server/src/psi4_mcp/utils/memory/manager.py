"""
Memory Manager for Psi4 MCP Server.

Handles memory allocation and tracking.
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryAllocation:
    """Record of a memory allocation."""
    name: str
    size_mb: float
    timestamp: datetime = field(default_factory=datetime.now)
    released: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryManager:
    """Manages memory for Psi4 calculations."""
    
    def __init__(self, max_memory_mb: float = 2048.0, reserve_mb: float = 256.0):
        self.max_memory_mb = max_memory_mb
        self.reserve_mb = reserve_mb
        self._allocations: List[MemoryAllocation] = []
        self._current_used: float = 0.0
    
    @property
    def available_mb(self) -> float:
        return max(0.0, self.max_memory_mb - self._current_used - self.reserve_mb)
    
    @property
    def used_mb(self) -> float:
        return self._current_used
    
    @property
    def usage_percent(self) -> float:
        if self.max_memory_mb <= 0:
            return 0.0
        return (self._current_used / self.max_memory_mb) * 100
    
    def can_allocate(self, size_mb: float) -> bool:
        return size_mb <= self.available_mb
    
    def allocate(self, name: str, size_mb: float, **metadata: Any) -> Optional[MemoryAllocation]:
        if not self.can_allocate(size_mb):
            return None
        allocation = MemoryAllocation(name=name, size_mb=size_mb, metadata=metadata)
        self._allocations.append(allocation)
        self._current_used += size_mb
        return allocation
    
    def release(self, allocation: MemoryAllocation) -> bool:
        if allocation.released:
            return False
        allocation.released = True
        self._current_used -= allocation.size_mb
        return True
    
    def release_by_name(self, name: str) -> int:
        count = 0
        for alloc in self._allocations:
            if alloc.name == name and not alloc.released:
                self.release(alloc)
                count += 1
        return count
    
    def release_all(self) -> int:
        count = 0
        for alloc in self._allocations:
            if not alloc.released:
                alloc.released = True
                count += 1
        self._current_used = 0.0
        return count
    
    def get_allocations(self, include_released: bool = False) -> List[MemoryAllocation]:
        if include_released:
            return list(self._allocations)
        return [a for a in self._allocations if not a.released]
    
    def get_statistics(self) -> Dict[str, Any]:
        active = [a for a in self._allocations if not a.released]
        return {
            "max_memory_mb": self.max_memory_mb,
            "used_mb": self._current_used,
            "available_mb": self.available_mb,
            "usage_percent": self.usage_percent,
            "active_allocations": len(active),
            "total_allocations": len(self._allocations),
        }
    
    def to_psi4_memory_string(self) -> str:
        available = self.available_mb
        if available >= 1024:
            return f"{available / 1024:.1f} GB"
        return f"{available:.0f} MB"


_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


def configure_memory(max_memory_mb: float, reserve_mb: float = 256.0) -> MemoryManager:
    global _memory_manager
    _memory_manager = MemoryManager(max_memory_mb=max_memory_mb, reserve_mb=reserve_mb)
    return _memory_manager


def get_available_memory() -> float:
    return get_memory_manager().available_mb


def get_system_memory_mb() -> float:
    """Get total system memory in MB."""
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return kb / 1024
    except (FileNotFoundError, PermissionError, ValueError):
        pass
    return 8192.0  # Default 8GB


def parse_memory_string(memory_str: str) -> float:
    """Parse memory string to MB."""
    memory_str = memory_str.strip().upper()
    multipliers = {"B": 1e-6, "KB": 1e-3, "MB": 1.0, "GB": 1024.0, "TB": 1024 * 1024}
    
    for suffix, mult in multipliers.items():
        if memory_str.endswith(suffix):
            value_str = memory_str[:-len(suffix)].strip()
            try:
                return float(value_str) * mult
            except ValueError:
                return 2048.0
    
    try:
        return float(memory_str)
    except ValueError:
        return 2048.0
