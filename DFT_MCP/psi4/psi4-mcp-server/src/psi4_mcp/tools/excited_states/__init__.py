"""
Excited States Tools Package.

MCP tools for computing electronic excited states:
    - TD-DFT (Time-Dependent Density Functional Theory)
    - TDA (Tamm-Dancoff Approximation)
    - CIS (Configuration Interaction Singles)
    - ADC (Algebraic Diagrammatic Construction)
    - EOM-CC (Equation of Motion Coupled Cluster)
    - Excited state geometry optimization
    - Transition properties
"""

from psi4_mcp.tools.excited_states.tddft import (
    TDDFTTool,
    calculate_tddft,
)

from psi4_mcp.tools.excited_states.tda import (
    TDATool,
    calculate_tda,
)

from psi4_mcp.tools.excited_states.cis import (
    CISTool,
    calculate_cis,
)

from psi4_mcp.tools.excited_states.adc import (
    ADCTool,
    calculate_adc,
)

from psi4_mcp.tools.excited_states.eom_cc import (
    EOMCCTool,
    calculate_eom_cc,
)

from psi4_mcp.tools.excited_states.excited_opt import (
    ExcitedOptTool,
    optimize_excited_state,
)

from psi4_mcp.tools.excited_states.transition_properties import (
    TransitionPropertiesTool,
    calculate_transition_properties,
)


__all__ = [
    # TD-DFT
    "TDDFTTool",
    "calculate_tddft",
    # TDA
    "TDATool",
    "calculate_tda",
    # CIS
    "CISTool",
    "calculate_cis",
    # ADC
    "ADCTool",
    "calculate_adc",
    # EOM-CC
    "EOMCCTool",
    "calculate_eom_cc",
    # Excited optimization
    "ExcitedOptTool",
    "optimize_excited_state",
    # Transition properties
    "TransitionPropertiesTool",
    "calculate_transition_properties",
]
