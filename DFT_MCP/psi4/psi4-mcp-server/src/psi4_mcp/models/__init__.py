"""
Data Models for Psi4 MCP Server.

This package provides comprehensive Pydantic data models for quantum
chemistry calculations, including:

- Base models and common types
- Error and result handling
- Molecule representations
- Calculation options
- Enumeration types
- Output models (in subpackages)
- Calculation input models (in subpackages)

Example Usage:
    from psi4_mcp.models import (
        Molecule,
        CalculationOptions,
        SCFOptions,
        EnergyComponents,
        Result,
    )
    
    # Create a molecule
    mol = Molecule.from_xyz_string(xyz_content)
    
    # Configure calculation
    opts = CalculationOptions(
        scf=SCFOptions(reference="rhf", maxiter=100),
    )
"""

# Base models
from psi4_mcp.models.base import (
    # Base classes
    Psi4BaseModel,
    StrictModel,
    CalculationInput,
    CalculationOutput,
    ResourceModel,
    ToolInput,
    ToolOutput,
    
    # Coordinate types
    Coordinate3D,
    AtomSpec,
    MoleculeSpec,
    
    # Energy and property types
    EnergyComponents,
    DipoleMoment,
    OrbitalInfo,
    ConvergenceInfo,
    
    # Metadata
    VersionInfo,
    CalculationMetadataModel,
)

# Error handling
from psi4_mcp.models.errors import (
    # Categories and severity
    ErrorCategory,
    ErrorSeverity,
    ConvergenceType,
    
    # Error classes
    ErrorContext,
    RecoverySuggestion,
    CalculationError,
    
    # Result type
    Result,
    
    # Error factories
    input_error,
    validation_error,
    convergence_error,
    resource_error,
    method_error,
    basis_set_error,
    geometry_error,
    warning,
)

# Molecule models
from psi4_mcp.models.molecules import (
    AtomicPosition,
    Molecule,
    MolecularSystem,
)

# Option models
from psi4_mcp.models.options import (
    SCFOptions,
    DFTOptions,
    CorrelationOptions,
    OptimizationOptions,
    FrequencyOptions,
    PropertyOptions,
    SolvationOptions,
    CalculationOptions,
)

# Resources
from psi4_mcp.models.resources import (
    Resource,
    ResourceType,
    ResourceCategory,
    BasisSetResource,
    MethodResource,
    FunctionalResource,
    MoleculeResource,
    BenchmarkResource,
    LiteratureResource,
    TutorialResource,
    ResourceRegistry,
)

# Enumeration types (re-export from enums subpackage)
from psi4_mcp.models.enums import (
    # References
    ReferenceType,
    SpinMultiplicity,
    OrbitalOccupation,
    SpinState,
    
    # Methods
    MethodCategory,
    DFTFunctional,
    DFTFunctionalType,
    PerturbationMethod,
    CoupledClusterMethod,
    CIMethod,
    MCSCFMethod,
    SAPTMethod,
    TDDFTMethod,
    CompositeMethod,
    Method,
    
    # Basis sets
    BasisSetFamily,
    BasisSetSize,
    BasisSet,
    DunningBasis,
    KarlsruheBasis,
    PopleBasis,
    AuxiliaryBasis,
    
    # Properties
    PropertyCategory,
    ElectronicProperty,
    ChargeType,
    BondOrderType,
    OrbitalType,
    SpectroscopyType,
    ThermodynamicProperty,
    VibrationalProperty,
    ExcitedStateProperty,
)


__all__ = [
    # Base models
    "Psi4BaseModel",
    "StrictModel",
    "CalculationInput",
    "CalculationOutput",
    "ResourceModel",
    "ToolInput",
    "ToolOutput",
    "Coordinate3D",
    "AtomSpec",
    "MoleculeSpec",
    "EnergyComponents",
    "DipoleMoment",
    "OrbitalInfo",
    "ConvergenceInfo",
    "VersionInfo",
    "CalculationMetadataModel",
    
    # Errors
    "ErrorCategory",
    "ErrorSeverity",
    "ConvergenceType",
    "ErrorContext",
    "RecoverySuggestion",
    "CalculationError",
    "Result",
    "input_error",
    "validation_error",
    "convergence_error",
    "resource_error",
    "method_error",
    "basis_set_error",
    "geometry_error",
    "warning",
    
    # Molecules
    "AtomicPosition",
    "Molecule",
    "MolecularSystem",
    
    # Options
    "SCFOptions",
    "DFTOptions",
    "CorrelationOptions",
    "OptimizationOptions",
    "FrequencyOptions",
    "PropertyOptions",
    "SolvationOptions",
    "CalculationOptions",
    
    # Enums - References
    "ReferenceType",
    "SpinMultiplicity",
    "OrbitalOccupation",
    "SpinState",
    
    # Enums - Methods
    "MethodCategory",
    "DFTFunctional",
    "DFTFunctionalType",
    "PerturbationMethod",
    "CoupledClusterMethod",
    "CIMethod",
    "MCSCFMethod",
    "SAPTMethod",
    "TDDFTMethod",
    "CompositeMethod",
    "Method",
    
    # Enums - Basis sets
    "BasisSetFamily",
    "BasisSetSize",
    "BasisSet",
    "DunningBasis",
    "KarlsruheBasis",
    "PopleBasis",
    "AuxiliaryBasis",
    
    # Enums - Properties
    "PropertyCategory",
    "ElectronicProperty",
    "ChargeType",
    "BondOrderType",
    "OrbitalType",
    "SpectroscopyType",
    "ThermodynamicProperty",
    "VibrationalProperty",
    "ExcitedStateProperty",
    
    # Resources
    "Resource",
    "ResourceType",
    "ResourceCategory",
    "BasisSetResource",
    "MethodResource",
    "FunctionalResource",
    "MoleculeResource",
    "BenchmarkResource",
    "LiteratureResource",
    "TutorialResource",
    "ResourceRegistry",
]
