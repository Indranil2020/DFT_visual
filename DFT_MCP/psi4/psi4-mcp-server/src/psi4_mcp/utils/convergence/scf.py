"""
SCF Convergence Utilities for Psi4 MCP Server.

Provides tools for diagnosing and improving SCF convergence issues.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class SCFAlgorithm(str, Enum):
    """SCF algorithms available in Psi4."""
    DIIS = "diis"  # Direct Inversion in the Iterative Subspace
    SOSCF = "soscf"  # Second-Order SCF
    DAMPING = "damping"  # Fock matrix damping
    MOM = "mom"  # Maximum Overlap Method
    LEVEL_SHIFT = "level_shift"  # Virtual orbital level shifting


class SCFConvergenceStatus(str, Enum):
    """SCF convergence status."""
    CONVERGED = "converged"
    NOT_CONVERGED = "not_converged"
    OSCILLATING = "oscillating"
    DIVERGING = "diverging"
    SLOW = "slow"


@dataclass
class SCFConvergenceSettings:
    """Settings for SCF convergence."""
    e_convergence: float = 1e-6
    d_convergence: float = 1e-6
    max_iterations: int = 100
    algorithm: SCFAlgorithm = SCFAlgorithm.DIIS
    diis_start: int = 1
    diis_max_vecs: int = 8
    damping_percentage: float = 0.0
    level_shift: float = 0.0
    soscf: bool = False
    soscf_start_convergence: float = 1e-3
    mom_start: int = 20
    stability_check: bool = False
    
    def to_psi4_options(self) -> Dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        options = {
            "e_convergence": self.e_convergence,
            "d_convergence": self.d_convergence,
            "maxiter": self.max_iterations,
            "diis": self.algorithm == SCFAlgorithm.DIIS,
            "diis_start": self.diis_start,
            "diis_max_vecs": self.diis_max_vecs,
        }
        
        if self.damping_percentage > 0:
            options["damping_percentage"] = self.damping_percentage
        
        if self.level_shift > 0:
            options["level_shift"] = self.level_shift
        
        if self.soscf or self.algorithm == SCFAlgorithm.SOSCF:
            options["soscf"] = True
            options["soscf_start_convergence"] = self.soscf_start_convergence
        
        if self.algorithm == SCFAlgorithm.MOM:
            options["mom_start"] = self.mom_start
        
        return options


@dataclass
class SCFConvergenceAnalysis:
    """Analysis of SCF convergence behavior."""
    status: SCFConvergenceStatus
    final_energy_change: Optional[float] = None
    final_density_change: Optional[float] = None
    iterations_used: int = 0
    energy_history: List[float] = field(default_factory=list)
    density_history: List[float] = field(default_factory=list)
    oscillation_detected: bool = False
    divergence_detected: bool = False
    recommendations: List[str] = field(default_factory=list)


class SCFConvergenceHelper:
    """
    Helper class for SCF convergence issues.
    
    Provides methods to analyze convergence behavior and
    suggest improvements.
    """
    
    def __init__(self):
        """Initialize the SCF convergence helper."""
        self._default_settings = SCFConvergenceSettings()
    
    def get_settings_for_system(
        self,
        n_electrons: int,
        n_basis: int = 0,
        is_open_shell: bool = False,
        has_heavy_atoms: bool = False,
        is_anion: bool = False,
        is_transition_metal: bool = False,
    ) -> SCFConvergenceSettings:
        """
        Get recommended SCF settings for a system type.
        
        Args:
            n_electrons: Number of electrons
            n_basis: Number of basis functions (0 to auto-estimate)
            is_open_shell: Whether system is open-shell
            has_heavy_atoms: Whether system has heavy atoms (Z > 36)
            is_anion: Whether system is an anion
            is_transition_metal: Whether system contains transition metals
            
        Returns:
            Recommended SCF settings
        """
        settings = SCFConvergenceSettings()
        
        # Base settings adjustments
        if n_electrons > 100:
            settings.max_iterations = 150
            settings.e_convergence = 1e-5
            settings.d_convergence = 1e-5
        
        # Open-shell systems often need help
        if is_open_shell:
            settings.soscf = True
            settings.soscf_start_convergence = 1e-2
        
        # Anions need diffuse functions and careful convergence
        if is_anion:
            settings.damping_percentage = 20.0
            settings.max_iterations = 150
        
        # Transition metals are notoriously difficult
        if is_transition_metal:
            settings.soscf = True
            settings.level_shift = 0.5
            settings.max_iterations = 200
            settings.e_convergence = 1e-5
        
        # Heavy atoms may need relativistic treatment
        if has_heavy_atoms:
            settings.max_iterations = 150
        
        return settings
    
    def analyze_convergence(
        self,
        energy_history: List[float],
        density_history: Optional[List[float]] = None,
        e_threshold: float = 1e-6,
        d_threshold: float = 1e-6,
    ) -> SCFConvergenceAnalysis:
        """
        Analyze SCF convergence from iteration history.
        
        Args:
            energy_history: List of energies per iteration
            density_history: List of density RMS changes per iteration
            e_threshold: Energy convergence threshold
            d_threshold: Density convergence threshold
            
        Returns:
            Analysis of convergence behavior
        """
        analysis = SCFConvergenceAnalysis(
            status=SCFConvergenceStatus.NOT_CONVERGED,
            energy_history=list(energy_history),
            density_history=list(density_history) if density_history else [],
            iterations_used=len(energy_history),
        )
        
        if len(energy_history) < 2:
            analysis.recommendations.append("Too few iterations to analyze")
            return analysis
        
        # Calculate energy changes
        energy_changes = [
            abs(energy_history[i] - energy_history[i-1])
            for i in range(1, len(energy_history))
        ]
        
        analysis.final_energy_change = energy_changes[-1] if energy_changes else None
        
        if density_history and len(density_history) >= 1:
            analysis.final_density_change = density_history[-1]
        
        # Check for convergence
        converged_e = analysis.final_energy_change is not None and analysis.final_energy_change < e_threshold
        converged_d = (density_history is None or 
                       (analysis.final_density_change is not None and 
                        analysis.final_density_change < d_threshold))
        
        if converged_e and converged_d:
            analysis.status = SCFConvergenceStatus.CONVERGED
            return analysis
        
        # Check for oscillation (energy alternating up/down)
        if len(energy_changes) >= 6:
            signs = [1 if energy_changes[i] > energy_changes[i-1] else -1 
                    for i in range(1, len(energy_changes))]
            sign_changes = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])
            if sign_changes >= len(signs) * 0.6:
                analysis.oscillation_detected = True
                analysis.status = SCFConvergenceStatus.OSCILLATING
                analysis.recommendations.append("Try damping (20-50%) to reduce oscillations")
                analysis.recommendations.append("Try SOSCF algorithm")
        
        # Check for divergence (energy increasing)
        if len(energy_changes) >= 3:
            recent_changes = energy_changes[-3:]
            if all(recent_changes[i] > recent_changes[i-1] for i in range(1, len(recent_changes))):
                analysis.divergence_detected = True
                analysis.status = SCFConvergenceStatus.DIVERGING
                analysis.recommendations.append("Try level shift (0.3-1.0)")
                analysis.recommendations.append("Check initial guess")
        
        # Check for slow convergence
        if len(energy_changes) >= 10:
            recent_avg = sum(energy_changes[-5:]) / 5
            early_avg = sum(energy_changes[:5]) / 5
            if recent_avg > early_avg * 0.8:
                analysis.status = SCFConvergenceStatus.SLOW
                analysis.recommendations.append("Try SOSCF for faster convergence")
                analysis.recommendations.append("Increase DIIS vector space")
        
        return analysis
    
    def get_recovery_options(
        self,
        analysis: SCFConvergenceAnalysis,
    ) -> List[SCFConvergenceSettings]:
        """
        Get options to try for recovery from convergence failure.
        
        Args:
            analysis: Convergence analysis
            
        Returns:
            List of settings to try
        """
        options = []
        
        if analysis.oscillation_detected:
            # Try damping
            damping_settings = SCFConvergenceSettings(
                damping_percentage=30.0,
                max_iterations=150,
            )
            options.append(damping_settings)
            
            # Try SOSCF
            soscf_settings = SCFConvergenceSettings(
                soscf=True,
                soscf_start_convergence=1e-2,
                max_iterations=150,
            )
            options.append(soscf_settings)
        
        if analysis.divergence_detected:
            # Try level shift
            shift_settings = SCFConvergenceSettings(
                level_shift=0.5,
                max_iterations=150,
            )
            options.append(shift_settings)
            
            # Try stronger damping
            strong_damp = SCFConvergenceSettings(
                damping_percentage=50.0,
                max_iterations=200,
            )
            options.append(strong_damp)
        
        if analysis.status == SCFConvergenceStatus.SLOW:
            # Try SOSCF
            soscf_settings = SCFConvergenceSettings(
                soscf=True,
                max_iterations=200,
            )
            options.append(soscf_settings)
        
        # Always add a combined approach as last resort
        combined = SCFConvergenceSettings(
            soscf=True,
            damping_percentage=20.0,
            level_shift=0.3,
            max_iterations=250,
            e_convergence=1e-5,
            d_convergence=1e-5,
        )
        options.append(combined)
        
        return options


def diagnose_scf_convergence(
    energy_history: List[float],
    density_history: Optional[List[float]] = None,
    e_threshold: float = 1e-6,
    d_threshold: float = 1e-6,
) -> SCFConvergenceAnalysis:
    """
    Diagnose SCF convergence issues.
    
    Convenience function wrapping SCFConvergenceHelper.
    
    Args:
        energy_history: List of energies per iteration
        density_history: List of density RMS changes
        e_threshold: Energy convergence threshold
        d_threshold: Density convergence threshold
        
    Returns:
        Convergence analysis
    """
    helper = SCFConvergenceHelper()
    return helper.analyze_convergence(
        energy_history, density_history, e_threshold, d_threshold
    )


def get_scf_recommendations(
    n_electrons: int,
    is_open_shell: bool = False,
    has_transition_metals: bool = False,
    is_anion: bool = False,
    previous_failure: bool = False,
) -> Dict[str, Any]:
    """
    Get SCF recommendations for a system.
    
    Args:
        n_electrons: Number of electrons
        is_open_shell: Whether open-shell
        has_transition_metals: Contains TM
        is_anion: Is an anion
        previous_failure: Had previous failure
        
    Returns:
        Dictionary of recommended Psi4 options
    """
    helper = SCFConvergenceHelper()
    settings = helper.get_settings_for_system(
        n_electrons=n_electrons,
        is_open_shell=is_open_shell,
        is_transition_metal=has_transition_metals,
        is_anion=is_anion,
    )
    
    if previous_failure:
        settings.soscf = True
        settings.damping_percentage = 20.0
        settings.max_iterations = 200
    
    return settings.to_psi4_options()
