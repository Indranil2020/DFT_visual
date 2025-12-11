"""
Core Tools Package.

This package provides the fundamental quantum chemistry calculation tools:
    - Energy calculations
    - Gradient calculations
    - Hessian calculations
    - Geometry optimization
"""

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolMetadata,
    ToolCategory,
    ToolStatus,
    ToolRegistry,
    register_tool,
    get_tool,
    list_tools,
    run_tool,
)

from psi4_mcp.tools.core.energy import (
    EnergyTool,
    EnergyToolInput,
    calculate_energy,
)

from psi4_mcp.tools.core.gradient import (
    GradientTool,
    GradientToolInput,
    calculate_gradient,
)

from psi4_mcp.tools.core.hessian import (
    HessianTool,
    HessianToolInput,
    calculate_hessian,
)

from psi4_mcp.tools.core.optimization import (
    OptimizationTool,
    OptimizationToolInput,
    optimize_geometry,
)


__all__ = [
    # Base
    "BaseTool",
    "ToolInput",
    "ToolOutput",
    "ToolMetadata",
    "ToolCategory",
    "ToolStatus",
    "ToolRegistry",
    "register_tool",
    "get_tool",
    "list_tools",
    "run_tool",
    # Energy
    "EnergyTool",
    "EnergyToolInput",
    "calculate_energy",
    # Gradient
    "GradientTool",
    "GradientToolInput",
    "calculate_gradient",
    # Hessian
    "HessianTool",
    "HessianToolInput",
    "calculate_hessian",
    # Optimization
    "OptimizationTool",
    "OptimizationToolInput",
    "optimize_geometry",
]
