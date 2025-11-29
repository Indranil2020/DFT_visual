"""
Output Models for Psi4 MCP Server.

This package provides comprehensive Pydantic models for representing
results from various quantum chemistry calculations.

Submodules:
    - energy: Energy calculation outputs
    - optimization: Geometry optimization outputs
    - frequencies: Vibrational frequency outputs
    - orbitals: Molecular orbital outputs
    - properties: Molecular property outputs
    - spectrum: Spectroscopy outputs
    - coupled_cluster: CC method outputs
    - sapt: SAPT outputs
    - tddft: TDDFT and excited state outputs
    - analysis: Wavefunction analysis outputs

Example Usage:
    from psi4_mcp.models.outputs import (
        TotalEnergyOutput,
        OptimizationOutput,
        FrequencyOutput,
        SAPTOutput,
        TDDFTOutput,
    )
"""

# Energy outputs
from psi4_mcp.models.outputs.energy import (
    SCFEnergyComponents,
    SCFConvergence,
    SCFEnergyOutput,
    MP2EnergyComponents,
    CCEnergyComponents,
    CorrelationConvergence,
    CorrelationEnergyOutput,
    DFTEnergyComponents,
    DFTEnergyOutput,
    TotalEnergyOutput,
    RelativeEnergy,
    RelativeEnergyOutput,
)

# Optimization outputs
from psi4_mcp.models.outputs.optimization import (
    GradientInfo,
    DisplacementInfo,
    ConvergenceCriteria,
    ConvergenceStatus,
    OptimizationStep,
    OptimizationTrajectory,
    InternalCoordinateValue,
    InternalCoordinates,
    OptimizationOutput,
    TransitionStateOutput,
    IRCPoint,
    IRCOutput,
)

# Frequency outputs
from psi4_mcp.models.outputs.frequencies import (
    VibrationalMode,
    FrequencySummary,
    MomentOfInertia,
    ThermodynamicQuantities,
    ThermodynamicComponents,
    ThermodynamicsOutput,
    FrequencyOutput,
    AnharmonicMode,
    AnharmonicOutput,
)

# Orbital outputs
from psi4_mcp.models.outputs.orbitals import (
    MolecularOrbital,
    OrbitalSet,
    OrbitalOutput,
    AtomicCharge,
    AtomicPopulation,
    PopulationAnalysis,
    BondOrder,
    BondOrderAnalysis,
    NaturalBondOrbital,
    NBOInteraction,
    NaturalAtomicOrbital,
    NBOOutput,
)

# Property outputs
from psi4_mcp.models.outputs.properties import (
    DipoleMomentOutput,
    QuadrupoleMomentOutput,
    OctupoleMomentOutput,
    MultipoleOutput,
    PolarizabilityOutput,
    HyperpolarizabilityOutput,
    SecondHyperpolarizabilityOutput,
    OpticalRotationOutput,
    ElectrostaticPotentialPoint,
    ElectrostaticOutput,
    PropertyOutput,
)

# Spectrum outputs
from psi4_mcp.models.outputs.spectrum import (
    IRPeak,
    IRSpectrum,
    RamanPeak,
    RamanSpectrum,
    ElectronicTransition,
    UVVisSpectrum,
    CDSpectrum,
    NMRShielding,
    NMRCoupling,
    NMROutput,
    EPRGTensor,
    HyperfineCoupling,
    EPROutput,
)

# Coupled cluster outputs
from psi4_mcp.models.outputs.coupled_cluster import (
    CCAmplitudes,
    CCDiagnostics,
    CCConvergence,
    CCSDOutput,
    CCSDTOutput,
    EOMCCState,
    EOMCCOutput,
    CC2Output,
    DLPNOOutput,
)

# SAPT outputs
from psi4_mcp.models.outputs.sapt import (
    SAPTFirstOrder,
    SAPTSecondOrder,
    SAPTHigherOrder,
    SAPTEnergyComponents,
    SAPT0Output,
    SAPT2Output,
    SAPT2PlusOutput,
    SAPT2Plus3Output,
    FSAPTFragment,
    FSAPTPairInteraction,
    FSAPTOutput,
    SAPTOutput,
)

# TDDFT outputs
from psi4_mcp.models.outputs.tddft import (
    OrbitalTransition,
    NaturalTransitionOrbital,
    ExcitedStateCharacter,
    TDDFTState,
    TDDFTConvergence,
    TDDFTOutput,
    ADCState,
    ADCOutput,
    CISOutput,
)

# Analysis outputs
from psi4_mcp.models.outputs.analysis import (
    CriticalPoint,
    DensityGridPoint,
    DensityAnalysis,
    AIMAtom,
    AIMBond,
    AIMOutput,
    ELFBasin,
    ELFOutput,
    LocalizedOrbital,
    LocalizedOrbitalsOutput,
    SpinDensityAnalysis,
    FukuiFunctions,
)


__all__ = [
    # Energy
    "SCFEnergyComponents",
    "SCFConvergence",
    "SCFEnergyOutput",
    "MP2EnergyComponents",
    "CCEnergyComponents",
    "CorrelationConvergence",
    "CorrelationEnergyOutput",
    "DFTEnergyComponents",
    "DFTEnergyOutput",
    "TotalEnergyOutput",
    "RelativeEnergy",
    "RelativeEnergyOutput",
    
    # Optimization
    "GradientInfo",
    "DisplacementInfo",
    "ConvergenceCriteria",
    "ConvergenceStatus",
    "OptimizationStep",
    "OptimizationTrajectory",
    "InternalCoordinateValue",
    "InternalCoordinates",
    "OptimizationOutput",
    "TransitionStateOutput",
    "IRCPoint",
    "IRCOutput",
    
    # Frequencies
    "VibrationalMode",
    "FrequencySummary",
    "MomentOfInertia",
    "ThermodynamicQuantities",
    "ThermodynamicComponents",
    "ThermodynamicsOutput",
    "FrequencyOutput",
    "AnharmonicMode",
    "AnharmonicOutput",
    
    # Orbitals
    "MolecularOrbital",
    "OrbitalSet",
    "OrbitalOutput",
    "AtomicCharge",
    "AtomicPopulation",
    "PopulationAnalysis",
    "BondOrder",
    "BondOrderAnalysis",
    "NaturalBondOrbital",
    "NBOInteraction",
    "NaturalAtomicOrbital",
    "NBOOutput",
    
    # Properties
    "DipoleMomentOutput",
    "QuadrupoleMomentOutput",
    "OctupoleMomentOutput",
    "MultipoleOutput",
    "PolarizabilityOutput",
    "HyperpolarizabilityOutput",
    "SecondHyperpolarizabilityOutput",
    "OpticalRotationOutput",
    "ElectrostaticPotentialPoint",
    "ElectrostaticOutput",
    "PropertyOutput",
    
    # Spectrum
    "IRPeak",
    "IRSpectrum",
    "RamanPeak",
    "RamanSpectrum",
    "ElectronicTransition",
    "UVVisSpectrum",
    "CDSpectrum",
    "NMRShielding",
    "NMRCoupling",
    "NMROutput",
    "EPRGTensor",
    "HyperfineCoupling",
    "EPROutput",
    
    # Coupled Cluster
    "CCAmplitudes",
    "CCDiagnostics",
    "CCConvergence",
    "CCSDOutput",
    "CCSDTOutput",
    "EOMCCState",
    "EOMCCOutput",
    "CC2Output",
    "DLPNOOutput",
    
    # SAPT
    "SAPTFirstOrder",
    "SAPTSecondOrder",
    "SAPTHigherOrder",
    "SAPTEnergyComponents",
    "SAPT0Output",
    "SAPT2Output",
    "SAPT2PlusOutput",
    "SAPT2Plus3Output",
    "FSAPTFragment",
    "FSAPTPairInteraction",
    "FSAPTOutput",
    "SAPTOutput",
    
    # TDDFT
    "OrbitalTransition",
    "NaturalTransitionOrbital",
    "ExcitedStateCharacter",
    "TDDFTState",
    "TDDFTConvergence",
    "TDDFTOutput",
    "ADCState",
    "ADCOutput",
    "CISOutput",
    
    # Analysis
    "CriticalPoint",
    "DensityGridPoint",
    "DensityAnalysis",
    "AIMAtom",
    "AIMBond",
    "AIMOutput",
    "ELFBasin",
    "ELFOutput",
    "LocalizedOrbital",
    "LocalizedOrbitalsOutput",
    "SpinDensityAnalysis",
    "FukuiFunctions",
]
