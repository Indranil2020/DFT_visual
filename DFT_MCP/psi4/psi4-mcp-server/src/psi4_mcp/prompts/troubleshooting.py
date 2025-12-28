"""
Troubleshooting Prompts for Psi4 MCP Server.

Provides diagnostic prompts and troubleshooting guidance for
common calculation problems.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ProblemCategory(str, Enum):
    """Categories of problems."""
    CONVERGENCE = "convergence"
    MEMORY = "memory"
    INPUT = "input"
    BASIS = "basis"
    METHOD = "method"
    GEOMETRY = "geometry"
    PERFORMANCE = "performance"
    OUTPUT = "output"


class Severity(str, Enum):
    """Problem severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class DiagnosticQuestion:
    """A diagnostic question to help identify the problem."""
    question: str
    options: List[str] = field(default_factory=list)
    followup_action: str = ""


@dataclass
class Solution:
    """A potential solution to a problem."""
    title: str
    description: str
    steps: List[str] = field(default_factory=list)
    code_example: str = ""
    success_rate: str = ""


@dataclass
class TroubleshootingGuide:
    """Complete troubleshooting guide for a problem."""
    problem_id: str
    title: str
    category: ProblemCategory
    severity: Severity
    symptoms: List[str] = field(default_factory=list)
    causes: List[str] = field(default_factory=list)
    diagnostic_questions: List[DiagnosticQuestion] = field(default_factory=list)
    solutions: List[Solution] = field(default_factory=list)
    prevention_tips: List[str] = field(default_factory=list)
    related_problems: List[str] = field(default_factory=list)


class TroubleshootingDatabase:
    """Database of troubleshooting guides."""
    
    def __init__(self):
        self._guides: Dict[str, TroubleshootingGuide] = {}
        self._load_default_guides()
    
    def _load_default_guides(self) -> None:
        """Load default troubleshooting guides."""
        self._load_scf_convergence_guide()
        self._load_memory_error_guide()
        self._load_geometry_error_guide()
        self._load_basis_error_guide()
        self._load_optimization_convergence_guide()
    
    def _load_scf_convergence_guide(self) -> None:
        """Load SCF convergence troubleshooting guide."""
        guide = TroubleshootingGuide(
            problem_id="scf_convergence",
            title="SCF Convergence Failure",
            category=ProblemCategory.CONVERGENCE,
            severity=Severity.ERROR,
            symptoms=[
                "SCF iterations exceed maximum",
                "Energy oscillates without converging",
                "DIIS error remains large",
                "Error message: 'Could not converge SCF'",
            ],
            causes=[
                "Poor initial guess",
                "Difficult electronic structure (near-degeneracy)",
                "Inappropriate SCF algorithm",
                "Basis set issues",
                "Geometry problems (atoms too close)",
            ],
            diagnostic_questions=[
                DiagnosticQuestion(
                    question="Does the energy oscillate or monotonically fail to converge?",
                    options=["Oscillates", "Monotonically increases", "Stuck at plateau"],
                    followup_action="Oscillation suggests damping may help",
                ),
                DiagnosticQuestion(
                    question="Is this an open-shell system?",
                    options=["Yes", "No"],
                    followup_action="Open-shell may need UHF or stability analysis",
                ),
                DiagnosticQuestion(
                    question="Is the geometry reasonable?",
                    options=["Yes", "No", "Uncertain"],
                    followup_action="Check for atoms too close together",
                ),
            ],
            solutions=[
                Solution(
                    title="Try SOSCF algorithm",
                    description="Second-order SCF can help with difficult convergence",
                    steps=[
                        "Add soscf option to calculation",
                        "May need more iterations",
                    ],
                    code_example='options={"soscf": True, "maxiter": 200}',
                    success_rate="High for oscillating cases",
                ),
                Solution(
                    title="Apply damping",
                    description="Slow down Fock matrix updates",
                    steps=[
                        "Set damping percentage (try 20-50%)",
                        "Disable SOSCF if using damping",
                    ],
                    code_example='options={"damping_percentage": 20}',
                    success_rate="Good for early iterations",
                ),
                Solution(
                    title="Use level shifting",
                    description="Shift virtual orbital energies",
                    code_example='options={"level_shift": 0.5}',
                    success_rate="Moderate",
                ),
                Solution(
                    title="Try different initial guess",
                    description="SAD or GWH instead of core guess",
                    code_example='options={"guess": "sad"}',
                    success_rate="Good for transition metals",
                ),
                Solution(
                    title="Increase convergence tolerance",
                    description="Temporary measure for very difficult cases",
                    code_example='options={"e_convergence": 1e-5, "d_convergence": 1e-4}',
                    success_rate="Last resort",
                ),
            ],
            prevention_tips=[
                "Always pre-optimize geometry with cheaper method",
                "Start with smaller basis set, then increase",
                "Check for unusual electronic structure",
                "Use stability analysis for open-shell systems",
            ],
            related_problems=["geometry_error", "basis_error"],
        )
        self._guides[guide.problem_id] = guide
    
    def _load_memory_error_guide(self) -> None:
        """Load memory error troubleshooting guide."""
        guide = TroubleshootingGuide(
            problem_id="memory_error",
            title="Out of Memory Error",
            category=ProblemCategory.MEMORY,
            severity=Severity.CRITICAL,
            symptoms=[
                "Process killed by OOM killer",
                "Memory allocation failed",
                "Calculation hangs then crashes",
                "Very slow disk swapping",
            ],
            causes=[
                "System too large for available memory",
                "Inefficient algorithm selection",
                "Too many threads",
                "Large basis set",
            ],
            solutions=[
                Solution(
                    title="Use density fitting",
                    description="DF reduces memory by approximating integrals",
                    code_example='method = "df-mp2"  # or options={"scf_type": "df"}',
                    success_rate="Very high",
                ),
                Solution(
                    title="Reduce memory allocation",
                    description="Explicitly limit Psi4 memory",
                    code_example='options={"memory": "4 GB"}',
                    success_rate="High",
                ),
                Solution(
                    title="Use smaller basis set",
                    description="Try cc-pVDZ instead of cc-pVTZ",
                    success_rate="High",
                ),
                Solution(
                    title="Reduce number of threads",
                    description="Each thread uses memory for integrals",
                    code_example='options={"num_threads": 2}',
                    success_rate="Moderate",
                ),
            ],
            prevention_tips=[
                "Estimate memory before starting large calculations",
                "Use density fitting for systems > 30 atoms",
                "Monitor memory usage during calculation",
            ],
        )
        self._guides[guide.problem_id] = guide
    
    def _load_geometry_error_guide(self) -> None:
        """Load geometry error troubleshooting guide."""
        guide = TroubleshootingGuide(
            problem_id="geometry_error",
            title="Invalid Geometry Error",
            category=ProblemCategory.GEOMETRY,
            severity=Severity.ERROR,
            symptoms=[
                "Atoms too close together",
                "Linear molecule issues",
                "Symmetry detection failed",
                "Invalid Z-matrix",
            ],
            causes=[
                "Atoms overlapping or too close (< 0.5 Å)",
                "Incorrect coordinate format",
                "Invalid bond angles (0° or 180°)",
                "Missing atoms",
            ],
            solutions=[
                Solution(
                    title="Check interatomic distances",
                    description="Ensure no atoms are too close",
                    steps=[
                        "Visualize the structure",
                        "Check for distances < 0.5 Å",
                        "Adjust positions if needed",
                    ],
                ),
                Solution(
                    title="Disable symmetry",
                    description="Avoid symmetry detection issues",
                    code_example='molecule["symmetry"] = "c1"',
                    success_rate="High for symmetry issues",
                ),
                Solution(
                    title="Use Cartesian instead of Z-matrix",
                    description="More robust for complex geometries",
                ),
            ],
            prevention_tips=[
                "Always visualize geometry before calculation",
                "Use validated structure formats",
                "Pre-optimize with molecular mechanics",
            ],
        )
        self._guides[guide.problem_id] = guide
    
    def _load_basis_error_guide(self) -> None:
        """Load basis set error troubleshooting guide."""
        guide = TroubleshootingGuide(
            problem_id="basis_error",
            title="Basis Set Error",
            category=ProblemCategory.BASIS,
            severity=Severity.ERROR,
            symptoms=[
                "Basis set not found",
                "Basis not available for element",
                "Linear dependency warning",
            ],
            causes=[
                "Misspelled basis set name",
                "Element not covered by basis",
                "Incompatible basis/element combination",
            ],
            solutions=[
                Solution(
                    title="Check basis set name",
                    description="Ensure correct spelling and format",
                    steps=[
                        "Use lowercase with hyphens: cc-pvdz, not CC-PVDZ",
                        "Check Psi4 documentation for available bases",
                    ],
                ),
                Solution(
                    title="Use different basis for heavy elements",
                    description="Some bases don't cover all elements",
                    code_example='basis = "def2-svp"  # Wide element coverage',
                ),
            ],
        )
        self._guides[guide.problem_id] = guide
    
    def _load_optimization_convergence_guide(self) -> None:
        """Load optimization convergence troubleshooting guide."""
        guide = TroubleshootingGuide(
            problem_id="optimization_convergence",
            title="Geometry Optimization Not Converging",
            category=ProblemCategory.CONVERGENCE,
            severity=Severity.WARNING,
            symptoms=[
                "Max iterations exceeded",
                "Forces remain large",
                "Energy oscillates",
                "Steps too small",
            ],
            causes=[
                "Flat potential energy surface",
                "Poor initial geometry",
                "Inappropriate coordinate system",
                "Numerical noise from SCF",
            ],
            solutions=[
                Solution(
                    title="Use tighter SCF convergence",
                    description="Optimization needs accurate gradients",
                    code_example='options={"e_convergence": 1e-8, "d_convergence": 1e-8}',
                ),
                Solution(
                    title="Try different coordinate system",
                    description="Redundant internals often work better",
                    code_example='options={"opt_coordinates": "redundant"}',
                ),
                Solution(
                    title="Reset Hessian",
                    description="Accumulated Hessian errors can cause problems",
                    code_example='options={"full_hess_every": 5}',
                ),
            ],
            prevention_tips=[
                "Start with reasonable initial geometry",
                "Use appropriate convergence criteria",
                "Check SCF convergence at each step",
            ],
        )
        self._guides[guide.problem_id] = guide
    
    def add_guide(self, guide: TroubleshootingGuide) -> None:
        """Add a troubleshooting guide."""
        self._guides[guide.problem_id] = guide
    
    def get_guide(self, problem_id: str) -> Optional[TroubleshootingGuide]:
        """Get guide by problem ID."""
        return self._guides.get(problem_id)
    
    def search_by_symptom(self, symptom: str) -> List[TroubleshootingGuide]:
        """Search guides by symptom."""
        symptom_lower = symptom.lower()
        results = []
        for guide in self._guides.values():
            for s in guide.symptoms:
                if symptom_lower in s.lower():
                    results.append(guide)
                    break
        return results
    
    def search_by_category(self, category: ProblemCategory) -> List[TroubleshootingGuide]:
        """Search guides by category."""
        return [g for g in self._guides.values() if g.category == category]
    
    def list_all(self) -> List[str]:
        """List all problem IDs."""
        return list(self._guides.keys())


# Global database instance
_troubleshooting_db: Optional[TroubleshootingDatabase] = None


def get_troubleshooting_database() -> TroubleshootingDatabase:
    """Get the global troubleshooting database."""
    global _troubleshooting_db
    if _troubleshooting_db is None:
        _troubleshooting_db = TroubleshootingDatabase()
    return _troubleshooting_db


def diagnose_problem(error_message: str) -> List[TroubleshootingGuide]:
    """Diagnose problem from error message."""
    db = get_troubleshooting_database()
    
    error_lower = error_message.lower()
    
    # Check for common patterns
    if "converge" in error_lower and "scf" in error_lower:
        guide = db.get_guide("scf_convergence")
        return [guide] if guide else []
    
    if "memory" in error_lower or "oom" in error_lower or "allocation" in error_lower:
        guide = db.get_guide("memory_error")
        return [guide] if guide else []
    
    if "geometry" in error_lower or "atoms too close" in error_lower:
        guide = db.get_guide("geometry_error")
        return [guide] if guide else []
    
    if "basis" in error_lower or "not found" in error_lower:
        guide = db.get_guide("basis_error")
        return [guide] if guide else []
    
    # Fall back to symptom search
    return db.search_by_symptom(error_message)


def get_scf_convergence_help() -> TroubleshootingGuide:
    """Get SCF convergence troubleshooting guide."""
    db = get_troubleshooting_database()
    guide = db.get_guide("scf_convergence")
    if guide is None:
        return TroubleshootingGuide(
            problem_id="scf_convergence",
            title="SCF Convergence",
            category=ProblemCategory.CONVERGENCE,
            severity=Severity.ERROR,
        )
    return guide


def format_troubleshooting_guide(guide: TroubleshootingGuide) -> str:
    """Format troubleshooting guide as text."""
    lines = [f"=== {guide.title} ==="]
    lines.append(f"Category: {guide.category.value}")
    lines.append(f"Severity: {guide.severity.value}")
    lines.append("")
    
    if guide.symptoms:
        lines.append("Symptoms:")
        for symptom in guide.symptoms:
            lines.append(f"  - {symptom}")
        lines.append("")
    
    if guide.causes:
        lines.append("Common Causes:")
        for cause in guide.causes:
            lines.append(f"  - {cause}")
        lines.append("")
    
    if guide.solutions:
        lines.append("Solutions:")
        for i, solution in enumerate(guide.solutions, 1):
            lines.append(f"\n{i}. {solution.title}")
            lines.append(f"   {solution.description}")
            if solution.code_example:
                lines.append(f"   Code: {solution.code_example}")
            if solution.success_rate:
                lines.append(f"   Success rate: {solution.success_rate}")
        lines.append("")
    
    if guide.prevention_tips:
        lines.append("Prevention Tips:")
        for tip in guide.prevention_tips:
            lines.append(f"  - {tip}")
    
    return "\n".join(lines)
