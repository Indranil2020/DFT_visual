"""
Lowdin Charges Tool.
"""

from psi4_mcp.tools.core.base_tool import ToolOutput


class LowdinChargesTool:
    """Tool for Lowdin charge calculations."""
    pass


def calculate_lowdin_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate Lowdin charges."""
    from psi4_mcp.tools.properties.charges import calculate_charges
    return calculate_charges(geometry, method, basis, charge_types=["lowdin"], **kwargs)
