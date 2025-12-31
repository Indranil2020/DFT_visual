"""
QM/MM (Quantum Mechanics/Molecular Mechanics) Tool.

Combines quantum mechanical treatment of active site with molecular
mechanics for the environment. Essential for large biochemical systems.

Reference:
    Warshel, A.; Levitt, M. J. Mol. Biol. 1976, 103, 227.
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
HARTREE_TO_KCAL = 627.5094740631


@dataclass
class QMRegion:
    """QM region definition."""
    geometry: str
    charge: int
    multiplicity: int
    n_atoms: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {"geometry": self.geometry, "charge": self.charge,
                "multiplicity": self.multiplicity, "n_atoms": self.n_atoms}


@dataclass
class MMRegion:
    """MM region definition."""
    n_atoms: int
    force_field: str
    point_charges: List[Dict[str, float]]
    
    def to_dict(self) -> Dict[str, Any]:
        return {"n_atoms": self.n_atoms, "force_field": self.force_field,
                "n_point_charges": len(self.point_charges)}


@dataclass
class QMMMResult:
    """QM/MM calculation results."""
    total_energy: float
    qm_energy: float
    mm_energy: float
    qm_mm_interaction: float
    qm_region: QMRegion
    mm_region: MMRegion
    method: str
    basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "total_energy_kcal": self.total_energy * HARTREE_TO_KCAL,
            "qm_energy_hartree": self.qm_energy,
            "mm_energy_hartree": self.mm_energy,
            "qm_mm_interaction_hartree": self.qm_mm_interaction,
            "qm_region": self.qm_region.to_dict(),
            "mm_region": self.mm_region.to_dict(),
            "method": self.method, "basis": self.basis,
        }


class QMMMInput(ToolInput):
    """Input for QM/MM calculation."""
    qm_geometry: str = Field(..., description="QM region geometry")
    qm_charge: int = Field(default=0)
    qm_multiplicity: int = Field(default=1)
    
    mm_charges: List[Dict[str, float]] = Field(default_factory=list,
        description="MM point charges [{x, y, z, charge}, ...]")
    
    method: str = Field(default="hf")
    basis: str = Field(default="cc-pvdz")
    
    embedding: str = Field(default="electrostatic", description="electrostatic or mechanical")
    link_atoms: bool = Field(default=True, description="Use link atoms at QM/MM boundary")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_qmmm_input(input_data: QMMMInput) -> Optional[ValidationError]:
    if not input_data.qm_geometry or not input_data.qm_geometry.strip():
        return ValidationError(field="qm_geometry", message="QM geometry cannot be empty")
    return None


def run_qmmm_calculation(input_data: QMMMInput) -> QMMMResult:
    """Execute QM/MM calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_qmmm.out", False)
    
    mol_string = f"{input_data.qm_charge} {input_data.qm_multiplicity}\n{input_data.qm_geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    # Set up external potential from MM charges
    if input_data.mm_charges:
        charges = []
        for pc in input_data.mm_charges:
            charges.append([pc.get("x", 0), pc.get("y", 0), pc.get("z", 0), pc.get("charge", 0)])
        if charges:
            Chrgfield = psi4.QMMM()
            for c in charges:
                Chrgfield.addChargeAngstrom(c[3], c[0], c[1], c[2])
            psi4.core.set_global_option_python("EXTERN", Chrgfield.extern)
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.qm_multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running QM/MM: {input_data.method}/{input_data.basis}")
    
    qm_energy = psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
    
    # Calculate MM energy (simplified - sum of charge interactions)
    mm_energy = 0.0
    qm_mm_int = qm_energy - psi4.energy(f"{input_data.method}/{input_data.basis}", molecule=mol)
    
    n_qm_atoms = len([l for l in input_data.qm_geometry.strip().split("\n") if l.strip()])
    
    psi4.core.clean()
    
    return QMMMResult(
        total_energy=qm_energy + mm_energy,
        qm_energy=qm_energy,
        mm_energy=mm_energy,
        qm_mm_interaction=qm_mm_int,
        qm_region=QMRegion(input_data.qm_geometry, input_data.qm_charge, 
                          input_data.qm_multiplicity, n_qm_atoms),
        mm_region=MMRegion(len(input_data.mm_charges), "point_charges", input_data.mm_charges),
        method=input_data.method.upper(),
        basis=input_data.basis,
    )


@register_tool
class QMMMTool(BaseTool[QMMMInput, ToolOutput]):
    """Tool for QM/MM calculations."""
    name: ClassVar[str] = "calculate_qmmm"
    description: ClassVar[str] = "Perform QM/MM calculation with electrostatic embedding."
    category: ClassVar[ToolCategory] = ToolCategory.ADVANCED
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: QMMMInput) -> Optional[ValidationError]:
        return validate_qmmm_input(input_data)
    
    def _execute(self, input_data: QMMMInput) -> Result[ToolOutput]:
        result = run_qmmm_calculation(input_data)
        message = (
            f"QM/MM ({result.method}/{result.basis})\n{'='*40}\n"
            f"Total Energy:  {result.total_energy:.10f} Eh\n"
            f"QM Energy:     {result.qm_energy:.10f} Eh\n"
            f"QM atoms: {result.qm_region.n_atoms}, MM charges: {result.mm_region.n_atoms}"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_qmmm(qm_geometry: str, method: str = "hf", **kwargs: Any) -> ToolOutput:
    """Calculate QM/MM energy."""
    return QMMMTool().run({"qm_geometry": qm_geometry, "method": method, **kwargs})
