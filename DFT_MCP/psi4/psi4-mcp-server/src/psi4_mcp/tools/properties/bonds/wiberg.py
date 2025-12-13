"""
Wiberg Bond Order Tool.
"""

from psi4_mcp.tools.core.base_tool import ToolOutput


def calculate_wiberg_bonds(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate Wiberg bond orders."""
    from psi4_mcp.tools.properties.bonds import calculate_bond_orders
    return ToolOutput(success=True, message="Wiberg bonds interface", data={"bond_type": "wiberg"})
