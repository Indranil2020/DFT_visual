"""
Geometry optimization convergence utilities.

Provides tools for monitoring and improving geometry optimization convergence,
including step analysis, coordinate system recommendations, and recovery strategies.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
import math


class OptimizationAlgorithm(str, Enum):
    """Available optimization algorithms."""
    
    BFGS = "bfgs"
    RFO = "rfo"
    STEEP = "steepest_descent"
    CONJ_GRAD = "conjugate_gradient"
    NEWTON = "newton"
    LBFGS = "lbfgs"
    
    @property
    def description(self) -> str:
        """Get algorithm description."""
        descriptions = {
            self.BFGS: "Broyden-Fletcher-Goldfarb-Shanno quasi-Newton",
            self.RFO: "Rational Function Optimization",
            self.STEEP: "Steepest descent",
            self.CONJ_GRAD: "Conjugate gradient",
            self.NEWTON: "Full Newton-Raphson",
            self.LBFGS: "Limited-memory BFGS",
        }
        return descriptions.get(self, "Unknown algorithm")
    
    @property
    def requires_hessian(self) -> bool:
        """Whether algorithm requires Hessian."""
        return self in (self.NEWTON, self.RFO)


class CoordinateSystem(str, Enum):
    """Coordinate systems for optimization."""
    
    CARTESIAN = "cartesian"
    INTERNAL = "internal"
    REDUNDANT = "redundant"
    DELOCALIZED = "delocalized"
    NATURAL = "natural"
    
    @property
    def description(self) -> str:
        """Get coordinate system description."""
        descriptions = {
            self.CARTESIAN: "Cartesian coordinates (x, y, z)",
            self.INTERNAL: "Z-matrix internal coordinates",
            self.REDUNDANT: "Redundant internal coordinates",
            self.DELOCALIZED: "Delocalized internal coordinates",
            self.NATURAL: "Natural internal coordinates",
        }
        return descriptions.get(self, "Unknown coordinate system")


class OptimizationStatus(str, Enum):
    """Optimization convergence status."""
    
    CONVERGED = "converged"
    NOT_CONVERGED = "not_converged"
    STEP_TOO_SMALL = "step_too_small"
    STEP_TOO_LARGE = "step_too_large"
    OSCILLATING = "oscillating"
    UPHILL = "uphill"
    STUCK = "stuck"
    MAX_CYCLES = "max_cycles"


class ConvergenceCriterion(str, Enum):
    """Convergence criteria types."""
    
    GAU = "gau"
    GAU_LOOSE = "gau_loose"
    GAU_TIGHT = "gau_tight"
    GAU_VERYTIGHT = "gau_verytight"
    TURBOMOLE = "turbomole"
    CFOUR = "cfour"
    NWCHEM_LOOSE = "nwchem_loose"
    
    def get_thresholds(self) -> Dict[str, float]:
        """Get convergence thresholds for this criterion."""
        criteria = {
            self.GAU: {
                "max_force": 4.5e-4,
                "rms_force": 3.0e-4,
                "max_disp": 1.8e-3,
                "rms_disp": 1.2e-3,
            },
            self.GAU_LOOSE: {
                "max_force": 2.5e-3,
                "rms_force": 1.7e-3,
                "max_disp": 1.0e-2,
                "rms_disp": 6.7e-3,
            },
            self.GAU_TIGHT: {
                "max_force": 1.5e-5,
                "rms_force": 1.0e-5,
                "max_disp": 6.0e-5,
                "rms_disp": 4.0e-5,
            },
            self.GAU_VERYTIGHT: {
                "max_force": 2.0e-6,
                "rms_force": 1.0e-6,
                "max_disp": 6.0e-6,
                "rms_disp": 4.0e-6,
            },
            self.TURBOMOLE: {
                "max_force": 1.0e-3,
                "rms_force": 5.0e-4,
                "max_disp": 1.0e-3,
                "rms_disp": 5.0e-4,
                "energy_change": 1.0e-6,
            },
            self.CFOUR: {
                "max_force": 1.0e-4,
                "rms_force": None,
                "max_disp": None,
                "rms_disp": None,
            },
            self.NWCHEM_LOOSE: {
                "max_force": 4.5e-3,
                "rms_force": 3.0e-3,
                "max_disp": 5.4e-3,
                "rms_disp": 3.6e-3,
            },
        }
        return criteria.get(self, criteria[self.GAU])


@dataclass
class OptimizationStep:
    """Data for a single optimization step."""
    
    step_number: int
    energy: float
    max_force: float
    rms_force: float
    max_displacement: float
    rms_displacement: float
    step_size: float = 0.0
    trust_radius: float = 0.0
    energy_change: float = 0.0
    predicted_change: float = 0.0
    
    @property
    def ratio(self) -> Optional[float]:
        """Calculate actual/predicted energy change ratio."""
        if abs(self.predicted_change) < 1e-15:
            return None
        return self.energy_change / self.predicted_change


@dataclass
class OptimizationSettings:
    """Settings for geometry optimization."""
    
    algorithm: OptimizationAlgorithm = OptimizationAlgorithm.BFGS
    coordinate_system: CoordinateSystem = CoordinateSystem.REDUNDANT
    convergence: ConvergenceCriterion = ConvergenceCriterion.GAU
    max_iterations: int = 100
    initial_trust_radius: float = 0.3
    max_trust_radius: float = 1.0
    min_trust_radius: float = 0.001
    step_limit: float = 0.5
    
    # Hessian options
    initial_hessian: str = "simple"
    hessian_update: str = "bfgs"
    full_hessian_every: int = 0
    
    # Special options
    geom_maxiter: int = 100
    dynamic_level: int = 0
    ensure_bt_convergence: bool = True
    
    def to_psi4_options(self) -> Dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        return {
            "geom_maxiter": self.max_iterations,
            "g_convergence": self.convergence.value,
            "opt_coordinates": self.coordinate_system.value,
            "step_type": self.algorithm.value,
            "intrafrag_hess": self.initial_hessian,
            "hess_update": self.hessian_update,
            "full_hess_every": self.full_hessian_every,
            "dynamic_level": self.dynamic_level,
        }


@dataclass
class OptimizationAnalysis:
    """Analysis of optimization progress."""
    
    status: OptimizationStatus
    current_step: int
    total_steps: int
    energy_history: List[float] = field(default_factory=list)
    force_history: List[float] = field(default_factory=list)
    step_history: List[OptimizationStep] = field(default_factory=list)
    
    is_oscillating: bool = False
    oscillation_period: int = 0
    is_progressing: bool = True
    average_energy_change: float = 0.0
    estimated_steps_remaining: int = 0
    
    recommendations: List[str] = field(default_factory=list)
    
    @property
    def convergence_rate(self) -> float:
        """Estimate convergence rate from force history."""
        if len(self.force_history) < 2:
            return 0.0
        
        # Use log-linear fit to estimate rate
        recent = self.force_history[-10:] if len(self.force_history) >= 10 else self.force_history
        if recent[0] <= 0 or recent[-1] <= 0:
            return 0.0
        
        return (math.log(recent[-1]) - math.log(recent[0])) / len(recent)


class OptimizationConvergenceHelper:
    """Helper class for geometry optimization convergence."""
    
    def __init__(self, criterion: ConvergenceCriterion = ConvergenceCriterion.GAU):
        """Initialize with convergence criterion."""
        self.criterion = criterion
        self.thresholds = criterion.get_thresholds()
    
    def get_settings_for_system(
        self,
        n_atoms: int,
        has_weak_interactions: bool = False,
        is_transition_state: bool = False,
        is_flexible: bool = False,
        has_ring_systems: bool = False,
    ) -> OptimizationSettings:
        """
        Get recommended settings for a molecular system.
        
        Args:
            n_atoms: Number of atoms
            has_weak_interactions: Whether system has weak interactions
            is_transition_state: Whether searching for TS
            is_flexible: Whether system is conformationally flexible
            has_ring_systems: Whether system has rings
            
        Returns:
            Recommended optimization settings
        """
        settings = OptimizationSettings()
        
        # Large systems need more iterations
        if n_atoms > 100:
            settings.max_iterations = 200
            settings.algorithm = OptimizationAlgorithm.LBFGS
            settings.coordinate_system = CoordinateSystem.DELOCALIZED
        elif n_atoms > 50:
            settings.max_iterations = 150
            settings.coordinate_system = CoordinateSystem.DELOCALIZED
        
        # Weak interactions need tighter convergence
        if has_weak_interactions:
            settings.convergence = ConvergenceCriterion.GAU_TIGHT
            settings.step_limit = 0.3
        
        # Transition state search
        if is_transition_state:
            settings.algorithm = OptimizationAlgorithm.RFO
            settings.step_limit = 0.2
            settings.initial_hessian = "lindh"
            settings.full_hessian_every = 5
        
        # Flexible molecules need careful stepping
        if is_flexible:
            settings.initial_trust_radius = 0.2
            settings.step_limit = 0.3
            settings.dynamic_level = 1
        
        # Ring systems benefit from delocalized coords
        if has_ring_systems:
            settings.coordinate_system = CoordinateSystem.DELOCALIZED
        
        return settings
    
    def check_convergence(
        self,
        max_force: float,
        rms_force: float,
        max_displacement: float,
        rms_displacement: float,
        energy_change: Optional[float] = None,
    ) -> Tuple[bool, Dict[str, bool]]:
        """
        Check if optimization has converged.
        
        Returns:
            Tuple of (converged, individual_criteria_met)
        """
        criteria_met = {}
        
        # Check each criterion
        if "max_force" in self.thresholds and self.thresholds["max_force"]:
            criteria_met["max_force"] = max_force <= self.thresholds["max_force"]
        
        if "rms_force" in self.thresholds and self.thresholds["rms_force"]:
            criteria_met["rms_force"] = rms_force <= self.thresholds["rms_force"]
        
        if "max_disp" in self.thresholds and self.thresholds["max_disp"]:
            criteria_met["max_disp"] = max_displacement <= self.thresholds["max_disp"]
        
        if "rms_disp" in self.thresholds and self.thresholds["rms_disp"]:
            criteria_met["rms_disp"] = rms_displacement <= self.thresholds["rms_disp"]
        
        if energy_change is not None and "energy_change" in self.thresholds:
            if self.thresholds["energy_change"]:
                criteria_met["energy_change"] = abs(energy_change) <= self.thresholds["energy_change"]
        
        # All criteria must be met
        converged = all(criteria_met.values()) if criteria_met else False
        
        return converged, criteria_met
    
    def analyze_optimization(
        self,
        steps: List[OptimizationStep],
    ) -> OptimizationAnalysis:
        """
        Analyze optimization progress.
        
        Args:
            steps: List of optimization steps
            
        Returns:
            Analysis with status and recommendations
        """
        if not steps:
            return OptimizationAnalysis(
                status=OptimizationStatus.NOT_CONVERGED,
                current_step=0,
                total_steps=0,
                recommendations=["No optimization steps to analyze"],
            )
        
        current_step = steps[-1]
        energy_history = [s.energy for s in steps]
        force_history = [s.max_force for s in steps]
        
        analysis = OptimizationAnalysis(
            status=OptimizationStatus.NOT_CONVERGED,
            current_step=current_step.step_number,
            total_steps=len(steps),
            energy_history=energy_history,
            force_history=force_history,
            step_history=steps,
        )
        
        # Check convergence
        converged, _ = self.check_convergence(
            current_step.max_force,
            current_step.rms_force,
            current_step.max_displacement,
            current_step.rms_displacement,
            current_step.energy_change,
        )
        
        if converged:
            analysis.status = OptimizationStatus.CONVERGED
            return analysis
        
        # Detect oscillation
        analysis.is_oscillating, analysis.oscillation_period = self._detect_oscillation(energy_history)
        
        if analysis.is_oscillating:
            analysis.status = OptimizationStatus.OSCILLATING
            analysis.recommendations.append(
                f"Oscillation detected with period ~{analysis.oscillation_period}. "
                "Try reducing step size or trust radius."
            )
        
        # Check if going uphill
        if len(energy_history) >= 2 and energy_history[-1] > energy_history[-2]:
            if len(energy_history) >= 3 and energy_history[-2] > energy_history[-3]:
                analysis.status = OptimizationStatus.UPHILL
                analysis.recommendations.append(
                    "Energy increasing over multiple steps. Consider restarting "
                    "with a different initial guess or coordinate system."
                )
        
        # Check if stuck
        if len(energy_history) >= 5:
            recent_changes = [abs(energy_history[i] - energy_history[i-1]) 
                            for i in range(-4, 0)]
            if all(c < 1e-10 for c in recent_changes):
                analysis.status = OptimizationStatus.STUCK
                analysis.recommendations.append(
                    "Optimization appears stuck. Try using a different "
                    "coordinate system or optimization algorithm."
                )
        
        # Check step sizes
        if current_step.step_size < 1e-8:
            analysis.status = OptimizationStatus.STEP_TOO_SMALL
            analysis.recommendations.append(
                "Step size is very small. May need looser convergence criteria "
                "or different coordinate system."
            )
        
        # Estimate remaining steps
        if len(force_history) >= 3 and analysis.convergence_rate < 0:
            target_force = self.thresholds.get("max_force", 4.5e-4)
            if current_step.max_force > target_force:
                log_ratio = math.log(current_step.max_force / target_force)
                analysis.estimated_steps_remaining = int(log_ratio / abs(analysis.convergence_rate)) + 1
        
        # Calculate average energy change
        if len(energy_history) >= 2:
            changes = [abs(energy_history[i] - energy_history[i-1]) 
                      for i in range(1, len(energy_history))]
            analysis.average_energy_change = sum(changes) / len(changes)
        
        # Add general recommendations
        if not analysis.recommendations:
            analysis.is_progressing = analysis.convergence_rate < 0
            if analysis.is_progressing:
                analysis.recommendations.append(
                    f"Optimization progressing normally. Estimated "
                    f"{analysis.estimated_steps_remaining} steps remaining."
                )
            else:
                analysis.recommendations.append(
                    "Convergence rate is slow. Consider tighter SCF convergence "
                    "or a finer integration grid for DFT."
                )
        
        return analysis
    
    def _detect_oscillation(
        self,
        energy_history: List[float],
        min_period: int = 2,
        max_period: int = 10,
    ) -> Tuple[bool, int]:
        """
        Detect oscillation in energy history.
        
        Returns:
            Tuple of (is_oscillating, period)
        """
        if len(energy_history) < 2 * min_period:
            return False, 0
        
        # Check for sign changes in energy differences
        diffs = [energy_history[i] - energy_history[i-1] 
                for i in range(1, len(energy_history))]
        
        sign_changes = sum(1 for i in range(1, len(diffs)) 
                          if diffs[i] * diffs[i-1] < 0)
        
        # High frequency of sign changes indicates oscillation
        if len(diffs) >= 4 and sign_changes >= len(diffs) * 0.6:
            # Try to detect period
            for period in range(min_period, min(max_period, len(energy_history) // 2)):
                if self._check_periodic(energy_history, period):
                    return True, period
            return True, 2  # Default period if pattern unclear
        
        return False, 0
    
    def _check_periodic(
        self,
        values: List[float],
        period: int,
        tolerance: float = 0.1,
    ) -> bool:
        """Check if values show periodic pattern."""
        if len(values) < 2 * period:
            return False
        
        # Compare each value with value period steps earlier
        matches = 0
        comparisons = 0
        
        for i in range(period, len(values)):
            ref = values[i - period]
            if ref != 0:
                diff = abs(values[i] - ref) / abs(ref)
                if diff < tolerance:
                    matches += 1
            comparisons += 1
        
        return comparisons > 0 and matches / comparisons > 0.5
    
    def get_recovery_options(
        self,
        analysis: OptimizationAnalysis,
    ) -> List[Dict[str, Any]]:
        """
        Get recovery options for problematic optimization.
        
        Args:
            analysis: Current optimization analysis
            
        Returns:
            List of recovery option dictionaries
        """
        options = []
        
        if analysis.status == OptimizationStatus.OSCILLATING:
            options.append({
                "name": "reduce_trust_radius",
                "description": "Reduce trust radius to prevent large steps",
                "psi4_options": {
                    "intrafrag_trust": 0.1,
                    "intrafrag_trust_max": 0.3,
                },
            })
            options.append({
                "name": "use_damped_bfgs",
                "description": "Use damped BFGS update",
                "psi4_options": {
                    "hess_update": "bfgs",
                    "dynamic_level": 1,
                },
            })
        
        if analysis.status == OptimizationStatus.UPHILL:
            options.append({
                "name": "reset_hessian",
                "description": "Reset Hessian to initial guess",
                "psi4_options": {
                    "full_hess_every": 1,
                    "intrafrag_hess": "simple",
                },
            })
            options.append({
                "name": "steepest_descent",
                "description": "Use steepest descent for a few steps",
                "psi4_options": {
                    "step_type": "sd",
                    "consecutive_backsteps": 0,
                },
            })
        
        if analysis.status == OptimizationStatus.STUCK:
            options.append({
                "name": "change_coordinates",
                "description": "Try different coordinate system",
                "psi4_options": {
                    "opt_coordinates": "cartesian",
                },
            })
            options.append({
                "name": "perturb_geometry",
                "description": "Add small random displacement",
                "action": "perturb",
                "magnitude": 0.05,
            })
        
        if analysis.status == OptimizationStatus.STEP_TOO_SMALL:
            options.append({
                "name": "loosen_convergence",
                "description": "Use looser convergence criteria",
                "psi4_options": {
                    "g_convergence": "gau_loose",
                },
            })
        
        # Always add coordinate system options
        options.append({
            "name": "try_delocalized",
            "description": "Use delocalized internal coordinates",
            "psi4_options": {
                "opt_coordinates": "delocalized",
            },
        })
        
        return options


def get_optimization_settings(
    n_atoms: int,
    is_ts: bool = False,
    **kwargs,
) -> OptimizationSettings:
    """
    Convenience function to get optimization settings.
    
    Args:
        n_atoms: Number of atoms
        is_ts: Whether this is a transition state search
        **kwargs: Additional options
        
    Returns:
        Recommended optimization settings
    """
    helper = OptimizationConvergenceHelper()
    return helper.get_settings_for_system(
        n_atoms=n_atoms,
        is_transition_state=is_ts,
        **kwargs,
    )


def analyze_optimization_progress(
    steps: List[Dict[str, float]],
    criterion: str = "gau",
) -> OptimizationAnalysis:
    """
    Convenience function to analyze optimization progress.
    
    Args:
        steps: List of step dictionaries with energy, forces, etc.
        criterion: Convergence criterion name
        
    Returns:
        Optimization analysis
    """
    # Convert dictionaries to OptimizationStep objects
    opt_steps = []
    for i, step in enumerate(steps):
        opt_steps.append(OptimizationStep(
            step_number=i + 1,
            energy=step.get("energy", 0.0),
            max_force=step.get("max_force", 0.0),
            rms_force=step.get("rms_force", 0.0),
            max_displacement=step.get("max_disp", 0.0),
            rms_displacement=step.get("rms_disp", 0.0),
            step_size=step.get("step_size", 0.0),
            energy_change=step.get("energy_change", 0.0),
        ))
    
    helper = OptimizationConvergenceHelper(ConvergenceCriterion(criterion))
    return helper.analyze_optimization(opt_steps)
