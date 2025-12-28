"""
Convergence Utilities for Psi4 MCP Server.

This module provides utilities for handling convergence in:
- SCF calculations
- Geometry optimization
- TD-DFT calculations
- General iterative procedures

Example Usage:
    from psi4_mcp.utils.convergence import (
        SCFConvergenceHelper,
        OptimizationConvergenceHelper,
        ConvergenceStrategy,
        apply_convergence_strategy,
    )
    
    # Get SCF convergence settings
    helper = SCFConvergenceHelper()
    settings = helper.get_settings_for_system(n_electrons=50)
"""

from psi4_mcp.utils.convergence.scf import (
    SCFConvergenceHelper,
    SCFConvergenceSettings,
    SCFConvergenceStatus,
    SCFAlgorithm,
    diagnose_scf_convergence,
    get_scf_recommendations,
)

from psi4_mcp.utils.convergence.optimization import (
    OptimizationConvergenceHelper,
    OptimizationSettings,
    OptimizationStatus,
    OptimizationAlgorithm,
    get_optimization_settings,
    analyze_optimization_progress,
)

from psi4_mcp.utils.convergence.strategies import (
    ConvergenceStrategy,
    ConvergenceStrategyType,
    DampingStrategy,
    LevelShiftStrategy,
    SOSCFStrategy,
    MOMStrategy,
    apply_convergence_strategy,
    get_strategy_sequence,
)

from psi4_mcp.utils.convergence.tddft import (
    TDDFTConvergenceHelper,
    TDDFTConvergenceSettings,
    TDDFTConvergenceStatus,
    TDDFTConvergenceAnalysis,
    diagnose_tddft_convergence,
    get_tddft_recommendations,
    estimate_tddft_cost,
)

__all__ = [
    # SCF
    "SCFConvergenceHelper",
    "SCFConvergenceSettings",
    "SCFConvergenceStatus",
    "SCFAlgorithm",
    "diagnose_scf_convergence",
    "get_scf_recommendations",
    
    # Optimization
    "OptimizationConvergenceHelper",
    "OptimizationSettings",
    "OptimizationStatus",
    "OptimizationAlgorithm",
    "get_optimization_settings",
    "analyze_optimization_progress",
    
    # Strategies
    "ConvergenceStrategy",
    "ConvergenceStrategyType",
    "DampingStrategy",
    "LevelShiftStrategy",
    "SOSCFStrategy",
    "MOMStrategy",
    "apply_convergence_strategy",
    "get_strategy_sequence",
    
    # TDDFT
    "TDDFTConvergenceHelper",
    "TDDFTConvergenceSettings",
    "TDDFTConvergenceStatus",
    "TDDFTConvergenceAnalysis",
    "diagnose_tddft_convergence",
    "get_tddft_recommendations",
    "estimate_tddft_cost",
]
