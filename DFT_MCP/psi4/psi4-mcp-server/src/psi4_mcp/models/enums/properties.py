"""
Property Type Enumerations for Quantum Chemistry Calculations.

This module defines enumerations for all types of molecular properties
that can be computed using Psi4, including electronic, geometric,
spectroscopic, and response properties.

Property Categories:
    - Electronic: Energies, charges, populations, orbitals
    - Geometric: Bond lengths, angles, dihedrals
    - Spectroscopic: NMR, IR, Raman, UV-Vis
    - Response: Polarizabilities, hyperpolarizabilities
    - Thermodynamic: Enthalpies, entropies, free energies
"""

from enum import Enum, auto
from typing import Final


class PropertyCategory(str, Enum):
    """
    High-level categorization of molecular properties.
    
    Attributes:
        ELECTRONIC: Electronic structure properties
        GEOMETRIC: Molecular geometry properties
        ENERGETIC: Energy-related properties
        SPECTROSCOPIC: Spectroscopic properties
        RESPONSE: Response properties (linear and nonlinear)
        THERMODYNAMIC: Thermodynamic properties
        BONDING: Chemical bonding analysis
        MAGNETIC: Magnetic properties
    """
    ELECTRONIC = "electronic"
    GEOMETRIC = "geometric"
    ENERGETIC = "energetic"
    SPECTROSCOPIC = "spectroscopic"
    RESPONSE = "response"
    THERMODYNAMIC = "thermodynamic"
    BONDING = "bonding"
    MAGNETIC = "magnetic"


class ElectronicProperty(str, Enum):
    """
    Electronic structure properties.
    
    Attributes:
        TOTAL_ENERGY: Total electronic energy
        CORRELATION_ENERGY: Electron correlation energy
        HF_ENERGY: Hartree-Fock energy
        NUCLEAR_REPULSION: Nuclear repulsion energy
        ONE_ELECTRON_ENERGY: One-electron energy
        TWO_ELECTRON_ENERGY: Two-electron energy
        KINETIC_ENERGY: Electronic kinetic energy
        HOMO_ENERGY: HOMO orbital energy
        LUMO_ENERGY: LUMO orbital energy
        HOMO_LUMO_GAP: HOMO-LUMO gap
        IONIZATION_POTENTIAL: Vertical ionization potential
        ELECTRON_AFFINITY: Vertical electron affinity
    """
    TOTAL_ENERGY = "total_energy"
    CORRELATION_ENERGY = "correlation_energy"
    HF_ENERGY = "hf_energy"
    NUCLEAR_REPULSION = "nuclear_repulsion"
    ONE_ELECTRON_ENERGY = "one_electron_energy"
    TWO_ELECTRON_ENERGY = "two_electron_energy"
    KINETIC_ENERGY = "kinetic_energy"
    HOMO_ENERGY = "homo_energy"
    LUMO_ENERGY = "lumo_energy"
    HOMO_LUMO_GAP = "homo_lumo_gap"
    IONIZATION_POTENTIAL = "ionization_potential"
    ELECTRON_AFFINITY = "electron_affinity"


class ChargeType(str, Enum):
    """
    Types of atomic partial charges.
    
    Attributes:
        MULLIKEN: Mulliken population analysis charges
        LOWDIN: Löwdin population analysis charges
        NPA: Natural Population Analysis charges
        ESP: Electrostatic potential fitted charges
        RESP: Restrained ESP charges
        HIRSHFELD: Hirshfeld partitioning charges
        CM5: Charge Model 5 charges
        MBIS: Minimal Basis Iterative Stockholder charges
        CHELPG: Charges from Electrostatic Potentials Grid
    """
    MULLIKEN = "mulliken"
    LOWDIN = "lowdin"
    NPA = "npa"
    ESP = "esp"
    RESP = "resp"
    HIRSHFELD = "hirshfeld"
    CM5 = "cm5"
    MBIS = "mbis"
    CHELPG = "chelpg"


class BondOrderType(str, Enum):
    """
    Types of bond order analyses.
    
    Attributes:
        WIBERG: Wiberg bond indices (from NBO analysis)
        MAYER: Mayer bond orders
        FUZZY: Fuzzy atom bond orders
        NBO: Natural Bond Orbital bond orders
        LAPLACIAN: Laplacian bond indices
    """
    WIBERG = "wiberg"
    MAYER = "mayer"
    FUZZY = "fuzzy"
    NBO = "nbo"
    LAPLACIAN = "laplacian"


class OrbitalType(str, Enum):
    """
    Types of molecular orbitals.
    
    Attributes:
        CANONICAL: Canonical (delocalized) MOs
        NATURAL: Natural orbitals
        LOCALIZED: Localized MOs
        BOYS: Boys localized orbitals
        PIPEK_MEZEY: Pipek-Mezey localized orbitals
        IBO: Intrinsic Bond Orbitals
        NBO: Natural Bond Orbitals
        FOSTER_BOYS: Foster-Boys localized orbitals
        EDMISTON_RUEDENBERG: Edmiston-Ruedenberg localized orbitals
    """
    CANONICAL = "canonical"
    NATURAL = "natural"
    LOCALIZED = "localized"
    BOYS = "boys"
    PIPEK_MEZEY = "pipek_mezey"
    IBO = "ibo"
    NBO = "nbo"
    FOSTER_BOYS = "foster_boys"
    EDMISTON_RUEDENBERG = "edmiston_ruedenberg"


class DipoleMomentType(str, Enum):
    """
    Types of dipole moment calculations.
    
    Attributes:
        SCF: SCF/DFT dipole moment (expectation value)
        MP2: MP2 relaxed dipole moment
        CCSD: CCSD relaxed dipole moment
        CCSD_T: CCSD(T) relaxed dipole moment
        CI: CI dipole moment
        TRANSITION: Transition dipole moment
    """
    SCF = "scf"
    MP2 = "mp2"
    CCSD = "ccsd"
    CCSD_T = "ccsd_t"
    CI = "ci"
    TRANSITION = "transition"


class MultipoleType(str, Enum):
    """
    Types of electric multipole moments.
    
    Attributes:
        DIPOLE: Electric dipole moment (1st order)
        QUADRUPOLE: Electric quadrupole moment (2nd order)
        OCTUPOLE: Electric octupole moment (3rd order)
        HEXADECAPOLE: Electric hexadecapole moment (4th order)
    """
    DIPOLE = "dipole"
    QUADRUPOLE = "quadrupole"
    OCTUPOLE = "octupole"
    HEXADECAPOLE = "hexadecapole"


class ResponseProperty(str, Enum):
    """
    Linear and nonlinear response properties.
    
    Attributes:
        POLARIZABILITY: Static electric polarizability (α)
        HYPERPOLARIZABILITY_BETA: First hyperpolarizability (β)
        HYPERPOLARIZABILITY_GAMMA: Second hyperpolarizability (γ)
        OPTICAL_ROTATION: Optical rotation
        MAGNETO_OPTICAL: Magneto-optical rotation
        RAMAN_ACTIVITY: Raman scattering activity
        ROA: Raman Optical Activity
        VCD: Vibrational Circular Dichroism intensity
        ECD: Electronic Circular Dichroism
    """
    POLARIZABILITY = "polarizability"
    HYPERPOLARIZABILITY_BETA = "hyperpolarizability_beta"
    HYPERPOLARIZABILITY_GAMMA = "hyperpolarizability_gamma"
    OPTICAL_ROTATION = "optical_rotation"
    MAGNETO_OPTICAL = "magneto_optical"
    RAMAN_ACTIVITY = "raman_activity"
    ROA = "roa"
    VCD = "vcd"
    ECD = "ecd"


class SpectroscopyType(str, Enum):
    """
    Types of spectroscopic calculations.
    
    Attributes:
        IR: Infrared spectroscopy
        RAMAN: Raman spectroscopy
        UV_VIS: UV-Visible absorption
        ECD: Electronic Circular Dichroism
        VCD: Vibrational Circular Dichroism
        NMR_SHIELDING: NMR chemical shielding
        NMR_COUPLING: NMR spin-spin coupling
        EPR_G_TENSOR: EPR g-tensor
        EPR_A_TENSOR: EPR hyperfine coupling (A-tensor)
        EPR_D_TENSOR: EPR zero-field splitting (D-tensor)
        MOSSBAUER: Mössbauer spectroscopy parameters
        FLUORESCENCE: Fluorescence spectra
        PHOSPHORESCENCE: Phosphorescence spectra
    """
    IR = "ir"
    RAMAN = "raman"
    UV_VIS = "uv_vis"
    ECD = "ecd"
    VCD = "vcd"
    NMR_SHIELDING = "nmr_shielding"
    NMR_COUPLING = "nmr_coupling"
    EPR_G_TENSOR = "epr_g_tensor"
    EPR_A_TENSOR = "epr_a_tensor"
    EPR_D_TENSOR = "epr_d_tensor"
    MOSSBAUER = "mossbauer"
    FLUORESCENCE = "fluorescence"
    PHOSPHORESCENCE = "phosphorescence"


class ThermodynamicProperty(str, Enum):
    """
    Thermodynamic properties from frequency calculations.
    
    Attributes:
        ZPVE: Zero-point vibrational energy
        ENTHALPY: Enthalpy (H)
        ENTROPY: Entropy (S)
        GIBBS_FREE_ENERGY: Gibbs free energy (G)
        INTERNAL_ENERGY: Internal energy (U)
        HEAT_CAPACITY_CV: Heat capacity at constant volume
        HEAT_CAPACITY_CP: Heat capacity at constant pressure
    """
    ZPVE = "zpve"
    ENTHALPY = "enthalpy"
    ENTROPY = "entropy"
    GIBBS_FREE_ENERGY = "gibbs_free_energy"
    INTERNAL_ENERGY = "internal_energy"
    HEAT_CAPACITY_CV = "heat_capacity_cv"
    HEAT_CAPACITY_CP = "heat_capacity_cp"


class GeometricProperty(str, Enum):
    """
    Geometric/structural properties.
    
    Attributes:
        BOND_LENGTH: Interatomic distance
        BOND_ANGLE: Three-atom angle
        DIHEDRAL_ANGLE: Four-atom torsion angle
        OUT_OF_PLANE: Out-of-plane angle
        CARTESIAN_COORDINATES: Cartesian coordinates
        INTERNAL_COORDINATES: Internal coordinates (Z-matrix)
        PRINCIPAL_AXES: Principal moments of inertia and axes
        CENTER_OF_MASS: Center of mass
        ROTATIONAL_CONSTANTS: Rotational constants (A, B, C)
    """
    BOND_LENGTH = "bond_length"
    BOND_ANGLE = "bond_angle"
    DIHEDRAL_ANGLE = "dihedral_angle"
    OUT_OF_PLANE = "out_of_plane"
    CARTESIAN_COORDINATES = "cartesian_coordinates"
    INTERNAL_COORDINATES = "internal_coordinates"
    PRINCIPAL_AXES = "principal_axes"
    CENTER_OF_MASS = "center_of_mass"
    ROTATIONAL_CONSTANTS = "rotational_constants"


class VibrationalProperty(str, Enum):
    """
    Vibrational analysis properties.
    
    Attributes:
        FREQUENCIES: Harmonic vibrational frequencies
        NORMAL_MODES: Normal mode displacements
        IR_INTENSITIES: IR absorption intensities
        RAMAN_INTENSITIES: Raman scattering intensities
        FORCE_CONSTANTS: Harmonic force constants
        ANHARMONIC_FREQUENCIES: Anharmonic frequencies (VPT2)
        FERMI_RESONANCES: Fermi resonance analysis
        ISOTOPE_SHIFTS: Isotopic frequency shifts
    """
    FREQUENCIES = "frequencies"
    NORMAL_MODES = "normal_modes"
    IR_INTENSITIES = "ir_intensities"
    RAMAN_INTENSITIES = "raman_intensities"
    FORCE_CONSTANTS = "force_constants"
    ANHARMONIC_FREQUENCIES = "anharmonic_frequencies"
    FERMI_RESONANCES = "fermi_resonances"
    ISOTOPE_SHIFTS = "isotope_shifts"


class ExcitedStateProperty(str, Enum):
    """
    Excited state properties.
    
    Attributes:
        EXCITATION_ENERGY: Vertical excitation energy
        OSCILLATOR_STRENGTH: Oscillator strength
        TRANSITION_DIPOLE: Transition dipole moment
        ROTATORY_STRENGTH: Rotatory strength (for ECD)
        EXCITED_GRADIENT: Excited state gradient
        STATE_CHARACTER: State character (π→π*, n→π*, CT, etc.)
        NTO: Natural Transition Orbitals
        DETACHMENT_ATTACHMENT: Detachment/attachment densities
    """
    EXCITATION_ENERGY = "excitation_energy"
    OSCILLATOR_STRENGTH = "oscillator_strength"
    TRANSITION_DIPOLE = "transition_dipole"
    ROTATORY_STRENGTH = "rotatory_strength"
    EXCITED_GRADIENT = "excited_gradient"
    STATE_CHARACTER = "state_character"
    NTO = "nto"
    DETACHMENT_ATTACHMENT = "detachment_attachment"


class InteractionProperty(str, Enum):
    """
    Intermolecular interaction properties.
    
    Attributes:
        INTERACTION_ENERGY: Total interaction energy
        ELECTROSTATIC: Electrostatic interaction energy
        EXCHANGE: Exchange repulsion energy
        INDUCTION: Induction energy
        DISPERSION: Dispersion energy
        CHARGE_TRANSFER: Charge transfer energy
        BSSE: Basis set superposition error
        COUNTERPOISE_CORRECTED: Counterpoise-corrected energy
    """
    INTERACTION_ENERGY = "interaction_energy"
    ELECTROSTATIC = "electrostatic"
    EXCHANGE = "exchange"
    INDUCTION = "induction"
    DISPERSION = "dispersion"
    CHARGE_TRANSFER = "charge_transfer"
    BSSE = "bsse"
    COUNTERPOISE_CORRECTED = "counterpoise_corrected"


class SAPTComponent(str, Enum):
    """
    SAPT energy decomposition components.
    
    Attributes:
        ELST: Total electrostatic energy
        ELST10: First-order electrostatic
        EXCH: Total exchange energy
        EXCH10: First-order exchange
        EXCH10_S2: Exchange (S^2 approximation)
        IND: Total induction energy
        IND20: Second-order induction
        EXCH_IND20: Exchange-induction
        DISP: Total dispersion energy
        DISP20: Second-order dispersion
        EXCH_DISP20: Exchange-dispersion
        DELTA_HF: δ(HF) higher-order correction
    """
    ELST = "elst"
    ELST10 = "elst10"
    EXCH = "exch"
    EXCH10 = "exch10"
    EXCH10_S2 = "exch10_s2"
    IND = "ind"
    IND20 = "ind20"
    EXCH_IND20 = "exch_ind20"
    DISP = "disp"
    DISP20 = "disp20"
    EXCH_DISP20 = "exch_disp20"
    DELTA_HF = "delta_hf"


class WavefunctionProperty(str, Enum):
    """
    Wavefunction analysis properties.
    
    Attributes:
        DENSITY_MATRIX: One-particle density matrix
        NATURAL_OCCUPATIONS: Natural orbital occupation numbers
        SPIN_DENSITY: Spin density (alpha - beta)
        ELECTRON_DENSITY: Total electron density
        ELECTROSTATIC_POTENTIAL: Molecular electrostatic potential
        FUKUI_FUNCTION: Fukui reactivity indices
        DUAL_DESCRIPTOR: Dual descriptor (Fukui f+ - f-)
        ELF: Electron Localization Function
        LOL: Localized Orbital Locator
    """
    DENSITY_MATRIX = "density_matrix"
    NATURAL_OCCUPATIONS = "natural_occupations"
    SPIN_DENSITY = "spin_density"
    ELECTRON_DENSITY = "electron_density"
    ELECTROSTATIC_POTENTIAL = "electrostatic_potential"
    FUKUI_FUNCTION = "fukui_function"
    DUAL_DESCRIPTOR = "dual_descriptor"
    ELF = "elf"
    LOL = "lol"


class ConvergenceProperty(str, Enum):
    """
    Calculation convergence properties.
    
    Attributes:
        SCF_ITERATIONS: Number of SCF iterations
        SCF_ENERGY_CHANGE: Final SCF energy change
        SCF_DENSITY_CHANGE: Final density matrix change
        OPT_ITERATIONS: Number of optimization steps
        GRADIENT_NORM: RMS gradient norm
        MAX_GRADIENT: Maximum gradient component
        STEP_SIZE: Optimization step size
        CORRELATION_ITERATIONS: Correlation iterations (CC, CI)
    """
    SCF_ITERATIONS = "scf_iterations"
    SCF_ENERGY_CHANGE = "scf_energy_change"
    SCF_DENSITY_CHANGE = "scf_density_change"
    OPT_ITERATIONS = "opt_iterations"
    GRADIENT_NORM = "gradient_norm"
    MAX_GRADIENT = "max_gradient"
    STEP_SIZE = "step_size"
    CORRELATION_ITERATIONS = "correlation_iterations"


# =============================================================================
# PROPERTY REQUIREMENTS
# =============================================================================

# Properties that require frequency calculations
FREQUENCY_REQUIRED_PROPERTIES: Final[frozenset[str]] = frozenset({
    ThermodynamicProperty.ZPVE.value,
    ThermodynamicProperty.ENTHALPY.value,
    ThermodynamicProperty.ENTROPY.value,
    ThermodynamicProperty.GIBBS_FREE_ENERGY.value,
    ThermodynamicProperty.HEAT_CAPACITY_CV.value,
    ThermodynamicProperty.HEAT_CAPACITY_CP.value,
    VibrationalProperty.FREQUENCIES.value,
    VibrationalProperty.NORMAL_MODES.value,
    VibrationalProperty.IR_INTENSITIES.value,
    VibrationalProperty.FORCE_CONSTANTS.value,
    SpectroscopyType.IR.value,
    SpectroscopyType.RAMAN.value,
    SpectroscopyType.VCD.value,
})

# Properties that require response calculations
RESPONSE_REQUIRED_PROPERTIES: Final[frozenset[str]] = frozenset({
    ResponseProperty.POLARIZABILITY.value,
    ResponseProperty.HYPERPOLARIZABILITY_BETA.value,
    ResponseProperty.HYPERPOLARIZABILITY_GAMMA.value,
    ResponseProperty.OPTICAL_ROTATION.value,
    ResponseProperty.RAMAN_ACTIVITY.value,
    SpectroscopyType.NMR_SHIELDING.value,
    SpectroscopyType.NMR_COUPLING.value,
})

# Properties that require excited state calculations
EXCITED_STATE_REQUIRED_PROPERTIES: Final[frozenset[str]] = frozenset({
    ExcitedStateProperty.EXCITATION_ENERGY.value,
    ExcitedStateProperty.OSCILLATOR_STRENGTH.value,
    ExcitedStateProperty.TRANSITION_DIPOLE.value,
    ExcitedStateProperty.ROTATORY_STRENGTH.value,
    ExcitedStateProperty.NTO.value,
    SpectroscopyType.UV_VIS.value,
    SpectroscopyType.ECD.value,
    SpectroscopyType.FLUORESCENCE.value,
})


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_property_category(property_name: str) -> PropertyCategory:
    """
    Determine the category of a property.
    
    Args:
        property_name: Name of the property.
        
    Returns:
        The PropertyCategory for this property.
    """
    property_lower = property_name.lower()
    
    electronic_keywords = ["energy", "homo", "lumo", "gap", "ionization", "affinity"]
    geometric_keywords = ["bond", "angle", "dihedral", "coordinate", "distance"]
    spectroscopic_keywords = ["ir", "raman", "nmr", "epr", "uv", "vis", "spectrum"]
    response_keywords = ["polarizability", "hyperpolarizability", "optical_rotation"]
    thermodynamic_keywords = ["enthalpy", "entropy", "free_energy", "zpve", "heat_capacity"]
    bonding_keywords = ["charge", "bond_order", "population", "nbo", "orbital"]
    magnetic_keywords = ["magnetic", "spin", "g_tensor", "shielding"]
    
    if any(kw in property_lower for kw in electronic_keywords):
        return PropertyCategory.ELECTRONIC
    elif any(kw in property_lower for kw in geometric_keywords):
        return PropertyCategory.GEOMETRIC
    elif any(kw in property_lower for kw in spectroscopic_keywords):
        return PropertyCategory.SPECTROSCOPIC
    elif any(kw in property_lower for kw in response_keywords):
        return PropertyCategory.RESPONSE
    elif any(kw in property_lower for kw in thermodynamic_keywords):
        return PropertyCategory.THERMODYNAMIC
    elif any(kw in property_lower for kw in bonding_keywords):
        return PropertyCategory.BONDING
    elif any(kw in property_lower for kw in magnetic_keywords):
        return PropertyCategory.MAGNETIC
    else:
        return PropertyCategory.ELECTRONIC


def requires_frequency_calculation(property_name: str) -> bool:
    """
    Check if a property requires a frequency calculation.
    
    Args:
        property_name: Name of the property.
        
    Returns:
        True if frequency calculation is required.
    """
    return property_name.lower() in FREQUENCY_REQUIRED_PROPERTIES


def requires_response_calculation(property_name: str) -> bool:
    """
    Check if a property requires a response calculation.
    
    Args:
        property_name: Name of the property.
        
    Returns:
        True if response calculation is required.
    """
    return property_name.lower() in RESPONSE_REQUIRED_PROPERTIES


def requires_excited_state_calculation(property_name: str) -> bool:
    """
    Check if a property requires an excited state calculation.
    
    Args:
        property_name: Name of the property.
        
    Returns:
        True if excited state calculation is required.
    """
    return property_name.lower() in EXCITED_STATE_REQUIRED_PROPERTIES


def get_property_unit(property_type: str) -> str:
    """
    Get the standard unit for a property type.
    
    Args:
        property_type: Name of the property.
        
    Returns:
        Standard unit string for the property.
    """
    units: dict[str, str] = {
        "total_energy": "Hartree",
        "correlation_energy": "Hartree",
        "excitation_energy": "eV",
        "oscillator_strength": "dimensionless",
        "dipole": "Debye",
        "quadrupole": "Debye·Å",
        "polarizability": "Å³",
        "frequencies": "cm⁻¹",
        "ir_intensities": "km/mol",
        "raman_intensities": "Å⁴/amu",
        "nmr_shielding": "ppm",
        "nmr_coupling": "Hz",
        "g_tensor": "dimensionless",
        "hyperfine": "MHz",
        "bond_length": "Å",
        "bond_angle": "degrees",
        "dihedral_angle": "degrees",
        "charge": "e",
        "entropy": "cal/(mol·K)",
        "enthalpy": "kcal/mol",
        "gibbs_free_energy": "kcal/mol",
        "zpve": "kcal/mol",
    }
    
    return units.get(property_type.lower(), "a.u.")
