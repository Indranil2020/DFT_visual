"""
Configuration Interaction Singles, Doubles, and Triples (CISDT) Tool.

CISDT extends CISD by including triple excitations, providing
improved accuracy for systems with significant triple contributions.

Key Features:
    - Single, double, and triple excitations
    - Improved correlation recovery
    - Higher accuracy than CISD
    - Computationally more demanding

Reference:
    Laidig, W.D.; Bartlett, R.J. Chem. Phys. Lett. 1984, 104, 424.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
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


HARTREE_TO_EV = 27.211386245988
HARTREE_TO_KCAL = 627.5094740631


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class CISDTResult:
    """Complete CISDT calculation results."""
    total_energy: float
    correlation_energy: float
    hf_energy: float
    cisd_energy: float
    triples_contribution: float
    n_determinants: int
    t1_diagnostic: float
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "hf_energy_hartree": self.hf_energy,
            "cisd_energy_hartree": self.cisd_energy,
            "triples_contribution_hartree": self.triples_contribution,
            "triples_contribution_kcal": self.triples_contribution * HARTREE_TO_KCAL,
            "n_determinants": self.n_determinants,
            "t1_diagnostic": self.t1_diagnostic,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class CISDTInput(ToolInput):
    """Input schema for CISDT calculation."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ format")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    freeze_core: bool = Field(default=True, description="Freeze core orbitals")
    n_roots: int = Field(default=1, description="Number of CI roots")
    
    convergence: float = Field(default=1e-8, description="Energy convergence")
    max_iterations: int = Field(default=100)
    
    memory: int = Field(default=8000, description="Memory (CISDT needs more)")
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_cisdt_input(input_data: CISDTInput) -> Optional[ValidationError]:
    """Validate CISDT input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


# =============================================================================
# CISDT COMPUTATION
# =============================================================================

def estimate_cisdt_determinants(n_occ: int, n_vir: int) -> int:
    """Estimate number of determinants for CISDT."""
    from math import comb
    
    n_det = 1
    n_det += n_occ * n_vir
    n_det += comb(n_occ, 2) * comb(n_vir, 2)
    n_det += comb(n_occ, 3) * comb(n_vir, 3)
    
    return n_det


def run_cisdt_calculation(input_data: CISDTInput) -> CISDTResult:
    """Execute CISDT calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_cisdt.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    options = {
        "basis": input_data.basis,
        "freeze_core": input_data.freeze_core,
        "ex_level": 3,
        "num_roots": input_data.n_roots,
        "e_convergence": input_data.convergence,
        "ci_maxiter": input_data.max_iterations,
    }
    
    if input_data.multiplicity > 1:
        options["reference"] = "rohf"
    
    psi4.set_options(options)
    
    logger.info(f"Running CISDT/{input_data.basis}")
    
    hf_energy, hf_wfn = psi4.energy("hf", return_wfn=True, molecule=mol)
    
    psi4.set_options({"ex_level": 2})
    cisd_energy = psi4.energy("detci", ref_wfn=hf_wfn, molecule=mol)
    
    psi4.set_options({"ex_level": 3})
    cisdt_energy, cisdt_wfn = psi4.energy("detci", ref_wfn=hf_wfn, return_wfn=True, molecule=mol)
    
    correlation_energy = cisdt_energy - hf_energy
    triples_contribution = cisdt_energy - cisd_energy
    
    n_occ = cisdt_wfn.nalpha()
    n_vir = cisdt_wfn.nmo() - n_occ
    n_determinants = estimate_cisdt_determinants(n_occ, n_vir)
    
    t1_diagnostic = abs(correlation_energy) / (n_occ * 2)
    
    psi4.core.clean()
    
    return CISDTResult(
        total_energy=cisdt_energy,
        correlation_energy=correlation_energy,
        hf_energy=hf_energy,
        cisd_energy=cisd_energy,
        triples_contribution=triples_contribution,
        n_determinants=n_determinants,
        t1_diagnostic=t1_diagnostic,
        basis=input_data.basis,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class CISDTTool(BaseTool[CISDTInput, ToolOutput]):
    """Tool for CISDT calculations."""
    
    name: ClassVar[str] = "calculate_cisdt"
    description: ClassVar[str] = "Calculate CISDT energy with triple excitations."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: CISDTInput) -> Optional[ValidationError]:
        return validate_cisdt_input(input_data)
    
    def _execute(self, input_data: CISDTInput) -> Result[ToolOutput]:
        result = run_cisdt_calculation(input_data)
        
        message = (
            f"CISDT/{input_data.basis} Calculation\n"
            f"{'='*50}\n"
            f"Total Energy:       {result.total_energy:16.10f} Eh\n"
            f"HF Energy:          {result.hf_energy:16.10f} Eh\n"
            f"CISD Energy:        {result.cisd_energy:16.10f} Eh\n"
            f"Correlation:        {result.correlation_energy:16.10f} Eh\n"
            f"Triples:            {result.triples_contribution:16.10f} Eh\n"
            f"N Determinants:     ~{result.n_determinants}"
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_cisdt(
    geometry: str,
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    freeze_core: bool = True,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate CISDT energy."""
    tool = CISDTTool()
    return tool.run({
        "geometry": geometry, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "freeze_core": freeze_core, **kwargs,
    })
