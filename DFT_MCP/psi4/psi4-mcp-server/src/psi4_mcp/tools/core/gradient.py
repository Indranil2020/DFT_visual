"""
Gradient Calculation Tool.

MCP tool for computing nuclear gradients (forces) using various quantum
chemistry methods.

Key Functions:
    - calculate_gradient: Convenience function for gradient calculations
    
Key Classes:
    - GradientTool: MCP tool class for gradient calculations
    - GradientToolInput: Input schema for gradient tool
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
from psi4_mcp.runners.base_runner import RunnerConfig


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class GradientToolInput(ToolInput):
    """
    Input schema for gradient calculation tool.
    
    Attributes:
        geometry: Molecular geometry (XYZ or Psi4 format).
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
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
    
    memory: int = Field(
        default=2000,
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
# GRADIENT TOOL
# =============================================================================

@register_tool
class GradientTool(BaseTool[GradientToolInput, ToolOutput]):
    """
    MCP tool for gradient (force) calculations.
    
    Computes the nuclear gradient (first derivative of energy with
    respect to nuclear coordinates) for a molecule.
    
    The gradient is useful for:
        - Geometry optimization
        - Force calculations
        - Checking stationary points
        - Molecular dynamics
    
    Returns:
        Gradient output including:
        - Energy at current geometry
        - Gradient array (forces on each atom)
        - RMS gradient
        - Maximum gradient component
    """
    
    name: ClassVar[str] = "calculate_gradient"
    description: ClassVar[str] = (
        "Calculate the nuclear gradient (forces) of a molecule. "
        "Returns the derivative of energy with respect to nuclear coordinates."
    )
    category: ClassVar[ToolCategory] = ToolCategory.CORE
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
            "memory": {
                "type": "integer",
                "description": "Memory limit in MB",
                "default": 2000,
            },
            "n_threads": {
                "type": "integer",
                "description": "Number of threads",
                "default": 1,
            },
        }
    
    def _execute(self, input_data: GradientToolInput) -> Result[ToolOutput]:
        """Execute gradient calculation."""
        try:
            from psi4_mcp.services.psi4_interface import get_psi4_interface
            
            # Get Psi4 interface
            psi4 = get_psi4_interface()
            
            # Initialize
            init_result = psi4.initialize(
                memory=input_data.memory,
                n_threads=input_data.n_threads,
            )
            if init_result.is_failure:
                return Result.failure(init_result.error)
            
            # Create molecule
            mol_result = psi4.create_molecule(
                f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            )
            if mol_result.is_failure:
                return Result.failure(mol_result.error)
            
            molecule = mol_result.value
            
            # Set options
            options = {"basis": input_data.basis}
            if input_data.options:
                options.update(input_data.options)
            psi4.set_options(options)
            
            # Calculate gradient
            grad_result = psi4.gradient(
                input_data.method,
                molecule=molecule,
                return_wfn=True,
            )
            
            if grad_result.is_failure:
                return Result.failure(grad_result.error)
            
            gradient, wfn = grad_result.value
            
            # Extract gradient array
            grad_array = gradient.np.tolist()
            
            # Calculate statistics
            import math
            flat_grad = [g for row in grad_array for g in row]
            rms_grad = math.sqrt(sum(g**2 for g in flat_grad) / len(flat_grad))
            max_grad = max(abs(g) for g in flat_grad)
            
            # Get energy
            energy = wfn.energy()
            
            # Build response
            data = {
                "energy": energy,
                "energy_unit": "Hartree",
                "gradient": grad_array,
                "gradient_unit": "Hartree/Bohr",
                "rms_gradient": rms_grad,
                "max_gradient": max_grad,
                "method": input_data.method,
                "basis": input_data.basis,
                "n_atoms": len(grad_array),
            }
            
            message = (
                f"Gradient calculation completed: {input_data.method}/{input_data.basis}\n"
                f"Energy: {energy:.10f} Hartree\n"
                f"RMS Gradient: {rms_grad:.6e} Hartree/Bohr\n"
                f"Max Gradient: {max_grad:.6e} Hartree/Bohr"
            )
            
            # Cleanup
            psi4.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data,
            ))
            
        except Exception as e:
            logger.exception("Gradient calculation failed")
            return Result.failure(CalculationError(
                code="GRADIENT_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_gradient(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    memory: int = 2000,
    n_threads: int = 1,
    **options: Any,
) -> ToolOutput:
    """
    Calculate nuclear gradient (forces).
    
    Args:
        geometry: Molecular geometry string.
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        **options: Additional Psi4 options.
        
    Returns:
        ToolOutput with gradient results.
        
    Examples:
        >>> result = calculate_gradient(
        ...     geometry="H 0 0 0\\nH 0 0 0.74",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        >>> print(result.data["rms_gradient"])
    """
    tool = GradientTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "memory": memory,
        "n_threads": n_threads,
    }
    
    if options:
        input_data["options"] = options
    
    return tool.run(input_data)
