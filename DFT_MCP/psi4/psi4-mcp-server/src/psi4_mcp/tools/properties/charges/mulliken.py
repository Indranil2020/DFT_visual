"""
Mulliken Charges Tool.
"""

from psi4_mcp.tools.core.base_tool import ToolOutput


class MullikenChargesTool:
    """Tool for Mulliken charge calculations."""
    pass


def calculate_mulliken_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate Mulliken charges."""
    from psi4_mcp.tools.properties.charges import calculate_charges
    return calculate_charges(geometry, method, basis, charge_types=["mulliken"], **kwargs)
