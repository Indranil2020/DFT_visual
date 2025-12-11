"""
Geometry Optimization Input Models.

This module provides Pydantic models for specifying geometry optimization
inputs, including minima, transition states, and reaction paths.

Key Classes:
    - OptimizationInput: Basic geometry optimization
    - ConstrainedOptimizationInput: Optimization with constraints
    - TransitionStateInput: Transition state search
    - IRCInput: Intrinsic reaction coordinate
    - ScanInput: Coordinate scans
"""

from typing import Any, Optional, Literal, Union
from pydantic import Field, field_validator, model_validator

from psi4_mcp.models.base import Psi4BaseModel
from psi4_mcp.models.calculations.energy import MoleculeInput, EnergyInput
from psi4_mcp.models.options import OptimizationOptions, SCFOptions


# =============================================================================
# COORDINATE CONSTRAINTS
# =============================================================================

class FrozenCoordinate(Psi4BaseModel):
    """
    Frozen coordinate specification.
    
    Attributes:
        coord_type: Type of coordinate (distance, angle, dihedral).
        atoms: Atom indices (1-indexed).
    """
    
    coord_type: Literal["distance", "angle", "dihedral"] = Field(
        ...,
        description="Coordinate type",
    )
    atoms: list[int] = Field(
        ...,
        min_length=2,
        max_length=4,
        description="Atom indices (1-indexed)",
    )
    
    @field_validator("atoms")
    @classmethod
    def validate_atoms(cls, v: list[int], info: Any) -> list[int]:
        """Validate atom count matches coordinate type."""
        coord_type = info.data.get("coord_type", "distance")
        expected = {"distance": 2, "angle": 3, "dihedral": 4}
        if len(v) != expected.get(coord_type, 2):
            raise ValueError(
                f"{coord_type} requires {expected[coord_type]} atoms, got {len(v)}"
            )
        return v


class FixedCoordinate(Psi4BaseModel):
    """
    Fixed coordinate at specific value.
    
    Attributes:
        coord_type: Type of coordinate.
        atoms: Atom indices (1-indexed).
        value: Fixed value (Angstrom for distance, degrees for angles).
    """
    
    coord_type: Literal["distance", "angle", "dihedral"] = Field(
        ...,
        description="Coordinate type",
    )
    atoms: list[int] = Field(
        ...,
        min_length=2,
        max_length=4,
        description="Atom indices (1-indexed)",
    )
    value: float = Field(
        ...,
        description="Fixed value",
    )


class CartesianConstraint(Psi4BaseModel):
    """
    Cartesian coordinate constraint.
    
    Attributes:
        atom: Atom index (1-indexed).
        x: Fix X coordinate.
        y: Fix Y coordinate.
        z: Fix Z coordinate.
    """
    
    atom: int = Field(
        ...,
        ge=1,
        description="Atom index (1-indexed)",
    )
    x: bool = Field(
        default=False,
        description="Fix X",
    )
    y: bool = Field(
        default=False,
        description="Fix Y",
    )
    z: bool = Field(
        default=False,
        description="Fix Z",
    )
    
    @property
    def is_fully_frozen(self) -> bool:
        """Check if atom is fully frozen."""
        return self.x and self.y and self.z


# =============================================================================
# BASIC OPTIMIZATION INPUT
# =============================================================================

class OptimizationInput(EnergyInput):
    """
    Basic geometry optimization input.
    
    Attributes:
        opt_options: Optimization-specific options.
        opt_type: Optimization type (min, ts).
        coord_type: Coordinate system.
        full_hess_every: Compute full Hessian every N steps.
        hess_update: Hessian update scheme.
        trajectory: Save optimization trajectory.
        geom_maxiter: Maximum optimization steps.
    """
    
    opt_options: OptimizationOptions = Field(
        default_factory=OptimizationOptions,
        description="Optimization options",
    )
    opt_type: Literal["min", "ts"] = Field(
        default="min",
        description="Optimization type",
    )
    coord_type: Literal["cartesian", "internal", "both"] = Field(
        default="cartesian",
        description="Coordinate system",
    )
    full_hess_every: int = Field(
        default=-1,
        description="Full Hessian frequency (-1 for never)",
    )
    hess_update: str = Field(
        default="bfgs",
        description="Hessian update (bfgs, ms, powell, none)",
    )
    trajectory: bool = Field(
        default=True,
        description="Save trajectory",
    )
    geom_maxiter: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum optimization steps",
    )
    
    @field_validator("hess_update")
    @classmethod
    def validate_hess_update(cls, v: str) -> str:
        """Validate Hessian update method."""
        valid = {"bfgs", "ms", "powell", "none", "sr1"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid hess_update: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = self.opt_options.to_psi4_options()
        opts.update(self.options)
        
        opts["geom_maxiter"] = self.geom_maxiter
        opts["opt_coordinates"] = self.coord_type
        
        if self.full_hess_every >= 0:
            opts["full_hess_every"] = self.full_hess_every
        
        if self.opt_type == "ts":
            opts["opt_type"] = "ts"
        
        return opts


# =============================================================================
# CONSTRAINED OPTIMIZATION
# =============================================================================

class ConstrainedOptimizationInput(OptimizationInput):
    """
    Geometry optimization with constraints.
    
    Attributes:
        frozen_coordinates: Coordinates to freeze.
        fixed_coordinates: Coordinates fixed at specific values.
        cartesian_constraints: Cartesian coordinate constraints.
        frozen_atoms: Atoms to completely freeze.
    """
    
    frozen_coordinates: list[FrozenCoordinate] = Field(
        default_factory=list,
        description="Frozen coordinates",
    )
    fixed_coordinates: list[FixedCoordinate] = Field(
        default_factory=list,
        description="Fixed coordinates",
    )
    cartesian_constraints: list[CartesianConstraint] = Field(
        default_factory=list,
        description="Cartesian constraints",
    )
    frozen_atoms: list[int] = Field(
        default_factory=list,
        description="Completely frozen atoms (1-indexed)",
    )
    
    def get_optking_frozen_string(self) -> Optional[str]:
        """Generate optking frozen coordinate string."""
        lines = []
        
        # Frozen internal coordinates
        for coord in self.frozen_coordinates:
            atoms_str = " ".join(str(a) for a in coord.atoms)
            if coord.coord_type == "distance":
                lines.append(f"R {atoms_str}")
            elif coord.coord_type == "angle":
                lines.append(f"B {atoms_str}")
            elif coord.coord_type == "dihedral":
                lines.append(f"D {atoms_str}")
        
        # Fixed internal coordinates
        for coord in self.fixed_coordinates:
            atoms_str = " ".join(str(a) for a in coord.atoms)
            if coord.coord_type == "distance":
                lines.append(f"R {atoms_str} = {coord.value}")
            elif coord.coord_type == "angle":
                lines.append(f"B {atoms_str} = {coord.value}")
            elif coord.coord_type == "dihedral":
                lines.append(f"D {atoms_str} = {coord.value}")
        
        # Frozen Cartesians
        for constraint in self.cartesian_constraints:
            if constraint.x:
                lines.append(f"X {constraint.atom}")
            if constraint.y:
                lines.append(f"Y {constraint.atom}")
            if constraint.z:
                lines.append(f"Z {constraint.atom}")
        
        # Completely frozen atoms
        for atom in self.frozen_atoms:
            lines.append(f"X {atom}")
            lines.append(f"Y {atom}")
            lines.append(f"Z {atom}")
        
        if lines:
            return "\n".join(lines)
        return None


# =============================================================================
# TRANSITION STATE SEARCH
# =============================================================================

class TransitionStateInput(OptimizationInput):
    """
    Transition state search input.
    
    Attributes:
        initial_hessian: Initial Hessian source.
        ts_mode: Mode to follow to TS.
        eigenvector_follow: Follow specific eigenvector.
        reactant_geometry: Reactant geometry (for QST methods).
        product_geometry: Product geometry (for QST methods).
        qst_method: QST method (qst2, qst3).
    """
    
    initial_hessian: str = Field(
        default="calc",
        description="Initial Hessian (calc, read, guess)",
    )
    ts_mode: Optional[int] = Field(
        default=None,
        ge=1,
        description="Mode to follow (1-indexed)",
    )
    eigenvector_follow: bool = Field(
        default=True,
        description="Follow eigenvector",
    )
    reactant_geometry: Optional[str] = Field(
        default=None,
        description="Reactant geometry (for QST)",
    )
    product_geometry: Optional[str] = Field(
        default=None,
        description="Product geometry (for QST)",
    )
    qst_method: Optional[Literal["qst2", "qst3"]] = Field(
        default=None,
        description="QST method",
    )
    
    def __init__(self, **data: Any) -> None:
        data["opt_type"] = "ts"
        super().__init__(**data)
    
    @field_validator("initial_hessian")
    @classmethod
    def validate_initial_hessian(cls, v: str) -> str:
        """Validate initial Hessian source."""
        valid = {"calc", "read", "guess", "fischer", "lindh", "simple", "schlegel"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid initial_hessian: {v}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = super().to_psi4_options()
        opts["opt_type"] = "ts"
        opts["full_hess_every"] = 0 if self.initial_hessian == "calc" else -1
        
        if self.ts_mode is not None:
            opts["ts_eigenvector_follow"] = self.ts_mode
        
        return opts


# =============================================================================
# IRC CALCULATION
# =============================================================================

class IRCInput(Psi4BaseModel):
    """
    Intrinsic Reaction Coordinate calculation input.
    
    Attributes:
        molecule: Transition state geometry.
        method: Calculation method.
        basis: Basis set.
        direction: IRC direction.
        step_size: Step size in amu^1/2 bohr.
        max_steps: Maximum IRC steps.
        algorithm: IRC algorithm.
        hessian: Hessian source.
        mode: Reaction mode to follow.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="TS geometry",
    )
    method: str = Field(
        default="hf",
        description="Calculation method",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    direction: Literal["forward", "backward", "both"] = Field(
        default="both",
        description="IRC direction",
    )
    step_size: float = Field(
        default=0.2,
        gt=0,
        le=1.0,
        description="Step size",
    )
    max_steps: int = Field(
        default=20,
        ge=1,
        le=200,
        description="Maximum steps",
    )
    algorithm: str = Field(
        default="gs2",
        description="IRC algorithm",
    )
    hessian: str = Field(
        default="calc",
        description="Hessian source",
    )
    mode: int = Field(
        default=1,
        ge=1,
        description="Reaction mode",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Number of threads",
    )
    
    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        """Validate IRC algorithm."""
        valid = {"gs2", "euler", "dvv"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid IRC algorithm: {v}")
        return normalized


# =============================================================================
# COORDINATE SCAN
# =============================================================================

class ScanCoordinate(Psi4BaseModel):
    """
    Coordinate to scan.
    
    Attributes:
        coord_type: Type of coordinate.
        atoms: Atom indices (1-indexed).
        start: Starting value.
        stop: Ending value.
        steps: Number of steps.
    """
    
    coord_type: Literal["distance", "angle", "dihedral"] = Field(
        ...,
        description="Coordinate type",
    )
    atoms: list[int] = Field(
        ...,
        min_length=2,
        max_length=4,
        description="Atom indices (1-indexed)",
    )
    start: float = Field(
        ...,
        description="Start value",
    )
    stop: float = Field(
        ...,
        description="Stop value",
    )
    steps: int = Field(
        default=10,
        ge=2,
        le=100,
        description="Number of steps",
    )
    
    @property
    def step_size(self) -> float:
        """Calculate step size."""
        return (self.stop - self.start) / (self.steps - 1)
    
    @property
    def values(self) -> list[float]:
        """Get all scan values."""
        step = self.step_size
        return [self.start + i * step for i in range(self.steps)]


class ScanInput(Psi4BaseModel):
    """
    Potential energy surface scan input.
    
    Attributes:
        molecule: Initial geometry.
        method: Calculation method.
        basis: Basis set.
        scan_coordinates: Coordinates to scan.
        optimize_other: Optimize non-scanned coordinates.
        grid_scan: Perform grid scan (multiple coordinates).
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Initial geometry",
    )
    method: str = Field(
        default="hf",
        description="Calculation method",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    scan_coordinates: list[ScanCoordinate] = Field(
        ...,
        min_length=1,
        description="Coordinates to scan",
    )
    optimize_other: bool = Field(
        default=True,
        description="Optimize other coordinates",
    )
    grid_scan: bool = Field(
        default=False,
        description="Grid scan (all combinations)",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Number of threads",
    )
    
    @property
    def n_dimensions(self) -> int:
        """Number of scan dimensions."""
        return len(self.scan_coordinates)
    
    @property
    def n_points(self) -> int:
        """Total number of scan points."""
        if self.grid_scan:
            product = 1
            for coord in self.scan_coordinates:
                product *= coord.steps
            return product
        else:
            # Sequential scan
            return sum(coord.steps for coord in self.scan_coordinates)


# =============================================================================
# BATCH OPTIMIZATION
# =============================================================================

class BatchOptimizationInput(Psi4BaseModel):
    """
    Batch geometry optimization for multiple structures.
    
    Attributes:
        structures: Dictionary of name -> geometry.
        method: Calculation method.
        basis: Basis set.
        opt_options: Optimization options.
        parallel: Run in parallel.
        max_parallel: Maximum parallel jobs.
    """
    
    structures: dict[str, str] = Field(
        ...,
        min_length=1,
        description="Name -> geometry mapping",
    )
    method: str = Field(
        default="b3lyp",
        description="Calculation method",
    )
    basis: str = Field(
        default="def2-svp",
        description="Basis set",
    )
    opt_options: OptimizationOptions = Field(
        default_factory=OptimizationOptions,
        description="Optimization options",
    )
    parallel: bool = Field(
        default=False,
        description="Run in parallel",
    )
    max_parallel: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Max parallel jobs",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory per job in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads per job",
    )
    
    def get_optimization_inputs(self) -> dict[str, OptimizationInput]:
        """Generate individual optimization inputs."""
        inputs = {}
        for name, geometry in self.structures.items():
            mol_input = MoleculeInput(geometry=geometry, name=name)
            inputs[name] = OptimizationInput(
                molecule=mol_input,
                method=self.method,
                basis=self.basis,
                opt_options=self.opt_options,
                memory=self.memory,
                n_threads=self.n_threads,
            )
        return inputs
