"""
Basis Set Utilities for Psi4 MCP Server.

This module provides utilities for working with basis sets, including:
- Basis set generation and manipulation
- Basis set library access
- Basis set optimization
- Basis set file parsing

Example Usage:
    from psi4_mcp.utils.basis import (
        BasisSetLibrary,
        BasisFunction,
        parse_gbs_file,
        generate_even_tempered_basis,
    )
"""

from psi4_mcp.utils.basis.library import (
    BasisSetLibrary,
    BasisSetInfo,
    BasisSetFamily,
    BasisSetSize,
    get_basis_set_info,
    list_basis_sets,
    get_recommended_basis,
    is_basis_available,
    get_elements_supported,
)

from psi4_mcp.utils.basis.generator import (
    BasisFunction,
    ContractedFunction,
    ShellType,
    generate_even_tempered_basis,
    generate_well_tempered_basis,
    decontract_basis,
    augment_basis,
    create_minimal_basis,
)

from psi4_mcp.utils.basis.parser import (
    parse_gbs_file,
    parse_nwchem_basis,
    parse_gaussian_basis,
    format_gbs_output,
    format_nwchem_output,
    BasisSetData,
    ElementBasis,
)

from psi4_mcp.utils.basis.optimizer import (
    BasisOptimizer,
    OptimizationTarget,
    optimize_exponents,
    optimize_contraction_coefficients,
    optimize_basis_for_property,
)

__all__ = [
    # Library
    "BasisSetLibrary",
    "BasisSetInfo",
    "BasisSetFamily",
    "BasisSetSize",
    "get_basis_set_info",
    "list_basis_sets",
    "get_recommended_basis",
    "is_basis_available",
    "get_elements_supported",
    
    # Generator
    "BasisFunction",
    "ContractedFunction",
    "ShellType",
    "generate_even_tempered_basis",
    "generate_well_tempered_basis",
    "decontract_basis",
    "augment_basis",
    "create_minimal_basis",
    
    # Parser
    "parse_gbs_file",
    "parse_nwchem_basis",
    "parse_gaussian_basis",
    "format_gbs_output",
    "format_nwchem_output",
    "BasisSetData",
    "ElementBasis",
    
    # Optimizer
    "BasisOptimizer",
    "OptimizationTarget",
    "optimize_exponents",
    "optimize_contraction_coefficients",
    "optimize_basis_for_property",
]
