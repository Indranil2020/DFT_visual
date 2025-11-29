"""
Conversion Utilities for Psi4 MCP Server.

This package provides comprehensive conversion utilities for:

- Unit conversions (energy, length, angle, etc.)
- Geometry format conversions (XYZ, Z-matrix, Psi4, PDB)
- Basis set name normalization and validation
- Output format conversions (JSON, text, CSV, QCSchema)

Example Usage:
    from psi4_mcp.utils.conversion import (
        # Unit conversions
        EnergyValue,
        LengthValue,
        convert_energy_array,
        parse_energy_string,
        
        # Geometry conversions
        Geometry,
        Atom,
        parse_xyz,
        geometry_to_psi4,
        
        # Basis set utilities
        normalize_basis_name,
        select_auxiliary_basis,
        
        # Output formatting
        to_json,
        format_energy_report,
    )
    
    # Parse an XYZ file
    geom = parse_xyz(xyz_content)
    
    # Convert to Psi4 format
    psi4_string = geometry_to_psi4(geom)
    
    # Format energy with unit conversion
    energy = EnergyValue.from_hartree(-76.123)
    print(f"Energy: {energy.to_kcal_mol()} kcal/mol")
"""

# Unit conversion utilities
from psi4_mcp.utils.conversion.units import (
    # Data classes
    ValueWithUnit,
    EnergyValue,
    LengthValue,
    
    # Unit detection
    detect_energy_unit,
    detect_length_unit,
    detect_angle_unit,
    
    # Batch conversions
    convert_energy_array,
    convert_length_array,
    convert_coordinates_to_bohr,
    convert_coordinates_to_angstrom,
    convert_gradient_to_hartree_bohr,
    convert_hessian_to_hartree_bohr2,
    
    # String parsing
    parse_energy_string,
    parse_length_string,
    
    # Table formatting
    format_energy_table,
    format_length_table,
)

# Geometry conversion utilities
from psi4_mcp.utils.conversion.geometry import (
    # Enums
    CoordinateFormat,
    LengthUnitType,
    
    # Data classes
    Atom,
    Geometry,
    InternalCoordinate,
    BondLength,
    BondAngle,
    DihedralAngle,
    
    # XYZ format
    parse_xyz,
    geometry_to_xyz,
    
    # Psi4 format
    parse_psi4_geometry,
    geometry_to_psi4,
    
    # Internal coordinates
    calculate_bond_length,
    calculate_bond_angle,
    calculate_dihedral_angle,
    get_all_bond_lengths,
    
    # Validation and comparison
    validate_geometry,
    geometries_are_similar,
    calculate_rmsd,
)

# Basis set utilities
from psi4_mcp.utils.conversion.basis_sets import (
    # Data classes
    BasisSetSpecification,
    BasisFunction,
    ElementBasis,
    CBSExtrapolation,
    
    # Name parsing
    normalize_basis_name,
    parse_basis_name,
    get_zeta_level,
    
    # Auxiliary basis
    select_auxiliary_basis,
    
    # Validation
    validate_basis_for_elements,
    suggest_basis_for_system,
    
    # CBS extrapolation
    get_cbs_pair,
)

# Output formatting utilities
from psi4_mcp.utils.conversion.output import (
    # Enums
    OutputFormat,
    ReportStyle,
    
    # Data classes
    OutputConfig,
    CalculationMetadata,
    EnergyResult,
    
    # JSON
    ResultEncoder,
    to_json,
    from_json,
    
    # Text reports
    format_energy_report,
    format_time,
    
    # Table formatting
    format_data_table,
    format_csv,
    format_markdown_table,
    
    # QCSchema
    to_qcschema_result,
    from_qcschema_result,
    
    # Utility functions
    truncate_float,
    format_scientific,
    format_fixed,
    format_with_uncertainty,
)


__all__ = [
    # Unit conversions
    "ValueWithUnit",
    "EnergyValue",
    "LengthValue",
    "detect_energy_unit",
    "detect_length_unit",
    "detect_angle_unit",
    "convert_energy_array",
    "convert_length_array",
    "convert_coordinates_to_bohr",
    "convert_coordinates_to_angstrom",
    "convert_gradient_to_hartree_bohr",
    "convert_hessian_to_hartree_bohr2",
    "parse_energy_string",
    "parse_length_string",
    "format_energy_table",
    "format_length_table",
    
    # Geometry conversions
    "CoordinateFormat",
    "LengthUnitType",
    "Atom",
    "Geometry",
    "InternalCoordinate",
    "BondLength",
    "BondAngle",
    "DihedralAngle",
    "parse_xyz",
    "geometry_to_xyz",
    "parse_psi4_geometry",
    "geometry_to_psi4",
    "calculate_bond_length",
    "calculate_bond_angle",
    "calculate_dihedral_angle",
    "get_all_bond_lengths",
    "validate_geometry",
    "geometries_are_similar",
    "calculate_rmsd",
    
    # Basis set utilities
    "BasisSetSpecification",
    "BasisFunction",
    "ElementBasis",
    "CBSExtrapolation",
    "normalize_basis_name",
    "parse_basis_name",
    "get_zeta_level",
    "select_auxiliary_basis",
    "validate_basis_for_elements",
    "suggest_basis_for_system",
    "get_cbs_pair",
    
    # Output formatting
    "OutputFormat",
    "ReportStyle",
    "OutputConfig",
    "CalculationMetadata",
    "EnergyResult",
    "ResultEncoder",
    "to_json",
    "from_json",
    "format_energy_report",
    "format_time",
    "format_data_table",
    "format_csv",
    "format_markdown_table",
    "to_qcschema_result",
    "from_qcschema_result",
    "truncate_float",
    "format_scientific",
    "format_fixed",
    "format_with_uncertainty",
]
