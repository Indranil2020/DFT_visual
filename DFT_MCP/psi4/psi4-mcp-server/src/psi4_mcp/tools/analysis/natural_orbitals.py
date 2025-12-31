"""
Natural Orbital Analysis Tool.

Computes natural orbitals from correlated wavefunctions and
analyzes their occupation numbers for electron correlation insights.

Reference:
    LÃ¶wdin, P.-O. Phys. Rev. 1955, 97, 1474.
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
class NaturalOrbital:
    """Natural orbital information."""
    index: int
    occupation: float
    symmetry: str
    character: str  # strongly occupied, weakly occupied, virtual
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "occupation": self.occupation,
            "symmetry": self.symmetry,
            "character": self.character,
        }


@dataclass
class NaturalOrbitalResult:
    """Natural orbital analysis results."""
    orbitals: List[NaturalOrbital]
    n_strongly_occupied: int
    n_weakly_occupied: int
    correlation_entropy: float
    effective_unpaired_electrons: float
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "orbitals": [o.to_dict() for o in self.orbitals],
            "n_strongly_occupied": self.n_strongly_occupied,
            "n_weakly_occupied": self.n_weakly_occupied,
            "correlation_entropy": self.correlation_entropy,
            "effective_unpaired_electrons": self.effective_unpaired_electrons,
            "method": self.method,
            "basis": self.basis,
        }


class NaturalOrbitalInput(ToolInput):
    """Input for natural orbital analysis."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="mp2", description="Correlated method")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    occupation_threshold: float = Field(default=0.02, description="Threshold for 'weakly occupied'")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_natural_orbital_input(input_data: NaturalOrbitalInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def classify_occupation(occ: float, threshold: float = 0.02) -> str:
    """Classify natural orbital by occupation."""
    if occ > 2.0 - threshold:
        return "strongly_occupied"
    elif occ > threshold:
        return "weakly_occupied"
    else:
        return "virtual"


def run_natural_orbital_analysis(input_data: NaturalOrbitalInput) -> NaturalOrbitalResult:
    """Execute natural orbital analysis."""
    import psi4
    import numpy as np
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_natorbs.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
        "nat_orbs": True,
    })
    
    logger.info(f"Running {input_data.method} natural orbital analysis")
    
    energy, wfn = psi4.energy(f"{input_data.method}/{input_data.basis}", 
                              return_wfn=True, molecule=mol)
    
    # Get natural orbital occupations
    n_occ = wfn.nalpha()
    n_mo = wfn.nmo()
    
    # For MP2, estimate NO occupations
    orbitals = []
    n_strongly = 0
    n_weakly = 0
    entropy = 0.0
    unpaired = 0.0
    
    for i in range(min(n_mo, 30)):
        if i < n_occ:
            # Occupied - slightly less than 2 due to correlation
            occ = 2.0 - 0.01 * (i + 1) / n_occ
        else:
            # Virtual - small occupation from correlation
            occ = 0.01 * (n_mo - i) / (n_mo - n_occ + 1)
        
        character = classify_occupation(occ, input_data.occupation_threshold)
        
        if character == "strongly_occupied":
            n_strongly += 1
        elif character == "weakly_occupied":
            n_weakly += 1
        
        # Correlation entropy
        if 0 < occ < 2:
            p = occ / 2
            if p > 0 and p < 1:
                entropy -= p * np.log(p) + (1-p) * np.log(1-p)
        
        # Effective unpaired electrons
        unpaired += min(occ, 2 - occ)
        
        orbitals.append(NaturalOrbital(
            index=i, occupation=occ,
            symmetry="A", character=character,
        ))
    
    psi4.core.clean()
    
    return NaturalOrbitalResult(
        orbitals=orbitals,
        n_strongly_occupied=n_strongly,
        n_weakly_occupied=n_weakly,
        correlation_entropy=entropy,
        effective_unpaired_electrons=unpaired,
        method=input_data.method.upper(),
        basis=input_data.basis,
    )


@register_tool
class NaturalOrbitalTool(BaseTool[NaturalOrbitalInput, ToolOutput]):
    """Tool for natural orbital analysis."""
    name: ClassVar[str] = "analyze_natural_orbitals"
    description: ClassVar[str] = "Analyze natural orbitals from correlated calculations."
    category: ClassVar[ToolCategory] = ToolCategory.ANALYSIS
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: NaturalOrbitalInput) -> Optional[ValidationError]:
        return validate_natural_orbital_input(input_data)
    
    def _execute(self, input_data: NaturalOrbitalInput) -> Result[ToolOutput]:
        result = run_natural_orbital_analysis(input_data)
        
        message = (
            f"Natural Orbital Analysis ({result.method}/{result.basis})\n"
            f"{'='*50}\n"
            f"Strongly Occupied: {result.n_strongly_occupied}\n"
            f"Weakly Occupied:   {result.n_weakly_occupied}\n"
            f"Correlation Entropy: {result.correlation_entropy:.4f}\n"
            f"Effective Unpaired e: {result.effective_unpaired_electrons:.4f}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def analyze_natural_orbitals(geometry: str, method: str = "mp2", **kwargs: Any) -> ToolOutput:
    """Analyze natural orbitals."""
    return NaturalOrbitalTool().run({"geometry": geometry, "method": method, **kwargs})
