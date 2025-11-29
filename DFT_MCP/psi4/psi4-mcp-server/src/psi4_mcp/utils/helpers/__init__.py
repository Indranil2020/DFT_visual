"""
Helper Utilities for Psi4 MCP Server.

This package provides fundamental utility functions used throughout
the Psi4 MCP server, including:

- Physical and chemical constants
- Unit conversion factors and functions
- Mathematical utilities
- String processing functions

Example Usage:
    from psi4_mcp.utils.helpers import (
        BOHR_TO_ANGSTROM,
        hartree_to_kcal_mol,
        vector_norm,
        normalize_element_symbol,
    )
    
    # Convert coordinates
    angstrom_value = bohr_value * BOHR_TO_ANGSTROM
    
    # Convert energy
    kcal = hartree_to_kcal_mol(-76.123)
    
    # Normalize element
    element = normalize_element_symbol("fe")  # Returns "Fe"
"""

# Physical and chemical constants
from psi4_mcp.utils.helpers.constants import (
    # Fundamental constants
    SPEED_OF_LIGHT,
    PLANCK_CONSTANT,
    HBAR,
    ELEMENTARY_CHARGE,
    ELECTRON_MASS,
    PROTON_MASS,
    ATOMIC_MASS_UNIT,
    AVOGADRO,
    BOLTZMANN,
    GAS_CONSTANT,
    FINE_STRUCTURE,
    BOHR_RADIUS,
    HARTREE,
    
    # Atomic units
    AU_LENGTH,
    AU_ENERGY,
    AU_TIME,
    AU_DIPOLE,
    AU_ELECTRIC_FIELD,
    
    # Energy conversion factors
    HARTREE_TO_EV,
    HARTREE_TO_KJMOL,
    HARTREE_TO_KCALMOL,
    HARTREE_TO_CM,
    HARTREE_TO_KELVIN,
    EV_TO_HARTREE,
    KJMOL_TO_HARTREE,
    KCALMOL_TO_HARTREE,
    CM_TO_HARTREE,
    
    # Length conversion factors
    BOHR_TO_ANGSTROM,
    ANGSTROM_TO_BOHR,
    BOHR_TO_NM,
    BOHR_TO_PM,
    
    # Dipole conversion factors
    AU_TO_DEBYE,
    DEBYE_TO_AU,
    
    # Mass conversion factors
    AMU_TO_ME,
    ME_TO_AMU,
    
    # Thermodynamic constants
    STANDARD_TEMPERATURE,
    STANDARD_PRESSURE,
    
    # Mathematical constants
    PI,
    TWO_PI,
    SQRT2,
    
    # Element data
    ATOMIC_NUMBERS,
    ELEMENT_SYMBOLS,
    ATOMIC_MASSES,
    COVALENT_RADII,
    VDW_RADII,
    MAIN_GROUP_ELEMENTS,
    TRANSITION_METALS,
    LANTHANIDES,
    ACTINIDES,
    NOBLE_GASES,
    HALOGENS,
    
    # Element helper functions
    get_atomic_number,
    get_element_symbol,
    get_atomic_mass,
    get_covalent_radius,
    get_vdw_radius,
    is_valid_element,
    mass_to_atomic_units,
)

# Unit conversion functions
from psi4_mcp.utils.helpers.units import (
    # Unit enumerations
    EnergyUnit,
    LengthUnit,
    AngleUnit,
    TimeUnit,
    MassUnit,
    DipoleUnit,
    PolarizabilityUnit,
    ForceUnit,
    PressureUnit,
    
    # Generic conversion functions
    convert_energy,
    convert_length,
    convert_angle,
    convert_time,
    convert_mass,
    convert_dipole,
    convert_polarizability,
    convert_force,
    convert_pressure,
    
    # Convenience energy conversions
    hartree_to_ev,
    ev_to_hartree,
    hartree_to_kcal_mol,
    kcal_mol_to_hartree,
    hartree_to_kj_mol,
    kj_mol_to_hartree,
    hartree_to_cm_inv,
    cm_inv_to_hartree,
    hartree_to_kelvin,
    kelvin_to_hartree,
    ev_to_cm_inv,
    cm_inv_to_ev,
    ev_to_nm,
    nm_to_ev,
    cm_inv_to_nm,
    nm_to_cm_inv,
    
    # Convenience length conversions
    bohr_to_angstrom,
    angstrom_to_bohr,
    bohr_to_nm,
    nm_to_bohr,
    angstrom_to_nm,
    nm_to_angstrom,
    
    # Angle conversions
    degrees_to_radians,
    radians_to_degrees,
    
    # Dipole conversions
    au_to_debye,
    debye_to_au,
    
    # Force conversions
    hartree_bohr_to_ev_angstrom,
    ev_angstrom_to_hartree_bohr,
    
    # Frequency conversions
    cm_inv_to_thz,
    thz_to_cm_inv,
    cm_inv_to_mev,
    mev_to_cm_inv,
    
    # Thermodynamic conversions
    celsius_to_kelvin,
    kelvin_to_celsius,
    atm_to_pascal,
    pascal_to_atm,
    bar_to_pascal,
    pascal_to_bar,
    
    # Mass conversions
    amu_to_kg,
    kg_to_amu,
    amu_to_electron_mass,
    electron_mass_to_amu,
    
    # Unit label functions
    get_energy_unit_label,
    get_length_unit_label,
    get_angle_unit_label,
)

# Mathematical utilities
from psi4_mcp.utils.helpers.math_utils import (
    # Basic math
    clamp,
    lerp,
    sign,
    is_close,
    safe_divide,
    safe_sqrt,
    safe_log,
    factorial,
    double_factorial,
    binomial,
    
    # Vector operations
    dot_product,
    vector_norm,
    vector_normalize,
    vector_add,
    vector_subtract,
    vector_scale,
    cross_product,
    distance,
    angle_between_vectors,
    
    # Matrix operations
    matrix_multiply_vector,
    matrix_transpose,
    matrix_trace,
    identity_matrix,
    determinant_3x3,
    
    # Statistical functions
    mean,
    variance,
    std_dev,
    rms,
    max_abs,
    median,
    
    # Special functions
    erf,
    erfc,
    gamma_function,
    boys_function,
    
    # Numerical methods
    newton_raphson,
    bisection,
    numerical_derivative,
    trapezoidal_integration,
)

# String utilities
from psi4_mcp.utils.helpers.string_utils import (
    # Element symbol handling
    normalize_element_symbol,
    is_valid_element_symbol,
    parse_element_and_isotope,
    
    # Coordinate parsing
    parse_xyz_line,
    format_xyz_line,
    parse_geometry_string,
    
    # Number formatting
    is_numeric_string,
    parse_float_safe,
    format_scientific,
    format_fixed,
    format_energy,
    
    # Text processing
    clean_whitespace,
    remove_comments,
    indent_text,
    wrap_text,
    
    # Identifier manipulation
    to_snake_case,
    to_camel_case,
    to_pascal_case,
    sanitize_filename,
    truncate,
    
    # Table formatting
    format_table,
    format_key_value_pairs,
    
    # Molecular formula
    parse_molecular_formula,
    format_molecular_formula,
)


__all__ = [
    # Constants
    "SPEED_OF_LIGHT",
    "PLANCK_CONSTANT",
    "HBAR",
    "ELEMENTARY_CHARGE",
    "ELECTRON_MASS",
    "PROTON_MASS",
    "ATOMIC_MASS_UNIT",
    "AVOGADRO",
    "BOLTZMANN",
    "GAS_CONSTANT",
    "FINE_STRUCTURE",
    "BOHR_RADIUS",
    "HARTREE",
    "AU_LENGTH",
    "AU_ENERGY",
    "AU_TIME",
    "AU_DIPOLE",
    "AU_ELECTRIC_FIELD",
    "HARTREE_TO_EV",
    "HARTREE_TO_KJMOL",
    "HARTREE_TO_KCALMOL",
    "HARTREE_TO_CM",
    "HARTREE_TO_KELVIN",
    "EV_TO_HARTREE",
    "KJMOL_TO_HARTREE",
    "KCALMOL_TO_HARTREE",
    "CM_TO_HARTREE",
    "BOHR_TO_ANGSTROM",
    "ANGSTROM_TO_BOHR",
    "BOHR_TO_NM",
    "BOHR_TO_PM",
    "AU_TO_DEBYE",
    "DEBYE_TO_AU",
    "AMU_TO_ME",
    "ME_TO_AMU",
    "STANDARD_TEMPERATURE",
    "STANDARD_PRESSURE",
    "PI",
    "TWO_PI",
    "SQRT2",
    "ATOMIC_NUMBERS",
    "ELEMENT_SYMBOLS",
    "ATOMIC_MASSES",
    "COVALENT_RADII",
    "VDW_RADII",
    "MAIN_GROUP_ELEMENTS",
    "TRANSITION_METALS",
    "LANTHANIDES",
    "ACTINIDES",
    "NOBLE_GASES",
    "HALOGENS",
    "get_atomic_number",
    "get_element_symbol",
    "get_atomic_mass",
    "get_covalent_radius",
    "get_vdw_radius",
    "is_valid_element",
    "mass_to_atomic_units",
    
    # Unit conversions
    "EnergyUnit",
    "LengthUnit",
    "AngleUnit",
    "TimeUnit",
    "MassUnit",
    "DipoleUnit",
    "PolarizabilityUnit",
    "ForceUnit",
    "PressureUnit",
    "convert_energy",
    "convert_length",
    "convert_angle",
    "convert_time",
    "convert_mass",
    "convert_dipole",
    "convert_polarizability",
    "convert_force",
    "convert_pressure",
    "hartree_to_ev",
    "ev_to_hartree",
    "hartree_to_kcal_mol",
    "kcal_mol_to_hartree",
    "hartree_to_kj_mol",
    "kj_mol_to_hartree",
    "hartree_to_cm_inv",
    "cm_inv_to_hartree",
    "hartree_to_kelvin",
    "kelvin_to_hartree",
    "ev_to_cm_inv",
    "cm_inv_to_ev",
    "ev_to_nm",
    "nm_to_ev",
    "cm_inv_to_nm",
    "nm_to_cm_inv",
    "bohr_to_angstrom",
    "angstrom_to_bohr",
    "bohr_to_nm",
    "nm_to_bohr",
    "angstrom_to_nm",
    "nm_to_angstrom",
    "degrees_to_radians",
    "radians_to_degrees",
    "au_to_debye",
    "debye_to_au",
    "hartree_bohr_to_ev_angstrom",
    "ev_angstrom_to_hartree_bohr",
    "cm_inv_to_thz",
    "thz_to_cm_inv",
    "cm_inv_to_mev",
    "mev_to_cm_inv",
    "celsius_to_kelvin",
    "kelvin_to_celsius",
    "atm_to_pascal",
    "pascal_to_atm",
    "bar_to_pascal",
    "pascal_to_bar",
    "amu_to_kg",
    "kg_to_amu",
    "amu_to_electron_mass",
    "electron_mass_to_amu",
    "get_energy_unit_label",
    "get_length_unit_label",
    "get_angle_unit_label",
    
    # Math utilities
    "clamp",
    "lerp",
    "sign",
    "is_close",
    "safe_divide",
    "safe_sqrt",
    "safe_log",
    "factorial",
    "double_factorial",
    "binomial",
    "dot_product",
    "vector_norm",
    "vector_normalize",
    "vector_add",
    "vector_subtract",
    "vector_scale",
    "cross_product",
    "distance",
    "angle_between_vectors",
    "matrix_multiply_vector",
    "matrix_transpose",
    "matrix_trace",
    "identity_matrix",
    "determinant_3x3",
    "mean",
    "variance",
    "std_dev",
    "rms",
    "max_abs",
    "median",
    "erf",
    "erfc",
    "gamma_function",
    "boys_function",
    "newton_raphson",
    "bisection",
    "numerical_derivative",
    "trapezoidal_integration",
    
    # String utilities
    "normalize_element_symbol",
    "is_valid_element_symbol",
    "parse_element_and_isotope",
    "parse_xyz_line",
    "format_xyz_line",
    "parse_geometry_string",
    "is_numeric_string",
    "parse_float_safe",
    "format_scientific",
    "format_fixed",
    "format_energy",
    "clean_whitespace",
    "remove_comments",
    "indent_text",
    "wrap_text",
    "to_snake_case",
    "to_camel_case",
    "to_pascal_case",
    "sanitize_filename",
    "truncate",
    "format_table",
    "format_key_value_pairs",
    "parse_molecular_formula",
    "format_molecular_formula",
]
