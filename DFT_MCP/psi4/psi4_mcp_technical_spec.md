# Psi4 MCP Server - Technical Specification

**Version:** 1.0  
**Date:** November 27, 2025  
**Status:** Specification Document

---

## **1. Data Models (Pydantic Schemas)**

### **1.1 Core Models**

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal, Union
from enum import Enum

# ==================== Enumerations ====================

class BasisSet(str, Enum):
    """All supported basis sets in Psi4"""
    # Minimal basis
    STO_3G = "sto-3g"
    
    # Double-zeta
    _3_21G = "3-21g"
    _6_31G = "6-31g"
    _6_31Gd = "6-31g*"
    _6_31Gdp = "6-31g**"
    CC_PVDZ = "cc-pvdz"
    AUG_CC_PVDZ = "aug-cc-pvdz"
    DEF2_SVP = "def2-svp"
    DEF2_SVPD = "def2-svpd"
    
    # Triple-zeta
    _6_311G = "6-311g"
    _6_311Gd = "6-311g*"
    _6_311Gdp = "6-311g**"
    CC_PVTZ = "cc-pvtz"
    AUG_CC_PVTZ = "aug-cc-pvtz"
    DEF2_TZVP = "def2-tzvp"
    DEF2_TZVPD = "def2-tzvpd"
    
    # Quadruple-zeta
    CC_PVQZ = "cc-pvqz"
    AUG_CC_PVQZ = "aug-cc-pvqz"
    DEF2_QZVP = "def2-qzvp"
    
    # Diffuse & polarization variants
    AUG_CC_PV5Z = "aug-cc-pv5z"
    AUG_CC_PV6Z = "aug-cc-pv6z"

class Method(str, Enum):
    """Computational methods"""
    # Hartree-Fock
    HF = "hf"
    RHF = "rhf"
    UHF = "uhf"
    ROHF = "rohf"
    
    # DFT
    SVWN = "svwn"  # LDA
    BLYP = "blyp"
    PBE = "pbe"
    PBE0 = "pbe0"
    B3LYP = "b3lyp"
    B3LYP5 = "b3lyp5"
    WB97 = "wb97"
    WB97X = "wb97x"
    WB97X_D = "wb97x-d"
    M06 = "m06"
    M06_2X = "m06-2x"
    CAM_B3LYP = "cam-b3lyp"
    LC_WPBE = "lc-wpbe"
    
    # Post-HF
    MP2 = "mp2"
    MP3 = "mp3"
    MP4 = "mp4"
    CCSD = "ccsd"
    CCSD_T = "ccsd(t)"
    CCSDT = "ccsdt"
    CISD = "cisd"
    CISDT = "cisdt"
    FCI = "fci"
    
    # SAPT
    SAPT0 = "sapt0"
    SAPT2 = "sapt2"
    SAPT2_PLUS = "sapt2+"
    SAPT2_PLUS_3 = "sapt2+(3)"

class Reference(str, Enum):
    """Reference wavefunction types"""
    RHF = "rhf"   # Restricted (closed-shell)
    UHF = "uhf"   # Unrestricted (open-shell)
    ROHF = "rohf" # Restricted open-shell

class Units(str, Enum):
    """Distance units"""
    ANGSTROM = "angstrom"
    BOHR = "bohr"

class Symmetry(str, Enum):
    """Point group symmetry"""
    C1 = "c1"        # No symmetry
    CI = "ci"
    CS = "cs"
    C2 = "c2"
    C2V = "c2v"
    C2H = "c2h"
    D2 = "d2"
    D2H = "d2h"
    D3 = "d3"
    D3H = "d3h"
    D4H = "d4h"
    D5H = "d5h"
    D6H = "d6h"
    TD = "td"
    OH = "oh"
    IH = "ih"

# ==================== Input Models ====================

class MoleculeInput(BaseModel):
    """Molecular structure specification"""
    geometry: str = Field(
        description="Molecular geometry in Z-matrix or Cartesian format"
    )
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    units: Units = Units.ANGSTROM
    symmetry: Symmetry = Symmetry.C1
    
    @validator('geometry')
    def validate_geometry(cls, v):
        """Validate geometry format"""
        if not v or not v.strip():
            raise ValueError("Geometry cannot be empty")
        
        lines = v.strip().split('\n')
        if len(lines) < 1:
            raise ValueError("Geometry must have at least one line")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "geometry": "O\nH 1 0.96\nH 1 0.96 2 104.5",
                "charge": 0,
                "multiplicity": 1,
                "units": "angstrom",
                "symmetry": "c1"
            }
        }

class CalculationOptions(BaseModel):
    """General calculation options"""
    memory: str = Field(default="2 GB", description="Available memory")
    num_threads: int = Field(default=1, ge=1, le=64)
    scratch_dir: Optional[str] = None
    output_file: Optional[str] = None
    
    # Convergence options
    e_convergence: Optional[float] = Field(default=1e-6, ge=1e-12, le=1e-3)
    d_convergence: Optional[float] = Field(default=1e-6, ge=1e-12, le=1e-3)
    maxiter: Optional[int] = Field(default=100, ge=1, le=1000)
    
    # SCF options
    scf_type: Optional[Literal["pk", "direct", "df", "cd", "mem_df"]] = "df"
    guess: Optional[Literal["auto", "sad", "gwh", "read", "core"]] = "sad"
    soscf: Optional[bool] = False
    damping_percentage: Optional[float] = Field(default=0, ge=0, le=100)
    
    # Custom options
    custom_options: Optional[Dict[str, Union[str, int, float, bool]]] = None

# ==================== Tool Input Models ====================

class EnergyCalculationInput(BaseModel):
    """Input for energy calculation"""
    molecule: MoleculeInput
    method: Method
    basis: BasisSet
    reference: Optional[Reference] = None
    options: Optional[CalculationOptions] = CalculationOptions()
    
    class Config:
        json_schema_extra = {
            "example": {
                "molecule": {
                    "geometry": "O\nH 1 0.96\nH 1 0.96 2 104.5",
                    "charge": 0,
                    "multiplicity": 1
                },
                "method": "b3lyp",
                "basis": "cc-pvdz",
                "options": {
                    "memory": "2 GB",
                    "num_threads": 4
                }
            }
        }

class OptimizationInput(BaseModel):
    """Input for geometry optimization"""
    molecule: MoleculeInput
    method: Method
    basis: BasisSet
    reference: Optional[Reference] = None
    options: Optional[CalculationOptions] = CalculationOptions()
    
    # Optimization-specific options
    convergence_threshold: Literal["gau", "gau_loose", "gau_tight", "interfrag_tight", "qchem"] = "gau"
    max_force: float = Field(default=3e-4, ge=1e-6, le=1e-2)
    max_displacement: float = Field(default=1.2e-3, ge=1e-6, le=1e-1)
    max_iterations: int = Field(default=50, ge=1, le=500)
    coordinate_system: Literal["cartesian", "internal", "both"] = "internal"
    
    # Constrained optimization
    constraints: Optional[List[Dict[str, Union[str, float]]]] = None
    
    # Transition state search
    ts_search: bool = False
    hessian_update: Literal["bfgs", "ms", "powell", "none"] = "bfgs"

class FrequencyInput(BaseModel):
    """Input for frequency calculation"""
    molecule: MoleculeInput
    method: Method
    basis: BasisSet
    reference: Optional[Reference] = None
    options: Optional[CalculationOptions] = CalculationOptions()
    
    # Frequency-specific options
    temperature: float = Field(default=298.15, ge=0, le=1000)
    pressure: float = Field(default=101325, ge=0, le=1e7)  # Pa
    frequency_threshold: float = Field(default=1.0, ge=0, le=100)  # cm^-1
    compute_raman: bool = False
    compute_vcd: bool = False
    check_optimized: bool = True

class PropertiesInput(BaseModel):
    """Input for molecular properties calculation"""
    molecule: MoleculeInput
    method: Method
    basis: BasisSet
    reference: Optional[Reference] = None
    options: Optional[CalculationOptions] = CalculationOptions()
    
    # Properties to calculate
    requested_properties: List[Literal[
        "dipole",
        "quadrupole",
        "polarizability",
        "homo_lumo",
        "mulliken",
        "lowdin",
        "esp",
        "npa",
        "wiberg_bonds",
        "mayer_bonds"
    ]] = ["dipole", "homo_lumo", "mulliken"]

class TDDFTInput(BaseModel):
    """Input for TD-DFT calculation"""
    molecule: MoleculeInput
    method: Method  # Must be DFT method
    basis: BasisSet
    reference: Optional[Reference] = None
    options: Optional[CalculationOptions] = CalculationOptions()
    
    # TDDFT-specific options
    n_states: int = Field(default=5, ge=1, le=100)
    use_tda: bool = False  # Tamm-Dancoff approximation
    triplets: bool = False
    convergence: float = Field(default=1e-5, ge=1e-10, le=1e-3)
    max_iterations: int = Field(default=60, ge=10, le=200)
    
    # Spectrum generation
    spectrum_range: tuple[float, float] = (200, 800)  # nm
    broadening: float = 0.4  # eV

class DimerInput(BaseModel):
    """Dimer specification for SAPT"""
    monomer1: str = Field(description="First monomer geometry")
    monomer2: str = Field(description="Second monomer geometry")
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    units: Units = Units.ANGSTROM

class SAPTInput(BaseModel):
    """Input for SAPT calculation"""
    dimer: DimerInput
    sapt_level: Literal["sapt0", "sapt2", "sapt2+", "sapt2+(3)"] = "sapt0"
    basis: BasisSet
    freeze_core: bool = True
    options: Optional[CalculationOptions] = CalculationOptions()

# ==================== Output Models ====================

class EnergyCalculationOutput(BaseModel):
    """Output from energy calculation"""
    energy: float = Field(description="Total energy in hartree")
    units: str = "hartree"
    method: str
    basis: str
    natoms: int
    nelec: int
    multiplicity: int
    scf_iterations: Optional[int] = None
    converged: bool
    dipole_moment: Optional[float] = None
    
    # Additional data
    timing: Optional[Dict[str, float]] = None
    memory_used: Optional[str] = None

class OptimizationOutput(BaseModel):
    """Output from geometry optimization"""
    final_energy: float
    final_geometry: str
    initial_geometry: str
    n_iterations: int
    converged: bool
    
    # Convergence details
    max_force: Optional[float] = None
    rms_force: Optional[float] = None
    max_displacement: Optional[float] = None
    rms_displacement: Optional[float] = None
    
    # Method info
    method: str
    basis: str
    
    # Additional data
    trajectory: Optional[List[Dict[str, float]]] = None
    timing: Optional[Dict[str, float]] = None

class FrequencyOutput(BaseModel):
    """Output from frequency calculation"""
    frequencies: List[float]
    units: Dict[str, str] = {
        "frequencies": "cm^-1",
        "energy": "hartree",
        "entropy": "cal/(mol·K)"
    }
    n_frequencies: int
    n_imaginary: int
    imaginary_frequencies: List[float]
    
    # Thermodynamic properties
    zero_point_energy: float
    thermal_energy: float
    enthalpy: float
    entropy: float
    gibbs_free_energy: float
    temperature: float
    
    # Characterization
    is_minimum: bool
    is_transition_state: bool
    is_higher_order_saddle: bool
    
    # Optional spectroscopic data
    ir_intensities: Optional[List[float]] = None
    raman_activities: Optional[List[float]] = None
    
    # Method info
    method: str
    basis: str

class MolecularProperties(BaseModel):
    """Collection of molecular properties"""
    energy: float
    
    # Electric moments
    dipole_moment: Optional[Dict[str, float]] = None
    quadrupole_moment: Optional[Dict[str, float]] = None
    
    # Orbital properties
    homo_lumo: Optional[Dict[str, float]] = None
    
    # Charge analysis
    mulliken_charges: Optional[List[float]] = None
    lowdin_charges: Optional[List[float]] = None
    esp_charges: Optional[List[float]] = None
    npa_charges: Optional[List[float]] = None
    
    # Bond orders
    wiberg_bond_orders: Optional[List[List[float]]] = None
    mayer_bond_orders: Optional[List[List[float]]] = None

class ExcitedState(BaseModel):
    """Single excited state information"""
    state_number: int
    excitation_energy_au: float
    excitation_energy_ev: float
    excitation_energy_nm: float
    oscillator_strength: float
    transition_dipole: List[float]
    dominant_excitation: str
    symmetry: Optional[str] = None

class UVVisSpectrum(BaseModel):
    """UV-Vis absorption spectrum"""
    wavelengths: List[float]
    intensities: List[float]
    units: Dict[str, str] = {
        "wavelength": "nm",
        "intensity": "arbitrary"
    }

class TDDFTOutput(BaseModel):
    """Output from TDDFT calculation"""
    ground_state_energy: float
    n_states_computed: int
    excited_states: List[ExcitedState]
    uv_vis_spectrum: UVVisSpectrum
    method: str
    basis: str
    approximation: str  # "TDA" or "RPA"

class SAPTComponents(BaseModel):
    """SAPT energy components"""
    electrostatic: float
    exchange: float
    induction: float
    dispersion: float
    total_sapt: float
    hf_interaction: float
    
    # Higher-order terms (if available)
    exchange_induction: Optional[float] = None
    exchange_dispersion: Optional[float] = None

class SAPTInterpretation(BaseModel):
    """Interpretation of SAPT results"""
    dominant_attractive: str
    dominant_repulsive: str
    percentages: Dict[str, float]
    interaction_type: Optional[str] = None

class SAPTOutput(BaseModel):
    """Output from SAPT calculation"""
    sapt_level: str
    basis: str
    energy_components: SAPTComponents
    total_interaction_energy: float
    units: str = "hartree"
    interpretation: SAPTInterpretation

# ==================== Error Models ====================

class ValidationError(BaseModel):
    """Validation error details"""
    field: str
    error_type: str
    message: str
    suggestion: Optional[str] = None

class CalculationError(BaseModel):
    """Calculation error details"""
    error_type: str
    message: str
    psi4_error: Optional[str] = None
    suggestions: List[str] = []
    auto_recovery_attempted: bool = False
    recovery_successful: Optional[bool] = None
```

---

## **2. MCP Tool Signatures**

### **2.1 Calculate Energy**

```python
@mcp.tool()
async def calculate_energy(
    input_data: EnergyCalculationInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> EnergyCalculationOutput:
    """
    Calculate single-point electronic energy.
    
    Performs SCF or post-SCF calculation to obtain the electronic energy
    of a molecular system at a fixed geometry.
    
    Supported Methods:
    - Hartree-Fock: HF, RHF, UHF, ROHF
    - DFT: B3LYP, PBE, PBE0, wB97X, M06-2X, CAM-B3LYP, etc.
    - MP2/MP3/MP4: Second/third/fourth-order perturbation theory
    - Coupled Cluster: CCSD, CCSD(T), CCSDT
    - Configuration Interaction: CISD, CISDT, FCI
    
    Basis Sets:
    - Minimal: STO-3G
    - Double-zeta: 6-31G, cc-pVDZ, def2-SVP
    - Triple-zeta: 6-311G, cc-pVTZ, def2-TZVP
    - Quadruple-zeta: cc-pVQZ, def2-QZVP
    - Augmented: aug-cc-pVXZ series
    
    Args:
        input_data: Molecular structure and calculation parameters
        ctx: MCP context for progress reporting and logging
        
    Returns:
        EnergyCalculationOutput containing:
        - Total electronic energy (hartree)
        - SCF convergence information
        - Dipole moment (if computed)
        - Timing and resource usage
        
    Raises:
        ValidationError: Invalid input parameters
        ConvergenceError: SCF did not converge
        ResourceError: Insufficient memory or disk space
        
    Example:
        >>> result = await calculate_energy({
        ...     "molecule": {
        ...         "geometry": "O\nH 1 0.96\nH 1 0.96 2 104.5",
        ...         "charge": 0,
        ...         "multiplicity": 1
        ...     },
        ...     "method": "b3lyp",
        ...     "basis": "cc-pvdz"
        ... })
        >>> print(f"Energy: {result.energy} hartree")
    """
```

### **2.2 Optimize Geometry**

```python
@mcp.tool()
async def optimize_geometry(
    input_data: OptimizationInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> OptimizationOutput:
    """
    Optimize molecular geometry to find energy minimum.
    
    Performs iterative geometry optimization using gradient-based methods
    to locate stationary points (minima or transition states) on the
    potential energy surface.
    
    Optimization Algorithms:
    - Quasi-Newton: BFGS, MS, Powell
    - Conjugate gradient
    - Steepest descent
    
    Convergence Criteria:
    - Maximum force
    - RMS force
    - Maximum displacement
    - RMS displacement
    - Energy change
    
    Special Features:
    - Constrained optimization (fix atoms, bonds, angles)
    - Transition state search
    - Multiple coordinate systems (Cartesian, internal, redundant)
    
    Args:
        input_data: Initial geometry and optimization parameters
        ctx: MCP context
        
    Returns:
        OptimizationOutput containing:
        - Optimized geometry
        - Final energy
        - Convergence information
        - Optimization trajectory
        
    Raises:
        ValidationError: Invalid input
        ConvergenceError: Optimization did not converge
        
    Example:
        >>> result = await optimize_geometry({
        ...     "molecule": {"geometry": "..."},
        ...     "method": "b3lyp",
        ...     "basis": "6-31g*",
        ...     "max_iterations": 100
        ... })
    """
```

### **2.3 Calculate Frequencies**

```python
@mcp.tool()
async def calculate_frequencies(
    input_data: FrequencyInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> FrequencyOutput:
    """
    Calculate vibrational frequencies and thermodynamic properties.
    
    Computes the molecular Hessian (second derivative of energy) and
    diagonalizes it to obtain vibrational frequencies, normal modes,
    and thermodynamic corrections.
    
    IMPORTANT: Geometry MUST be optimized first for meaningful results.
    
    Computed Properties:
    - Harmonic vibrational frequencies (cm⁻¹)
    - Zero-point energy (ZPE)
    - Thermal energy corrections
    - Enthalpy (H)
    - Entropy (S)
    - Gibbs free energy (G)
    - IR intensities
    - Raman activities (optional)
    
    Stationary Point Classification:
    - Minimum: All real frequencies (0 imaginary)
    - Transition state: One imaginary frequency
    - Higher-order saddle: Multiple imaginary frequencies
    
    Args:
        input_data: Optimized geometry and calculation parameters
        ctx: MCP context
        
    Returns:
        FrequencyOutput containing all vibrational data
        
    Example:
        >>> result = await calculate_frequencies({
        ...     "molecule": {"geometry": "..."},
        ...     "method": "b3lyp",
        ...     "basis": "6-31g*",
        ...     "temperature": 298.15
        ... })
        >>> print(f"Is minimum: {result.is_minimum}")
        >>> print(f"ZPE: {result.zero_point_energy} hartree")
    """
```

### **2.4 Calculate Properties**

```python
@mcp.tool()
async def calculate_properties(
    input_data: PropertiesInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> MolecularProperties:
    """
    Calculate various molecular properties.
    
    Available Properties:
    
    Electric Moments:
    - Dipole moment (debye)
    - Quadrupole moment (debye·Å)
    - Polarizability (Å³)
    
    Orbital Properties:
    - HOMO energy
    - LUMO energy
    - HOMO-LUMO gap
    - Molecular orbital energies
    
    Charge Analysis:
    - Mulliken charges
    - Löwdin charges
    - ESP charges
    - NPA (Natural Population Analysis)
    
    Bond Analysis:
    - Wiberg bond orders
    - Mayer bond orders
    
    Args:
        input_data: Geometry and requested properties
        ctx: MCP context
        
    Returns:
        MolecularProperties with all requested data
        
    Example:
        >>> result = await calculate_properties({
        ...     "molecule": {"geometry": "..."},
        ...     "method": "b3lyp",
        ...     "basis": "cc-pvdz",
        ...     "requested_properties": ["dipole", "homo_lumo", "mulliken"]
        ... })
    """
```

### **2.5 Calculate Excited States**

```python
@mcp.tool()
async def calculate_excited_states(
    input_data: TDDFTInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> TDDFTOutput:
    """
    Calculate excited electronic states using TD-DFT.
    
    Computes electronic excitation energies, oscillator strengths,
    and transition properties using time-dependent density functional
    theory.
    
    Methods:
    - Full TDDFT (RPA): Complete response
    - Tamm-Dancoff Approximation (TDA): Faster, neglects de-excitations
    
    State Types:
    - Singlet states (default)
    - Triplet states (optional)
    
    Output:
    - Excitation energies (eV, nm, hartree)
    - Oscillator strengths
    - Transition dipole moments
    - Dominant orbital transitions
    - UV-Vis absorption spectrum (computed with Gaussian broadening)
    
    Args:
        input_data: Ground state geometry and TDDFT parameters
        ctx: MCP context
        
    Returns:
        TDDFTOutput with excited state data and spectrum
        
    Example:
        >>> result = await calculate_excited_states({
        ...     "molecule": {"geometry": "..."},
        ...     "method": "b3lyp",
        ...     "basis": "aug-cc-pvdz",
        ...     "n_states": 10,
        ...     "use_tda": False
        ... })
        >>> for state in result.excited_states:
        ...     print(f"S{state.state_number}: {state.excitation_energy_nm:.1f} nm, f={state.oscillator_strength:.3f}")
    """
```

### **2.6 Calculate SAPT**

```python
@mcp.tool()
async def calculate_sapt(
    input_data: SAPTInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> SAPTOutput:
    """
    Perform Symmetry-Adapted Perturbation Theory analysis.
    
    Decomposes intermolecular interaction energy into physically
    meaningful components:
    
    Energy Components:
    - Electrostatic: Classical charge-charge interaction
    - Exchange: Pauli repulsion from orbital overlap
    - Induction: Polarization/charge transfer effects
    - Dispersion: London dispersion forces (van der Waals)
    
    SAPT Levels (increasing accuracy):
    - SAPT0: Fastest, HF-based, good for initial screening
    - SAPT2: Medium accuracy, includes MP2 correlation
    - SAPT2+: Improved dispersion description
    - SAPT2+(3): SAPT2+ with third-order corrections
    
    Input Format:
    Dimer must be specified with two monomers separated by "--":
    ```
    monomer1: "He 0 0 0"
    monomer2: "He 0 0 3.0"
    ```
    
    Args:
        input_data: Dimer geometry and SAPT parameters
        ctx: MCP context
        
    Returns:
        SAPTOutput with energy decomposition and interpretation
        
    Example:
        >>> result = await calculate_sapt({
        ...     "dimer": {
        ...         "monomer1": "O\nH 1 0.96\nH 1 0.96 2 104.5",
        ...         "monomer2": "O 3.0 0 0\nH 1 0.96\nH 1 0.96 2 104.5"
        ...     },
        ...     "sapt_level": "sapt0",
        ...     "basis": "aug-cc-pvdz"
        ... })
        >>> print(f"Electrostatic: {result.energy_components.electrostatic:.6f} hartree")
        >>> print(f"Dominant attractive: {result.interpretation.dominant_attractive}")
    """
```

---

## **3. MCP Resources**

### **3.1 Basis Set Resources**

```python
@mcp.resource("basis://list")
def list_basis_sets() -> str:
    """
    List all available basis sets.
    
    Returns JSON array with:
    - name: Basis set name
    - type: Classification (minimal, DZ, TZ, QZ, etc.)
    - description: Brief description
    - elements: Supported elements
    """

@mcp.resource("basis://{basis_name}")
def get_basis_info(basis_name: str) -> str:
    """
    Get detailed information about a specific basis set.
    
    Returns:
    - Full name
    - Type and size
    - Supported elements
    - Recommended uses
    - Citations
    """
```

### **3.2 Method Resources**

```python
@mcp.resource("method://list")
def list_methods() -> str:
    """
    List all available computational methods.
    
    Returns JSON with method categories:
    - Hartree-Fock
    - DFT
    - Post-HF (MP2, CC, CI)
    - SAPT
    
    For each method:
    - Computational cost (scaling)
    - Typical accuracy
    - Recommended use cases
    """

@mcp.resource("method://{method_name}")
def get_method_info(method_name: str) -> str:
    """
    Get detailed information about a computational method.
    """
```

---

## **4. Error Handling Specifications**

### **4.1 Error Types**

```python
class ErrorType(Enum):
    VALIDATION_ERROR = "validation"
    CONVERGENCE_ERROR = "convergence"
    MEMORY_ERROR = "memory"
    BASIS_ERROR = "basis"
    GEOMETRY_ERROR = "geometry"
    SYMMETRY_ERROR = "symmetry"
    METHOD_ERROR = "method"
    UNKNOWN_ERROR = "unknown"
```

### **4.2 Error Response Format**

```python
class ErrorResponse(BaseModel):
    error_type: ErrorType
    message: str
    details: Optional[str] = None
    suggestions: List[str] = []
    recoverable: bool
    attempted_recovery: bool = False
    recovery_successful: Optional[bool] = None
```

---

## **5. Performance Specifications**

### **5.1 Resource Limits**

```python
class ResourceLimits(BaseModel):
    max_memory: str = "16 GB"
    max_threads: int = 32
    max_calculation_time: int = 3600  # seconds
    max_atoms: int = 500
    max_basis_functions: int = 10000
```

### **5.2 Progress Reporting**

All long-running calculations must report progress:

```python
# Progress at key points
await ctx.report_progress(0, 100, "Starting...")
await ctx.report_progress(10, 100, "SCF iteration 1/10")
await ctx.report_progress(50, 100, "Halfway through...")
await ctx.report_progress(100, 100, "Complete!")
```

---

## **6. Testing Requirements**

### **6.1 Reference Values**

All calculations must be validated against these reference values:

```python
REFERENCE_VALUES = {
    'h2o_hf_sto3g': {
        'energy': -74.965901217080,
        'tolerance': 1e-6
    },
    'h2o_b3lyp_631gd': {
        'energy': -76.404849968,
        'dipole': 1.975,
        'tolerance': 1e-5
    },
    'ch4_freq_b3lyp_631gd': {
        'frequencies': [1353.3, 1353.5, 1566.4, 1566.5, 
                       1566.5, 3065.2, 3176.3, 3176.4, 3176.5],
        'tolerance': 5.0  # cm^-1
    }
}
```

---

**This technical specification must be followed exactly during implementation.**

**Version:** 1.0  
**Last Updated:** 2025-11-27
