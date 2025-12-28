"""
Memory Management Utilities for Psi4 MCP Server.

This module provides utilities for memory management:
- Memory estimation for calculations
- Memory allocation management
- Memory optimization strategies

Example Usage:
    from psi4_mcp.utils.memory import (
        MemoryEstimator,
        MemoryManager,
        estimate_calculation_memory,
    )
    
    # Estimate memory for calculation
    estimator = MemoryEstimator()
    memory_mb = estimator.estimate_scf_memory(n_basis=100)
"""

from psi4_mcp.utils.memory.estimator import (
    MemoryEstimator,
    MemoryEstimate,
    estimate_calculation_memory,
    estimate_scf_memory,
    estimate_mp2_memory,
    estimate_ccsd_memory,
)

from psi4_mcp.utils.memory.manager import (
    MemoryManager,
    MemoryAllocation,
    get_memory_manager,
    configure_memory,
    get_available_memory,
)

from psi4_mcp.utils.memory.optimizer import (
    MemoryOptimizer,
    OptimizationResult,
    optimize_for_memory,
    get_memory_saving_options,
)

__all__ = [
    # Estimator
    "MemoryEstimator",
    "MemoryEstimate",
    "estimate_calculation_memory",
    "estimate_scf_memory",
    "estimate_mp2_memory",
    "estimate_ccsd_memory",
    
    # Manager
    "MemoryManager",
    "MemoryAllocation",
    "get_memory_manager",
    "configure_memory",
    "get_available_memory",
    
    # Optimizer
    "MemoryOptimizer",
    "OptimizationResult",
    "optimize_for_memory",
    "get_memory_saving_options",
]
