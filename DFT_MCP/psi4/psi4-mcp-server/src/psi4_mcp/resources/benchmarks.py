"""
Benchmark Resources for Psi4 MCP Server.

Provides access to standard benchmark datasets, reference values,
and validation data for computational chemistry calculations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class BenchmarkType(str, Enum):
    """Types of benchmarks."""
    ATOMIZATION = "atomization"
    REACTION = "reaction"
    BARRIER = "barrier"
    INTERACTION = "interaction"
    GEOMETRY = "geometry"
    FREQUENCY = "frequency"
    EXCITATION = "excitation"
    IONIZATION = "ionization"


@dataclass
class MoleculeData:
    """Data for a benchmark molecule."""
    name: str
    formula: str
    geometry: str  # XYZ format
    charge: int = 0
    multiplicity: int = 1
    reference_energy: Optional[float] = None
    reference_method: str = ""
    smiles: str = ""


@dataclass
class BenchmarkEntry:
    """Single entry in a benchmark dataset."""
    name: str
    reference_value: float
    unit: str
    uncertainty: float = 0.0
    reference_method: str = ""
    molecules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkDataset:
    """A complete benchmark dataset."""
    name: str
    description: str
    benchmark_type: BenchmarkType
    entries: List[BenchmarkEntry] = field(default_factory=list)
    molecules: Dict[str, MoleculeData] = field(default_factory=dict)
    reference: str = ""
    citation_key: str = ""
    
    def get_entry(self, name: str) -> Optional[BenchmarkEntry]:
        """Get entry by name."""
        for entry in self.entries:
            if entry.name == name:
                return entry
        return None
    
    def get_molecule(self, name: str) -> Optional[MoleculeData]:
        """Get molecule by name."""
        return self.molecules.get(name)
    
    def list_entries(self) -> List[str]:
        """List all entry names."""
        return [e.name for e in self.entries]


class BenchmarkDatabase:
    """Database of benchmark datasets."""
    
    def __init__(self):
        self._datasets: Dict[str, BenchmarkDataset] = {}
        self._load_default_benchmarks()
    
    def _load_default_benchmarks(self) -> None:
        """Load default benchmark datasets."""
        self._load_s22()
        self._load_w4_11()
        self._load_gmtkn55_subset()
    
    def _load_s22(self) -> None:
        """Load S22 interaction energy benchmark."""
        s22 = BenchmarkDataset(
            name="S22",
            description="22 noncovalent interaction energies",
            benchmark_type=BenchmarkType.INTERACTION,
            reference="Jurecka et al., PCCP 2006",
            citation_key="s22_2006",
        )
        
        # Add molecules
        s22.molecules["water_dimer"] = MoleculeData(
            name="water_dimer",
            formula="H4O2",
            geometry="""O  0.000000  0.000000  0.117489
H -0.756950  0.000000 -0.469957
H  0.756950  0.000000 -0.469957
--
O  0.000000  0.000000  2.902210
H  0.756950  0.000000  3.489656
H -0.756950  0.000000  3.489656""",
            charge=0,
            multiplicity=1,
        )
        
        s22.molecules["ammonia_dimer"] = MoleculeData(
            name="ammonia_dimer",
            formula="H6N2",
            geometry="""N  0.000000  0.000000  0.000000
H  0.000000  0.938871 -0.347206
H  0.813160 -0.469435 -0.347206
H -0.813160 -0.469435 -0.347206
--
N  0.000000  0.000000  3.200000
H  0.000000  0.938871  3.547206
H  0.813160 -0.469435  3.547206
H -0.813160 -0.469435  3.547206""",
        )
        
        # Add reference values (kcal/mol)
        s22_refs = [
            ("water_dimer", -4.989, 0.02),
            ("ammonia_dimer", -3.133, 0.02),
            ("formic_acid_dimer", -18.753, 0.05),
            ("formamide_dimer", -16.062, 0.05),
            ("uracil_dimer_hb", -20.641, 0.05),
            ("2pyridoxine_2aminopyridine", -16.934, 0.05),
            ("adenine_thymine_wc", -16.660, 0.05),
            ("methane_dimer", -0.527, 0.01),
            ("ethene_dimer", -1.472, 0.02),
            ("benzene_methane", -1.448, 0.02),
            ("benzene_dimer_pd", -2.654, 0.02),
            ("pyrazine_dimer", -4.255, 0.03),
            ("uracil_dimer_stack", -9.805, 0.03),
            ("indole_benzene_stack", -4.524, 0.03),
            ("adenine_thymine_stack", -11.730, 0.05),
            ("ethene_ethyne", -1.496, 0.02),
            ("benzene_water", -3.275, 0.02),
            ("benzene_ammonia", -2.312, 0.02),
            ("benzene_hcn", -4.541, 0.02),
            ("benzene_dimer_t", -2.717, 0.02),
            ("indole_benzene_t", -5.627, 0.03),
            ("phenol_dimer", -7.097, 0.03),
        ]
        
        for name, value, uncert in s22_refs:
            s22.entries.append(BenchmarkEntry(
                name=name,
                reference_value=value,
                unit="kcal/mol",
                uncertainty=uncert,
                reference_method="CCSD(T)/CBS",
            ))
        
        self._datasets["S22"] = s22
    
    def _load_w4_11(self) -> None:
        """Load W4-11 atomization energy benchmark (subset)."""
        w4 = BenchmarkDataset(
            name="W4-11",
            description="Atomization energies from W4 theory",
            benchmark_type=BenchmarkType.ATOMIZATION,
            reference="Karton et al., JCP 2011",
            citation_key="w4_2011",
        )
        
        # Common molecules with reference atomization energies (kcal/mol)
        w4_data = [
            ("H2", "H2", "H 0 0 0\nH 0 0 0.74", 109.49, 0.01),
            ("CH4", "CH4", "C 0 0 0\nH 0.629 0.629 0.629\nH -0.629 -0.629 0.629\nH -0.629 0.629 -0.629\nH 0.629 -0.629 -0.629", 420.42, 0.05),
            ("H2O", "H2O", "O 0 0 0.117\nH 0 0.757 -0.470\nH 0 -0.757 -0.470", 232.97, 0.02),
            ("NH3", "NH3", "N 0 0 0\nH 0 0.939 -0.347\nH 0.813 -0.469 -0.347\nH -0.813 -0.469 -0.347", 298.02, 0.03),
            ("CO", "CO", "C 0 0 0\nO 0 0 1.128", 259.73, 0.03),
            ("CO2", "CO2", "C 0 0 0\nO 0 0 1.16\nO 0 0 -1.16", 390.14, 0.05),
            ("N2", "N2", "N 0 0 0\nN 0 0 1.098", 228.48, 0.02),
            ("O2", "O2", "O 0 0 0\nO 0 0 1.208", 120.82, 0.02),
            ("F2", "F2", "F 0 0 0\nF 0 0 1.412", 39.04, 0.02),
        ]
        
        for name, formula, geom, ae, uncert in w4_data:
            w4.molecules[name] = MoleculeData(
                name=name,
                formula=formula,
                geometry=geom,
                reference_energy=ae,
                reference_method="W4",
            )
            w4.entries.append(BenchmarkEntry(
                name=name,
                reference_value=ae,
                unit="kcal/mol",
                uncertainty=uncert,
                reference_method="W4",
                molecules=[name],
            ))
        
        self._datasets["W4-11"] = w4
    
    def _load_gmtkn55_subset(self) -> None:
        """Load GMTKN55 subset for DFT benchmarking."""
        gmtkn = BenchmarkDataset(
            name="GMTKN55-subset",
            description="Subset of GMTKN55 general main group thermochemistry",
            benchmark_type=BenchmarkType.REACTION,
            reference="Goerigk et al., PCCP 2017",
            citation_key="gmtkn55_2017",
        )
        
        # Barrier heights from BH76 subset (kcal/mol)
        bh_data = [
            ("H + N2O -> OH + N2 (f)", 17.13),
            ("H + N2O -> OH + N2 (b)", 82.47),
            ("H + ClH -> HCl + H (f)", 17.8),
            ("H + ClH -> HCl + H (b)", 17.8),
            ("H + FCH3 -> HF + CH3 (f)", 30.5),
            ("H + FCH3 -> HF + CH3 (b)", 56.9),
            ("H + F2 -> HF + F (f)", 1.5),
            ("H + F2 -> HF + F (b)", 104.8),
        ]
        
        for name, value in bh_data:
            gmtkn.entries.append(BenchmarkEntry(
                name=name,
                reference_value=value,
                unit="kcal/mol",
                uncertainty=0.5,
                reference_method="W2-F12",
            ))
        
        self._datasets["GMTKN55-subset"] = gmtkn
    
    def add_dataset(self, dataset: BenchmarkDataset) -> None:
        """Add a dataset to the database."""
        self._datasets[dataset.name] = dataset
    
    def get_dataset(self, name: str) -> Optional[BenchmarkDataset]:
        """Get dataset by name."""
        return self._datasets.get(name)
    
    def list_datasets(self) -> List[str]:
        """List all dataset names."""
        return list(self._datasets.keys())
    
    def search_by_type(self, benchmark_type: BenchmarkType) -> List[BenchmarkDataset]:
        """Search datasets by type."""
        return [d for d in self._datasets.values() if d.benchmark_type == benchmark_type]


# Global database instance
_benchmark_db: Optional[BenchmarkDatabase] = None


def get_benchmark_database() -> BenchmarkDatabase:
    """Get the global benchmark database."""
    global _benchmark_db
    if _benchmark_db is None:
        _benchmark_db = BenchmarkDatabase()
    return _benchmark_db


def get_s22_reference(system: str) -> Optional[float]:
    """Get S22 reference interaction energy."""
    db = get_benchmark_database()
    s22 = db.get_dataset("S22")
    if s22 is None:
        return None
    entry = s22.get_entry(system)
    return entry.reference_value if entry else None


def calculate_mae(
    calculated: Dict[str, float],
    dataset_name: str,
) -> Tuple[float, int]:
    """Calculate mean absolute error against benchmark."""
    db = get_benchmark_database()
    dataset = db.get_dataset(dataset_name)
    
    if dataset is None:
        return 0.0, 0
    
    errors = []
    for entry in dataset.entries:
        if entry.name in calculated:
            error = abs(calculated[entry.name] - entry.reference_value)
            errors.append(error)
    
    if not errors:
        return 0.0, 0
    
    return sum(errors) / len(errors), len(errors)


def calculate_rmse(
    calculated: Dict[str, float],
    dataset_name: str,
) -> Tuple[float, int]:
    """Calculate root mean square error against benchmark."""
    db = get_benchmark_database()
    dataset = db.get_dataset(dataset_name)
    
    if dataset is None:
        return 0.0, 0
    
    sq_errors = []
    for entry in dataset.entries:
        if entry.name in calculated:
            error = (calculated[entry.name] - entry.reference_value) ** 2
            sq_errors.append(error)
    
    if not sq_errors:
        return 0.0, 0
    
    return (sum(sq_errors) / len(sq_errors)) ** 0.5, len(sq_errors)
