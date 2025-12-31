"""
DFT Dispersion Correction Tool.

Computes and applies empirical dispersion corrections to DFT calculations
using various DFT-D schemes (D2, D3, D3BJ, D4).

Reference:
    Grimme, S. et al. J. Chem. Phys. 2010, 132, 154104.
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
class DispersionResult:
    """Dispersion correction results."""
    dft_energy: float
    dispersion_energy: float
    total_energy: float
    dispersion_method: str
    functional: str
    basis: str
    
    two_body_contribution: Optional[float] = None
    three_body_contribution: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dft_energy_hartree": self.dft_energy,
            "dispersion_energy_hartree": self.dispersion_energy,
            "dispersion_energy_kcal": self.dispersion_energy * HARTREE_TO_KCAL,
            "total_energy_hartree": self.total_energy,
            "dispersion_method": self.dispersion_method,
            "functional": self.functional,
            "basis": self.basis,
            "two_body_hartree": self.two_body_contribution,
            "three_body_hartree": self.three_body_contribution,
        }


class DispersionInput(ToolInput):
    """Input for dispersion calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    functional: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    dispersion_method: str = Field(
        default="d3bj",
        description="Dispersion method: d2, d3, d3bj, d3m, d3mbj, d4"
    )
    
    include_three_body: bool = Field(default=False, description="Include 3-body ATM term")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_dispersion_input(input_data: DispersionInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    
    valid_methods = ["d2", "d3", "d3bj", "d3m", "d3mbj", "d4"]
    if input_data.dispersion_method.lower() not in valid_methods:
        return ValidationError(
            field="dispersion_method",
            message=f"Invalid method. Use: {', '.join(valid_methods)}"
        )
    return None


def run_dispersion_calculation(input_data: DispersionInput) -> DispersionResult:
    """Execute DFT-D calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_dispersion.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    disp_method = input_data.dispersion_method.lower()
    
    # Build method string with dispersion
    if disp_method == "d2":
        method_string = f"{input_data.functional}-d2"
    elif disp_method == "d3":
        method_string = f"{input_data.functional}-d3"
    elif disp_method == "d3bj":
        method_string = f"{input_data.functional}-d3bj"
    elif disp_method == "d3m":
        method_string = f"{input_data.functional}-d3m"
    elif disp_method == "d3mbj":
        method_string = f"{input_data.functional}-d3mbj"
    else:  # d4
        method_string = f"{input_data.functional}-d4"
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    logger.info(f"Running {method_string}/{input_data.basis}")
    
    # Run DFT-D calculation
    total_energy = psi4.energy(f"{method_string}/{input_data.basis}", molecule=mol)
    
    # Get dispersion energy
    disp_energy = psi4.variable("DISPERSION CORRECTION ENERGY")
    
    # DFT energy without dispersion
    dft_energy = total_energy - disp_energy
    
    # Try to get two-body and three-body terms
    two_body = psi4.variable("2-BODY DISPERSION CORRECTION ENERGY")
    three_body = psi4.variable("3-BODY DISPERSION CORRECTION ENERGY") if input_data.include_three_body else None
    
    psi4.core.clean()
    
    return DispersionResult(
        dft_energy=dft_energy,
        dispersion_energy=disp_energy,
        total_energy=total_energy,
        dispersion_method=disp_method.upper(),
        functional=input_data.functional.upper(),
        basis=input_data.basis,
        two_body_contribution=two_body if two_body != 0 else None,
        three_body_contribution=three_body if three_body and three_body != 0 else None,
    )


@register_tool
class DispersionTool(BaseTool[DispersionInput, ToolOutput]):
    """Tool for DFT dispersion calculations."""
    name: ClassVar[str] = "calculate_dispersion"
    description: ClassVar[str] = "Calculate DFT energy with empirical dispersion correction."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: DispersionInput) -> Optional[ValidationError]:
        return validate_dispersion_input(input_data)
    
    def _execute(self, input_data: DispersionInput) -> Result[ToolOutput]:
        result = run_dispersion_calculation(input_data)
        
        message = (
            f"{result.functional}-{result.dispersion_method}/{input_data.basis}\n"
            f"{'='*50}\n"
            f"DFT Energy:        {result.dft_energy:16.10f} Eh\n"
            f"Dispersion:        {result.dispersion_energy:16.10f} Eh\n"
            f"                   {result.dispersion_energy * HARTREE_TO_KCAL:16.4f} kcal/mol\n"
            f"Total Energy:      {result.total_energy:16.10f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_dispersion(geometry: str, functional: str = "b3lyp", 
                         dispersion_method: str = "d3bj", **kwargs: Any) -> ToolOutput:
    """Calculate DFT-D energy."""
    return DispersionTool().run({
        "geometry": geometry, "functional": functional,
        "dispersion_method": dispersion_method, **kwargs,
    })
