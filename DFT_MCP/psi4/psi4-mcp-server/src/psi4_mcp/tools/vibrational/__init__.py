"""
Vibrational Tools Package.

This package provides tools for vibrational analysis:
    - Harmonic frequency calculations
    - Thermochemistry analysis
    - Anharmonic corrections (VPT2)
    - Vibrational Circular Dichroism (VCD)
"""

from psi4_mcp.tools.vibrational.frequencies import (
    FrequencyTool,
    FrequencyToolInput,
    calculate_frequencies,
)

from psi4_mcp.tools.vibrational.thermochemistry import (
    ThermochemistryTool,
    ThermochemistryToolInput,
    calculate_thermochemistry,
)

from psi4_mcp.tools.vibrational.anharmonic import (
    AnharmonicTool,
    AnharmonicToolInput,
    calculate_anharmonic,
)

from psi4_mcp.tools.vibrational.vcd import (
    VCDTool,
    VCDToolInput,
    calculate_vcd,
)


__all__ = [
    # Frequencies
    "FrequencyTool",
    "FrequencyToolInput",
    "calculate_frequencies",
    # Thermochemistry
    "ThermochemistryTool",
    "ThermochemistryToolInput",
    "calculate_thermochemistry",
    # Anharmonic
    "AnharmonicTool",
    "AnharmonicToolInput",
    "calculate_anharmonic",
    # VCD
    "VCDTool",
    "VCDToolInput",
    "calculate_vcd",
]
