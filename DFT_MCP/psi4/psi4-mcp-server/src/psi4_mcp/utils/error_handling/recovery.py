"""
Error Recovery for Psi4 MCP Server.

Provides automatic and assisted error recovery strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

from psi4_mcp.utils.error_handling.categorization import ErrorCategory, ErrorInfo


class RecoveryStatus(str, Enum):
    """Status of recovery attempt."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"
    NOT_RECOVERABLE = "not_recoverable"


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""
    status: RecoveryStatus
    strategy_used: str
    message: str
    modified_options: Dict[str, Any] = field(default_factory=dict)
    iterations_needed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_successful(self) -> bool:
        """Check if recovery was successful."""
        return self.status in (RecoveryStatus.SUCCESS, RecoveryStatus.PARTIAL)


class RecoveryStrategy(ABC):
    """
    Abstract base class for recovery strategies.
    
    Recovery strategies modify calculation parameters to
    overcome specific error types.
    """
    
    def __init__(
        self,
        name: str,
        applicable_categories: List[ErrorCategory],
        priority: int = 50,
    ):
        """
        Initialize recovery strategy.
        
        Args:
            name: Strategy name
            applicable_categories: Error categories this handles
            priority: Priority (lower = tried first)
        """
        self.name = name
        self.applicable_categories = applicable_categories
        self.priority = priority
    
    def is_applicable(self, error_info: ErrorInfo) -> bool:
        """Check if strategy applies to error."""
        return error_info.category in self.applicable_categories
    
    @abstractmethod
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Get modified options for recovery.
        
        Args:
            error_info: Error information
            current_options: Current calculation options
            
        Returns:
            Modified options dictionary
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description."""
        pass


class SCFDampingRecovery(RecoveryStrategy):
    """Recovery via SCF damping."""
    
    def __init__(self, damping_percentage: float = 30.0):
        super().__init__(
            name="SCF Damping",
            applicable_categories=[
                ErrorCategory.SCF_CONVERGENCE,
                ErrorCategory.CONVERGENCE,
            ],
            priority=20,
        )
        self.damping_percentage = damping_percentage
    
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply damping to options."""
        options = dict(current_options)
        options["damping_percentage"] = self.damping_percentage
        options["damping_convergence"] = 1e-4
        return options
    
    def get_description(self) -> str:
        return f"Apply {self.damping_percentage}% Fock matrix damping"


class SCFLevelShiftRecovery(RecoveryStrategy):
    """Recovery via level shifting."""
    
    def __init__(self, level_shift: float = 0.5):
        super().__init__(
            name="Level Shift",
            applicable_categories=[
                ErrorCategory.SCF_CONVERGENCE,
                ErrorCategory.CONVERGENCE,
            ],
            priority=30,
        )
        self.level_shift = level_shift
    
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Apply level shift to options."""
        options = dict(current_options)
        options["level_shift"] = self.level_shift
        options["level_shift_convergence"] = 1e-4
        return options
    
    def get_description(self) -> str:
        return f"Apply {self.level_shift} hartree level shift"


class SCFSOSCFRecovery(RecoveryStrategy):
    """Recovery via second-order SCF."""
    
    def __init__(self, start_convergence: float = 1e-2):
        super().__init__(
            name="SOSCF",
            applicable_categories=[
                ErrorCategory.SCF_CONVERGENCE,
                ErrorCategory.CONVERGENCE,
            ],
            priority=10,
        )
        self.start_convergence = start_convergence
    
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Enable SOSCF."""
        options = dict(current_options)
        options["soscf"] = True
        options["soscf_start_convergence"] = self.start_convergence
        return options
    
    def get_description(self) -> str:
        return f"Enable SOSCF at convergence {self.start_convergence}"


class MemoryReductionRecovery(RecoveryStrategy):
    """Recovery via memory reduction."""
    
    def __init__(self):
        super().__init__(
            name="Memory Reduction",
            applicable_categories=[ErrorCategory.MEMORY],
            priority=10,
        )
    
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Reduce memory usage."""
        options = dict(current_options)
        
        # Enable density fitting
        options["scf_type"] = "df"
        
        # Reduce DIIS vectors
        current_diis = options.get("diis_max_vecs", 8)
        options["diis_max_vecs"] = max(4, current_diis // 2)
        
        return options
    
    def get_description(self) -> str:
        return "Enable density fitting and reduce DIIS vectors"


class LinearDependencyRecovery(RecoveryStrategy):
    """Recovery for linear dependency issues."""
    
    def __init__(self, s_min: float = 1e-5):
        super().__init__(
            name="Linear Dependency Fix",
            applicable_categories=[ErrorCategory.LINEAR_DEPENDENCY],
            priority=10,
        )
        self.s_min = s_min
    
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Adjust linear dependency threshold."""
        options = dict(current_options)
        options["s_orthogonalization"] = "canonical"
        options["s_tolerance"] = self.s_min
        return options
    
    def get_description(self) -> str:
        return f"Adjust linear dependency threshold to {self.s_min}"


class OptimizationRecovery(RecoveryStrategy):
    """Recovery for geometry optimization."""
    
    def __init__(self):
        super().__init__(
            name="Optimization Recovery",
            applicable_categories=[ErrorCategory.GEOMETRY_CONVERGENCE],
            priority=20,
        )
    
    def get_modified_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Modify optimization parameters."""
        options = dict(current_options)
        
        # Reduce step size
        current_step = options.get("step_limit", 0.3)
        options["step_limit"] = current_step * 0.5
        
        # Increase iterations
        current_iter = options.get("geom_maxiter", 50)
        options["geom_maxiter"] = int(current_iter * 1.5)
        
        return options
    
    def get_description(self) -> str:
        return "Reduce step size and increase max iterations"


class RecoveryManager:
    """
    Manager for error recovery strategies.
    
    Coordinates multiple recovery strategies and tracks
    recovery attempts.
    """
    
    def __init__(self):
        """Initialize with default strategies."""
        self._strategies: List[RecoveryStrategy] = []
        self._setup_default_strategies()
        self._attempts: Dict[str, List[RecoveryResult]] = {}
    
    def _setup_default_strategies(self) -> None:
        """Set up default recovery strategies."""
        self._strategies.extend([
            SCFSOSCFRecovery(),
            SCFDampingRecovery(damping_percentage=20.0),
            SCFDampingRecovery(damping_percentage=40.0),
            SCFLevelShiftRecovery(level_shift=0.3),
            SCFLevelShiftRecovery(level_shift=0.6),
            MemoryReductionRecovery(),
            LinearDependencyRecovery(),
            OptimizationRecovery(),
        ])
        
        # Sort by priority
        self._strategies.sort(key=lambda s: s.priority)
    
    def add_strategy(self, strategy: RecoveryStrategy) -> None:
        """Add a custom recovery strategy."""
        self._strategies.append(strategy)
        self._strategies.sort(key=lambda s: s.priority)
    
    def get_applicable_strategies(
        self,
        error_info: ErrorInfo,
    ) -> List[RecoveryStrategy]:
        """
        Get strategies applicable to an error.
        
        Args:
            error_info: Error information
            
        Returns:
            List of applicable strategies
        """
        return [s for s in self._strategies if s.is_applicable(error_info)]
    
    def get_recovery_options(
        self,
        error_info: ErrorInfo,
        current_options: Dict[str, Any],
        max_strategies: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get list of recovery option sets to try.
        
        Args:
            error_info: Error information
            current_options: Current options
            max_strategies: Maximum strategies to return
            
        Returns:
            List of modified option dictionaries
        """
        strategies = self.get_applicable_strategies(error_info)[:max_strategies]
        return [
            s.get_modified_options(error_info, current_options)
            for s in strategies
        ]
    
    def record_attempt(
        self,
        calculation_id: str,
        result: RecoveryResult,
    ) -> None:
        """Record a recovery attempt."""
        if calculation_id not in self._attempts:
            self._attempts[calculation_id] = []
        self._attempts[calculation_id].append(result)
    
    def get_attempts(
        self,
        calculation_id: str,
    ) -> List[RecoveryResult]:
        """Get recovery attempts for a calculation."""
        return self._attempts.get(calculation_id, [])
    
    def clear_attempts(self, calculation_id: Optional[str] = None) -> None:
        """Clear recorded attempts."""
        if calculation_id:
            self._attempts.pop(calculation_id, None)
        else:
            self._attempts.clear()


# Global recovery manager
_recovery_manager: Optional[RecoveryManager] = None


def get_recovery_manager() -> RecoveryManager:
    """Get the global recovery manager."""
    global _recovery_manager
    if _recovery_manager is None:
        _recovery_manager = RecoveryManager()
    return _recovery_manager


def attempt_recovery(
    error_info: ErrorInfo,
    current_options: Dict[str, Any],
    calculation_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Attempt to get recovery options for an error.
    
    Args:
        error_info: Error information
        current_options: Current calculation options
        calculation_id: Optional calculation ID
        
    Returns:
        Modified options or None if not recoverable
    """
    if not error_info.recoverable:
        return None
    
    manager = get_recovery_manager()
    options_list = manager.get_recovery_options(error_info, current_options, max_strategies=1)
    
    if options_list:
        return options_list[0]
    
    return None


def get_recovery_strategies(
    error_info: ErrorInfo,
) -> List[str]:
    """
    Get descriptions of available recovery strategies.
    
    Args:
        error_info: Error information
        
    Returns:
        List of strategy descriptions
    """
    manager = get_recovery_manager()
    strategies = manager.get_applicable_strategies(error_info)
    return [s.get_description() for s in strategies]


def create_composite_recovery(
    strategies: List[RecoveryStrategy],
    current_options: Dict[str, Any],
    error_info: ErrorInfo,
) -> Dict[str, Any]:
    """
    Create composite recovery options from multiple strategies.
    
    Args:
        strategies: Strategies to combine
        current_options: Current options
        error_info: Error information
        
    Returns:
        Combined recovery options
    """
    options = dict(current_options)
    
    for strategy in strategies:
        if strategy.is_applicable(error_info):
            modified = strategy.get_modified_options(error_info, options)
            options.update(modified)
    
    return options
