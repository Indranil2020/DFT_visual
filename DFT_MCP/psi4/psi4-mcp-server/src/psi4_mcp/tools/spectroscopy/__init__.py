"""
Spectroscopy Tools Package.

MCP tools for computing various spectroscopic properties:
    - IR/Raman vibrational spectroscopy
    - UV-Vis electronic absorption
    - ECD (Electronic Circular Dichroism)
    - ORD (Optical Rotatory Dispersion)
    - NMR (Nuclear Magnetic Resonance)
    - EPR (Electron Paramagnetic Resonance)
"""

# Main spectroscopy tools
from psi4_mcp.tools.spectroscopy.ir_raman import (
    IRRamanTool,
    calculate_ir_spectrum,
    calculate_raman_spectrum,
)

from psi4_mcp.tools.spectroscopy.uv_vis import (
    UVVisTool,
    calculate_uv_vis_spectrum,
)

from psi4_mcp.tools.spectroscopy.ecd import (
    ECDTool,
    calculate_ecd_spectrum,
)

from psi4_mcp.tools.spectroscopy.ord import (
    ORDTool,
    calculate_ord_spectrum,
)

# NMR subpackage
from psi4_mcp.tools.spectroscopy.nmr import (
    NMRShieldingTool,
    NMRCouplingTool,
    calculate_nmr_shielding,
    calculate_nmr_coupling,
    simulate_nmr_spectrum,
)

# EPR subpackage
from psi4_mcp.tools.spectroscopy.epr import (
    GTensorTool,
    HyperfineTool,
    calculate_g_tensor,
    calculate_hyperfine,
)


__all__ = [
    # IR/Raman
    "IRRamanTool",
    "calculate_ir_spectrum",
    "calculate_raman_spectrum",
    # UV-Vis
    "UVVisTool",
    "calculate_uv_vis_spectrum",
    # ECD
    "ECDTool",
    "calculate_ecd_spectrum",
    # ORD
    "ORDTool",
    "calculate_ord_spectrum",
    # NMR
    "NMRShieldingTool",
    "NMRCouplingTool",
    "calculate_nmr_shielding",
    "calculate_nmr_coupling",
    "simulate_nmr_spectrum",
    # EPR
    "GTensorTool",
    "HyperfineTool",
    "calculate_g_tensor",
    "calculate_hyperfine",
]
