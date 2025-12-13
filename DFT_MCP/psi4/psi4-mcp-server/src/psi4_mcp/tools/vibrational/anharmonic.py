"""
Anharmonic Correction Tool.

MCP tool for computing anharmonic corrections to vibrational
frequencies using VPT2 (second-order vibrational perturbation theory).

Key Functions:
    - calculate_anharmonic: Convenience function
    
Key Classes:
    - AnharmonicTool: MCP tool class
    - AnharmonicToolInput: Input schema
"""

from typing import Any, Optional, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool,
    ToolInput,
    ToolOutput,
    ToolCategory,
    register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class AnharmonicToolInput(ToolInput):
    """
    Input schema for anharmonic calculation tool.
    
    Attributes:
        geometry: Molecular geometry (XYZ or Psi4 format).
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        vpt2_level: VPT2 calculation level.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        options: Additional Psi4 options.
    """
    
    geometry: str = Field(
        ...,
        description="Molecular geometry in XYZ or Psi4 format",
    )
    
    method: str = Field(
        default="hf",
        description="Calculation method",
    )
    
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
    )
    
    charge: int = Field(
        default=0,
        description="Molecular charge",
    )
    
    multiplicity: int = Field(
        default=1,
        description="Spin multiplicity (2S+1)",
    )
    
    vpt2_level: str = Field(
        default="full",
        description="VPT2 calculation level",
        pattern="^(full|simple|deperturbed)$",
    )
    
    memory: int = Field(
        default=4000,
        description="Memory limit in MB",
    )
    
    n_threads: int = Field(
        default=1,
        description="Number of threads",
    )
    
    options: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional Psi4 options",
    )


# =============================================================================
# ANHARMONIC TOOL
# =============================================================================

@register_tool
class AnharmonicTool(BaseTool[AnharmonicToolInput, ToolOutput]):
    """
    MCP tool for anharmonic frequency calculations.
    
    Computes anharmonic corrections using VPT2 (second-order
    vibrational perturbation theory).
    
    Computed Properties:
        - Fundamental frequencies (anharmonic)
        - Overtones
        - Combination bands
        - Anharmonic ZPE
        - X_ij anharmonic constants
    
    Note:
        This calculation is significantly more expensive than
        harmonic frequency calculations as it requires third
        and fourth derivatives of the energy.
    """
    
    name: ClassVar[str] = "calculate_anharmonic"
    description: ClassVar[str] = (
        "Calculate anharmonic corrections to vibrational frequencies using VPT2. "
        "Provides more accurate frequencies for comparison with experiment."
    )
    category: ClassVar[ToolCategory] = ToolCategory.VIBRATIONAL
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        """Get JSON schema for input validation."""
        return {
            "geometry": {
                "type": "string",
                "description": "Molecular geometry in XYZ or Psi4 format",
            },
            "method": {
                "type": "string",
                "description": "Calculation method",
                "default": "hf",
            },
            "basis": {
                "type": "string",
                "description": "Basis set name",
                "default": "cc-pvdz",
            },
            "charge": {
                "type": "integer",
                "description": "Molecular charge",
                "default": 0,
            },
            "multiplicity": {
                "type": "integer",
                "description": "Spin multiplicity (2S+1)",
                "default": 1,
            },
            "vpt2_level": {
                "type": "string",
                "description": "VPT2 level (full, simple, deperturbed)",
                "default": "full",
            },
            "memory": {
                "type": "integer",
                "description": "Memory limit in MB",
                "default": 4000,
            },
            "n_threads": {
                "type": "integer",
                "description": "Number of threads",
                "default": 1,
            },
        }
    
    def _execute(self, input_data: AnharmonicToolInput) -> Result[ToolOutput]:
        """Execute anharmonic calculation."""
        try:
            # Note: Anharmonic calculations in Psi4 require additional setup
            # This is a placeholder that documents the expected interface
            
            from psi4_mcp.services.psi4_interface import get_psi4_interface
            
            psi4 = get_psi4_interface()
            
            # Initialize
            init_result = psi4.initialize(
                memory=input_data.memory,
                n_threads=input_data.n_threads,
            )
            if init_result.is_failure:
                return Result.failure(init_result.error)
            
            # Create molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            mol_result = psi4.create_molecule(mol_string)
            if mol_result.is_failure:
                return Result.failure(mol_result.error)
            
            molecule = mol_result.value
            
            # Set options
            options = {"basis": input_data.basis}
            if input_data.options:
                options.update(input_data.options)
            psi4.set_options(options)
            
            # For now, return a NOT_IMPLEMENTED message
            # Full anharmonic calculations require findif or QFF
            message = (
                "Anharmonic calculations are not fully implemented.\n"
                "Full VPT2 anharmonic frequency analysis requires:\n"
                "1. Harmonic frequency calculation\n"
                "2. Third and fourth derivative calculations\n"
                "3. VPT2 analysis of the quartic force field\n"
                "\n"
                "For production use, consider using Psi4's fdiff_gradient_5pt\n"
                "or external anharmonic analysis programs."
            )
            
            data = {
                "status": "not_fully_implemented",
                "method": input_data.method,
                "basis": input_data.basis,
                "vpt2_level": input_data.vpt2_level,
                "note": "Full VPT2 requires QFF derivatives",
            }
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data,
            ))
            
        except Exception as e:
            logger.exception("Anharmonic calculation failed")
            return Result.failure(CalculationError(
                code="ANHARMONIC_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_anharmonic(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    vpt2_level: str = "full",
    memory: int = 4000,
    n_threads: int = 1,
    **options: Any,
) -> ToolOutput:
    """
    Calculate anharmonic corrections.
    
    Args:
        geometry: Molecular geometry string.
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        vpt2_level: VPT2 calculation level.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        **options: Additional Psi4 options.
        
    Returns:
        ToolOutput with anharmonic results.
    """
    tool = AnharmonicTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "vpt2_level": vpt2_level,
        "memory": memory,
        "n_threads": n_threads,
    }
    
    if options:
        input_data["options"] = options
    
    return tool.run(input_data)
