"""
EPR Spectroscopy Tools Package.

MCP tools for Electron Paramagnetic Resonance calculations:
    - g-tensor
    - Hyperfine coupling constants
    - Zero-field splitting
"""

from psi4_mcp.tools.spectroscopy.epr.g_tensor import (
    GTensorTool,
    calculate_g_tensor,
)

from psi4_mcp.tools.spectroscopy.epr.hyperfine import (
    HyperfineTool,
    calculate_hyperfine,
)

from psi4_mcp.tools.spectroscopy.epr.zero_field import (
    ZeroFieldSplittingTool,
    calculate_zero_field_splitting,
)


__all__ = [
    "GTensorTool",
    "HyperfineTool",
    "ZeroFieldSplittingTool",
    "calculate_g_tensor",
    "calculate_hyperfine",
    "calculate_zero_field_splitting",
]
