"""
Enumeration Types for Psi4 MCP Server.

This package provides comprehensive enumeration types for all aspects
of quantum chemistry calculations, including methods, basis sets,
reference types, and property types.

Modules:
    references: Reference wavefunction types (RHF, UHF, ROHF, etc.)
    methods: Quantum chemistry methods (HF, DFT, MP2, CCSD, etc.)
    basis_sets: Basis set families and specific basis sets
    properties: Molecular property types

Example Usage:
    from psi4_mcp.models.enums import (
        ReferenceType,
        DFTFunctional,
        BasisSet,
        ChargeType,
    )
    
    # Use enums for type-safe configuration
    reference = ReferenceType.RHF
    functional = DFTFunctional.B3LYP
    basis = BasisSet.CC_PVTZ
    charge_method = ChargeType.MULLIKEN
"""

# Reference types
from psi4_mcp.models.enums.references import (
    ReferenceType,
    SpinMultiplicity,
    OrbitalOccupation,
    SpinState,
    REFERENCE_METHOD_COMPATIBILITY,
    DEFAULT_REFERENCES,
    suggest_reference,
    validate_multiplicity_electrons,
    get_n_alpha_beta,
)

# Methods
from psi4_mcp.models.enums.methods import (
    MethodCategory,
    HFMethod,
    DFTFunctionalType,
    DFTFunctional,
    PerturbationMethod,
    CoupledClusterMethod,
    CIMethod,
    MCSCFMethod,
    SAPTMethod,
    TDDFTMethod,
    CompositeMethod,
    Method,
    METHOD_SCALING,
    METHOD_ACCURACY,
    is_dft_method,
    is_post_hf_method,
    requires_reference,
    get_method_description,
)

# Basis sets
from psi4_mcp.models.enums.basis_sets import (
    BasisSetFamily,
    BasisSetSize,
    MinimalBasis,
    PopleBasis,
    DunningBasis,
    KarlsruheBasis,
    JensenBasis,
    AuxiliaryBasis,
    ECPBasis,
    BasisSet,
    RECOMMENDED_BASIS,
    MINIMUM_BASIS,
    get_matching_auxiliary_basis,
    estimate_basis_functions,
    validate_basis_for_elements,
)

# Properties
from psi4_mcp.models.enums.properties import (
    PropertyCategory,
    ElectronicProperty,
    ChargeType,
    BondOrderType,
    OrbitalType,
    DipoleMomentType,
    MultipoleType,
    ResponseProperty,
    SpectroscopyType,
    ThermodynamicProperty,
    GeometricProperty,
    VibrationalProperty,
    ExcitedStateProperty,
    InteractionProperty,
    SAPTComponent,
    WavefunctionProperty,
    ConvergenceProperty,
    FREQUENCY_REQUIRED_PROPERTIES,
    RESPONSE_REQUIRED_PROPERTIES,
    EXCITED_STATE_REQUIRED_PROPERTIES,
    get_property_category,
    requires_frequency_calculation,
    requires_response_calculation,
    requires_excited_state_calculation,
    get_property_unit,
)


__all__ = [
    # References
    "ReferenceType",
    "SpinMultiplicity",
    "OrbitalOccupation",
    "SpinState",
    "REFERENCE_METHOD_COMPATIBILITY",
    "DEFAULT_REFERENCES",
    "suggest_reference",
    "validate_multiplicity_electrons",
    "get_n_alpha_beta",
    
    # Methods
    "MethodCategory",
    "HFMethod",
    "DFTFunctionalType",
    "DFTFunctional",
    "PerturbationMethod",
    "CoupledClusterMethod",
    "CIMethod",
    "MCSCFMethod",
    "SAPTMethod",
    "TDDFTMethod",
    "CompositeMethod",
    "Method",
    "METHOD_SCALING",
    "METHOD_ACCURACY",
    "is_dft_method",
    "is_post_hf_method",
    "requires_reference",
    "get_method_description",
    
    # Basis sets
    "BasisSetFamily",
    "BasisSetSize",
    "MinimalBasis",
    "PopleBasis",
    "DunningBasis",
    "KarlsruheBasis",
    "JensenBasis",
    "AuxiliaryBasis",
    "ECPBasis",
    "BasisSet",
    "RECOMMENDED_BASIS",
    "MINIMUM_BASIS",
    "get_matching_auxiliary_basis",
    "estimate_basis_functions",
    "validate_basis_for_elements",
    
    # Properties
    "PropertyCategory",
    "ElectronicProperty",
    "ChargeType",
    "BondOrderType",
    "OrbitalType",
    "DipoleMomentType",
    "MultipoleType",
    "ResponseProperty",
    "SpectroscopyType",
    "ThermodynamicProperty",
    "GeometricProperty",
    "VibrationalProperty",
    "ExcitedStateProperty",
    "InteractionProperty",
    "SAPTComponent",
    "WavefunctionProperty",
    "ConvergenceProperty",
    "FREQUENCY_REQUIRED_PROPERTIES",
    "RESPONSE_REQUIRED_PROPERTIES",
    "EXCITED_STATE_REQUIRED_PROPERTIES",
    "get_property_category",
    "requires_frequency_calculation",
    "requires_response_calculation",
    "requires_excited_state_calculation",
    "get_property_unit",
]
