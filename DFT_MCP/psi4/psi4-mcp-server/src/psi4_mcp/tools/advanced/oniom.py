"""
ONIOM (Our own N-layered Integrated molecular Orbital and Molecular mechanics) Tool.

Multi-layer method for large systems combining different levels of theory.

Reference:
    Dapprich, S. et al. J. Mol. Struct. THEOCHEM 1999, 461-462, 1.
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
class ONIOMLayer:
    """ONIOM layer definition."""
    name: str
    geometry: str
    method: str
    basis: str
    energy: float
    n_atoms: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "method": self.method, "basis": self.basis,
                "energy_hartree": self.energy, "n_atoms": self.n_atoms}


@dataclass
class ONIOMResult:
    """ONIOM calculation results."""
    total_energy: float
    layers: List[ONIOMLayer]
    extrapolated_energy: float
    high_level_contribution: float
    low_level_contribution: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "total_energy_kcal": self.total_energy * HARTREE_TO_KCAL,
            "layers": [l.to_dict() for l in self.layers],
            "extrapolated_energy_hartree": self.extrapolated_energy,
            "high_level_contribution_hartree": self.high_level_contribution,
            "low_level_contribution_hartree": self.low_level_contribution,
        }


class ONIOMInput(ToolInput):
    """Input for ONIOM calculation."""
    model_geometry: str = Field(..., description="High-level model region")
    real_geometry: str = Field(..., description="Full system geometry")
    
    high_method: str = Field(default="mp2", description="High-level method")
    high_basis: str = Field(default="cc-pvdz")
    low_method: str = Field(default="hf", description="Low-level method")
    low_basis: str = Field(default="sto-3g")
    
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    link_atoms: bool = Field(default=True)
    link_atom_type: str = Field(default="H")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_oniom_input(input_data: ONIOMInput) -> Optional[ValidationError]:
    if not input_data.model_geometry or not input_data.model_geometry.strip():
        return ValidationError(field="model_geometry", message="Model geometry cannot be empty")
    if not input_data.real_geometry or not input_data.real_geometry.strip():
        return ValidationError(field="real_geometry", message="Real geometry cannot be empty")
    return None


def count_atoms(geometry: str) -> int:
    return len([l for l in geometry.strip().split("\n") if l.strip() and len(l.split()) >= 4])


def run_oniom_calculation(input_data: ONIOMInput) -> ONIOMResult:
    """Execute ONIOM calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_oniom.out", False)
    
    psi4.set_options({"reference": "rhf" if input_data.multiplicity == 1 else "uhf"})
    
    logger.info(f"Running ONIOM: {input_data.high_method}/{input_data.high_basis}:{input_data.low_method}/{input_data.low_basis}")
    
    # High level on model
    mol_model = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.model_geometry}")
    mol_model.update_geometry()
    psi4.set_options({"basis": input_data.high_basis})
    e_model_high = psi4.energy(f"{input_data.high_method}/{input_data.high_basis}", molecule=mol_model)
    
    # Low level on model
    psi4.set_options({"basis": input_data.low_basis})
    e_model_low = psi4.energy(f"{input_data.low_method}/{input_data.low_basis}", molecule=mol_model)
    
    # Low level on real
    mol_real = psi4.geometry(f"{input_data.charge} {input_data.multiplicity}\n{input_data.real_geometry}")
    mol_real.update_geometry()
    e_real_low = psi4.energy(f"{input_data.low_method}/{input_data.low_basis}", molecule=mol_real)
    
    # ONIOM extrapolation: E = E(real,low) + E(model,high) - E(model,low)
    e_oniom = e_real_low + e_model_high - e_model_low
    
    layers = [
        ONIOMLayer("model_high", input_data.model_geometry, input_data.high_method, 
                   input_data.high_basis, e_model_high, count_atoms(input_data.model_geometry)),
        ONIOMLayer("model_low", input_data.model_geometry, input_data.low_method,
                   input_data.low_basis, e_model_low, count_atoms(input_data.model_geometry)),
        ONIOMLayer("real_low", input_data.real_geometry, input_data.low_method,
                   input_data.low_basis, e_real_low, count_atoms(input_data.real_geometry)),
    ]
    
    psi4.core.clean()
    
    return ONIOMResult(
        total_energy=e_oniom,
        layers=layers,
        extrapolated_energy=e_oniom,
        high_level_contribution=e_model_high - e_model_low,
        low_level_contribution=e_real_low,
    )


@register_tool
class ONIOMTool(BaseTool[ONIOMInput, ToolOutput]):
    """Tool for ONIOM calculations."""
    name: ClassVar[str] = "calculate_oniom"
    description: ClassVar[str] = "Perform ONIOM multi-layer calculation."
    category: ClassVar[ToolCategory] = ToolCategory.ADVANCED
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: ONIOMInput) -> Optional[ValidationError]:
        return validate_oniom_input(input_data)
    
    def _execute(self, input_data: ONIOMInput) -> Result[ToolOutput]:
        result = run_oniom_calculation(input_data)
        message = (
            f"ONIOM({input_data.high_method}:{input_data.low_method})\n{'='*40}\n"
            f"Total Energy: {result.total_energy:.10f} Eh\n"
            f"High-level contrib: {result.high_level_contribution:.10f} Eh\n"
            f"Low-level contrib:  {result.low_level_contribution:.10f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_oniom(model_geometry: str, real_geometry: str, **kwargs: Any) -> ToolOutput:
    """Calculate ONIOM energy."""
    return ONIOMTool().run({"model_geometry": model_geometry, "real_geometry": real_geometry, **kwargs})
