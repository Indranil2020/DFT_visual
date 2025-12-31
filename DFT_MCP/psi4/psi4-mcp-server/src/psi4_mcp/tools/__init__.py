"""
Psi4 MCP Tools Package.

This package provides all MCP tools for quantum chemistry calculations.
Each tool is designed to be called via the MCP protocol.

Tool Categories:
    - core: Energy, gradient, hessian, optimization
    - vibrational: Frequencies, thermochemistry, anharmonic, VCD
    - properties: Electric moments, charges, bonds, orbitals
    - spectroscopy: NMR, EPR, IR/Raman, UV-Vis
    - excited_states: TDDFT, EOM-CC, CIS, ADC
    - coupled_cluster: CCSD, CCSD(T), CC2, CC3, EOM methods
    - perturbation_theory: MP2-MP4, DF-MP2, SCS-MP2
    - configuration_interaction: CISD, FCI, DETCI
    - mcscf: CASSCF, RASSCF
    - sapt: SAPT0-SAPT2+3, F-SAPT
    - solvation: PCM, CPCM, SMD
    - dft: Functionals, dispersion, range-separated
    - basis_sets: Info, extrapolation, composite
    - analysis: Population, localization, wavefunction
    - composite: G1-G4, W1, CBS-QB3
    - advanced: QM/MM, ONIOM, EFP, scans
    - utilities: Batch runner, converter, workflow
"""

from typing import TYPE_CHECKING

# Core tools
from psi4_mcp.tools.core import (
    calculate_energy,
    calculate_gradient,
    calculate_hessian,
    optimize_geometry,
    EnergyTool,
    GradientTool,
    HessianTool,
    OptimizationTool,
)

# Vibrational tools
from psi4_mcp.tools.vibrational import (
    calculate_frequencies,
    calculate_thermochemistry,
    FrequencyTool,
    ThermochemistryTool,
)

# Property tools
from psi4_mcp.tools.properties import (
    calculate_dipole,
    calculate_multipoles,
    calculate_polarizability,
    calculate_charges,
    calculate_bond_orders,
    DipoleTool,
    MultipoleTool,
    PolarizabilityTool,
    ChargesTool,
    BondOrderTool,
)

# Excited state tools
from psi4_mcp.tools.excited_states import (
    calculate_tddft,
    calculate_eom_ccsd,
    calculate_cis,
    TDDFTTool,
    EOMCCSDTool,
    CISTool,
)

# Coupled cluster tools
from psi4_mcp.tools.coupled_cluster import (
    calculate_ccsd,
    calculate_ccsd_t,
    calculate_cc2,
    CCSDTool,
    CCSDT_Tool,
    CC2Tool,
)

# Perturbation theory tools
from psi4_mcp.tools.perturbation_theory import (
    calculate_mp2,
    calculate_mp3,
    calculate_mp4,
    MP2Tool,
    MP3Tool,
    MP4Tool,
)

# SAPT tools
from psi4_mcp.tools.sapt import (
    calculate_sapt0,
    calculate_sapt2,
    calculate_sapt2_plus,
    SAPT0Tool,
    SAPT2Tool,
    SAPT2PlusTool,
)

# Solvation tools
from psi4_mcp.tools.solvation import (
    calculate_pcm,
    calculate_smd,
    PCMTool,
    SMDTool,
)

# DFT tools
from psi4_mcp.tools.dft import (
    calculate_dft_energy,
    scan_functional,
    DFTEnergyTool,
    FunctionalScanTool,
)

# Utility tools
from psi4_mcp.tools.utilities import (
    convert_geometry,
    batch_calculate,
    FormatConverterTool,
    BatchRunnerTool,
)

# Base tool class
from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolMetadata,
    ToolRegistry,
    register_tool,
    get_tool,
    list_tools,
)


__all__ = [
    # Base
    "BaseTool",
    "ToolInput",
    "ToolOutput",
    "ToolMetadata",
    "ToolRegistry",
    "register_tool",
    "get_tool",
    "list_tools",
    # Core
    "calculate_energy",
    "calculate_gradient",
    "calculate_hessian",
    "optimize_geometry",
    "EnergyTool",
    "GradientTool",
    "HessianTool",
    "OptimizationTool",
    # Vibrational
    "calculate_frequencies",
    "calculate_thermochemistry",
    "FrequencyTool",
    "ThermochemistryTool",
    # Properties
    "calculate_dipole",
    "calculate_multipoles",
    "calculate_polarizability",
    "calculate_charges",
    "calculate_bond_orders",
    "DipoleTool",
    "MultipoleTool",
    "PolarizabilityTool",
    "ChargesTool",
    "BondOrderTool",
    # Excited states
    "calculate_tddft",
    "calculate_eom_ccsd",
    "calculate_cis",
    "TDDFTTool",
    "EOMCCSDTool",
    "CISTool",
    # Coupled cluster
    "calculate_ccsd",
    "calculate_ccsd_t",
    "calculate_cc2",
    "CCSDTool",
    "CCSDT_Tool",
    "CC2Tool",
    # Perturbation theory
    "calculate_mp2",
    "calculate_mp3",
    "calculate_mp4",
    "MP2Tool",
    "MP3Tool",
    "MP4Tool",
    # SAPT
    "calculate_sapt0",
    "calculate_sapt2",
    "calculate_sapt2_plus",
    "SAPT0Tool",
    "SAPT2Tool",
    "SAPT2PlusTool",
    # Solvation
    "calculate_pcm",
    "calculate_smd",
    "PCMTool",
    "SMDTool",
    # DFT
    "calculate_dft_energy",
    "scan_functional",
    "DFTEnergyTool",
    "FunctionalScanTool",
    # Utilities
    "convert_geometry",
    "batch_calculate",
    "FormatConverterTool",
    "BatchRunnerTool",
]
