"""
Calculation Options Models for Psi4 MCP Server.

This module provides Pydantic models for configuring quantum chemistry
calculations in Psi4. Options are organized by calculation type and
functionality.

Key Option Classes:
    - SCFOptions: Self-consistent field options
    - CorrelationOptions: Post-HF correlation options
    - OptimizationOptions: Geometry optimization options
    - FrequencyOptions: Frequency calculation options
    - PropertyOptions: Property calculation options
"""

from typing import Any, Optional, Literal, Union
from pydantic import Field, field_validator, model_validator 

from psi4_mcp.models.base import Psi4BaseModel


# =============================================================================
# SCF OPTIONS
# =============================================================================

class SCFOptions(Psi4BaseModel):
    """
    Options for Self-Consistent Field (SCF) calculations.
    
    Attributes:
        reference: Reference wavefunction type.
        maxiter: Maximum number of SCF iterations.
        e_convergence: Energy convergence criterion.
        d_convergence: Density convergence criterion.
        scf_type: SCF algorithm type.
        guess: Initial orbital guess method.
        level_shift: Level shift for convergence.
        damping_percentage: Damping percentage for convergence.
        diis: Enable DIIS extrapolation.
        diis_start: Iteration to start DIIS.
        diis_max_vecs: Maximum DIIS vectors.
        soscf: Use second-order SCF.
        mom: Use Maximum Overlap Method for excited states.
        stability_analysis: Perform stability analysis.
        print_level: Print verbosity level.
    """
    
    reference: str = Field(
        default="rhf",
        description="Reference wavefunction type (rhf, uhf, rohf, rks, uks)",
    )
    maxiter: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum SCF iterations",
    )
    e_convergence: float = Field(
        default=1e-8,
        gt=0,
        le=1e-2,
        description="Energy convergence criterion",
    )
    d_convergence: float = Field(
        default=1e-8,
        gt=0,
        le=1e-2,
        description="Density convergence criterion",
    )
    scf_type: str = Field(
        default="df",
        description="SCF type (direct, df, pk, cd, out_of_core)",
    )
    guess: str = Field(
        default="sad",
        description="Initial guess (sad, core, gwh, read, auto)",
    )
    level_shift: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Level shift for convergence (Hartree)",
    )
    damping_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Damping percentage",
    )
    diis: bool = Field(
        default=True,
        description="Enable DIIS extrapolation",
    )
    diis_start: int = Field(
        default=1,
        ge=1,
        description="Iteration to start DIIS",
    )
    diis_max_vecs: int = Field(
        default=10,
        ge=2,
        le=50,
        description="Maximum DIIS vectors",
    )
    soscf: bool = Field(
        default=False,
        description="Use second-order SCF",
    )
    mom: bool = Field(
        default=False,
        description="Use Maximum Overlap Method",
    )
    stability_analysis: str = Field(
        default="none",
        description="Stability analysis type (none, check, follow)",
    )
    print_level: int = Field(
        default=1,
        ge=0,
        le=5,
        description="Print verbosity level",
    )
    
    @field_validator("reference")
    @classmethod
    def validate_reference(cls, v: str) -> str:
        """Validate reference type."""
        valid = {"rhf", "uhf", "rohf", "rks", "uks", "cuhf", "ghf", "gks"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid reference: {v}. Must be one of {valid}")
        return normalized
    
    @field_validator("scf_type")
    @classmethod
    def validate_scf_type(cls, v: str) -> str:
        """Validate SCF type."""
        valid = {"direct", "df", "pk", "cd", "out_of_core", "disk_df"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid scf_type: {v}. Must be one of {valid}")
        return normalized
    
    @field_validator("guess")
    @classmethod
    def validate_guess(cls, v: str) -> str:
        """Validate initial guess type."""
        valid = {"sad", "core", "gwh", "huckel", "read", "auto"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid guess: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {
            "reference": self.reference,
            "maxiter": self.maxiter,
            "e_convergence": self.e_convergence,
            "d_convergence": self.d_convergence,
            "scf_type": self.scf_type,
            "guess": self.guess,
            "diis": self.diis,
            "diis_start": self.diis_start,
            "diis_max_vecs": self.diis_max_vecs,
            "soscf": self.soscf,
            "print": self.print_level,
        }
        
        if self.level_shift > 0:
            opts["level_shift"] = self.level_shift
        if self.damping_percentage > 0:
            opts["damping_percentage"] = self.damping_percentage
        if self.mom:
            opts["mom_start"] = 1
        if self.stability_analysis != "none":
            opts["stability_analysis"] = self.stability_analysis
        
        return opts


# =============================================================================
# DFT OPTIONS
# =============================================================================

class DFTOptions(Psi4BaseModel):
    """
    Options specific to Density Functional Theory calculations.
    
    Attributes:
        functional: DFT functional name.
        dispersion: Dispersion correction type.
        grid: DFT grid specification.
        nlc: Non-local correlation functional.
        vv10_b: VV10 damping parameter b.
        vv10_c: VV10 short-range parameter C.
    """
    
    functional: str = Field(
        default="b3lyp",
        description="DFT functional name",
    )
    dispersion: Optional[str] = Field(
        default=None,
        description="Dispersion correction (d3, d3bj, d4, nl)",
    )
    grid: str = Field(
        default="default",
        description="DFT grid (coarse, default, fine, ultrafine, superfine)",
    )
    nlc: Optional[str] = Field(
        default=None,
        description="Non-local correlation functional",
    )
    vv10_b: Optional[float] = Field(
        default=None,
        description="VV10 b parameter",
    )
    vv10_c: Optional[float] = Field(
        default=None,
        description="VV10 C parameter",
    )
    
    @field_validator("functional")
    @classmethod
    def normalize_functional(cls, v: str) -> str:
        """Normalize functional name."""
        return v.lower().strip().replace("_", "-")
    
    @field_validator("dispersion")
    @classmethod
    def validate_dispersion(cls, v: Optional[str]) -> Optional[str]:
        """Validate dispersion correction."""
        if v is None:
            return None
        valid = {"d2", "d3", "d3bj", "d3m", "d3mbj", "d4", "nl", "chg"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid dispersion: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {}
        
        # Grid options based on keyword
        grid_settings = {
            "coarse": {"dft_spherical_points": 194, "dft_radial_points": 50},
            "default": {},  # Use Psi4 defaults
            "fine": {"dft_spherical_points": 590, "dft_radial_points": 99},
            "ultrafine": {"dft_spherical_points": 974, "dft_radial_points": 150},
            "superfine": {"dft_spherical_points": 1202, "dft_radial_points": 200},
        }
        
        if self.grid in grid_settings:
            opts.update(grid_settings[self.grid])
        
        if self.dispersion:
            opts["dft_dispersion_parameters"] = [self.dispersion]
        
        if self.nlc:
            opts["dft_nlc"] = self.nlc
        
        if self.vv10_b is not None:
            opts["dft_vv10_b"] = self.vv10_b
        if self.vv10_c is not None:
            opts["dft_vv10_c"] = self.vv10_c
        
        return opts


# =============================================================================
# CORRELATION OPTIONS
# =============================================================================

class CorrelationOptions(Psi4BaseModel):
    """
    Options for post-Hartree-Fock correlation methods.
    
    Attributes:
        freeze_core: Freeze core electrons.
        frozen_docc: Number of frozen doubly occupied orbitals per irrep.
        frozen_uocc: Number of frozen virtual orbitals per irrep.
        mp2_type: MP2 algorithm type.
        cc_type: Coupled cluster algorithm type.
        r_convergence: Residual convergence.
        e_convergence: Energy convergence.
        maxiter: Maximum iterations.
        t1_diagnostic: Calculate T1 diagnostic.
        nat_orbs: Use natural orbitals.
    """
    
    freeze_core: bool = Field(
        default=True,
        description="Freeze core electrons",
    )
    frozen_docc: Optional[list[int]] = Field(
        default=None,
        description="Frozen doubly occupied orbitals per irrep",
    )
    frozen_uocc: Optional[list[int]] = Field(
        default=None,
        description="Frozen virtual orbitals per irrep",
    )
    mp2_type: str = Field(
        default="df",
        description="MP2 type (conv, df, cd)",
    )
    cc_type: str = Field(
        default="conv",
        description="CC type (conv, df, cd)",
    )
    r_convergence: float = Field(
        default=1e-7,
        gt=0,
        description="Residual convergence",
    )
    e_convergence: float = Field(
        default=1e-8,
        gt=0,
        description="Energy convergence",
    )
    maxiter: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum iterations",
    )
    t1_diagnostic: bool = Field(
        default=True,
        description="Calculate T1 diagnostic",
    )
    nat_orbs: bool = Field(
        default=False,
        description="Use natural orbitals",
    )
    
    @field_validator("mp2_type")
    @classmethod
    def validate_mp2_type(cls, v: str) -> str:
        """Validate MP2 type."""
        valid = {"conv", "df", "cd"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid mp2_type: {v}. Must be one of {valid}")
        return normalized
    
    @field_validator("cc_type")
    @classmethod
    def validate_cc_type(cls, v: str) -> str:
        """Validate CC type."""
        valid = {"conv", "df", "cd"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid cc_type: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {
            "freeze_core": self.freeze_core,
            "mp2_type": self.mp2_type,
            "cc_type": self.cc_type,
            "r_convergence": self.r_convergence,
            "e_convergence": self.e_convergence,
            "maxiter": self.maxiter,
        }
        
        if self.frozen_docc is not None:
            opts["frozen_docc"] = self.frozen_docc
        if self.frozen_uocc is not None:
            opts["frozen_uocc"] = self.frozen_uocc
        if self.nat_orbs:
            opts["nat_orbs"] = True
        
        return opts


# =============================================================================
# GEOMETRY OPTIMIZATION OPTIONS
# =============================================================================

class OptimizationOptions(Psi4BaseModel):
    """
    Options for geometry optimization calculations.
    
    Attributes:
        geom_maxiter: Maximum optimization steps.
        g_convergence: Gradient convergence criteria.
        full_hess_every: Full Hessian calculation frequency.
        opt_coordinates: Coordinate system for optimization.
        step_type: Step type (rfo, pfo, linesearch).
        intcos_file: Filename for internal coordinates.
        frozen_distance: List of frozen bond distances.
        frozen_bend: List of frozen angles.
        frozen_dihedral: List of frozen dihedrals.
        ts_opt: Transition state optimization.
        irc: Follow intrinsic reaction coordinate.
        irc_direction: IRC direction (forward, backward).
    """
    
    geom_maxiter: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum optimization steps",
    )
    g_convergence: str = Field(
        default="gau_tight",
        description="Gradient convergence criteria",
    )
    full_hess_every: int = Field(
        default=-1,
        description="Full Hessian frequency (-1 for never)",
    )
    opt_coordinates: str = Field(
        default="cartesian",
        description="Coordinate system (cartesian, internal, both)",
    )
    step_type: str = Field(
        default="rfo",
        description="Step type (rfo, pfo, linesearch, sd)",
    )
    intcos_file: Optional[str] = Field(
        default=None,
        description="Internal coordinates file",
    )
    frozen_distance: Optional[list[tuple[int, int]]] = Field(
        default=None,
        description="Frozen bond distances (atom pairs)",
    )
    frozen_bend: Optional[list[tuple[int, int, int]]] = Field(
        default=None,
        description="Frozen angles (atom triplets)",
    )
    frozen_dihedral: Optional[list[tuple[int, int, int, int]]] = Field(
        default=None,
        description="Frozen dihedrals (atom quartets)",
    )
    ts_opt: bool = Field(
        default=False,
        description="Transition state optimization",
    )
    irc: bool = Field(
        default=False,
        description="Follow intrinsic reaction coordinate",
    )
    irc_direction: str = Field(
        default="forward",
        description="IRC direction (forward, backward)",
    )
    
    @field_validator("g_convergence")
    @classmethod
    def validate_g_convergence(cls, v: str) -> str:
        """Validate gradient convergence criteria."""
        valid = {
            "gau", "gau_tight", "gau_verytight", "gau_loose",
            "nwchem_loose", "interfrag_tight", "cfour",
        }
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid g_convergence: {v}. Must be one of {valid}")
        return normalized
    
    @field_validator("opt_coordinates")
    @classmethod
    def validate_opt_coordinates(cls, v: str) -> str:
        """Validate optimization coordinates."""
        valid = {"cartesian", "internal", "both", "delocalized", "natural"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid opt_coordinates: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {
            "geom_maxiter": self.geom_maxiter,
            "g_convergence": self.g_convergence,
            "opt_coordinates": self.opt_coordinates,
            "step_type": self.step_type,
        }
        
        if self.full_hess_every >= 0:
            opts["full_hess_every"] = self.full_hess_every
        
        if self.ts_opt:
            opts["opt_type"] = "ts"
        
        if self.irc:
            opts["opt_type"] = "irc"
            opts["irc_direction"] = self.irc_direction
        
        return opts


# =============================================================================
# FREQUENCY OPTIONS
# =============================================================================

class FrequencyOptions(Psi4BaseModel):
    """
    Options for vibrational frequency calculations.
    
    Attributes:
        dertype: Derivative type (energy, gradient, hessian).
        normal_modes: Compute normal modes.
        thermodynamics: Compute thermodynamic properties.
        temperature: Temperature for thermodynamics (K).
        pressure: Pressure for thermodynamics (atm).
        scale_factor: Frequency scaling factor.
        project_rotations: Project out rotations.
        project_translations: Project out translations.
    """
    
    dertype: str = Field(
        default="hessian",
        description="Derivative type (energy, gradient, hessian)",
    )
    normal_modes: bool = Field(
        default=True,
        description="Compute normal modes",
    )
    thermodynamics: bool = Field(
        default=True,
        description="Compute thermodynamic properties",
    )
    temperature: float = Field(
        default=298.15,
        gt=0,
        le=10000,
        description="Temperature in Kelvin",
    )
    pressure: float = Field(
        default=1.0,
        gt=0,
        le=1000,
        description="Pressure in atm",
    )
    scale_factor: float = Field(
        default=1.0,
        gt=0,
        le=2.0,
        description="Frequency scaling factor",
    )
    project_rotations: bool = Field(
        default=True,
        description="Project out rotations",
    )
    project_translations: bool = Field(
        default=True,
        description="Project out translations",
    )
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        return {
            "t": self.temperature,
            "p": self.pressure,
            "normal_modes_write": self.normal_modes,
        }


# =============================================================================
# PROPERTY OPTIONS
# =============================================================================

class PropertyOptions(Psi4BaseModel):
    """
    Options for property calculations.
    
    Attributes:
        properties: List of properties to compute.
        response: Compute response properties.
        polarizability: Compute polarizability.
        hyperpolarizability: Compute hyperpolarizability.
        nmr_shielding: Compute NMR shielding.
        nmr_coupling: Compute NMR coupling.
        epr: Compute EPR parameters.
    """
    
    properties: list[str] = Field(
        default_factory=list,
        description="Properties to compute",
    )
    response: bool = Field(
        default=False,
        description="Compute response properties",
    )
    polarizability: bool = Field(
        default=False,
        description="Compute polarizability",
    )
    hyperpolarizability: bool = Field(
        default=False,
        description="Compute hyperpolarizability",
    )
    nmr_shielding: bool = Field(
        default=False,
        description="Compute NMR shielding",
    )
    nmr_coupling: bool = Field(
        default=False,
        description="Compute NMR coupling",
    )
    epr: bool = Field(
        default=False,
        description="Compute EPR parameters",
    )
    
    def get_property_list(self) -> list[str]:
        """Get list of all requested properties."""
        props = list(self.properties)
        
        if self.polarizability and "polarizability" not in props:
            props.append("polarizability")
        if self.hyperpolarizability and "hyperpolarizability" not in props:
            props.append("hyperpolarizability")
        if self.nmr_shielding and "nmr_shielding" not in props:
            props.append("nmr_shielding")
        if self.nmr_coupling and "nmr_coupling" not in props:
            props.append("nmr_coupling")
        if self.epr and "epr_g_tensor" not in props:
            props.append("epr_g_tensor")
        
        return props


# =============================================================================
# SOLVATION OPTIONS
# =============================================================================

class SolvationOptions(Psi4BaseModel):
    """
    Options for implicit solvation models.
    
    Attributes:
        pcm: Use Polarizable Continuum Model.
        solvent: Solvent name.
        epsilon: Dielectric constant.
        probe_radius: Solvent probe radius (Angstrom).
        cavity_type: Cavity type (gepol, isodensity).
    """
    
    pcm: bool = Field(
        default=False,
        description="Use PCM solvation",
    )
    solvent: str = Field(
        default="water",
        description="Solvent name",
    )
    epsilon: Optional[float] = Field(
        default=None,
        gt=1.0,
        description="Dielectric constant",
    )
    probe_radius: float = Field(
        default=1.4,
        gt=0,
        le=5.0,
        description="Probe radius in Angstrom",
    )
    cavity_type: str = Field(
        default="gepol",
        description="Cavity type (gepol, isodensity)",
    )
    
    # Common solvent dielectric constants
    SOLVENT_EPSILON: dict[str, float] = {
        "water": 78.4,
        "acetone": 20.7,
        "acetonitrile": 37.5,
        "benzene": 2.3,
        "chloroform": 4.8,
        "cyclohexane": 2.0,
        "dichloromethane": 8.9,
        "dmf": 36.7,
        "dmso": 46.7,
        "ethanol": 24.5,
        "methanol": 32.7,
        "thf": 7.6,
        "toluene": 2.4,
    }
    
    @field_validator("solvent")
    @classmethod
    def normalize_solvent(cls, v: str) -> str:
        """Normalize solvent name."""
        return v.lower().strip()
    
    def get_epsilon(self) -> float:
        """Get dielectric constant for the solvent."""
        if self.epsilon is not None:
            return self.epsilon
        return self.SOLVENT_EPSILON.get(self.solvent, 78.4)
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        if not self.pcm:
            return {}
        
        return {
            "pcm": True,
            "pcm_scf_type": "total",
            "pcm__input": f"""
                Units = Angstrom
                Medium {{
                    SolverType = IEFPCM
                    Solvent = {self.solvent}
                }}
                Cavity {{
                    Type = GePol
                    Area = 0.3
                    Mode = Implicit
                }}
            """,
        }


# =============================================================================
# COMBINED CALCULATION OPTIONS
# =============================================================================

class CalculationOptions(Psi4BaseModel):
    """
    Combined options for a complete calculation.
    
    Attributes:
        memory: Memory allocation in MB.
        n_threads: Number of CPU threads.
        scf: SCF options.
        dft: DFT-specific options.
        correlation: Correlation method options.
        optimization: Geometry optimization options.
        frequency: Frequency calculation options.
        properties: Property calculation options.
        solvation: Solvation model options.
        extra_options: Additional Psi4 options.
    """
    
    memory: int = Field(
        default=2000,
        ge=100,
        le=1000000,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        le=256,
        description="Number of CPU threads",
    )
    scf: SCFOptions = Field(
        default_factory=SCFOptions,
        description="SCF options",
    )
    dft: Optional[DFTOptions] = Field(
        default=None,
        description="DFT options",
    )
    correlation: Optional[CorrelationOptions] = Field(
        default=None,
        description="Correlation options",
    )
    optimization: Optional[OptimizationOptions] = Field(
        default=None,
        description="Optimization options",
    )
    frequency: Optional[FrequencyOptions] = Field(
        default=None,
        description="Frequency options",
    )
    properties: Optional[PropertyOptions] = Field(
        default=None,
        description="Property options",
    )
    solvation: Optional[SolvationOptions] = Field(
        default=None,
        description="Solvation options",
    )
    extra_options: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Psi4 options",
    )
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Combine all options into a single Psi4 options dictionary."""
        opts: dict[str, Any] = {}
        
        # SCF options
        opts.update(self.scf.to_psi4_options())
        
        # DFT options
        if self.dft:
            opts.update(self.dft.to_psi4_options())
        
        # Correlation options
        if self.correlation:
            opts.update(self.correlation.to_psi4_options())
        
        # Optimization options
        if self.optimization:
            opts.update(self.optimization.to_psi4_options())
        
        # Frequency options
        if self.frequency:
            opts.update(self.frequency.to_psi4_options())
        
        # Solvation options
        if self.solvation:
            opts.update(self.solvation.to_psi4_options())
        
        # Extra options (override everything)
        opts.update(self.extra_options)
        
        return opts
