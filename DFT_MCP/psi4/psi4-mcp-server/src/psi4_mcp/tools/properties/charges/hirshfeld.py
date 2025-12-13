"""
Hirshfeld Charges Tool.
"""

from psi4_mcp.tools.core.base_tool import ToolOutput


class HirshfeldChargesTool:
    """Tool for Hirshfeld charge calculations."""
    pass


def calculate_hirshfeld_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate Hirshfeld charges."""
    from psi4_mcp.tools.properties.charges import calculate_charges
    return calculate_charges(geometry, method, basis, charge_types=["hirshfeld"], **kwargs)
