"""
ESP Charges Tool.
"""

from psi4_mcp.tools.core.base_tool import ToolOutput


class ESPChargesTool:
    """Tool for ESP charge calculations."""
    pass


def calculate_esp_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate ESP charges."""
    from psi4_mcp.tools.properties.charges import calculate_charges
    return calculate_charges(geometry, method, basis, charge_types=["esp"], **kwargs)
