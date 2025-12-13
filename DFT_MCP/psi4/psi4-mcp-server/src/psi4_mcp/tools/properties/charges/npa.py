"""
NPA Charges Tool.
"""

from psi4_mcp.tools.core.base_tool import ToolOutput


class NPAChargesTool:
    """Tool for NPA charge calculations."""
    pass


def calculate_npa_charges(geometry: str, method: str = "hf", basis: str = "cc-pvdz", **kwargs) -> ToolOutput:
    """Calculate NPA charges."""
    from psi4_mcp.tools.properties.charges import calculate_charges
    return calculate_charges(geometry, method, basis, charge_types=["npa"], **kwargs)
