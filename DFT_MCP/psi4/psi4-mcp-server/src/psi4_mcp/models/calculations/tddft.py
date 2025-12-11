"""
TDDFT and Excited State Calculation Input Models.

This module provides Pydantic models for specifying time-dependent DFT
and other excited state calculations.

Key Classes:
    - TDDFTInput: Basic TDDFT calculation
    - TDAInput: Tamm-Dancoff approximation
    - EOMCCInput: EOM-CC calculations
    - CISInput: CIS calculations
    - ADCInput: ADC calculations
"""

from typing import Any, Optional, Literal
from pydantic import Field, field_validator, model_validator

from psi4_mcp.models.base import Psi4BaseModel
from psi4_mcp.models.calculations.energy import MoleculeInput, EnergyInput, DFTInput


# =============================================================================
# TDDFT INPUT
# =============================================================================

class TDDFTInput(Psi4BaseModel):
    """
    Time-dependent DFT calculation input.
    
    Attributes:
        molecule: Molecule specification.
        functional: DFT functional.
        basis: Basis set.
        n_states: Number of excited states.
        n_singlets: Number of singlet states.
        n_triplets: Number of triplet states.
        tda: Use Tamm-Dancoff approximation.
        rpa: Use random phase approximation (full TDDFT).
        target_states: Target specific states by symmetry.
        root_sym: Target symmetry irrep.
        e_convergence: Energy convergence threshold.
        r_convergence: Residual convergence threshold.
        max_iterations: Maximum Davidson iterations.
        guess: Initial guess type.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    functional: str = Field(
        default="b3lyp",
        description="DFT functional",
    )
    basis: str = Field(
        default="def2-tzvp",
        description="Basis set",
    )
    n_states: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of excited states",
    )
    n_singlets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of singlet states",
    )
    n_triplets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of triplet states",
    )
    tda: bool = Field(
        default=False,
        description="Use Tamm-Dancoff approximation",
    )
    rpa: bool = Field(
        default=True,
        description="Use RPA (full TDDFT)",
    )
    target_states: Optional[list[str]] = Field(
        default=None,
        description="Target states by symmetry",
    )
    root_sym: Optional[str] = Field(
        default=None,
        description="Target irrep",
    )
    e_convergence: float = Field(
        default=1e-6,
        gt=0,
        description="Energy convergence",
    )
    r_convergence: float = Field(
        default=1e-4,
        gt=0,
        description="Residual convergence",
    )
    max_iterations: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Max iterations",
    )
    guess: str = Field(
        default="denominators",
        description="Initial guess",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @model_validator(mode="after")
    def validate_state_counts(self) -> "TDDFTInput":
        """Validate state count specification."""
        if self.tda and self.rpa:
            # TDA takes precedence
            object.__setattr__(self, 'rpa', False)
        
        if self.n_singlets is not None or self.n_triplets is not None:
            # Use specific counts
            singlets = self.n_singlets or 0
            triplets = self.n_triplets or 0
            total = singlets + triplets
            if total > 0:
                object.__setattr__(self, 'n_states', total)
        
        return self
    
    @field_validator("functional")
    @classmethod
    def validate_functional(cls, v: str) -> str:
        """Normalize functional name."""
        return v.lower().strip().replace("_", "-")
    
    @field_validator("guess")
    @classmethod
    def validate_guess(cls, v: str) -> str:
        """Validate guess type."""
        valid = {"denominators", "read", "auto"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid guess: {v}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {
            "tdscf_states": self.n_states,
            "e_convergence": self.e_convergence,
            "r_convergence": self.r_convergence,
            "tdscf_maxiter": self.max_iterations,
            "tdscf_guess": self.guess,
        }
        
        if self.tda:
            opts["tdscf_tda"] = True
        
        if self.root_sym:
            opts["roots_per_irrep"] = self.root_sym
        
        return opts


class TDAInput(TDDFTInput):
    """
    Tamm-Dancoff Approximation input (simplified TDDFT).
    
    Same as TDDFTInput but with TDA enabled by default.
    """
    
    def __init__(self, **data: Any) -> None:
        data["tda"] = True
        data["rpa"] = False
        super().__init__(**data)


# =============================================================================
# EOM-CC INPUT
# =============================================================================

class EOMCCInput(Psi4BaseModel):
    """
    Equation-of-Motion Coupled Cluster input.
    
    Attributes:
        molecule: Molecule specification.
        eom_type: EOM-CC type (EE, IP, EA, SF).
        cc_method: CC method (ccsd, cc2, cc3).
        basis: Basis set.
        n_states: Number of excited states.
        n_singlets: Number of singlet states.
        n_triplets: Number of triplet states.
        roots_per_irrep: States per irrep.
        freeze_core: Freeze core orbitals.
        r_convergence: Residual convergence.
        max_iterations: Maximum iterations.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    eom_type: Literal["EE", "IP", "EA", "SF", "DIP", "DEA"] = Field(
        default="EE",
        description="EOM-CC type",
    )
    cc_method: str = Field(
        default="ccsd",
        description="CC method",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    n_states: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of states",
    )
    n_singlets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Singlet states",
    )
    n_triplets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Triplet states",
    )
    roots_per_irrep: Optional[dict[str, int]] = Field(
        default=None,
        description="Roots per irrep",
    )
    freeze_core: bool = Field(
        default=True,
        description="Freeze core",
    )
    r_convergence: float = Field(
        default=1e-6,
        gt=0,
        description="Residual convergence",
    )
    max_iterations: int = Field(
        default=100,
        ge=10,
        le=500,
        description="Max iterations",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @field_validator("cc_method")
    @classmethod
    def validate_cc_method(cls, v: str) -> str:
        """Validate CC method."""
        valid = {"ccsd", "cc2", "cc3", "ccsdt", "ccsdtq"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid CC method: {v}")
        return normalized
    
    def get_psi4_method(self) -> str:
        """Get Psi4 method string."""
        prefix = f"eom-{self.cc_method}" if self.eom_type == "EE" else f"{self.eom_type.lower()}-{self.cc_method}"
        return prefix
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {
            "freeze_core": self.freeze_core,
            "r_convergence": self.r_convergence,
            "maxiter": self.max_iterations,
        }
        
        # Set roots
        if self.eom_type == "EE":
            if self.n_singlets is not None:
                opts["roots_per_irrep"] = [self.n_singlets]
            else:
                opts["roots_per_irrep"] = [self.n_states]
        
        return opts


# =============================================================================
# CIS INPUT
# =============================================================================

class CISInput(Psi4BaseModel):
    """
    Configuration Interaction Singles input.
    
    Attributes:
        molecule: Molecule specification.
        basis: Basis set.
        n_states: Number of excited states.
        n_singlets: Singlet states.
        n_triplets: Triplet states.
        cis_d: Apply (D) correction.
        cis_d_plus: Apply (D+) correction.
        max_iterations: Max Davidson iterations.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    n_states: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of states",
    )
    n_singlets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Singlet states",
    )
    n_triplets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Triplet states",
    )
    cis_d: bool = Field(
        default=False,
        description="CIS(D) correction",
    )
    cis_d_plus: bool = Field(
        default=False,
        description="CIS(D+) correction",
    )
    max_iterations: int = Field(
        default=100,
        ge=10,
        le=500,
        description="Max iterations",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    def get_method(self) -> str:
        """Get method string."""
        if self.cis_d_plus:
            return "cis(d+)"
        elif self.cis_d:
            return "cis(d)"
        return "cis"


# =============================================================================
# ADC INPUT
# =============================================================================

class ADCInput(Psi4BaseModel):
    """
    Algebraic Diagrammatic Construction input.
    
    Attributes:
        molecule: Molecule specification.
        adc_level: ADC level (1, 2, 3).
        basis: Basis set.
        n_states: Number of excited states.
        n_singlets: Singlet states.
        n_triplets: Triplet states.
        strict: Use strict ADC.
        cvs: Use core-valence separation.
        cvs_orbitals: Core orbitals for CVS.
        freeze_core: Freeze core orbitals.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    adc_level: int = Field(
        default=2,
        ge=1,
        le=3,
        description="ADC level",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    n_states: int = Field(
        default=5,
        ge=1,
        le=100,
        description="Number of states",
    )
    n_singlets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Singlet states",
    )
    n_triplets: Optional[int] = Field(
        default=None,
        ge=0,
        description="Triplet states",
    )
    strict: bool = Field(
        default=False,
        description="Strict ADC",
    )
    cvs: bool = Field(
        default=False,
        description="Core-valence separation",
    )
    cvs_orbitals: Optional[list[int]] = Field(
        default=None,
        description="CVS core orbitals",
    )
    freeze_core: bool = Field(
        default=True,
        description="Freeze core",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    def get_method(self) -> str:
        """Get method string."""
        prefix = "cvs-" if self.cvs else ""
        suffix = "-s" if self.strict else ""
        return f"{prefix}adc({self.adc_level}){suffix}"


# =============================================================================
# NATURAL TRANSITION ORBITAL INPUT
# =============================================================================

class NTOInput(Psi4BaseModel):
    """
    Natural Transition Orbital analysis input.
    
    Attributes:
        molecule: Molecule specification.
        method: Excited state method.
        basis: Basis set.
        states: States to analyze.
        threshold: NTO threshold for printing.
        save_ntos: Save NTOs to file.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    method: str = Field(
        default="tddft",
        description="Excited state method",
    )
    basis: str = Field(
        default="def2-tzvp",
        description="Basis set",
    )
    states: list[int] = Field(
        default_factory=lambda: [1],
        description="States to analyze (1-indexed)",
    )
    threshold: float = Field(
        default=0.1,
        ge=0,
        le=1,
        description="NTO threshold",
    )
    save_ntos: bool = Field(
        default=False,
        description="Save NTOs to file",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )


# =============================================================================
# EXCITED STATE OPTIMIZATION INPUT
# =============================================================================

class ExcitedStateOptInput(Psi4BaseModel):
    """
    Excited state geometry optimization input.
    
    Attributes:
        molecule: Molecule specification.
        method: Excited state method.
        functional: DFT functional (for TDDFT).
        basis: Basis set.
        target_state: Target state number (1-indexed).
        target_multiplicity: Target multiplicity.
        geom_maxiter: Max optimization steps.
        gradient_method: Gradient method (analytical, numerical).
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    method: str = Field(
        default="tddft",
        description="Excited state method",
    )
    functional: str = Field(
        default="b3lyp",
        description="DFT functional",
    )
    basis: str = Field(
        default="def2-tzvp",
        description="Basis set",
    )
    target_state: int = Field(
        default=1,
        ge=1,
        description="Target state (1-indexed)",
    )
    target_multiplicity: int = Field(
        default=1,
        ge=1,
        description="Target multiplicity",
    )
    geom_maxiter: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Max optimization steps",
    )
    gradient_method: Literal["analytical", "numerical"] = Field(
        default="analytical",
        description="Gradient method",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )


# =============================================================================
# SPIN-FLIP INPUT
# =============================================================================

class SpinFlipInput(Psi4BaseModel):
    """
    Spin-flip TDDFT/EOM-CC input.
    
    For computing states with different spin from the reference.
    
    Attributes:
        molecule: Molecule specification.
        method: SF method (sf-tddft, sf-ccsd).
        functional: DFT functional (for SF-TDDFT).
        basis: Basis set.
        n_states: Number of states.
        reference_multiplicity: Reference state multiplicity.
        target_multiplicity: Target state multiplicity.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    method: str = Field(
        default="sf-tddft",
        description="SF method",
    )
    functional: str = Field(
        default="bhhlyp",
        description="DFT functional",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    n_states: int = Field(
        default=5,
        ge=1,
        description="Number of states",
    )
    reference_multiplicity: int = Field(
        default=3,
        ge=1,
        description="Reference multiplicity",
    )
    target_multiplicity: int = Field(
        default=1,
        ge=1,
        description="Target multiplicity",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate SF method."""
        valid = {"sf-tddft", "sf-ccsd", "sf-eom-ccsd", "sf-adc"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid SF method: {v}")
        return normalized
