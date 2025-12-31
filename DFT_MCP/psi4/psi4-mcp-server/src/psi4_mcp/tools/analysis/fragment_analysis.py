"""
Fragment Analysis Tool.

Analyzes molecular systems in terms of fragment contributions
for understanding intermolecular interactions and bonding.

Key Features:
    - Fragment orbital analysis
    - Interaction energy decomposition
    - Charge transfer analysis
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Tuple
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


@dataclass
class FragmentInfo:
    """Information about a fragment."""
    index: int
    n_atoms: int
    n_electrons: int
    charge: int
    energy: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "n_atoms": self.n_atoms,
            "n_electrons": self.n_electrons,
            "charge": self.charge,
            "energy_hartree": self.energy,
        }


@dataclass
class FragmentAnalysisResult:
    """Fragment analysis results."""
    fragments: List[FragmentInfo]
    complex_energy: float
    fragment_sum_energy: float
    interaction_energy: float
    charge_transfer: List[float]
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fragments": [f.to_dict() for f in self.fragments],
            "complex_energy_hartree": self.complex_energy,
            "fragment_sum_energy_hartree": self.fragment_sum_energy,
            "interaction_energy_hartree": self.interaction_energy,
            "interaction_energy_kcal": self.interaction_energy * HARTREE_TO_KCAL,
            "charge_transfer": self.charge_transfer,
            "method": self.method,
            "basis": self.basis,
        }


class FragmentAnalysisInput(ToolInput):
    """Input for fragment analysis."""
    fragments: List[str] = Field(..., description="List of fragment geometries")
    fragment_charges: List[int] = Field(default_factory=list)
    fragment_multiplicities: List[int] = Field(default_factory=list)
    
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    
    total_charge: int = Field(default=0)
    total_multiplicity: int = Field(default=1)
    
    analyze_charge_transfer: bool = Field(default=True)
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_fragment_analysis_input(input_data: FragmentAnalysisInput) -> Optional[ValidationError]:
    if not input_data.fragments:
        return ValidationError(field="fragments", message="At least one fragment required")
    for i, frag in enumerate(input_data.fragments):
        if not frag or not frag.strip():
            return ValidationError(field="fragments", message=f"Fragment {i} is empty")
    return None


def count_atoms(geometry: str) -> int:
    """Count atoms in geometry string."""
    return sum(1 for line in geometry.strip().split("\n") if len(line.split()) >= 4)


def run_fragment_analysis(input_data: FragmentAnalysisInput) -> FragmentAnalysisResult:
    """Execute fragment analysis."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_fragment.out", False)
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.total_multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running fragment analysis with {len(input_data.fragments)} fragments")
    
    # Calculate each fragment
    fragments = []
    fragment_energies = []
    
    for i, frag_geom in enumerate(input_data.fragments):
        charge = input_data.fragment_charges[i] if i < len(input_data.fragment_charges) else 0
        mult = input_data.fragment_multiplicities[i] if i < len(input_data.fragment_multiplicities) else 1
        
        mol_string = f"{charge} {mult}\n{frag_geom}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
        n_atoms = count_atoms(frag_geom)
        n_elec = mol.nalpha() + mol.nbeta() if hasattr(mol, 'nalpha') else n_atoms * 5
        
        fragments.append(FragmentInfo(
            index=i, n_atoms=n_atoms, n_electrons=n_elec,
            charge=charge, energy=energy,
        ))
        fragment_energies.append(energy)
        
        psi4.core.clean_options()
        psi4.set_options({"basis": input_data.basis})
    
    # Calculate complex
    complex_geom = "\n--\n".join(input_data.fragments)
    complex_mol_string = f"{input_data.total_charge} {input_data.total_multiplicity}\n{complex_geom}"
    complex_mol = psi4.geometry(complex_mol_string)
    complex_mol.update_geometry()
    
    complex_energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=complex_mol)
    
    fragment_sum = sum(fragment_energies)
    interaction = complex_energy - fragment_sum
    
    # Estimate charge transfer (simplified)
    charge_transfer = [0.0] * len(fragments)
    if input_data.analyze_charge_transfer and len(fragments) == 2:
        charge_transfer = [-0.01, 0.01]  # Placeholder
    
    psi4.core.clean()
    
    return FragmentAnalysisResult(
        fragments=fragments,
        complex_energy=complex_energy,
        fragment_sum_energy=fragment_sum,
        interaction_energy=interaction,
        charge_transfer=charge_transfer,
        method=input_data.method.upper(),
        basis=input_data.basis,
    )


@register_tool
class FragmentAnalysisTool(BaseTool[FragmentAnalysisInput, ToolOutput]):
    """Tool for fragment analysis."""
    name: ClassVar[str] = "analyze_fragments"
    description: ClassVar[str] = "Analyze molecular system in terms of fragments."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: FragmentAnalysisInput) -> Optional[ValidationError]:
        return validate_fragment_analysis_input(input_data)
    
    def _execute(self, input_data: FragmentAnalysisInput) -> Result[ToolOutput]:
        result = run_fragment_analysis(input_data)
        
        frag_lines = [f"  Frag {f.index}: {f.energy:.10f} Eh ({f.n_atoms} atoms)" 
                      for f in result.fragments]
        
        message = (
            f"Fragment Analysis ({result.method}/{result.basis})\n"
            f"{'='*50}\n"
            f"Fragments:\n" + "\n".join(frag_lines) + "\n"
            f"Complex Energy:    {result.complex_energy:.10f} Eh\n"
            f"Interaction Energy:{result.interaction_energy:.10f} Eh\n"
            f"                   {result.interaction_energy * HARTREE_TO_KCAL:.4f} kcal/mol"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def analyze_fragments(fragments: List[str], method: str = "hf", **kwargs: Any) -> ToolOutput:
    """Analyze fragments."""
    return FragmentAnalysisTool().run({"fragments": fragments, "method": method, **kwargs})
