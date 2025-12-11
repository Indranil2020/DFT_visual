"""
Calculation Models Package.

This package contains Pydantic models for all calculation types:
    - Energy calculations
    - Geometry optimization
    - Frequency analysis
    - Molecular properties
    - SAPT analysis
    - TDDFT excited states
    - Configuration Interaction
    - Coupled Cluster
    - MCSCF methods
    - Response properties
    - Solvation models

Example Usage:
    from psi4_mcp.models.calculations import (
        EnergyInput,
        OptimizationInput,
        FrequencyInput,
        SAPTInput,
        TDDFTInput,
        CCSDInput,
        CASSCFInput,
    )
"""

# Energy inputs
from psi4_mcp.models.calculations.energy import (
    MoleculeInput,
    EnergyInput,
    SCFInput,
    DFTInput,
    MP2Input,
    CoupledClusterInput as CCInput,
    CIInput as CIEnergyInput,
    CompositeInput,
    CBSInput,
    RelativeEnergyInput,
    SolvatedEnergyInput,
)

# Optimization inputs
from psi4_mcp.models.calculations.optimization import (
    FrozenCoordinate,
    FixedCoordinate,
    CartesianConstraint,
    OptimizationInput,
    ConstrainedOptimizationInput,
    TransitionStateInput,
    IRCInput,
    ScanCoordinate,
    ScanInput,
    BatchOptimizationInput,
)

# Frequency inputs
from psi4_mcp.models.calculations.frequencies import (
    FrequencyInput,
    ThermochemistryInput,
    MultiTemperatureInput,
    AnharmonicInput,
    HessianInput,
    NormalModeInput,
    IsotopeFrequencyInput,
)

# Property inputs
from psi4_mcp.models.calculations.properties import (
    PropertyInput,
    MultipoleInput,
    PolarizabilityInput as PropertyPolarizabilityInput,
    HyperpolarizabilityInput as PropertyHyperpolarizabilityInput,
    ResponseInput as PropertyResponseInput,
    PopulationInput,
    NBOInput,
    ESPInput,
    OrbitalAnalysisInput,
)

# SAPT inputs
from psi4_mcp.models.calculations.sapt import (
    SAPTMonomer,
    SAPTDimer,
    SAPTInput,
    FSAPTFragment,
    FSAPTInput,
    ISAPTInput,
    SAPTScanInput,
    InteractionEnergyInput,
    EDAInput,
)

# TDDFT inputs
from psi4_mcp.models.calculations.tddft import (
    TDDFTInput,
    TDAInput,
    EOMCCInput as TDDFTEOMCCInput,
    CISInput,
    ADCInput,
    NTOInput,
    ExcitedStateOptInput,
    SpinFlipInput,
)

# Configuration Interaction
from psi4_mcp.models.calculations.configuration_interaction import (
    CIInput,
    CISDInput,
    CISDTInput,
    FCIInput,
    DETCIInput,
    CIOutput,
    CISDOutput,
    FCIOutput,
    CIRoot,
)

# Coupled Cluster
from psi4_mcp.models.calculations.coupled_cluster import (
    CoupledClusterInput,
    CC2Input,
    CCSDInput,
    CCSD_T_Input,
    CC3Input,
    CCSDTInput,
    EOMCCInput,
    CoupledClusterOutput,
    CCSDOutput,
    CCSD_T_Output,
    EOMCCOutput,
    EOMCCState,
    CCAmplitudes,
    CCConvergence,
)

# MCSCF methods
from psi4_mcp.models.calculations.mcscf import (
    MCSCFInput,
    CASSCFInput,
    RASSCFInput,
    ActiveSpace,
    MCSCFOutput,
    CASSCFOutput,
    RASSCFOutput,
    MCSCFRoot,
    MCSCFConvergence,
)

# Response properties
from psi4_mcp.models.calculations.response import (
    ResponseInput,
    PolarizabilityInput,
    HyperpolarizabilityInput,
    OpticalRotationInput,
    NMRShieldingInput,
    EPRGTensorInput,
    PolarizabilityOutput,
    PolarizabilityTensor,
    DynamicPolarizability,
    HyperpolarizabilityOutput,
    OpticalRotationOutput,
    NMRShieldingOutput,
    NMRShielding,
    EPRGTensorOutput,
    EPRGTensor,
)

# Solvation models
from psi4_mcp.models.calculations.solvation import (
    SolvationInput,
    PCMInput,
    CPCMInput,
    IEFPCMInput,
    SMDInput,
    ddCOSMOInput,
    Solvent,
    COMMON_SOLVENTS,
    SolvationOutput,
    SolvationEnergy,
    PCMOutput,
    SMDOutput,
)


__all__ = [
    # Energy
    "MoleculeInput",
    "EnergyInput",
    "SCFInput",
    "DFTInput",
    "MP2Input",
    "CCInput",
    "CIEnergyInput",
    "CompositeInput",
    "CBSInput",
    "RelativeEnergyInput",
    "SolvatedEnergyInput",
    
    # Optimization
    "FrozenCoordinate",
    "FixedCoordinate",
    "CartesianConstraint",
    "OptimizationInput",
    "ConstrainedOptimizationInput",
    "TransitionStateInput",
    "IRCInput",
    "ScanCoordinate",
    "ScanInput",
    "BatchOptimizationInput",
    
    # Frequencies
    "FrequencyInput",
    "ThermochemistryInput",
    "MultiTemperatureInput",
    "AnharmonicInput",
    "HessianInput",
    "NormalModeInput",
    "IsotopeFrequencyInput",
    
    # Properties
    "PropertyInput",
    "MultipoleInput",
    "PropertyPolarizabilityInput",
    "PropertyHyperpolarizabilityInput",
    "PropertyResponseInput",
    "PopulationInput",
    "NBOInput",
    "ESPInput",
    "OrbitalAnalysisInput",
    
    # SAPT
    "SAPTMonomer",
    "SAPTDimer",
    "SAPTInput",
    "FSAPTFragment",
    "FSAPTInput",
    "ISAPTInput",
    "SAPTScanInput",
    "InteractionEnergyInput",
    "EDAInput",
    
    # TDDFT
    "TDDFTInput",
    "TDAInput",
    "TDDFTEOMCCInput",
    "CISInput",
    "ADCInput",
    "NTOInput",
    "ExcitedStateOptInput",
    "SpinFlipInput",
    
    # CI
    "CIInput",
    "CISDInput",
    "CISDTInput",
    "FCIInput",
    "DETCIInput",
    "CIOutput",
    "CISDOutput",
    "FCIOutput",
    "CIRoot",
    
    # CC
    "CoupledClusterInput",
    "CC2Input",
    "CCSDInput",
    "CCSD_T_Input",
    "CC3Input",
    "CCSDTInput",
    "EOMCCInput",
    "CoupledClusterOutput",
    "CCSDOutput",
    "CCSD_T_Output",
    "EOMCCOutput",
    "EOMCCState",
    "CCAmplitudes",
    "CCConvergence",
    
    # MCSCF
    "MCSCFInput",
    "CASSCFInput",
    "RASSCFInput",
    "ActiveSpace",
    "MCSCFOutput",
    "CASSCFOutput",
    "RASSCFOutput",
    "MCSCFRoot",
    "MCSCFConvergence",
    
    # Response
    "ResponseInput",
    "PolarizabilityInput",
    "HyperpolarizabilityInput",
    "OpticalRotationInput",
    "NMRShieldingInput",
    "EPRGTensorInput",
    "PolarizabilityOutput",
    "PolarizabilityTensor",
    "DynamicPolarizability",
    "HyperpolarizabilityOutput",
    "OpticalRotationOutput",
    "NMRShieldingOutput",
    "NMRShielding",
    "EPRGTensorOutput",
    "EPRGTensor",
    
    # Solvation
    "SolvationInput",
    "PCMInput",
    "CPCMInput",
    "IEFPCMInput",
    "SMDInput",
    "ddCOSMOInput",
    "Solvent",
    "COMMON_SOLVENTS",
    "SolvationOutput",
    "SolvationEnergy",
    "PCMOutput",
    "SMDOutput",
]
