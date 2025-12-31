"""
Psi4 MCP Server Utilities Package.

This package provides comprehensive utility functions and classes for the
Psi4 MCP server, organized into the following submodules:

Submodules:
    - basis: Basis set utilities (generation, parsing, optimization)
    - caching: Result and molecular caching systems
    - convergence: SCF and optimization convergence helpers
    - conversion: Format and unit conversion utilities
    - error_handling: Error detection, recovery, and suggestions
    - geometry: Molecular geometry manipulation and analysis
    - helpers: Constants, math, strings, and unit helpers
    - logging: Logging configuration and formatters
    - memory: Memory estimation and management
    - molecular: Molecular descriptors and similarity
    - parallel: Parallelization utilities
    - parsing: Output file parsing utilities
    - validation: Input validation utilities
    - visualization: Molecular and spectral visualization

Example Usage:
    from psi4_mcp.utils import (
        # Helpers
        BOHR_TO_ANGSTROM,
        hartree_to_ev,
        vector_norm,
        
        # Validation
        validate_geometry,
        validate_basis_set,
        
        # Parsing
        parse_energy_output,
        parse_frequencies,
        
        # Geometry
        calculate_distance,
        align_molecules,
    )
"""

from typing import List

# Version
__version__ = "1.0.0"

# Lazy imports to avoid circular dependencies
# Individual submodules should be imported as needed:
#   from psi4_mcp.utils.helpers import BOHR_TO_ANGSTROM
#   from psi4_mcp.utils.validation import validate_geometry


__all__: List[str] = [
    # Submodule names
    "basis",
    "caching",
    "convergence",
    "conversion",
    "error_handling",
    "geometry",
    "helpers",
    "logging",
    "memory",
    "molecular",
    "parallel",
    "parsing",
    "validation",
    "visualization",
]
