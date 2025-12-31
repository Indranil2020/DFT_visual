"""
Psi4 MCP Server - Model Context Protocol Server for Psi4 Quantum Chemistry.

A comprehensive MCP server providing 124 quantum chemistry tools for:
- Energy calculations (HF, DFT, MP2, CCSD, CCSD(T), FCI)
- Geometry optimization
- Vibrational analysis (frequencies, thermochemistry)
- Molecular properties (dipole, charges, orbitals)
- Spectroscopy (IR, Raman, UV-Vis, NMR, EPR)
- Excited states (TD-DFT, EOM-CCSD, ADC)
- Intermolecular interactions (SAPT)
- Solvation models (PCM, SMD)
- And much more...

Usage:
    # As MCP server
    python -m psi4_mcp.server
    
    # Import models directly
    from psi4_mcp.models import CalculationInput, CalculationOutput
    
See https://github.com/your-repo/psi4-mcp-server for documentation.
"""

from psi4_mcp.__version__ import __version__, __version_info__

__all__ = [
    "__version__",
    "__version_info__",
]
