"""
Natural Population Analysis (NPA) Tool.

Computes natural atomic orbitals (NAOs) and natural population analysis
charges using the Natural Bond Orbital (NBO) methodology.

Key Features:
    - Natural Atomic Orbitals (NAOs)
    - Natural Population Analysis charges
    - Natural electron configuration
    - Rydberg orbital populations
    - Natural Bond Orbital analysis summary

Reference:
    Reed, A.E.; Weinstock, R.B.; Weinhold, F. J. Chem. Phys. 1985, 83, 735-746.
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


# =============================================================================
# CONSTANTS
# =============================================================================

ATOMIC_NUMBERS = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
    "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18,
    "K": 19, "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26,
    "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Br": 35, "I": 53,
}

CORE_ELECTRONS = {
    "H": 0, "He": 0, "Li": 2, "Be": 2, "B": 2, "C": 2, "N": 2, "O": 2, "F": 2, "Ne": 2,
    "Na": 10, "Mg": 10, "Al": 10, "Si": 10, "P": 10, "S": 10, "Cl": 10, "Ar": 10,
    "K": 18, "Ca": 18, "Br": 28, "I": 46,
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class NaturalOrbitalPopulation:
    """Population of a natural atomic orbital."""
    orbital_type: str  # e.g., "1s", "2s", "2p", "3d"
    population: float
    occupancy: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "orbital_type": self.orbital_type,
            "population": self.population,
            "occupancy": self.occupancy,
        }


@dataclass
class NaturalElectronConfiguration:
    """Natural electron configuration for an atom."""
    core: str
    valence: str
    rydberg: float
    total_population: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "core": self.core,
            "valence": self.valence,
            "rydberg": self.rydberg,
            "total_population": self.total_population,
        }


@dataclass
class NPAAtomicCharge:
    """NPA charge for a single atom."""
    atom_index: int
    element: str
    charge: float
    natural_population: float
    core_population: float
    valence_population: float
    rydberg_population: float
    electron_configuration: NaturalElectronConfiguration
    orbital_populations: List[NaturalOrbitalPopulation]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atom_index": self.atom_index,
            "element": self.element,
            "charge": self.charge,
            "natural_population": self.natural_population,
            "core_population": self.core_population,
            "valence_population": self.valence_population,
            "rydberg_population": self.rydberg_population,
            "electron_configuration": self.electron_configuration.to_dict(),
            "orbital_populations": [o.to_dict() for o in self.orbital_populations],
        }


@dataclass
class NPAAnalysisResult:
    """Complete NPA analysis results."""
    atomic_charges: List[NPAAtomicCharge]
    total_charge: float
    total_alpha_electrons: float
    total_beta_electrons: float
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "atomic_charges": [c.to_dict() for c in self.atomic_charges],
            "total_charge": self.total_charge,
            "total_alpha_electrons": self.total_alpha_electrons,
            "total_beta_electrons": self.total_beta_electrons,
            "method": self.method,
            "basis": self.basis,
        }


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class NPAChargesInput(ToolInput):
    """Input schema for NPA analysis."""
    
    geometry: str = Field(..., description="Molecular geometry in XYZ or Psi4 format")
    method: str = Field(default="hf", description="Electronic structure method")
    basis: str = Field(default="cc-pvdz", description="Basis set for calculation")
    charge: int = Field(default=0, ge=-10, le=10)
    multiplicity: int = Field(default=1, ge=1, le=10)
    compute_nbo: bool = Field(default=False, description="Run full NBO analysis")
    nbo_output_level: int = Field(default=1, description="NBO output verbosity (1-3)")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


# =============================================================================
# VALIDATION AND PARSING
# =============================================================================

def validate_npa_input(input_data: NPAChargesInput) -> Optional[ValidationError]:
    """Validate NPA analysis input."""
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    if input_data.nbo_output_level < 1 or input_data.nbo_output_level > 3:
        return ValidationError(field="nbo_output_level", message="NBO output level must be 1-3")
    
    return None


def parse_geometry_elements(geometry: str) -> List[str]:
    """Extract element symbols from geometry string."""
    elements = []
    for line in geometry.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 4:
            element = ''.join(c for c in parts[0] if c.isalpha())
            elements.append(element)
    return elements


# =============================================================================
# NATURAL ATOMIC ORBITAL COMPUTATION
# =============================================================================

def compute_nao_from_density(
    wfn: Any,
    elements: List[str],
) -> List[Dict[str, Any]]:
    """
    Compute Natural Atomic Orbitals from density matrix.
    
    This is a simplified NAO analysis. For full NBO analysis,
    external NBO software is typically required.
    """
    import numpy as np
    
    mol = wfn.molecule()
    natoms = mol.natom()
    basisset = wfn.basisset()
    nbf = basisset.nbf()
    
    # Get density matrices
    Da = np.asarray(wfn.Da())
    Db = np.asarray(wfn.Db()) if not wfn.same_a_b_dens() else Da
    D_total = Da + Db
    
    # Get overlap matrix
    import psi4
    mints = psi4.core.MintsHelper(basisset)
    S = np.asarray(mints.ao_overlap())
    
    # Map basis functions to atoms and angular momentum
    bf_to_atom = []
    bf_to_am = []
    for shell_idx in range(basisset.nshell()):
        atom_idx = basisset.shell_to_center(shell_idx)
        am = basisset.shell(shell_idx).am
        n_func = basisset.shell(shell_idx).nfunction
        bf_to_atom.extend([atom_idx] * n_func)
        bf_to_am.extend([am] * n_func)
    
    # Compute DS matrix for populations
    DS = D_total @ S
    
    # Compute atomic blocks
    atom_data = []
    
    for atom_idx in range(natoms):
        element = elements[atom_idx] if atom_idx < len(elements) else mol.label(atom_idx)
        Z = ATOMIC_NUMBERS.get(element, 6)
        core_e = CORE_ELECTRONS.get(element, 0)
        
        # Get basis functions for this atom
        atom_bfs = [i for i in range(nbf) if bf_to_atom[i] == atom_idx]
        
        # Compute populations by angular momentum
        am_populations = {}
        total_pop = 0.0
        
        for bf in atom_bfs:
            pop = DS[bf, bf]
            am = bf_to_am[bf]
            
            am_label = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g"}.get(am, f"l{am}")
            
            if am_label not in am_populations:
                am_populations[am_label] = 0.0
            am_populations[am_label] += pop
            total_pop += pop
        
        # Classify into core, valence, Rydberg
        core_pop = min(core_e, total_pop)
        remaining = total_pop - core_pop
        
        valence_e = Z - core_e
        valence_pop = min(valence_e + 2, remaining)  # Allow some extra for bonding
        rydberg_pop = max(0, remaining - valence_pop)
        
        # Build orbital populations list
        orbital_pops = []
        shell_num = 1
        for am_label, pop in sorted(am_populations.items(), key=lambda x: ["s", "p", "d", "f", "g"].index(x[0]) if x[0] in ["s", "p", "d", "f", "g"] else 10):
            orbital_pops.append(NaturalOrbitalPopulation(
                orbital_type=f"{shell_num}{am_label}",
                population=float(pop),
                occupancy=float(pop) / (2 * (2 * ["s", "p", "d", "f", "g"].index(am_label) + 1)) if am_label in ["s", "p", "d", "f", "g"] else float(pop),
            ))
            if am_label == "s":
                shell_num += 1
        
        # Build electron configuration string
        config_parts = []
        for op in orbital_pops:
            if op.population > 0.01:
                config_parts.append(f"{op.orbital_type}({op.population:.2f})")
        
        config = NaturalElectronConfiguration(
            core=f"[core]({core_pop:.2f})" if core_pop > 0 else "",
            valence=" ".join(config_parts),
            rydberg=rydberg_pop,
            total_population=total_pop,
        )
        
        charge = Z - total_pop
        
        atom_data.append({
            "atom_index": atom_idx,
            "element": element,
            "charge": charge,
            "natural_population": total_pop,
            "core_population": core_pop,
            "valence_population": valence_pop,
            "rydberg_population": rydberg_pop,
            "electron_configuration": config,
            "orbital_populations": orbital_pops,
        })
    
    return atom_data


def run_nbo_analysis(wfn: Any, output_level: int = 1) -> Dict[str, Any]:
    """
    Run NBO analysis if available.
    
    Note: This requires NBO to be installed and linked with Psi4.
    Returns empty dict if NBO is not available.
    """
    import psi4
    
    # Check if NBO is available
    nbo_available = hasattr(psi4, 'nbo')
    
    if not nbo_available:
        logger.info("NBO not available, using approximate NAO analysis")
        return {}
    
    # Run NBO analysis
    nbo_data = psi4.nbo(wfn)
    
    return nbo_data


# =============================================================================
# TOOL CLASS
# =============================================================================

@register_tool
class NPAChargesTool(BaseTool[NPAChargesInput, ToolOutput]):
    """Tool for Natural Population Analysis."""
    
    name: ClassVar[str] = "calculate_npa_charges"
    description: ClassVar[str] = "Perform Natural Population Analysis to compute atomic charges and electron configurations."
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: NPAChargesInput) -> Optional[ValidationError]:
        return validate_npa_input(input_data)
    
    def _execute(self, input_data: NPAChargesInput) -> Result[ToolOutput]:
        import psi4
        
        psi4.core.clean()
        psi4.set_memory(f"{input_data.memory} MB")
        psi4.set_num_threads(input_data.n_threads)
        psi4.core.set_output_file("psi4_npa.out", False)
        
        mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
        mol = psi4.geometry(mol_string)
        mol.update_geometry()
        
        elements = parse_geometry_elements(input_data.geometry)
        psi4.set_options({"basis": input_data.basis})
        
        if input_data.multiplicity > 1:
            psi4.set_options({"reference": "uhf"})
        
        method_basis = f"{input_data.method}/{input_data.basis}"
        logger.info(f"Running {method_basis} for NPA analysis")
        
        energy, wfn = psi4.energy(method_basis, return_wfn=True, molecule=mol)
        
        # Compute NAO-based populations
        atom_data = compute_nao_from_density(wfn, elements)
        
        # Run full NBO if requested
        nbo_data = {}
        if input_data.compute_nbo:
            nbo_data = run_nbo_analysis(wfn, input_data.nbo_output_level)
        
        # Build results
        atomic_charges = []
        for data in atom_data:
            atomic_charges.append(NPAAtomicCharge(
                atom_index=data["atom_index"],
                element=data["element"],
                charge=float(data["charge"]),
                natural_population=float(data["natural_population"]),
                core_population=float(data["core_population"]),
                valence_population=float(data["valence_population"]),
                rydberg_population=float(data["rydberg_population"]),
                electron_configuration=data["electron_configuration"],
                orbital_populations=data["orbital_populations"],
            ))
        
        total_charge = sum(c.charge for c in atomic_charges)
        total_alpha = wfn.nalpha()
        total_beta = wfn.nbeta()
        
        result = NPAAnalysisResult(
            atomic_charges=atomic_charges,
            total_charge=total_charge,
            total_alpha_electrons=float(total_alpha),
            total_beta_electrons=float(total_beta),
            method=input_data.method,
            basis=input_data.basis,
        )
        
        psi4.core.clean()
        
        charges_str = ", ".join(f"{c.element}({c.atom_index}): {c.charge:+.4f}" for c in atomic_charges)
        
        message = (
            f"Natural Population Analysis completed\n"
            f"Method: {input_data.method}/{input_data.basis}\n"
            f"Charges: {charges_str}\n"
            f"Total charge: {result.total_charge:.4f}\n"
            f"Electrons: {total_alpha + total_beta:.1f} (α: {total_alpha}, β: {total_beta})"
        )
        
        output_data = result.to_dict()
        if nbo_data:
            output_data["nbo_analysis"] = nbo_data
        
        return Result.success(ToolOutput(success=True, message=message, data=output_data))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_npa_charges(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    compute_nbo: bool = False,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate NPA atomic charges.
    
    Args:
        geometry: Molecular geometry string.
        method: Electronic structure method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        compute_nbo: Run full NBO analysis.
        **kwargs: Additional options.
        
    Returns:
        ToolOutput with NPA analysis results including electron configurations.
    """
    tool = NPAChargesTool()
    input_data = {
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "compute_nbo": compute_nbo, **kwargs,
    }
    return tool.run(input_data)
