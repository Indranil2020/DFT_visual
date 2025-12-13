"""
Properties Tools Package.

This package provides tools for molecular property calculations:
    - Electric moments (dipole, quadrupole)
    - Polarizability
    - Atomic charges (Mulliken, Löwdin, ESP, NPA)
    - Bond orders (Wiberg, Mayer)
    - Orbitals and populations
    - Electrostatic properties
"""

from psi4_mcp.tools.properties.electric_moments import (
    DipoleTool,
    DipoleMomentToolInput,
    calculate_dipole,
    MultipoleTool,
    MultipoleToolInput,
    calculate_multipoles,
)

from psi4_mcp.tools.properties.polarizability import (
    PolarizabilityTool,
    PolarizabilityToolInput,
    calculate_polarizability,
)

from psi4_mcp.tools.properties.orbitals import (
    OrbitalsTool,
    OrbitalsToolInput,
    calculate_orbitals,
)

from psi4_mcp.tools.properties.bonds import (
    BondOrderTool,
    BondOrderToolInput,
    calculate_bond_orders,
)

from psi4_mcp.tools.properties.electrostatic import (
    ESPTool,
    ESPToolInput,
    calculate_esp,
)

from psi4_mcp.tools.properties.spin_properties import (
    SpinPropertiesTool,
    SpinPropertiesToolInput,
    calculate_spin_properties,
)

# Import charge tools from subpackage
from psi4_mcp.tools.properties.charges import (
    ChargesTool,
    ChargesToolInput,
    calculate_charges,
    calculate_mulliken_charges,
    calculate_lowdin_charges,
    calculate_esp_charges,
    calculate_npa_charges,
)


__all__ = [
    # Electric moments
    "DipoleTool",
    "DipoleMomentToolInput",
    "calculate_dipole",
    "MultipoleTool",
    "MultipoleToolInput",
    "calculate_multipoles",
    # Polarizability
    "PolarizabilityTool",
    "PolarizabilityToolInput",
    "calculate_polarizability",
    # Orbitals
    "OrbitalsTool",
    "OrbitalsToolInput",
    "calculate_orbitals",
    # Bonds
    "BondOrderTool",
    "BondOrderToolInput",
    "calculate_bond_orders",
    # Electrostatic
    "ESPTool",
    "ESPToolInput",
    "calculate_esp",
    # Spin
    "SpinPropertiesTool",
    "SpinPropertiesToolInput",
    "calculate_spin_properties",
    # Charges
    "ChargesTool",
    "ChargesToolInput",
    "calculate_charges",
    "calculate_mulliken_charges",
    "calculate_lowdin_charges",
    "calculate_esp_charges",
    "calculate_npa_charges",
]
