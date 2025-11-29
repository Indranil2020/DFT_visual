"""
Geometry Optimization Output Models.

This module provides Pydantic models for representing geometry optimization
results, including optimization trajectories, convergence information,
and transition state searches.

Key Classes:
    - OptimizationStep: Single optimization step data
    - OptimizationTrajectory: Complete optimization path
    - OptimizationOutput: Full optimization result
    - TransitionStateOutput: TS search results
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel, CalculationOutput


# =============================================================================
# OPTIMIZATION STEP
# =============================================================================

class GradientInfo(Psi4BaseModel):
    """
    Gradient information for an optimization step.
    
    Attributes:
        rms_gradient: RMS of gradient.
        max_gradient: Maximum gradient component.
        rms_force: RMS of forces.
        max_force: Maximum force component.
        gradient_norm: Total gradient norm.
    """
    
    rms_gradient: Optional[float] = Field(
        default=None,
        ge=0,
        description="RMS gradient",
    )
    max_gradient: Optional[float] = Field(
        default=None,
        ge=0,
        description="Maximum gradient component",
    )
    rms_force: Optional[float] = Field(
        default=None,
        ge=0,
        description="RMS force",
    )
    max_force: Optional[float] = Field(
        default=None,
        ge=0,
        description="Maximum force component",
    )
    gradient_norm: Optional[float] = Field(
        default=None,
        ge=0,
        description="Total gradient norm",
    )


class DisplacementInfo(Psi4BaseModel):
    """
    Displacement information for an optimization step.
    
    Attributes:
        rms_displacement: RMS displacement from previous step.
        max_displacement: Maximum displacement component.
        step_length: Total step length.
    """
    
    rms_displacement: Optional[float] = Field(
        default=None,
        ge=0,
        description="RMS displacement",
    )
    max_displacement: Optional[float] = Field(
        default=None,
        ge=0,
        description="Maximum displacement",
    )
    step_length: Optional[float] = Field(
        default=None,
        ge=0,
        description="Total step length",
    )


class ConvergenceCriteria(Psi4BaseModel):
    """
    Convergence criteria thresholds.
    
    Attributes:
        max_force: Maximum force threshold.
        rms_force: RMS force threshold.
        max_displacement: Maximum displacement threshold.
        rms_displacement: RMS displacement threshold.
        energy_change: Energy change threshold.
    """
    
    max_force: float = Field(
        default=4.5e-4,
        gt=0,
        description="Maximum force threshold (Hartree/Bohr)",
    )
    rms_force: float = Field(
        default=3.0e-4,
        gt=0,
        description="RMS force threshold (Hartree/Bohr)",
    )
    max_displacement: float = Field(
        default=1.8e-3,
        gt=0,
        description="Maximum displacement threshold (Bohr)",
    )
    rms_displacement: float = Field(
        default=1.2e-3,
        gt=0,
        description="RMS displacement threshold (Bohr)",
    )
    energy_change: float = Field(
        default=1.0e-6,
        gt=0,
        description="Energy change threshold (Hartree)",
    )
    
    @classmethod
    def gaussian_tight(cls) -> "ConvergenceCriteria":
        """Gaussian TIGHT convergence criteria."""
        return cls(
            max_force=1.5e-5,
            rms_force=1.0e-5,
            max_displacement=6.0e-5,
            rms_displacement=4.0e-5,
            energy_change=1.0e-8,
        )
    
    @classmethod
    def gaussian_verytight(cls) -> "ConvergenceCriteria":
        """Gaussian VERYTIGHT convergence criteria."""
        return cls(
            max_force=2.0e-6,
            rms_force=1.0e-6,
            max_displacement=6.0e-6,
            rms_displacement=4.0e-6,
            energy_change=1.0e-9,
        )
    
    @classmethod
    def gaussian_loose(cls) -> "ConvergenceCriteria":
        """Gaussian LOOSE convergence criteria."""
        return cls(
            max_force=2.5e-3,
            rms_force=1.7e-3,
            max_displacement=1.0e-2,
            rms_displacement=6.7e-3,
            energy_change=1.0e-4,
        )


class ConvergenceStatus(Psi4BaseModel):
    """
    Convergence status for a single criterion.
    
    Attributes:
        criterion: Name of the criterion.
        value: Current value.
        threshold: Convergence threshold.
        converged: Whether this criterion is converged.
    """
    
    criterion: str = Field(
        ...,
        description="Criterion name",
    )
    value: float = Field(
        ...,
        description="Current value",
    )
    threshold: float = Field(
        ...,
        gt=0,
        description="Convergence threshold",
    )
    converged: bool = Field(
        ...,
        description="Whether converged",
    )
    
    @model_validator(mode="after")
    def check_convergence(self) -> "ConvergenceStatus":
        """Auto-determine convergence if not set."""
        expected = abs(self.value) <= self.threshold
        if self.converged != expected:
            object.__setattr__(self, 'converged', expected)
        return self


class OptimizationStep(Psi4BaseModel):
    """
    Data for a single geometry optimization step.
    
    Attributes:
        step_number: Step number (0-indexed).
        energy: Energy at this geometry.
        energy_change: Energy change from previous step.
        gradient: Gradient information.
        displacement: Displacement information.
        convergence_status: Convergence status for each criterion.
        coordinates: Atomic coordinates at this step.
        trust_radius: Trust radius used.
        step_type: Type of step taken (RFO, SD, etc.).
        hessian_update: Hessian update method used.
        is_converged: Whether optimization is converged at this step.
    """
    
    step_number: int = Field(
        ...,
        ge=0,
        description="Step number",
    )
    energy: float = Field(
        ...,
        description="Energy in Hartree",
    )
    energy_change: Optional[float] = Field(
        default=None,
        description="Energy change from previous step",
    )
    gradient: Optional[GradientInfo] = Field(
        default=None,
        description="Gradient information",
    )
    displacement: Optional[DisplacementInfo] = Field(
        default=None,
        description="Displacement information",
    )
    convergence_status: list[ConvergenceStatus] = Field(
        default_factory=list,
        description="Convergence status",
    )
    coordinates: Optional[list[list[float]]] = Field(
        default=None,
        description="Coordinates [[x,y,z], ...]",
    )
    trust_radius: Optional[float] = Field(
        default=None,
        gt=0,
        description="Trust radius",
    )
    step_type: Optional[str] = Field(
        default=None,
        description="Step type (RFO, SD, etc.)",
    )
    hessian_update: Optional[str] = Field(
        default=None,
        description="Hessian update method",
    )
    is_converged: bool = Field(
        default=False,
        description="Whether converged",
    )
    
    @property
    def n_converged_criteria(self) -> int:
        """Number of converged criteria."""
        return sum(1 for s in self.convergence_status if s.converged)
    
    @property
    def n_total_criteria(self) -> int:
        """Total number of criteria."""
        return len(self.convergence_status)


# =============================================================================
# OPTIMIZATION TRAJECTORY
# =============================================================================

class OptimizationTrajectory(Psi4BaseModel):
    """
    Complete optimization trajectory.
    
    Attributes:
        steps: List of optimization steps.
        symbols: Atomic symbols.
        initial_energy: Initial energy.
        final_energy: Final energy.
        energy_lowering: Total energy lowering.
    """
    
    steps: list[OptimizationStep] = Field(
        ...,
        min_length=1,
        description="Optimization steps",
    )
    symbols: list[str] = Field(
        ...,
        min_length=1,
        description="Atomic symbols",
    )
    initial_energy: float = Field(
        ...,
        description="Initial energy in Hartree",
    )
    final_energy: float = Field(
        ...,
        description="Final energy in Hartree",
    )
    energy_lowering: Optional[float] = Field(
        default=None,
        description="Total energy lowering",
    )
    
    @property
    def n_steps(self) -> int:
        """Number of optimization steps."""
        return len(self.steps)
    
    @property
    def energies(self) -> list[float]:
        """List of energies at each step."""
        return [step.energy for step in self.steps]
    
    @property
    def converged_at_step(self) -> Optional[int]:
        """Step number where optimization converged (or None)."""
        for step in self.steps:
            if step.is_converged:
                return step.step_number
        return None
    
    @model_validator(mode="after")
    def compute_energy_lowering(self) -> "OptimizationTrajectory":
        """Compute energy lowering if not provided."""
        if self.energy_lowering is None:
            delta = self.initial_energy - self.final_energy
            object.__setattr__(self, 'energy_lowering', delta)
        return self
    
    def get_coordinates_at_step(self, step: int) -> Optional[list[list[float]]]:
        """Get coordinates at a specific step."""
        for s in self.steps:
            if s.step_number == step:
                return s.coordinates
        return None
    
    def to_xyz_trajectory(self, units: str = "angstrom") -> str:
        """
        Export trajectory as multi-frame XYZ file.
        
        Args:
            units: Coordinate units (angstrom or bohr).
            
        Returns:
            Multi-frame XYZ string.
        """
        from psi4_mcp.utils.helpers.constants import BOHR_TO_ANGSTROM
        
        frames = []
        factor = BOHR_TO_ANGSTROM if units == "angstrom" else 1.0
        
        for step in self.steps:
            if step.coordinates is None:
                continue
            
            lines = [str(len(self.symbols))]
            lines.append(f"Step {step.step_number}, E = {step.energy:.10f} Hartree")
            
            for symbol, coords in zip(self.symbols, step.coordinates):
                x, y, z = coords[0] * factor, coords[1] * factor, coords[2] * factor
                lines.append(f"{symbol:>2s}  {x:16.10f}  {y:16.10f}  {z:16.10f}")
            
            frames.append("\n".join(lines))
        
        return "\n".join(frames)


# =============================================================================
# INTERNAL COORDINATES
# =============================================================================

class InternalCoordinateValue(Psi4BaseModel):
    """
    Value of an internal coordinate.
    
    Attributes:
        coord_type: Type of coordinate (bond, angle, dihedral).
        atoms: Atom indices involved (1-indexed).
        value: Coordinate value.
        unit: Unit of the value (angstrom, degree).
        is_frozen: Whether this coordinate is frozen.
    """
    
    coord_type: Literal["bond", "angle", "dihedral", "out_of_plane"] = Field(
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
        description="Coordinate value",
    )
    unit: str = Field(
        default="angstrom",
        description="Value unit",
    )
    is_frozen: bool = Field(
        default=False,
        description="Whether frozen",
    )
    
    @property
    def atom_string(self) -> str:
        """String representation of atoms."""
        return "-".join(str(a) for a in self.atoms)


class InternalCoordinates(Psi4BaseModel):
    """
    Collection of internal coordinates.
    
    Attributes:
        bonds: Bond lengths.
        angles: Bond angles.
        dihedrals: Dihedral angles.
        out_of_plane: Out-of-plane angles.
    """
    
    bonds: list[InternalCoordinateValue] = Field(
        default_factory=list,
        description="Bond lengths",
    )
    angles: list[InternalCoordinateValue] = Field(
        default_factory=list,
        description="Bond angles",
    )
    dihedrals: list[InternalCoordinateValue] = Field(
        default_factory=list,
        description="Dihedral angles",
    )
    out_of_plane: list[InternalCoordinateValue] = Field(
        default_factory=list,
        description="Out-of-plane angles",
    )
    
    @property
    def n_coordinates(self) -> int:
        """Total number of internal coordinates."""
        return len(self.bonds) + len(self.angles) + len(self.dihedrals) + len(self.out_of_plane)


# =============================================================================
# OPTIMIZATION OUTPUT
# =============================================================================

class OptimizationOutput(CalculationOutput):
    """
    Complete geometry optimization output.
    
    Attributes:
        converged: Whether optimization converged.
        n_steps: Number of optimization steps.
        initial_energy: Initial energy.
        final_energy: Final (optimized) energy.
        energy_change: Total energy change.
        initial_coordinates: Initial coordinates.
        final_coordinates: Final (optimized) coordinates.
        symbols: Atomic symbols.
        trajectory: Complete optimization trajectory.
        convergence_criteria: Convergence criteria used.
        final_gradient: Final gradient information.
        internal_coordinates: Final internal coordinates.
        optimization_type: Type of optimization (min, ts, irc).
        coordinate_system: Coordinate system used.
        hessian_eigenvalues: Hessian eigenvalues at final geometry.
        n_imaginary: Number of imaginary frequencies (if computed).
    """
    
    converged: bool = Field(
        ...,
        description="Whether optimization converged",
    )
    n_steps: int = Field(
        ...,
        ge=0,
        description="Number of optimization steps",
    )
    initial_energy: float = Field(
        ...,
        description="Initial energy in Hartree",
    )
    final_energy: float = Field(
        ...,
        description="Final energy in Hartree",
    )
    energy_change: Optional[float] = Field(
        default=None,
        description="Total energy change",
    )
    initial_coordinates: list[list[float]] = Field(
        ...,
        description="Initial coordinates [[x,y,z], ...]",
    )
    final_coordinates: list[list[float]] = Field(
        ...,
        description="Final coordinates [[x,y,z], ...]",
    )
    symbols: list[str] = Field(
        ...,
        min_length=1,
        description="Atomic symbols",
    )
    trajectory: Optional[OptimizationTrajectory] = Field(
        default=None,
        description="Optimization trajectory",
    )
    convergence_criteria: Optional[ConvergenceCriteria] = Field(
        default=None,
        description="Convergence criteria used",
    )
    final_gradient: Optional[GradientInfo] = Field(
        default=None,
        description="Final gradient information",
    )
    internal_coordinates: Optional[InternalCoordinates] = Field(
        default=None,
        description="Final internal coordinates",
    )
    optimization_type: Literal["min", "ts", "irc_forward", "irc_backward"] = Field(
        default="min",
        description="Optimization type",
    )
    coordinate_system: str = Field(
        default="cartesian",
        description="Coordinate system used",
    )
    hessian_eigenvalues: Optional[list[float]] = Field(
        default=None,
        description="Hessian eigenvalues",
    )
    n_imaginary: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of imaginary frequencies",
    )
    
    @property
    def is_minimum(self) -> bool:
        """Check if this is likely a minimum (no imaginary frequencies)."""
        if self.n_imaginary is not None:
            return self.n_imaginary == 0
        if self.hessian_eigenvalues is not None:
            return all(ev > -1e-6 for ev in self.hessian_eigenvalues)
        return self.optimization_type == "min" and self.converged
    
    @property
    def is_transition_state(self) -> bool:
        """Check if this is likely a transition state (one imaginary)."""
        if self.n_imaginary is not None:
            return self.n_imaginary == 1
        if self.hessian_eigenvalues is not None:
            n_neg = sum(1 for ev in self.hessian_eigenvalues if ev < -1e-6)
            return n_neg == 1
        return self.optimization_type == "ts" and self.converged
    
    @model_validator(mode="after")
    def compute_energy_change(self) -> "OptimizationOutput":
        """Compute energy change if not provided."""
        if self.energy_change is None:
            delta = self.final_energy - self.initial_energy
            object.__setattr__(self, 'energy_change', delta)
        return self
    
    def to_xyz_string(self, which: str = "final") -> str:
        """
        Export geometry as XYZ string.
        
        Args:
            which: "initial" or "final" geometry.
            
        Returns:
            XYZ format string.
        """
        coords = self.final_coordinates if which == "final" else self.initial_coordinates
        energy = self.final_energy if which == "final" else self.initial_energy
        
        lines = [str(len(self.symbols))]
        lines.append(f"E = {energy:.10f} Hartree")
        
        for symbol, xyz in zip(self.symbols, coords):
            x, y, z = xyz
            lines.append(f"{symbol:>2s}  {x:16.10f}  {y:16.10f}  {z:16.10f}")
        
        return "\n".join(lines)


# =============================================================================
# TRANSITION STATE OUTPUT
# =============================================================================

class TransitionStateOutput(OptimizationOutput):
    """
    Transition state search output.
    
    Attributes:
        imaginary_frequency: The imaginary frequency in cm^-1.
        reaction_coordinate: Reaction coordinate mode.
        barrier_height_forward: Forward barrier height.
        barrier_height_reverse: Reverse barrier height.
        reactant_energy: Reactant energy (if provided).
        product_energy: Product energy (if provided).
    """
    
    imaginary_frequency: Optional[float] = Field(
        default=None,
        description="Imaginary frequency in cm^-1",
    )
    reaction_coordinate: Optional[list[list[float]]] = Field(
        default=None,
        description="Reaction coordinate displacement vectors",
    )
    barrier_height_forward: Optional[float] = Field(
        default=None,
        description="Forward barrier (TS - reactant) in Hartree",
    )
    barrier_height_reverse: Optional[float] = Field(
        default=None,
        description="Reverse barrier (TS - product) in Hartree",
    )
    reactant_energy: Optional[float] = Field(
        default=None,
        description="Reactant energy in Hartree",
    )
    product_energy: Optional[float] = Field(
        default=None,
        description="Product energy in Hartree",
    )
    
    def __init__(self, **data: Any) -> None:
        if "optimization_type" not in data:
            data["optimization_type"] = "ts"
        super().__init__(**data)


# =============================================================================
# IRC OUTPUT
# =============================================================================

class IRCPoint(Psi4BaseModel):
    """
    Single point along an IRC path.
    
    Attributes:
        step_number: Step number.
        reaction_coordinate: Reaction coordinate value.
        energy: Energy at this point.
        coordinates: Coordinates at this point.
    """
    
    step_number: int = Field(
        ...,
        description="Step number",
    )
    reaction_coordinate: float = Field(
        ...,
        description="Reaction coordinate value",
    )
    energy: float = Field(
        ...,
        description="Energy in Hartree",
    )
    coordinates: list[list[float]] = Field(
        ...,
        description="Coordinates [[x,y,z], ...]",
    )


class IRCOutput(CalculationOutput):
    """
    Intrinsic Reaction Coordinate calculation output.
    
    Attributes:
        ts_energy: Transition state energy.
        ts_coordinates: Transition state coordinates.
        forward_path: Forward IRC path.
        backward_path: Backward IRC path.
        symbols: Atomic symbols.
        n_forward_steps: Number of forward steps.
        n_backward_steps: Number of backward steps.
        forward_endpoint_energy: Energy at forward endpoint.
        backward_endpoint_energy: Energy at backward endpoint.
    """
    
    ts_energy: float = Field(
        ...,
        description="TS energy in Hartree",
    )
    ts_coordinates: list[list[float]] = Field(
        ...,
        description="TS coordinates",
    )
    forward_path: list[IRCPoint] = Field(
        default_factory=list,
        description="Forward IRC path",
    )
    backward_path: list[IRCPoint] = Field(
        default_factory=list,
        description="Backward IRC path",
    )
    symbols: list[str] = Field(
        ...,
        min_length=1,
        description="Atomic symbols",
    )
    n_forward_steps: int = Field(
        default=0,
        ge=0,
        description="Number of forward steps",
    )
    n_backward_steps: int = Field(
        default=0,
        ge=0,
        description="Number of backward steps",
    )
    forward_endpoint_energy: Optional[float] = Field(
        default=None,
        description="Forward endpoint energy",
    )
    backward_endpoint_energy: Optional[float] = Field(
        default=None,
        description="Backward endpoint energy",
    )
    
    @property
    def full_path(self) -> list[IRCPoint]:
        """Get complete IRC path (backward + TS + forward)."""
        # Reverse backward path so it goes from reactant to TS
        backward_reversed = list(reversed(self.backward_path))
        
        # Create TS point
        ts_point = IRCPoint(
            step_number=0,
            reaction_coordinate=0.0,
            energy=self.ts_energy,
            coordinates=self.ts_coordinates,
        )
        
        return backward_reversed + [ts_point] + self.forward_path
    
    @property
    def reaction_energy(self) -> Optional[float]:
        """Reaction energy (product - reactant)."""
        if self.forward_endpoint_energy is not None and self.backward_endpoint_energy is not None:
            return self.forward_endpoint_energy - self.backward_endpoint_energy
        return None
