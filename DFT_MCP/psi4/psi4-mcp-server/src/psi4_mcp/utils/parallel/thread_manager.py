"""
Thread Manager for Psi4 MCP Server.

Manages thread allocation for calculations.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ThreadConfig:
    """Thread configuration."""
    n_threads: int
    omp_threads: int
    mkl_threads: int


class ThreadManager:
    """Manages thread allocation for Psi4 calculations."""
    
    def __init__(self, max_threads: Optional[int] = None):
        self._max_threads = max_threads or os.cpu_count() or 4
        self._current_threads = self._max_threads
        self._reserved = 0
    
    @property
    def max_threads(self) -> int:
        return self._max_threads
    
    @property
    def available_threads(self) -> int:
        return max(1, self._max_threads - self._reserved)
    
    @property
    def current_threads(self) -> int:
        return self._current_threads
    
    def set_threads(self, n_threads: int) -> None:
        """Set number of threads for calculations."""
        n_threads = max(1, min(n_threads, self._max_threads))
        self._current_threads = n_threads
        os.environ["OMP_NUM_THREADS"] = str(n_threads)
        os.environ["MKL_NUM_THREADS"] = str(n_threads)
    
    def reserve(self, n_threads: int) -> int:
        """Reserve threads, returns actual reserved."""
        available = self.available_threads
        reserved = min(n_threads, available)
        self._reserved += reserved
        return reserved
    
    def release(self, n_threads: int) -> None:
        """Release reserved threads."""
        self._reserved = max(0, self._reserved - n_threads)
    
    def get_config(self) -> ThreadConfig:
        """Get current thread configuration."""
        return ThreadConfig(
            n_threads=self._current_threads,
            omp_threads=int(os.environ.get("OMP_NUM_THREADS", self._current_threads)),
            mkl_threads=int(os.environ.get("MKL_NUM_THREADS", self._current_threads)),
        )
    
    def optimal_threads_for_system(self, n_basis: int, n_atoms: int) -> int:
        """Suggest optimal thread count for system size."""
        if n_basis < 50:
            return min(2, self._max_threads)
        elif n_basis < 200:
            return min(4, self._max_threads)
        elif n_basis < 500:
            return min(8, self._max_threads)
        return self._max_threads


_thread_manager: Optional[ThreadManager] = None


def get_thread_manager() -> ThreadManager:
    global _thread_manager
    if _thread_manager is None:
        _thread_manager = ThreadManager()
    return _thread_manager


def configure_threads(n_threads: int) -> None:
    """Configure thread count."""
    get_thread_manager().set_threads(n_threads)
