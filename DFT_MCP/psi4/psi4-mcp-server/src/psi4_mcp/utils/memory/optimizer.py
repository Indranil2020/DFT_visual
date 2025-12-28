"""
Memory Optimization Utilities for Psi4 MCP Server.

Provides strategies to reduce memory usage.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class OptimizationStrategy(str, Enum):
    """Memory optimization strategies."""
    DENSITY_FITTING = "density_fitting"
    REDUCE_DIIS = "reduce_diis"
    SMALLER_BASIS = "smaller_basis"
    FREEZE_CORE = "freeze_core"
    DISK_STORAGE = "disk_storage"
    DIRECT_SCF = "direct_scf"


@dataclass
class OptimizationResult:
    """Result of memory optimization."""
    strategy: OptimizationStrategy
    original_memory_mb: float
    optimized_memory_mb: float
    option_changes: Dict[str, Any]
    description: str
    tradeoffs: List[str] = field(default_factory=list)
    
    @property
    def savings_mb(self) -> float:
        return self.original_memory_mb - self.optimized_memory_mb
    
    @property
    def savings_percent(self) -> float:
        if self.original_memory_mb <= 0:
            return 0.0
        return (self.savings_mb / self.original_memory_mb) * 100


class MemoryOptimizer:
    """Optimizer for reducing calculation memory usage."""
    
    def __init__(self, target_memory_mb: Optional[float] = None):
        self.target_memory_mb = target_memory_mb
    
    def get_optimizations(
        self,
        current_memory_mb: float,
        calculation_type: str,
        current_options: Optional[Dict[str, Any]] = None,
    ) -> List[OptimizationResult]:
        """Get applicable memory optimizations."""
        current_options = current_options or {}
        results = []
        
        # Density fitting
        if current_options.get("scf_type") != "df":
            results.append(OptimizationResult(
                strategy=OptimizationStrategy.DENSITY_FITTING,
                original_memory_mb=current_memory_mb,
                optimized_memory_mb=current_memory_mb * 0.3,
                option_changes={"scf_type": "df"},
                description="Use density-fitted integrals",
                tradeoffs=["Slight loss of accuracy (~0.1 mH)", "Requires auxiliary basis"],
            ))
        
        # Reduce DIIS vectors
        current_diis = current_options.get("diis_max_vecs", 10)
        if current_diis > 4:
            results.append(OptimizationResult(
                strategy=OptimizationStrategy.REDUCE_DIIS,
                original_memory_mb=current_memory_mb,
                optimized_memory_mb=current_memory_mb * 0.9,
                option_changes={"diis_max_vecs": 4},
                description="Reduce DIIS vector storage",
                tradeoffs=["May slow convergence", "Usually minimal impact"],
            ))
        
        # Freeze core
        if calculation_type.lower() in ("mp2", "ccsd", "ccsd_t"):
            if not current_options.get("freeze_core"):
                results.append(OptimizationResult(
                    strategy=OptimizationStrategy.FREEZE_CORE,
                    original_memory_mb=current_memory_mb,
                    optimized_memory_mb=current_memory_mb * 0.7,
                    option_changes={"freeze_core": True},
                    description="Freeze core electrons",
                    tradeoffs=["Standard approximation", "Negligible accuracy loss"],
                ))
        
        # Direct SCF
        results.append(OptimizationResult(
            strategy=OptimizationStrategy.DIRECT_SCF,
            original_memory_mb=current_memory_mb,
            optimized_memory_mb=current_memory_mb * 0.5,
            option_changes={"scf_type": "direct"},
            description="Use direct SCF (recompute integrals)",
            tradeoffs=["Slower computation", "Minimal memory footprint"],
        ))
        
        return results
    
    def optimize(
        self,
        current_memory_mb: float,
        calculation_type: str,
        current_options: Optional[Dict[str, Any]] = None,
    ) -> Optional[OptimizationResult]:
        """Get best optimization to reach target memory."""
        if self.target_memory_mb is None:
            return None
        
        if current_memory_mb <= self.target_memory_mb:
            return None
        
        optimizations = self.get_optimizations(current_memory_mb, calculation_type, current_options)
        
        # Sort by savings
        optimizations.sort(key=lambda x: x.savings_mb, reverse=True)
        
        # Find first that meets target
        for opt in optimizations:
            if opt.optimized_memory_mb <= self.target_memory_mb:
                return opt
        
        # Return best savings if none meet target
        return optimizations[0] if optimizations else None


def optimize_for_memory(
    target_mb: float,
    current_mb: float,
    calculation_type: str,
) -> Dict[str, Any]:
    """Get options to optimize for target memory."""
    optimizer = MemoryOptimizer(target_memory_mb=target_mb)
    result = optimizer.optimize(current_mb, calculation_type)
    return result.option_changes if result else {}


def get_memory_saving_options(calculation_type: str) -> List[Dict[str, Any]]:
    """Get all memory-saving option combinations."""
    optimizer = MemoryOptimizer()
    results = optimizer.get_optimizations(1000.0, calculation_type)
    return [r.option_changes for r in results]
