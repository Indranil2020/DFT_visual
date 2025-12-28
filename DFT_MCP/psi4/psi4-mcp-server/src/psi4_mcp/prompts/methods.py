"""
Method Selection Prompts for Psi4 MCP Server.

Provides prompt templates and guidance for computational method selection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class CalculationGoal(str, Enum):
    """Types of calculation goals."""
    ENERGY = "energy"
    GEOMETRY = "geometry"
    THERMOCHEMISTRY = "thermochemistry"
    SPECTRA = "spectra"
    INTERACTION = "interaction"
    REACTION = "reaction"
    BARRIER = "barrier"
    PROPERTY = "property"


class AccuracyLevel(str, Enum):
    """Accuracy requirements."""
    QUICK = "quick"
    STANDARD = "standard"
    HIGH = "high"
    BENCHMARK = "benchmark"


class SystemSize(str, Enum):
    """System size categories."""
    SMALL = "small"      # < 10 atoms
    MEDIUM = "medium"    # 10-50 atoms
    LARGE = "large"      # 50-200 atoms
    VERY_LARGE = "very_large"  # > 200 atoms


@dataclass
class MethodRecommendation:
    """A recommended method/basis combination."""
    method: str
    basis: str
    description: str
    accuracy: str
    computational_cost: str
    suitable_for: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class MethodSelectionPrompt:
    """Prompt for method selection."""
    goal: CalculationGoal
    accuracy: AccuracyLevel
    system_size: SystemSize
    recommendations: List[MethodRecommendation] = field(default_factory=list)
    general_guidance: str = ""
    warnings: List[str] = field(default_factory=list)


class MethodSelector:
    """Provides method selection guidance."""
    
    def __init__(self):
        self._method_database = self._build_method_database()
    
    def _build_method_database(self) -> Dict[str, Dict[str, Any]]:
        """Build database of method information."""
        return {
            "hf": {
                "name": "Hartree-Fock",
                "scaling": "N^4",
                "accuracy": "baseline",
                "description": "Mean-field approximation, no electron correlation",
                "suitable_for": ["quick estimates", "large systems", "initial orbitals"],
            },
            "b3lyp": {
                "name": "B3LYP",
                "scaling": "N^3-N^4",
                "accuracy": "good",
                "description": "Hybrid DFT functional, widely used",
                "suitable_for": ["geometries", "frequencies", "general chemistry"],
            },
            "wb97x-d": {
                "name": "ωB97X-D",
                "scaling": "N^3-N^4",
                "accuracy": "very good",
                "description": "Range-separated hybrid with dispersion",
                "suitable_for": ["noncovalent interactions", "thermochemistry"],
            },
            "mp2": {
                "name": "MP2",
                "scaling": "N^5",
                "accuracy": "good",
                "description": "Second-order perturbation theory",
                "suitable_for": ["correlation energies", "medium-sized systems"],
            },
            "ccsd": {
                "name": "CCSD",
                "scaling": "N^6",
                "accuracy": "high",
                "description": "Coupled cluster singles and doubles",
                "suitable_for": ["accurate energies", "small-medium systems"],
            },
            "ccsd(t)": {
                "name": "CCSD(T)",
                "scaling": "N^7",
                "accuracy": "benchmark",
                "description": "Gold standard of quantum chemistry",
                "suitable_for": ["benchmark calculations", "small systems"],
            },
        }
    
    def get_recommendations(
        self,
        goal: CalculationGoal,
        accuracy: AccuracyLevel,
        system_size: SystemSize,
        additional_requirements: Optional[List[str]] = None,
    ) -> MethodSelectionPrompt:
        """Get method recommendations based on requirements."""
        recommendations = []
        warnings = []
        
        # Energy calculations
        if goal == CalculationGoal.ENERGY:
            if accuracy == AccuracyLevel.QUICK:
                recommendations.append(MethodRecommendation(
                    method="hf",
                    basis="sto-3g" if system_size == SystemSize.VERY_LARGE else "6-31g",
                    description="Fast energy estimate",
                    accuracy="Low - baseline only",
                    computational_cost="Very fast",
                ))
            
            if accuracy in (AccuracyLevel.STANDARD, AccuracyLevel.QUICK):
                basis = "6-31g*" if system_size in (SystemSize.LARGE, SystemSize.VERY_LARGE) else "cc-pvdz"
                recommendations.append(MethodRecommendation(
                    method="b3lyp",
                    basis=basis,
                    description="Standard DFT calculation",
                    accuracy="Good for most applications",
                    computational_cost="Moderate",
                    suitable_for=["general chemistry", "organic molecules"],
                ))
            
            if accuracy == AccuracyLevel.HIGH and system_size in (SystemSize.SMALL, SystemSize.MEDIUM):
                recommendations.append(MethodRecommendation(
                    method="mp2",
                    basis="cc-pvtz",
                    description="Correlated wavefunction method",
                    accuracy="Good correlation treatment",
                    computational_cost="Expensive for large systems",
                ))
            
            if accuracy == AccuracyLevel.BENCHMARK and system_size == SystemSize.SMALL:
                recommendations.append(MethodRecommendation(
                    method="ccsd(t)",
                    basis="cc-pvtz",
                    description="Gold standard benchmark calculation",
                    accuracy="Benchmark quality",
                    computational_cost="Very expensive",
                    notes=["Consider CBS extrapolation for highest accuracy"],
                ))
        
        # Geometry optimization
        elif goal == CalculationGoal.GEOMETRY:
            recommendations.append(MethodRecommendation(
                method="b3lyp",
                basis="6-31g*" if system_size != SystemSize.SMALL else "cc-pvdz",
                description="Standard geometry optimization",
                accuracy="Good bond lengths and angles",
                computational_cost="Moderate",
            ))
            
            if accuracy == AccuracyLevel.HIGH:
                recommendations.append(MethodRecommendation(
                    method="wb97x-d",
                    basis="def2-tzvp",
                    description="High-accuracy geometry",
                    accuracy="Very good for most systems",
                    computational_cost="Moderate-expensive",
                ))
        
        # Thermochemistry
        elif goal == CalculationGoal.THERMOCHEMISTRY:
            recommendations.append(MethodRecommendation(
                method="b3lyp",
                basis="6-311+g(2d,p)",
                description="Standard thermochemistry",
                accuracy="~2-3 kcal/mol MAE",
                computational_cost="Moderate",
                notes=["Include thermal corrections from frequencies"],
            ))
            
            if accuracy == AccuracyLevel.HIGH:
                recommendations.append(MethodRecommendation(
                    method="wb97x-d",
                    basis="def2-tzvpp",
                    description="High-accuracy thermochemistry",
                    accuracy="~1-2 kcal/mol MAE",
                    computational_cost="Expensive",
                ))
        
        # Spectroscopy
        elif goal == CalculationGoal.SPECTRA:
            recommendations.append(MethodRecommendation(
                method="b3lyp",
                basis="6-31+g*",
                description="Standard UV-Vis/IR spectra",
                accuracy="Qualitative to semi-quantitative",
                computational_cost="Moderate",
            ))
            
            recommendations.append(MethodRecommendation(
                method="cam-b3lyp",
                basis="aug-cc-pvdz",
                description="Better for charge-transfer states",
                accuracy="Good for Rydberg and CT states",
                computational_cost="Moderate",
            ))
        
        # Noncovalent interactions
        elif goal == CalculationGoal.INTERACTION:
            recommendations.append(MethodRecommendation(
                method="sapt0",
                basis="jun-cc-pvdz",
                description="SAPT interaction energy decomposition",
                accuracy="Good for understanding interaction types",
                computational_cost="Moderate",
            ))
            
            recommendations.append(MethodRecommendation(
                method="wb97x-d",
                basis="def2-tzvp",
                description="DFT with dispersion",
                accuracy="Good for interaction energies",
                computational_cost="Moderate",
            ))
        
        # Add warnings based on system size
        if system_size == SystemSize.VERY_LARGE:
            warnings.append("Very large system - consider QM/MM or fragmentation approaches")
        
        if accuracy == AccuracyLevel.BENCHMARK and system_size != SystemSize.SMALL:
            warnings.append("Benchmark accuracy difficult for systems > 10 atoms")
        
        # Generate general guidance
        guidance = self._generate_guidance(goal, accuracy, system_size)
        
        return MethodSelectionPrompt(
            goal=goal,
            accuracy=accuracy,
            system_size=system_size,
            recommendations=recommendations,
            general_guidance=guidance,
            warnings=warnings,
        )
    
    def _generate_guidance(
        self,
        goal: CalculationGoal,
        accuracy: AccuracyLevel,
        system_size: SystemSize,
    ) -> str:
        """Generate general guidance text."""
        parts = []
        
        parts.append(f"For {goal.value} calculations with {accuracy.value} accuracy:")
        
        if system_size == SystemSize.SMALL:
            parts.append("Small systems allow high-level methods like CCSD(T).")
        elif system_size == SystemSize.MEDIUM:
            parts.append("Medium systems work well with DFT or MP2.")
        elif system_size == SystemSize.LARGE:
            parts.append("Large systems typically require DFT with efficient basis sets.")
        else:
            parts.append("Very large systems may need linear-scaling methods or fragmentation.")
        
        if goal == CalculationGoal.GEOMETRY:
            parts.append("Optimize geometry before running frequency calculations.")
        elif goal == CalculationGoal.THERMOCHEMISTRY:
            parts.append("Include zero-point energy and thermal corrections.")
        elif goal == CalculationGoal.SPECTRA:
            parts.append("Consider solvent effects for solution-phase spectra.")
        
        return " ".join(parts)


# Global selector instance
_method_selector: Optional[MethodSelector] = None


def get_method_selector() -> MethodSelector:
    """Get the global method selector."""
    global _method_selector
    if _method_selector is None:
        _method_selector = MethodSelector()
    return _method_selector


def recommend_method(
    goal: str,
    accuracy: str = "standard",
    n_atoms: int = 10,
) -> MethodSelectionPrompt:
    """Get method recommendation."""
    selector = get_method_selector()
    
    # Convert strings to enums
    goal_enum = CalculationGoal(goal.lower())
    accuracy_enum = AccuracyLevel(accuracy.lower())
    
    # Determine system size
    if n_atoms < 10:
        size = SystemSize.SMALL
    elif n_atoms < 50:
        size = SystemSize.MEDIUM
    elif n_atoms < 200:
        size = SystemSize.LARGE
    else:
        size = SystemSize.VERY_LARGE
    
    return selector.get_recommendations(goal_enum, accuracy_enum, size)


def get_method_info(method: str) -> Dict[str, Any]:
    """Get information about a method."""
    selector = get_method_selector()
    return selector._method_database.get(method.lower(), {})


def format_recommendation(prompt: MethodSelectionPrompt) -> str:
    """Format recommendation as text."""
    lines = [f"Method Recommendations for {prompt.goal.value}:"]
    lines.append(f"Accuracy level: {prompt.accuracy.value}")
    lines.append(f"System size: {prompt.system_size.value}")
    lines.append("")
    
    for i, rec in enumerate(prompt.recommendations, 1):
        lines.append(f"{i}. {rec.method}/{rec.basis}")
        lines.append(f"   {rec.description}")
        lines.append(f"   Accuracy: {rec.accuracy}")
        lines.append(f"   Cost: {rec.computational_cost}")
        if rec.notes:
            for note in rec.notes:
                lines.append(f"   Note: {note}")
        lines.append("")
    
    if prompt.warnings:
        lines.append("Warnings:")
        for warning in prompt.warnings:
            lines.append(f"  - {warning}")
    
    lines.append("")
    lines.append(prompt.general_guidance)
    
    return "\n".join(lines)
