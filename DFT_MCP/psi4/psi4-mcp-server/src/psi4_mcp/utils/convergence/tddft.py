"""
TDDFT Convergence Utilities for Psi4 MCP Server.

Provides tools for diagnosing and improving TDDFT convergence.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TDDFTAlgorithm(str, Enum):
    """TDDFT algorithms available in Psi4."""
    DAVIDSON = "davidson"
    RESIDUE = "residue"


class TDDFTConvergenceStatus(str, Enum):
    """TDDFT convergence status."""
    CONVERGED = "converged"
    NOT_CONVERGED = "not_converged"
    PARTIAL = "partial"
    ROOT_COLLAPSE = "root_collapse"
    SLOW = "slow"


@dataclass
class TDDFTConvergenceSettings:
    """Settings for TDDFT convergence."""
    r_convergence: float = 1e-5
    e_convergence: float = 1e-6
    max_iterations: int = 60
    n_guess: int = 0  # 0 = auto (2 * n_states)
    n_states: int = 5
    algorithm: TDDFTAlgorithm = TDDFTAlgorithm.DAVIDSON
    collapse_threshold: float = 1e-4
    orthogonalization: str = "gs"  # Gram-Schmidt
    
    def to_psi4_options(self) -> Dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        options = {
            "tdscf_r_convergence": self.r_convergence,
            "tdscf_e_convergence": self.e_convergence,
            "tdscf_maxiter": self.max_iterations,
            "tdscf_states": self.n_states,
        }
        
        if self.n_guess > 0:
            options["tdscf_nguess"] = self.n_guess
        
        return options


@dataclass
class TDDFTConvergenceAnalysis:
    """Analysis of TDDFT convergence behavior."""
    status: TDDFTConvergenceStatus
    states_converged: int = 0
    states_requested: int = 0
    iterations_used: int = 0
    residual_history: List[List[float]] = field(default_factory=list)
    root_collapse_detected: bool = False
    slow_roots: List[int] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class TDDFTConvergenceHelper:
    """
    Helper class for TDDFT convergence issues.
    
    Provides methods to analyze TDDFT convergence and
    suggest improvements.
    """
    
    def __init__(self):
        """Initialize the TDDFT convergence helper."""
        self._default_settings = TDDFTConvergenceSettings()
    
    def get_settings_for_system(
        self,
        n_states: int,
        n_electrons: int,
        homo_lumo_gap: Optional[float] = None,
        is_open_shell: bool = False,
        has_near_degeneracy: bool = False,
        use_tda: bool = False,
    ) -> TDDFTConvergenceSettings:
        """
        Get recommended TDDFT settings for a system type.
        
        Args:
            n_states: Number of excited states requested
            n_electrons: Number of electrons
            homo_lumo_gap: HOMO-LUMO gap in eV (None if unknown)
            is_open_shell: Whether system is open-shell
            has_near_degeneracy: Whether system has near-degenerate states
            use_tda: Whether using Tamm-Dancoff approximation
            
        Returns:
            Recommended TDDFT settings
        """
        settings = TDDFTConvergenceSettings(n_states=n_states)
        
        # More states need more guess vectors
        settings.n_guess = max(2 * n_states, n_states + 10)
        
        # Small gap systems are harder
        if homo_lumo_gap is not None and homo_lumo_gap < 2.0:
            settings.max_iterations = 100
            settings.r_convergence = 1e-4
            settings.n_guess = 3 * n_states
        
        # Open-shell systems need extra care
        if is_open_shell:
            settings.max_iterations = 80
            settings.n_guess = max(settings.n_guess, 2 * n_states + 5)
        
        # Near-degenerate states require tighter convergence
        if has_near_degeneracy:
            settings.r_convergence = 1e-6
            settings.collapse_threshold = 1e-5
            settings.n_guess = 3 * n_states
        
        # TDA is generally more stable
        if use_tda:
            settings.max_iterations = max(40, settings.max_iterations - 20)
        
        return settings
    
    def analyze_convergence(
        self,
        residual_history: List[List[float]],
        n_states: int,
        r_threshold: float = 1e-5,
    ) -> TDDFTConvergenceAnalysis:
        """
        Analyze TDDFT convergence from iteration history.
        
        Args:
            residual_history: List of residuals per state per iteration
                             Shape: [n_iterations][n_states]
            n_states: Number of states requested
            r_threshold: Residual convergence threshold
            
        Returns:
            Analysis of convergence behavior
        """
        analysis = TDDFTConvergenceAnalysis(
            status=TDDFTConvergenceStatus.NOT_CONVERGED,
            states_requested=n_states,
            residual_history=list(residual_history),
            iterations_used=len(residual_history),
        )
        
        if len(residual_history) < 1:
            analysis.recommendations.append("No iterations to analyze")
            return analysis
        
        # Get final residuals
        final_residuals = residual_history[-1] if residual_history else []
        
        if not final_residuals:
            return analysis
        
        # Count converged states
        converged_states = sum(1 for r in final_residuals if r < r_threshold)
        analysis.states_converged = converged_states
        
        # Check overall convergence
        if converged_states == n_states:
            analysis.status = TDDFTConvergenceStatus.CONVERGED
            return analysis
        elif converged_states > 0:
            analysis.status = TDDFTConvergenceStatus.PARTIAL
            analysis.recommendations.append(
                f"Only {converged_states}/{n_states} states converged"
            )
        
        # Check for root collapse (very similar residuals between roots)
        if len(final_residuals) >= 2:
            for i in range(len(final_residuals) - 1):
                diff = abs(final_residuals[i] - final_residuals[i + 1])
                if diff < 1e-8 and final_residuals[i] > r_threshold:
                    analysis.root_collapse_detected = True
                    analysis.status = TDDFTConvergenceStatus.ROOT_COLLAPSE
                    break
        
        if analysis.root_collapse_detected:
            analysis.recommendations.append("Root collapse detected")
            analysis.recommendations.append("Try increasing n_guess vectors")
            analysis.recommendations.append("Try tighter collapse_threshold")
        
        # Identify slow-converging roots
        if len(residual_history) >= 5:
            for state_idx in range(min(len(final_residuals), n_states)):
                state_residuals = [
                    residual_history[i][state_idx]
                    for i in range(len(residual_history))
                    if state_idx < len(residual_history[i])
                ]
                
                if len(state_residuals) >= 5:
                    # Check if convergence is slow
                    recent = state_residuals[-3:]
                    early = state_residuals[:3]
                    
                    if len(recent) == 3 and len(early) == 3:
                        recent_avg = sum(recent) / 3
                        early_avg = sum(early) / 3
                        
                        # Less than order of magnitude improvement
                        if recent_avg > early_avg * 0.5:
                            analysis.slow_roots.append(state_idx + 1)
        
        if analysis.slow_roots:
            analysis.status = TDDFTConvergenceStatus.SLOW
            analysis.recommendations.append(
                f"Roots {analysis.slow_roots} converging slowly"
            )
            analysis.recommendations.append("Try increasing max_iterations")
        
        return analysis
    
    def get_recovery_options(
        self,
        analysis: TDDFTConvergenceAnalysis,
        current_settings: TDDFTConvergenceSettings,
    ) -> List[TDDFTConvergenceSettings]:
        """
        Get options to try for recovery from convergence failure.
        
        Args:
            analysis: Convergence analysis
            current_settings: Current settings
            
        Returns:
            List of settings to try
        """
        options = []
        
        if analysis.root_collapse_detected:
            # Try more guess vectors
            more_guess = TDDFTConvergenceSettings(
                n_states=current_settings.n_states,
                n_guess=current_settings.n_guess * 2,
                max_iterations=current_settings.max_iterations + 20,
                r_convergence=current_settings.r_convergence,
            )
            options.append(more_guess)
            
            # Try tighter collapse threshold
            tighter = TDDFTConvergenceSettings(
                n_states=current_settings.n_states,
                n_guess=current_settings.n_guess + 10,
                collapse_threshold=current_settings.collapse_threshold / 10,
                max_iterations=current_settings.max_iterations,
            )
            options.append(tighter)
        
        if analysis.status == TDDFTConvergenceStatus.SLOW or analysis.slow_roots:
            # Try more iterations and looser threshold
            more_iter = TDDFTConvergenceSettings(
                n_states=current_settings.n_states,
                max_iterations=current_settings.max_iterations * 2,
                r_convergence=current_settings.r_convergence * 10,
                n_guess=current_settings.n_guess + 5,
            )
            options.append(more_iter)
        
        if analysis.status == TDDFTConvergenceStatus.PARTIAL:
            # Try more iterations with current threshold
            partial_fix = TDDFTConvergenceSettings(
                n_states=current_settings.n_states,
                max_iterations=current_settings.max_iterations + 40,
                n_guess=current_settings.n_guess + 10,
                r_convergence=current_settings.r_convergence,
            )
            options.append(partial_fix)
        
        # Always add a conservative last-resort option
        conservative = TDDFTConvergenceSettings(
            n_states=current_settings.n_states,
            n_guess=3 * current_settings.n_states + 10,
            max_iterations=150,
            r_convergence=1e-4,
            collapse_threshold=1e-6,
        )
        options.append(conservative)
        
        return options


def diagnose_tddft_convergence(
    residual_history: List[List[float]],
    n_states: int,
    r_threshold: float = 1e-5,
) -> TDDFTConvergenceAnalysis:
    """
    Diagnose TDDFT convergence issues.
    
    Convenience function wrapping TDDFTConvergenceHelper.
    
    Args:
        residual_history: Residuals per state per iteration
        n_states: Number of states requested
        r_threshold: Residual threshold
        
    Returns:
        Convergence analysis
    """
    helper = TDDFTConvergenceHelper()
    return helper.analyze_convergence(residual_history, n_states, r_threshold)


def get_tddft_recommendations(
    n_states: int,
    n_electrons: int,
    homo_lumo_gap: Optional[float] = None,
    is_open_shell: bool = False,
    use_tda: bool = False,
    previous_failure: bool = False,
) -> Dict[str, Any]:
    """
    Get TDDFT recommendations for a system.
    
    Args:
        n_states: Number of excited states
        n_electrons: Number of electrons
        homo_lumo_gap: HOMO-LUMO gap in eV
        is_open_shell: Whether open-shell
        use_tda: Use TDA
        previous_failure: Had previous failure
        
    Returns:
        Dictionary of recommended Psi4 options
    """
    helper = TDDFTConvergenceHelper()
    settings = helper.get_settings_for_system(
        n_states=n_states,
        n_electrons=n_electrons,
        homo_lumo_gap=homo_lumo_gap,
        is_open_shell=is_open_shell,
        use_tda=use_tda,
    )
    
    if previous_failure:
        settings.n_guess = max(settings.n_guess, 3 * n_states)
        settings.max_iterations = max(settings.max_iterations, 100)
        settings.r_convergence = max(settings.r_convergence, 1e-4)
    
    return settings.to_psi4_options()


def estimate_tddft_cost(
    n_states: int,
    n_basis: int,
    n_occupied: int,
    n_virtual: int,
    use_tda: bool = False,
) -> Dict[str, Any]:
    """
    Estimate computational cost of TDDFT calculation.
    
    Args:
        n_states: Number of excited states
        n_basis: Number of basis functions
        n_occupied: Number of occupied orbitals
        n_virtual: Number of virtual orbitals
        use_tda: Whether using TDA
        
    Returns:
        Dictionary with cost estimates
    """
    # Response dimension
    if use_tda:
        response_dim = n_occupied * n_virtual
    else:
        response_dim = 2 * n_occupied * n_virtual
    
    # Memory for response vectors
    vector_memory_mb = (response_dim * n_states * 8) / (1024 * 1024)
    
    # Memory for integrals (rough estimate)
    integral_memory_mb = (n_basis ** 4 * 8) / (1024 * 1024) / 8  # Assume 8-fold screening
    
    # Estimated iterations
    est_iterations = 20 if use_tda else 30
    
    # Scaling factor
    scaling = "O(N^4)" if use_tda else "O(N^5)"
    
    return {
        "response_dimension": response_dim,
        "vector_memory_mb": vector_memory_mb,
        "integral_memory_mb": integral_memory_mb,
        "estimated_iterations": est_iterations,
        "scaling": scaling,
        "recommended_nguess": min(2 * n_states + 5, response_dim),
        "use_tda_recommendation": response_dim > 10000,
    }
