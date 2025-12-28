"""
MPI Interface for Psi4 MCP Server.

Provides MPI support detection and configuration.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MPIInfo:
    """MPI configuration information."""
    available: bool = False
    rank: int = 0
    size: int = 1
    comm_world: Any = None
    implementation: str = ""
    version: str = ""


class MPIInterface:
    """Interface for MPI operations."""
    
    def __init__(self):
        self._mpi_available = False
        self._info = MPIInfo()
        self._try_init_mpi()
    
    def _try_init_mpi(self) -> None:
        """Try to initialize MPI."""
        # MPI4Py is optional
        self._mpi_available = False
        self._info = MPIInfo(available=False)
    
    @property
    def is_available(self) -> bool:
        return self._mpi_available
    
    @property
    def rank(self) -> int:
        return self._info.rank
    
    @property
    def size(self) -> int:
        return self._info.size
    
    @property
    def is_master(self) -> bool:
        return self._info.rank == 0
    
    def get_info(self) -> MPIInfo:
        return self._info
    
    def barrier(self) -> None:
        """Synchronize all processes."""
        pass
    
    def broadcast(self, data: Any, root: int = 0) -> Any:
        """Broadcast data from root."""
        return data
    
    def gather(self, data: Any, root: int = 0) -> list:
        """Gather data to root."""
        return [data]
    
    def scatter(self, data: list, root: int = 0) -> Any:
        """Scatter data from root."""
        return data[0] if data else None


_mpi_interface: Optional[MPIInterface] = None


def get_mpi_interface() -> MPIInterface:
    global _mpi_interface
    if _mpi_interface is None:
        _mpi_interface = MPIInterface()
    return _mpi_interface


def is_mpi_available() -> bool:
    return get_mpi_interface().is_available


def get_mpi_info() -> Dict[str, Any]:
    info = get_mpi_interface().get_info()
    return {
        "available": info.available,
        "rank": info.rank,
        "size": info.size,
        "implementation": info.implementation,
    }
