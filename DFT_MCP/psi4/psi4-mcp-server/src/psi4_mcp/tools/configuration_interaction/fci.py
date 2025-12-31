"""
Full Configuration Interaction (FCI) Tool.

FCI includes all possible excitations within a given active space,
providing the exact solution for that orbital space.

Key Features:
    - Exact correlation within active space
    - Multiple roots for excited states
    - Size-extensive within active space
    - Benchmark for other methods

Reference:
    Knowles, P.J.; Handy, N.C. Chem. Phys. Lett. 1984, 111, 315.
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
class FCIRoot:
    """Information for a single FCI root."""
    root_number: int
    total_energy: float
    excitation_energy: float
    spin: float
    multiplicity: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_number": self.root_number,
            "total_energy_hartree": self.total_energy,
            "excitation_energy_ev": self.excitation_energy * HARTREE_TO_EV,
            "spin": self.spin,
            "multiplicity": self.multiplicity,
        }


@dataclass
class FCIResult:
    """Complete FCI calculation results."""
    roots: List[FCIRoot]
    ground_state_energy: float
    correlation_energy: float
    hf_energy: float
    n_electrons: int
    n_orbitals: int
    n_determinants: int
    active_electrons: int
    active_orbitals: int
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "roots": [r.to_dict() for r in self.roots],
            "ground_state_energy_hartree": self.ground_state_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "hf_energy_hartree": self.hf_energy,
            "n_electrons": self.n_electrons,
            "n_orbitals": self.n_orbitals,
            "n_determinants": self.n_determinants,
            "active_electrons": self.active_electrons,
            "active_orbitals": self.active_orbitals,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class FCIInput(ToolInput):
    """Input schema for FCI calculation."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ format")
    basis: str = Field(default="cc-pvdz", description="Basis set (use small for FCI)")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    active_electrons: Optional[int] = Field(
        default=None,
        description="Number of active electrons (None = all valence)",
    )
    
    active_orbitals: Optional[int] = Field(
        default=None,
        description="Number of active orbitals (None = all)",
    )
    
    n_roots: int = Field(default=1, description="Number of FCI roots")
    
    convergence: float = Field(default=1e-10, description="Energy convergence")
    max_iterations: int = Field(default=100)
    
    memory: int = Field(default=8000, description="Memory in MB (FCI needs more)")
    n_threads: int = Field(default=1)


# =============================================================================
# VALIDATION
# =============================================================================

def validate_fci_input(input_data: FCIInput) -> Optional[ValidationError]:
    """Validate FCI input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    if input_data.active_orbitals and input_data.active_orbitals > 14:
        return ValidationError(
            field="active_orbitals",
            message="FCI with >14 active orbitals is typically intractable",
        )
    
    return None


# =============================================================================
# FCI COMPUTATION
# =============================================================================

def estimate_n_determinants(n_electrons: int, n_orbitals: int) -> int:
    """Estimate number of determinants for FCI."""
    from math import comb
    
    n_alpha = n_electrons // 2 + n_electrons % 2
    n_beta = n_electrons // 2
    
    return comb(n_orbitals, n_alpha) * comb(n_orbitals, n_beta)


def run_fci_calculation(input_data: FCIInput) -> FCIResult:
    """Execute FCI calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_fci.out", False)
    
    # Build molecule
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    # Set options
    options = {
        "basis": input_data.basis,
        "fci": True,
        "num_roots": input_data.n_roots,
        "e_convergence": input_data.convergence,
        "ci_maxiter": input_data.max_iterations,
    }
    
    if input_data.multiplicity > 1:
        options["reference"] = "rohf"
    
    # Active space
    if input_data.active_orbitals:
        options["active"] = [input_data.active_orbitals]
    if input_data.active_electrons:
        options["restricted_docc"] = [(mol.nelectron() - input_data.active_electrons) // 2]
    
    psi4.set_options(options)
    
    logger.info(f"Running FCI/{input_data.basis}")
    
    # Run HF first
    hf_energy, hf_wfn = psi4.energy("hf", return_wfn=True, molecule=mol)
    
    # Run FCI
    fci_energy, fci_wfn = psi4.energy("fci", ref_wfn=hf_wfn, return_wfn=True, molecule=mol)
    
    # Get info
    n_electrons = mol.nelectron()
    n_orbitals = fci_wfn.nmo()
    
    active_e = input_data.active_electrons or n_electrons
    active_o = input_data.active_orbitals or n_orbitals
    
    n_determinants = estimate_n_determinants(active_e, active_o)
    
    # Build roots list
    roots = []
    ground_energy = fci_energy
    
    for i in range(input_data.n_roots):
        root_energy = psi4.variable(f"CI ROOT {i} TOTAL ENERGY")
        if root_energy == 0 and i == 0:
            root_energy = fci_energy
        
        if i == 0:
            ground_energy = root_energy
        
        excitation = root_energy - ground_energy
        
        roots.append(FCIRoot(
            root_number=i,
            total_energy=root_energy,
            excitation_energy=excitation,
            spin=(input_data.multiplicity - 1) / 2,
            multiplicity=input_data.multiplicity,
        ))
    
    correlation_energy = ground_energy - hf_energy
    
    psi4.core.clean()
    
    return FCIResult(
        roots=roots,
        ground_state_energy=ground_energy,
        correlation_energy=correlation_energy,
        hf_energy=hf_energy,
        n_electrons=n_electrons,
        n_orbitals=n_orbitals,
        n_determinants=n_determinants,
        active_electrons=active_e,
        active_orbitals=active_o,
        basis=input_data.basis,
    )


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class FCITool(BaseTool[FCIInput, ToolOutput]):
    """Tool for Full Configuration Interaction calculations."""
    
    name: ClassVar[str] = "calculate_fci"
    description: ClassVar[str] = (
        "Calculate Full Configuration Interaction (FCI) - exact solution within active space."
    )
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: FCIInput) -> Optional[ValidationError]:
        return validate_fci_input(input_data)
    
    def _execute(self, input_data: FCIInput) -> Result[ToolOutput]:
        result = run_fci_calculation(input_data)
        
        root_lines = []
        for r in result.roots:
            if r.root_number == 0:
                root_lines.append(f"  Root {r.root_number}: {r.total_energy:16.10f} Eh (ground state)")
            else:
                root_lines.append(f"  Root {r.root_number}: {r.total_energy:16.10f} Eh ({r.excitation_energy * HARTREE_TO_EV:.4f} eV)")
        
        message = (
            f"FCI/{input_data.basis} Calculation\n"
            f"{'='*50}\n"
            f"Active Space: ({result.active_electrons}e, {result.active_orbitals}o)\n"
            f"N Determinants: {result.n_determinants}\n"
            f"{'='*50}\n"
            f"HF Energy:          {result.hf_energy:16.10f} Eh\n"
            f"Correlation Energy: {result.correlation_energy:16.10f} Eh\n"
            f"                    {result.correlation_energy * HARTREE_TO_KCAL:16.4f} kcal/mol\n"
            f"{'='*50}\n"
            f"Roots:\n" + "\n".join(root_lines)
        )
        
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_fci(
    geometry: str,
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    active_electrons: Optional[int] = None,
    active_orbitals: Optional[int] = None,
    n_roots: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate Full CI energy."""
    tool = FCITool()
    return tool.run({
        "geometry": geometry, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "active_electrons": active_electrons,
        "active_orbitals": active_orbitals,
        "n_roots": n_roots, **kwargs,
    })
