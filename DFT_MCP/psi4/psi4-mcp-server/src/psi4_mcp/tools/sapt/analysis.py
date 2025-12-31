"""
SAPT Analysis and Interpretation Tool.

Provides analysis tools for interpreting SAPT results, including
classification of interaction types, comparison utilities, and
visualization-ready data preparation.

Key Features:
    - Interaction type classification
    - Energy component percentage analysis
    - Comparison between SAPT levels
    - Distance dependence analysis
    - Benchmark comparisons
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolCategory,
    register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError, ValidationError


logger = logging.getLogger(__name__)


HARTREE_TO_KCAL = 627.5094740631


# =============================================================================
# INTERACTION CLASSIFICATION
# =============================================================================

@dataclass
class InteractionClassification:
    """Classification of intermolecular interaction type."""
    primary_type: str
    secondary_type: Optional[str]
    strength: str
    electrostatic_fraction: float
    exchange_fraction: float
    induction_fraction: float
    dispersion_fraction: float
    notes: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_type": self.primary_type,
            "secondary_type": self.secondary_type,
            "strength": self.strength,
            "electrostatic_fraction": self.electrostatic_fraction,
            "exchange_fraction": self.exchange_fraction,
            "induction_fraction": self.induction_fraction,
            "dispersion_fraction": self.dispersion_fraction,
            "notes": self.notes,
        }


def classify_interaction(
    elst: float,
    exch: float,
    ind: float,
    disp: float,
    total: float,
) -> InteractionClassification:
    """
    Classify the type of intermolecular interaction based on SAPT components.
    
    Classification rules based on dominant energy components.
    """
    # Compute fractions (use absolute values for percentages)
    total_attractive = abs(elst) + abs(ind) + abs(disp)
    
    if total_attractive < 1e-10:
        elst_frac = exch_frac = ind_frac = disp_frac = 0.25
    else:
        elst_frac = abs(elst) / total_attractive
        ind_frac = abs(ind) / total_attractive
        disp_frac = abs(disp) / total_attractive
    
    exch_frac = abs(exch) / (abs(exch) + total_attractive) if total_attractive > 0 else 0.5
    
    # Classification logic
    notes = []
    primary_type = "mixed"
    secondary_type = None
    
    # Strong electrostatic (>50% of attractive)
    if elst_frac > 0.5 and elst < 0:
        primary_type = "electrostatic"
        if ind_frac > 0.2:
            secondary_type = "hydrogen_bond"
            notes.append("Significant induction suggests hydrogen bonding character")
    
    # Dispersion dominated (>50% of attractive)
    elif disp_frac > 0.5:
        primary_type = "dispersion"
        if elst < 0 and elst_frac > 0.2:
            secondary_type = "mixed_dispersion_electrostatic"
            notes.append("Some electrostatic stabilization present")
        else:
            notes.append("van der Waals / London dispersion interaction")
    
    # Induction dominated (>40%)
    elif ind_frac > 0.4:
        primary_type = "charge_transfer"
        notes.append("Significant charge transfer/polarization character")
    
    # Mixed interaction
    else:
        primary_type = "mixed"
        if elst_frac > 0.3:
            secondary_type = "electrostatic_component"
        elif disp_frac > 0.3:
            secondary_type = "dispersion_component"
    
    # Classify strength
    total_kcal = total * HARTREE_TO_KCAL if abs(total) < 1 else total
    
    if abs(total_kcal) < 1:
        strength = "very_weak"
    elif abs(total_kcal) < 3:
        strength = "weak"
    elif abs(total_kcal) < 10:
        strength = "moderate"
    elif abs(total_kcal) < 20:
        strength = "strong"
    else:
        strength = "very_strong"
    
    # Additional notes
    if exch > 0 and exch > abs(total):
        notes.append("Warning: Large exchange repulsion, system may be too close")
    
    if total > 0:
        notes.append("Net repulsive interaction")
    
    return InteractionClassification(
        primary_type=primary_type,
        secondary_type=secondary_type,
        strength=strength,
        electrostatic_fraction=elst_frac,
        exchange_fraction=exch_frac,
        induction_fraction=ind_frac,
        dispersion_fraction=disp_frac,
        notes=notes,
    )


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SAPTComponentAnalysis:
    """Detailed analysis of SAPT energy components."""
    electrostatics_kcal: float
    exchange_kcal: float
    induction_kcal: float
    dispersion_kcal: float
    total_kcal: float
    
    attractive_sum_kcal: float
    repulsive_sum_kcal: float
    net_kcal: float
    
    classification: InteractionClassification
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "electrostatics_kcal": self.electrostatics_kcal,
            "exchange_kcal": self.exchange_kcal,
            "induction_kcal": self.induction_kcal,
            "dispersion_kcal": self.dispersion_kcal,
            "total_kcal": self.total_kcal,
            "attractive_sum_kcal": self.attractive_sum_kcal,
            "repulsive_sum_kcal": self.repulsive_sum_kcal,
            "net_kcal": self.net_kcal,
            "classification": self.classification.to_dict(),
        }


@dataclass
class SAPTComparisonResult:
    """Comparison between different SAPT levels."""
    sapt_levels: List[str]
    total_energies_kcal: Dict[str, float]
    differences_kcal: Dict[str, float]
    recommended_level: str
    recommendation_reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sapt_levels": self.sapt_levels,
            "total_energies_kcal": self.total_energies_kcal,
            "differences_kcal": self.differences_kcal,
            "recommended_level": self.recommended_level,
            "recommendation_reason": self.recommendation_reason,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class SAPTAnalysisInput(ToolInput):
    """Input schema for SAPT analysis."""
    
    electrostatics: float = Field(..., description="Electrostatic energy in kcal/mol")
    exchange: float = Field(..., description="Exchange energy in kcal/mol")
    induction: float = Field(..., description="Induction energy in kcal/mol")
    dispersion: float = Field(..., description="Dispersion energy in kcal/mol")
    total: Optional[float] = Field(default=None, description="Total energy (computed if not given)")
    
    sapt_level: str = Field(default="sapt0", description="SAPT level used")
    compare_levels: Optional[Dict[str, float]] = Field(
        default=None,
        description="Other SAPT level totals for comparison",
    )


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def analyze_sapt_components(
    elst: float,
    exch: float,
    ind: float,
    disp: float,
    total: Optional[float] = None,
) -> SAPTComponentAnalysis:
    """
    Perform comprehensive analysis of SAPT energy components.
    
    Args:
        elst: Electrostatic energy in kcal/mol
        exch: Exchange energy in kcal/mol
        ind: Induction energy in kcal/mol
        disp: Dispersion energy in kcal/mol
        total: Total energy (computed from components if not given)
        
    Returns:
        SAPTComponentAnalysis with classification and breakdown.
    """
    if total is None:
        total = elst + exch + ind + disp
    
    # Sum attractive and repulsive
    attractive = 0.0
    repulsive = 0.0
    
    for comp in [elst, ind, disp]:
        if comp < 0:
            attractive += comp
        else:
            repulsive += comp
    
    if exch > 0:
        repulsive += exch
    else:
        attractive += exch
    
    # Classify
    classification = classify_interaction(elst, exch, ind, disp, total)
    
    return SAPTComponentAnalysis(
        electrostatics_kcal=elst,
        exchange_kcal=exch,
        induction_kcal=ind,
        dispersion_kcal=disp,
        total_kcal=total,
        attractive_sum_kcal=attractive,
        repulsive_sum_kcal=repulsive,
        net_kcal=total,
        classification=classification,
    )


def compare_sapt_levels(
    totals: Dict[str, float],
) -> SAPTComparisonResult:
    """
    Compare energies from different SAPT levels.
    
    Args:
        totals: Dict mapping SAPT level names to total energies in kcal/mol.
        
    Returns:
        SAPTComparisonResult with comparison and recommendation.
    """
    levels = list(totals.keys())
    
    # Compute differences from highest level
    level_hierarchy = ["sapt0", "sapt2", "sapt2+", "sapt2+(3)", "sapt2+3"]
    
    highest = None
    for level in reversed(level_hierarchy):
        for key in totals:
            if level in key.lower():
                highest = key
                break
        if highest:
            break
    
    if highest is None:
        highest = levels[-1]
    
    reference_value = totals[highest]
    differences = {level: val - reference_value for level, val in totals.items()}
    
    # Make recommendation
    if len(totals) == 1:
        recommended = levels[0]
        reason = "Only one level provided"
    else:
        # Check for convergence
        max_diff = max(abs(d) for d in differences.values())
        
        if max_diff < 0.5:
            recommended = "sapt0"
            reason = "All levels agree within 0.5 kcal/mol; SAPT0 is sufficient"
        elif max_diff < 2.0:
            recommended = "sapt2"
            reason = "Moderate variation between levels; SAPT2 recommended"
        else:
            recommended = "sapt2+(3)"
            reason = "Significant level dependence; highest available level recommended"
    
    return SAPTComparisonResult(
        sapt_levels=levels,
        total_energies_kcal=totals,
        differences_kcal=differences,
        recommended_level=recommended,
        recommendation_reason=reason,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class SAPTAnalysisTool(BaseTool[SAPTAnalysisInput, ToolOutput]):
    """Tool for analyzing and interpreting SAPT results."""
    
    name: ClassVar[str] = "analyze_sapt_results"
    description: ClassVar[str] = (
        "Analyze SAPT energy components to classify interaction type and strength."
    )
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: SAPTAnalysisInput) -> Optional[ValidationError]:
        return None
    
    def _execute(self, input_data: SAPTAnalysisInput) -> Result[ToolOutput]:
        analysis = analyze_sapt_components(
            input_data.electrostatics,
            input_data.exchange,
            input_data.induction,
            input_data.dispersion,
            input_data.total,
        )
        
        result_data = analysis.to_dict()
        
        # Add comparison if provided
        if input_data.compare_levels:
            totals = {input_data.sapt_level: analysis.total_kcal}
            totals.update(input_data.compare_levels)
            comparison = compare_sapt_levels(totals)
            result_data["level_comparison"] = comparison.to_dict()
        
        c = analysis.classification
        message = (
            f"SAPT Interaction Analysis\n"
            f"{'='*50}\n"
            f"Components (kcal/mol):\n"
            f"  Electrostatics: {analysis.electrostatics_kcal:8.3f}\n"
            f"  Exchange:       {analysis.exchange_kcal:8.3f}\n"
            f"  Induction:      {analysis.induction_kcal:8.3f}\n"
            f"  Dispersion:     {analysis.dispersion_kcal:8.3f}\n"
            f"  Total:          {analysis.total_kcal:8.3f}\n"
            f"{'='*50}\n"
            f"Classification:\n"
            f"  Primary type: {c.primary_type}\n"
            f"  Strength: {c.strength}\n"
            f"  Notes: {'; '.join(c.notes) if c.notes else 'None'}"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result_data))


def analyze_sapt_results(
    electrostatics: float,
    exchange: float,
    induction: float,
    dispersion: float,
    total: Optional[float] = None,
    **kwargs: Any,
) -> ToolOutput:
    """
    Analyze SAPT energy components.
    
    Args:
        electrostatics: Electrostatic energy in kcal/mol.
        exchange: Exchange energy in kcal/mol.
        induction: Induction energy in kcal/mol.
        dispersion: Dispersion energy in kcal/mol.
        total: Total energy (optional).
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with analysis and classification.
    """
    tool = SAPTAnalysisTool()
    return tool.run({
        "electrostatics": electrostatics,
        "exchange": exchange,
        "induction": induction,
        "dispersion": dispersion,
        "total": total,
        **kwargs,
    })
