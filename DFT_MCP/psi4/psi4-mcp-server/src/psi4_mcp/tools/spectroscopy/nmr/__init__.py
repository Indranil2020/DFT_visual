"""
NMR Spectroscopy Tools Package.

MCP tools for Nuclear Magnetic Resonance calculations:
    - Chemical shielding tensors
    - Spin-spin coupling constants (J-coupling)
    - NMR spectrum simulation
"""

from psi4_mcp.tools.spectroscopy.nmr.shielding import (
    NMRShieldingTool,
    calculate_nmr_shielding,
)

from psi4_mcp.tools.spectroscopy.nmr.coupling import (
    NMRCouplingTool,
    calculate_nmr_coupling,
)

from psi4_mcp.tools.spectroscopy.nmr.spectra import (
    NMRSpectrumTool,
    simulate_nmr_spectrum,
)


__all__ = [
    "NMRShieldingTool",
    "NMRCouplingTool",
    "NMRSpectrumTool",
    "calculate_nmr_shielding",
    "calculate_nmr_coupling",
    "simulate_nmr_spectrum",
]
