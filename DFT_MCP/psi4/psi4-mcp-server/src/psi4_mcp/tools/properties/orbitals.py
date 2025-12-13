"""
Orbitals Tool.

MCP tool for computing orbital properties (HOMO, LUMO, etc.).
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class OrbitalsToolInput(ToolInput):
    """Input schema for orbital calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    n_orbitals: int = Field(default=5, description="Number of orbitals around HOMO/LUMO")
    memory: int = Field(default=2000, description="Memory limit in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class OrbitalsTool(BaseTool[OrbitalsToolInput, ToolOutput]):
    """MCP tool for orbital properties calculations."""
    
    name: ClassVar[str] = "calculate_orbitals"
    description: ClassVar[str] = (
        "Calculate orbital properties including HOMO-LUMO gap, "
        "orbital energies, and occupations."
    )
    category: ClassVar[ToolCategory] = ToolCategory.PROPERTIES
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "geometry": {"type": "string", "description": "Molecular geometry"},
            "method": {"type": "string", "default": "hf"},
            "basis": {"type": "string", "default": "cc-pvdz"},
            "n_orbitals": {"type": "integer", "default": 5},
        }
    
    def _execute(self, input_data: OrbitalsToolInput) -> Result[ToolOutput]:
        try:
            from psi4_mcp.services.psi4_interface import get_psi4_interface
            
            psi4 = get_psi4_interface()
            psi4.initialize(memory=input_data.memory, n_threads=input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            mol_result = psi4.create_molecule(mol_string)
            if mol_result.is_failure:
                return Result.failure(mol_result.error)
            
            molecule = mol_result.value
            psi4.set_options({"basis": input_data.basis})
            
            energy_result = psi4.energy(input_data.method, molecule=molecule, return_wfn=True)
            if energy_result.is_failure:
                return Result.failure(energy_result.error)
            
            energy, wfn = energy_result.value
            
            # Extract orbital info
            n_alpha = wfn.nalpha()
            n_beta = wfn.nbeta()
            epsilon_a = wfn.epsilon_a()
            
            homo_idx = n_alpha - 1
            lumo_idx = n_alpha
            
            homo_energy = epsilon_a.get(homo_idx) if homo_idx >= 0 else None
            lumo_energy = epsilon_a.get(lumo_idx) if lumo_idx < epsilon_a.dim() else None
            
            gap = (lumo_energy - homo_energy) if homo_energy and lumo_energy else None
            
            # Get range of orbital energies
            orb_energies = []
            start_idx = max(0, homo_idx - input_data.n_orbitals)
            end_idx = min(epsilon_a.dim(), lumo_idx + input_data.n_orbitals)
            
            for i in range(start_idx, end_idx):
                orb_energies.append({
                    "index": i,
                    "energy_hartree": epsilon_a.get(i),
                    "energy_eV": epsilon_a.get(i) * 27.2114,
                    "occupation": 2 if i < n_alpha else 0,
                    "type": "occupied" if i < n_alpha else "virtual",
                })
            
            data = {
                "energy": energy,
                "n_alpha": n_alpha,
                "n_beta": n_beta,
                "n_basis": wfn.nso(),
                "homo_index": homo_idx,
                "lumo_index": lumo_idx,
                "homo_energy_hartree": homo_energy,
                "lumo_energy_hartree": lumo_energy,
                "homo_lumo_gap_hartree": gap,
                "homo_lumo_gap_eV": gap * 27.2114 if gap else None,
                "orbital_energies": orb_energies,
            }
            
            message = (
                f"Orbital analysis complete\n"
                f"HOMO ({homo_idx}): {homo_energy:.4f} Hartree\n"
                f"LUMO ({lumo_idx}): {lumo_energy:.4f} Hartree\n"
                f"Gap: {gap * 27.2114:.2f} eV" if gap else ""
            )
            
            psi4.clean()
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("Orbital calculation failed")
            return Result.failure(CalculationError(code="ORBITAL_ERROR", message=str(e)))


def calculate_orbitals(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    n_orbitals: int = 5,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate orbital properties."""
    tool = OrbitalsTool()
    return tool.run({
        "geometry": geometry, "method": method, "basis": basis,
        "charge": charge, "multiplicity": multiplicity,
        "n_orbitals": n_orbitals, **kwargs
    })
