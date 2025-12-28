"""
Convergence Strategies for Psi4 MCP Server.

Provides pluggable convergence strategies that can be applied
to various iterative calculations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable


class ConvergenceStrategyType(str, Enum):
    """Types of convergence strategies."""
    DAMPING = "damping"
    LEVEL_SHIFT = "level_shift"
    SOSCF = "soscf"
    MOM = "mom"
    DIIS = "diis"
    TRUST_REGION = "trust_region"
    LINE_SEARCH = "line_search"
    COMPOSITE = "composite"


@dataclass
class StrategyResult:
    """Result of applying a convergence strategy."""
    success: bool
    options_applied: Dict[str, Any]
    message: str
    iterations_used: int = 0
    final_error: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConvergenceStrategy(ABC):
    """
    Abstract base class for convergence strategies.
    
    Convergence strategies modify calculation parameters to
    improve convergence behavior.
    """
    
    def __init__(self, name: str, strategy_type: ConvergenceStrategyType):
        """
        Initialize convergence strategy.
        
        Args:
            name: Strategy name
            strategy_type: Type of strategy
        """
        self.name = name
        self.strategy_type = strategy_type
        self._applied = False
    
    @abstractmethod
    def get_options(self) -> Dict[str, Any]:
        """
        Get Psi4 options for this strategy.
        
        Returns:
            Dictionary of Psi4 options
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of strategy.
        
        Returns:
            Description string
        """
        pass
    
    def apply(self) -> StrategyResult:
        """
        Apply the strategy and return result.
        
        Returns:
            StrategyResult with options to apply
        """
        self._applied = True
        return StrategyResult(
            success=True,
            options_applied=self.get_options(),
            message=f"Applied strategy: {self.name}",
        )
    
    @property
    def is_applied(self) -> bool:
        """Check if strategy has been applied."""
        return self._applied
    
    def reset(self) -> None:
        """Reset the strategy state."""
        self._applied = False


class DampingStrategy(ConvergenceStrategy):
    """
    Fock matrix damping strategy.
    
    Reduces oscillations by mixing old and new Fock matrices.
    """
    
    def __init__(
        self,
        damping_percentage: float = 20.0,
        damping_convergence: float = 1e-4,
    ):
        """
        Initialize damping strategy.
        
        Args:
            damping_percentage: Percentage of old Fock matrix to mix (0-100)
            damping_convergence: Convergence at which to turn off damping
        """
        super().__init__("Fock Damping", ConvergenceStrategyType.DAMPING)
        self.damping_percentage = max(0.0, min(100.0, damping_percentage))
        self.damping_convergence = damping_convergence
    
    def get_options(self) -> Dict[str, Any]:
        """Get Psi4 damping options."""
        return {
            "damping_percentage": self.damping_percentage,
            "damping_convergence": self.damping_convergence,
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return (
            f"Apply {self.damping_percentage}% Fock matrix damping "
            f"until convergence reaches {self.damping_convergence}"
        )


class LevelShiftStrategy(ConvergenceStrategy):
    """
    Virtual orbital level shifting strategy.
    
    Increases HOMO-LUMO gap to stabilize SCF.
    """
    
    def __init__(
        self,
        level_shift: float = 0.5,
        level_shift_convergence: float = 1e-4,
    ):
        """
        Initialize level shift strategy.
        
        Args:
            level_shift: Amount to shift virtual orbitals (hartree)
            level_shift_convergence: Convergence at which to turn off shift
        """
        super().__init__("Level Shift", ConvergenceStrategyType.LEVEL_SHIFT)
        self.level_shift = max(0.0, level_shift)
        self.level_shift_convergence = level_shift_convergence
    
    def get_options(self) -> Dict[str, Any]:
        """Get Psi4 level shift options."""
        return {
            "level_shift": self.level_shift,
            "level_shift_convergence": self.level_shift_convergence,
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return (
            f"Shift virtual orbitals by {self.level_shift} hartree "
            f"until convergence reaches {self.level_shift_convergence}"
        )


class SOSCFStrategy(ConvergenceStrategy):
    """
    Second-Order SCF strategy.
    
    Uses second-order optimization for faster convergence.
    """
    
    def __init__(
        self,
        soscf_start_convergence: float = 1e-3,
        soscf_min_iter: int = 1,
        soscf_max_iter: int = 5,
        soscf_conv: float = 1e-5,
    ):
        """
        Initialize SOSCF strategy.
        
        Args:
            soscf_start_convergence: DIIS error at which to start SOSCF
            soscf_min_iter: Minimum SOSCF micro-iterations
            soscf_max_iter: Maximum SOSCF micro-iterations
            soscf_conv: SOSCF micro-iteration convergence
        """
        super().__init__("Second-Order SCF", ConvergenceStrategyType.SOSCF)
        self.soscf_start_convergence = soscf_start_convergence
        self.soscf_min_iter = soscf_min_iter
        self.soscf_max_iter = soscf_max_iter
        self.soscf_conv = soscf_conv
    
    def get_options(self) -> Dict[str, Any]:
        """Get Psi4 SOSCF options."""
        return {
            "soscf": True,
            "soscf_start_convergence": self.soscf_start_convergence,
            "soscf_min_iter": self.soscf_min_iter,
            "soscf_max_iter": self.soscf_max_iter,
            "soscf_conv": self.soscf_conv,
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return (
            f"Enable SOSCF starting at DIIS error {self.soscf_start_convergence} "
            f"with {self.soscf_min_iter}-{self.soscf_max_iter} micro-iterations"
        )


class MOMStrategy(ConvergenceStrategy):
    """
    Maximum Overlap Method strategy.
    
    Maintains orbital character to prevent variational collapse.
    """
    
    def __init__(
        self,
        mom_start: int = 20,
        mom_occ_type: str = "a",
    ):
        """
        Initialize MOM strategy.
        
        Args:
            mom_start: Iteration at which to start MOM
            mom_occ_type: Occupation type ('a' for alpha, 'b' for beta)
        """
        super().__init__("Maximum Overlap Method", ConvergenceStrategyType.MOM)
        self.mom_start = max(1, mom_start)
        self.mom_occ_type = mom_occ_type
    
    def get_options(self) -> Dict[str, Any]:
        """Get Psi4 MOM options."""
        return {
            "mom_start": self.mom_start,
            "mom_occ": True,
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return f"Enable MOM starting at iteration {self.mom_start}"


class DIISStrategy(ConvergenceStrategy):
    """
    DIIS (Direct Inversion in the Iterative Subspace) strategy.
    
    Standard extrapolation method for SCF convergence.
    """
    
    def __init__(
        self,
        diis_start: int = 1,
        diis_max_vecs: int = 8,
        diis_rms_error: bool = True,
    ):
        """
        Initialize DIIS strategy.
        
        Args:
            diis_start: Iteration at which to start DIIS
            diis_max_vecs: Maximum number of error vectors to store
            diis_rms_error: Use RMS error (vs max error)
        """
        super().__init__("DIIS", ConvergenceStrategyType.DIIS)
        self.diis_start = max(1, diis_start)
        self.diis_max_vecs = max(2, diis_max_vecs)
        self.diis_rms_error = diis_rms_error
    
    def get_options(self) -> Dict[str, Any]:
        """Get Psi4 DIIS options."""
        return {
            "diis": True,
            "diis_start": self.diis_start,
            "diis_max_vecs": self.diis_max_vecs,
            "diis_rms_error": self.diis_rms_error,
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return (
            f"Enable DIIS starting at iteration {self.diis_start} "
            f"with {self.diis_max_vecs} error vectors"
        )


class TrustRegionStrategy(ConvergenceStrategy):
    """
    Trust region strategy for geometry optimization.
    
    Limits step size based on model quality.
    """
    
    def __init__(
        self,
        initial_trust_radius: float = 0.3,
        min_trust_radius: float = 1e-3,
        max_trust_radius: float = 1.0,
    ):
        """
        Initialize trust region strategy.
        
        Args:
            initial_trust_radius: Initial trust radius
            min_trust_radius: Minimum trust radius
            max_trust_radius: Maximum trust radius
        """
        super().__init__("Trust Region", ConvergenceStrategyType.TRUST_REGION)
        self.initial_trust_radius = initial_trust_radius
        self.min_trust_radius = min_trust_radius
        self.max_trust_radius = max_trust_radius
    
    def get_options(self) -> Dict[str, Any]:
        """Get optimization trust region options."""
        return {
            "intrafrag_trust": self.initial_trust_radius,
            "intrafrag_trust_min": self.min_trust_radius,
            "intrafrag_trust_max": self.max_trust_radius,
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return (
            f"Use trust region with initial radius {self.initial_trust_radius} "
            f"(range: {self.min_trust_radius}-{self.max_trust_radius})"
        )


class LineSearchStrategy(ConvergenceStrategy):
    """
    Line search strategy for optimization.
    
    Ensures steps decrease energy along search direction.
    """
    
    def __init__(
        self,
        line_search_type: str = "backtrack",
        alpha_init: float = 1.0,
        alpha_min: float = 1e-8,
        c1: float = 1e-4,
    ):
        """
        Initialize line search strategy.
        
        Args:
            line_search_type: Type of line search
            alpha_init: Initial step length
            alpha_min: Minimum step length
            c1: Armijo condition parameter
        """
        super().__init__("Line Search", ConvergenceStrategyType.LINE_SEARCH)
        self.line_search_type = line_search_type
        self.alpha_init = alpha_init
        self.alpha_min = alpha_min
        self.c1 = c1
    
    def get_options(self) -> Dict[str, Any]:
        """Get line search options."""
        return {
            "geom_maxiter": 100,
            "step_type": "rfo" if self.line_search_type == "backtrack" else "nr",
        }
    
    def get_description(self) -> str:
        """Get strategy description."""
        return f"Use {self.line_search_type} line search with initial alpha={self.alpha_init}"


class CompositeStrategy(ConvergenceStrategy):
    """
    Composite strategy combining multiple strategies.
    
    Applies multiple convergence aids together.
    """
    
    def __init__(
        self,
        strategies: List[ConvergenceStrategy],
        name: str = "Composite",
    ):
        """
        Initialize composite strategy.
        
        Args:
            strategies: List of strategies to combine
            name: Name for the composite
        """
        super().__init__(name, ConvergenceStrategyType.COMPOSITE)
        self.strategies = strategies
    
    def get_options(self) -> Dict[str, Any]:
        """Get combined options from all strategies."""
        combined = {}
        for strategy in self.strategies:
            combined.update(strategy.get_options())
        return combined
    
    def get_description(self) -> str:
        """Get composite description."""
        descriptions = [s.get_description() for s in self.strategies]
        return "Combined: " + "; ".join(descriptions)
    
    def apply(self) -> StrategyResult:
        """Apply all strategies."""
        results = []
        for strategy in self.strategies:
            results.append(strategy.apply())
        
        self._applied = True
        return StrategyResult(
            success=all(r.success for r in results),
            options_applied=self.get_options(),
            message=f"Applied composite strategy with {len(self.strategies)} components",
        )


def apply_convergence_strategy(
    strategy: ConvergenceStrategy,
    current_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Apply a convergence strategy to options.
    
    Args:
        strategy: Strategy to apply
        current_options: Current options dictionary
        
    Returns:
        Updated options dictionary
    """
    options = dict(current_options) if current_options else {}
    result = strategy.apply()
    
    if result.success:
        options.update(result.options_applied)
    
    return options


def get_strategy_sequence(
    problem_type: str,
    severity: str = "moderate",
) -> List[ConvergenceStrategy]:
    """
    Get a sequence of strategies to try for a problem type.
    
    Args:
        problem_type: Type of problem ('oscillation', 'divergence', 'slow')
        severity: Severity level ('mild', 'moderate', 'severe')
        
    Returns:
        List of strategies to try in order
    """
    strategies: List[ConvergenceStrategy] = []
    
    if problem_type == "oscillation":
        # Oscillations benefit from damping
        if severity == "mild":
            strategies.append(DampingStrategy(damping_percentage=15.0))
        elif severity == "moderate":
            strategies.append(DampingStrategy(damping_percentage=30.0))
            strategies.append(SOSCFStrategy())
        else:  # severe
            strategies.append(DampingStrategy(damping_percentage=50.0))
            strategies.append(SOSCFStrategy(soscf_start_convergence=1e-2))
            strategies.append(LevelShiftStrategy(level_shift=0.3))
    
    elif problem_type == "divergence":
        # Divergence needs stabilization
        if severity == "mild":
            strategies.append(LevelShiftStrategy(level_shift=0.3))
        elif severity == "moderate":
            strategies.append(LevelShiftStrategy(level_shift=0.5))
            strategies.append(DampingStrategy(damping_percentage=30.0))
        else:  # severe
            strategies.append(LevelShiftStrategy(level_shift=1.0))
            strategies.append(DampingStrategy(damping_percentage=50.0))
            strategies.append(SOSCFStrategy())
    
    elif problem_type == "slow":
        # Slow convergence benefits from SOSCF
        if severity == "mild":
            strategies.append(SOSCFStrategy())
        elif severity == "moderate":
            strategies.append(SOSCFStrategy())
            strategies.append(DIISStrategy(diis_max_vecs=10))
        else:  # severe
            strategies.append(SOSCFStrategy(soscf_start_convergence=1e-2))
            strategies.append(DIISStrategy(diis_max_vecs=12))
    
    else:
        # Default sequence
        strategies.append(SOSCFStrategy())
        strategies.append(DampingStrategy(damping_percentage=20.0))
        strategies.append(LevelShiftStrategy(level_shift=0.5))
    
    return strategies


def create_aggressive_strategy() -> CompositeStrategy:
    """
    Create an aggressive composite strategy for difficult cases.
    
    Returns:
        CompositeStrategy with multiple convergence aids
    """
    return CompositeStrategy(
        strategies=[
            SOSCFStrategy(soscf_start_convergence=1e-2),
            DampingStrategy(damping_percentage=30.0),
            LevelShiftStrategy(level_shift=0.5),
        ],
        name="Aggressive Convergence",
    )


def create_conservative_strategy() -> CompositeStrategy:
    """
    Create a conservative composite strategy for routine cases.
    
    Returns:
        CompositeStrategy with mild convergence aids
    """
    return CompositeStrategy(
        strategies=[
            DIISStrategy(diis_max_vecs=8),
            DampingStrategy(damping_percentage=10.0, damping_convergence=1e-3),
        ],
        name="Conservative Convergence",
    )
