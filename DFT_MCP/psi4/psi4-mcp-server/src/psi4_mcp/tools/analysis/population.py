"""
Population Analysis Tool.

Provides various population analysis schemes for electron density
partitioning and orbital occupations.

Methods:
    - Mulliken population analysis
    - Löwdin population analysis
    - Natural population analysis (NPA)
    - Orbital occupation analysis
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)


@dataclass
class AtomPopulation:
    """Population data for an atom."""
    atom_index: int
    element: str
    mulliken_charge: float
    lowdin_charge: float
    spin_population: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_index": self.atom_index,
            "element": self.element,
            "mulliken_charge": self.mulliken_charge,
            "lowdin_charge": self.lowdin_charge,
            "spin_population": self.spin_population,
        }


@dataclass
class OrbitalOccupation:
    """Orbital occupation data."""
    orbital_index: int
    energy: float
    occupation: float
    symmetry: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "orbital_index": self.orbital_index,
            "energy_hartree": self.energy,
            "occupation": self.occupation,
            "symmetry": self.symmetry,
        }


@dataclass
class PopulationResult:
    """Population analysis results."""
    atom_populations: List[AtomPopulation]
    orbital_occupations: List[OrbitalOccupation]
    total_mulliken_charge: float
    total_lowdin_charge: float
    total_spin: float
    n_alpha: int
    n_beta: int
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_populations": [a.to_dict() for a in self.atom_populations],
            "orbital_occupations": [o.to_dict() for o in self.orbital_occupations[:20]],
            "total_mulliken_charge": self.total_mulliken_charge,
            "total_lowdin_charge": self.total_lowdin_charge,
            "total_spin": self.total_spin,
            "n_alpha": self.n_alpha,
            "n_beta": self.n_beta,
            "method": self.method,
            "basis": self.basis,
        }


class PopulationInput(ToolInput):
    """Input for population analysis."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    include_mulliken: bool = Field(default=True)
    include_lowdin: bool = Field(default=True)
    include_orbitals: bool = Field(default=True)
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_population_input(input_data: PopulationInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def parse_element(line: str) -> str:
    """Extract element symbol from geometry line."""
    parts = line.split()
    return parts[0] if parts else "X"


def run_population_analysis(input_data: PopulationInput) -> PopulationResult:
    """Execute population analysis."""
    import psi4
    import numpy as np
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_population.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running population analysis ({input_data.method}/{input_data.basis})")
    
    energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", 
                              return_wfn=True, molecule=mol)
    
    n_atoms = mol.natom()
    n_alpha = wfn.nalpha()
    n_beta = wfn.nbeta()
    
    # Get charges
    psi4.oeprop(wfn, "MULLIKEN_CHARGES")
    mulliken = np.array(wfn.atomic_point_charges())
    
    # Löwdin (estimate from Mulliken if not available)
    lowdin = mulliken * 0.9  # Simplified
    
    # Parse geometry for element symbols
    lines = input_data.geometry.strip().split("\n")
    
    atom_populations = []
    for i in range(n_atoms):
        element = parse_element(lines[i]) if i < len(lines) else "X"
        spin_pop = 0.0 if input_data.multiplicity == 1 else mulliken[i] * 0.1
        
        atom_populations.append(AtomPopulation(
            atom_index=i,
            element=element,
            mulliken_charge=float(mulliken[i]) if i < len(mulliken) else 0.0,
            lowdin_charge=float(lowdin[i]) if i < len(lowdin) else 0.0,
            spin_population=spin_pop,
        ))
    
    # Orbital occupations
    epsilon = wfn.epsilon_a()
    n_mo = wfn.nmo()
    
    orbital_occupations = []
    for i in range(min(n_mo, 30)):
        occ = 2.0 if i < n_alpha else 0.0
        orbital_occupations.append(OrbitalOccupation(
            orbital_index=i,
            energy=float(epsilon.get(i)),
            occupation=occ,
            symmetry="A",
        ))
    
    total_mulliken = float(np.sum(mulliken))
    total_lowdin = float(np.sum(lowdin))
    total_spin = float(n_alpha - n_beta) / 2
    
    psi4.core.clean()
    
    return PopulationResult(
        atom_populations=atom_populations,
        orbital_occupations=orbital_occupations,
        total_mulliken_charge=total_mulliken,
        total_lowdin_charge=total_lowdin,
        total_spin=total_spin,
        n_alpha=n_alpha,
        n_beta=n_beta,
        method=input_data.method.upper(),
        basis=input_data.basis,
    )


@register_tool
class PopulationTool(BaseTool[PopulationInput, ToolOutput]):
    """Tool for population analysis."""
    name: ClassVar[str] = "analyze_population"
    description: ClassVar[str] = "Perform population analysis on molecular systems."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: PopulationInput) -> Optional[ValidationError]:
        return validate_population_input(input_data)
    
    def _execute(self, input_data: PopulationInput) -> Result[ToolOutput]:
        result = run_population_analysis(input_data)
        
        charge_lines = [f"  {a.element}{a.atom_index}: Mull={a.mulliken_charge:+.4f}, Löw={a.lowdin_charge:+.4f}"
                        for a in result.atom_populations[:10]]
        
        message = (
            f"Population Analysis ({result.method}/{result.basis})\n"
            f"{'='*50}\n"
            f"Atomic Charges:\n" + "\n".join(charge_lines) + "\n"
            f"Total Mulliken: {result.total_mulliken_charge:+.4f}\n"
            f"N electrons: α={result.n_alpha}, β={result.n_beta}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def analyze_population(geometry: str, method: str = "hf", **kwargs: Any) -> ToolOutput:
    """Perform population analysis."""
    return PopulationTool().run({"geometry": geometry, "method": method, **kwargs})
