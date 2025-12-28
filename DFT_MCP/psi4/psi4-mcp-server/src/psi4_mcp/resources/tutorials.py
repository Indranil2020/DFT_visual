"""
Tutorial Resources for Psi4 MCP Server.

Provides tutorial content, step-by-step guides, and educational
materials for quantum chemistry calculations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class DifficultyLevel(str, Enum):
    """Tutorial difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class TopicCategory(str, Enum):
    """Tutorial topic categories."""
    BASICS = "basics"
    ENERGY = "energy"
    OPTIMIZATION = "optimization"
    FREQUENCIES = "frequencies"
    PROPERTIES = "properties"
    EXCITED_STATES = "excited_states"
    INTERMOLECULAR = "intermolecular"
    ADVANCED_METHODS = "advanced_methods"
    BEST_PRACTICES = "best_practices"


@dataclass
class TutorialStep:
    """Single step in a tutorial."""
    step_number: int
    title: str
    description: str
    code_example: str = ""
    expected_output: str = ""
    tips: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Tutorial:
    """Complete tutorial."""
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    category: TopicCategory
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    steps: List[TutorialStep] = field(default_factory=list)
    estimated_time: int = 15  # minutes
    keywords: List[str] = field(default_factory=list)
    
    def get_step(self, number: int) -> Optional[TutorialStep]:
        """Get step by number."""
        for step in self.steps:
            if step.step_number == number:
                return step
        return None
    
    def total_steps(self) -> int:
        """Get total number of steps."""
        return len(self.steps)


class TutorialDatabase:
    """Database of tutorials."""
    
    def __init__(self):
        self._tutorials: Dict[str, Tutorial] = {}
        self._load_default_tutorials()
    
    def _load_default_tutorials(self) -> None:
        """Load default tutorials."""
        self._load_basic_energy_tutorial()
        self._load_geometry_optimization_tutorial()
        self._load_frequency_tutorial()
        self._load_tddft_tutorial()
        self._load_sapt_tutorial()
    
    def _load_basic_energy_tutorial(self) -> None:
        """Load basic energy calculation tutorial."""
        tutorial = Tutorial(
            id="basic_energy",
            title="Your First Energy Calculation",
            description="Learn how to calculate the electronic energy of a molecule using Psi4",
            difficulty=DifficultyLevel.BEGINNER,
            category=TopicCategory.ENERGY,
            prerequisites=[],
            learning_objectives=[
                "Understand molecular geometry input formats",
                "Choose appropriate method and basis set",
                "Interpret energy output",
                "Understand energy units",
            ],
            estimated_time=15,
            keywords=["energy", "HF", "DFT", "basis set", "beginner"],
        )
        
        tutorial.steps = [
            TutorialStep(
                step_number=1,
                title="Define the Molecule",
                description="First, we need to specify the molecular geometry. The simplest format is Cartesian coordinates.",
                code_example='''molecule = {
    "geometry": """
        O  0.000000  0.000000  0.117489
        H -0.756950  0.000000 -0.469957
        H  0.756950  0.000000 -0.469957
    """,
    "charge": 0,
    "multiplicity": 1
}''',
                tips=[
                    "Coordinates are typically in Angstroms",
                    "Charge 0 means neutral molecule",
                    "Multiplicity 1 means singlet (all electrons paired)",
                ],
            ),
            TutorialStep(
                step_number=2,
                title="Choose Method and Basis Set",
                description="Select a computational method and basis set. For beginners, B3LYP/6-31G* is a good starting point.",
                code_example='''method = "b3lyp"
basis = "6-31g*"''',
                tips=[
                    "B3LYP is a popular DFT functional",
                    "6-31G* is a medium-sized basis set",
                    "Larger basis sets are more accurate but slower",
                ],
            ),
            TutorialStep(
                step_number=3,
                title="Run the Calculation",
                description="Execute the energy calculation using the calculate_energy tool.",
                code_example='''result = await calculate_energy({
    "molecule": molecule,
    "method": method,
    "basis": basis
})''',
                expected_output="Energy: -76.4089 Hartree",
                tips=[
                    "Energies are reported in Hartree",
                    "1 Hartree = 627.509 kcal/mol",
                    "More negative energy means more stable",
                ],
            ),
            TutorialStep(
                step_number=4,
                title="Interpret Results",
                description="Understand what the energy value tells you about the molecule.",
                tips=[
                    "Absolute energies are less meaningful than relative energies",
                    "Compare energies of similar systems using the same method",
                    "Always check that SCF converged",
                ],
            ),
        ]
        
        self._tutorials[tutorial.id] = tutorial
    
    def _load_geometry_optimization_tutorial(self) -> None:
        """Load geometry optimization tutorial."""
        tutorial = Tutorial(
            id="geometry_optimization",
            title="Geometry Optimization",
            description="Learn how to find the minimum energy geometry of a molecule",
            difficulty=DifficultyLevel.BEGINNER,
            category=TopicCategory.OPTIMIZATION,
            prerequisites=["basic_energy"],
            learning_objectives=[
                "Understand the purpose of geometry optimization",
                "Set up and run an optimization",
                "Interpret convergence criteria",
                "Verify optimization success",
            ],
            estimated_time=20,
            keywords=["optimization", "geometry", "minimum", "convergence"],
        )
        
        tutorial.steps = [
            TutorialStep(
                step_number=1,
                title="Why Optimize Geometry?",
                description="Molecules naturally adopt geometries that minimize their energy. Optimization finds this stable structure.",
                tips=[
                    "Initial geometries from drawing programs are approximate",
                    "Optimized geometries are needed for accurate properties",
                    "Bond lengths and angles are refined during optimization",
                ],
            ),
            TutorialStep(
                step_number=2,
                title="Set Up the Optimization",
                description="Configure the optimization with appropriate convergence criteria.",
                code_example='''result = await optimize_geometry({
    "molecule": {
        "geometry": "H 0 0 0\\nH 0 0 1.0",  # Initial guess
        "charge": 0,
        "multiplicity": 1
    },
    "method": "b3lyp",
    "basis": "cc-pvdz",
    "max_iterations": 50
})''',
                tips=[
                    "Start with a reasonable initial geometry",
                    "Default convergence criteria work for most cases",
                ],
            ),
            TutorialStep(
                step_number=3,
                title="Check Convergence",
                description="Verify that the optimization converged successfully.",
                expected_output='''Optimization converged!
Final energy: -1.1754 Hartree
H-H distance: 0.743 Angstrom''',
                tips=[
                    "Check that 'converged' is True",
                    "Verify bond lengths are reasonable",
                    "Run frequencies to confirm minimum",
                ],
                warnings=[
                    "Non-convergence may indicate bad initial geometry",
                    "Very flat potential surfaces can cause problems",
                ],
            ),
        ]
        
        self._tutorials[tutorial.id] = tutorial
    
    def _load_frequency_tutorial(self) -> None:
        """Load vibrational frequency tutorial."""
        tutorial = Tutorial(
            id="frequencies",
            title="Vibrational Frequency Analysis",
            description="Calculate vibrational frequencies and thermodynamic properties",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=TopicCategory.FREQUENCIES,
            prerequisites=["geometry_optimization"],
            learning_objectives=[
                "Understand harmonic frequency calculations",
                "Interpret IR and Raman spectra",
                "Calculate thermodynamic properties",
                "Identify stationary point character",
            ],
            estimated_time=25,
            keywords=["frequencies", "vibrations", "thermochemistry", "IR"],
        )
        
        tutorial.steps = [
            TutorialStep(
                step_number=1,
                title="Prerequisites",
                description="Frequency calculations require an optimized geometry.",
                warnings=[
                    "Never run frequencies on non-optimized geometries",
                    "Use the same method for optimization and frequencies",
                ],
            ),
            TutorialStep(
                step_number=2,
                title="Run Frequency Calculation",
                description="Calculate vibrational frequencies at the optimized geometry.",
                code_example='''result = await calculate_frequencies({
    "molecule": optimized_molecule,
    "method": "b3lyp",
    "basis": "cc-pvdz",
    "temperature": 298.15
})''',
            ),
            TutorialStep(
                step_number=3,
                title="Interpret Results",
                description="Analyze the frequency output.",
                tips=[
                    "All positive frequencies = minimum",
                    "One imaginary frequency = transition state",
                    "Multiple imaginary = higher-order saddle point",
                    "ZPE is the zero-point energy correction",
                ],
            ),
        ]
        
        self._tutorials[tutorial.id] = tutorial
    
    def _load_tddft_tutorial(self) -> None:
        """Load TD-DFT tutorial."""
        tutorial = Tutorial(
            id="tddft",
            title="Excited States with TD-DFT",
            description="Calculate electronic excited states and UV-Vis spectra",
            difficulty=DifficultyLevel.INTERMEDIATE,
            category=TopicCategory.EXCITED_STATES,
            prerequisites=["geometry_optimization"],
            learning_objectives=[
                "Understand electronic excitations",
                "Set up TD-DFT calculations",
                "Interpret excitation energies and oscillator strengths",
                "Generate UV-Vis absorption spectra",
            ],
            estimated_time=30,
            keywords=["TDDFT", "excited states", "UV-Vis", "spectrum"],
        )
        
        self._tutorials[tutorial.id] = tutorial
    
    def _load_sapt_tutorial(self) -> None:
        """Load SAPT tutorial."""
        tutorial = Tutorial(
            id="sapt",
            title="Intermolecular Interactions with SAPT",
            description="Analyze noncovalent interactions using SAPT",
            difficulty=DifficultyLevel.ADVANCED,
            category=TopicCategory.INTERMOLECULAR,
            prerequisites=["basic_energy"],
            learning_objectives=[
                "Understand SAPT energy decomposition",
                "Set up dimer calculations",
                "Interpret interaction energy components",
                "Choose appropriate SAPT level",
            ],
            estimated_time=35,
            keywords=["SAPT", "interaction", "noncovalent", "dimer"],
        )
        
        self._tutorials[tutorial.id] = tutorial
    
    def add_tutorial(self, tutorial: Tutorial) -> None:
        """Add a tutorial."""
        self._tutorials[tutorial.id] = tutorial
    
    def get_tutorial(self, tutorial_id: str) -> Optional[Tutorial]:
        """Get tutorial by ID."""
        return self._tutorials.get(tutorial_id)
    
    def list_tutorials(self) -> List[str]:
        """List all tutorial IDs."""
        return list(self._tutorials.keys())
    
    def search_by_difficulty(self, difficulty: DifficultyLevel) -> List[Tutorial]:
        """Search tutorials by difficulty."""
        return [t for t in self._tutorials.values() if t.difficulty == difficulty]
    
    def search_by_category(self, category: TopicCategory) -> List[Tutorial]:
        """Search tutorials by category."""
        return [t for t in self._tutorials.values() if t.category == category]
    
    def search_by_keyword(self, keyword: str) -> List[Tutorial]:
        """Search tutorials by keyword."""
        keyword_lower = keyword.lower()
        results = []
        for t in self._tutorials.values():
            if any(keyword_lower in k.lower() for k in t.keywords):
                results.append(t)
            elif keyword_lower in t.title.lower():
                results.append(t)
            elif keyword_lower in t.description.lower():
                results.append(t)
        return results


# Global database instance
_tutorial_db: Optional[TutorialDatabase] = None


def get_tutorial_database() -> TutorialDatabase:
    """Get the global tutorial database."""
    global _tutorial_db
    if _tutorial_db is None:
        _tutorial_db = TutorialDatabase()
    return _tutorial_db


def get_tutorial(tutorial_id: str) -> Optional[Tutorial]:
    """Get a tutorial by ID."""
    db = get_tutorial_database()
    return db.get_tutorial(tutorial_id)


def list_beginner_tutorials() -> List[Tutorial]:
    """List tutorials for beginners."""
    db = get_tutorial_database()
    return db.search_by_difficulty(DifficultyLevel.BEGINNER)


def get_tutorial_for_topic(topic: str) -> List[Tutorial]:
    """Get tutorials related to a topic."""
    db = get_tutorial_database()
    return db.search_by_keyword(topic)
