"""
Hessian Calculation Tool.

MCP tool for computing the Hessian matrix (second derivatives of energy)
for molecular systems.

Key Functions:
    - calculate_hessian: Convenience function for Hessian calculations
    
Key Classes:
    - HessianTool: MCP tool class for Hessian calculations
    - HessianToolInput: Input schema for Hessian tool
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

class HessianToolInput(ToolInput):
    """
    Input schema for Hessian calculation tool.
    
    Attributes:
        geometry: Molecular geometry (XYZ or Psi4 format).
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        dertype: Derivative type (energy, gradient, or hessian).
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
    
    dertype: str = Field(
        default="energy",
        description="Derivative type for Hessian computation",
        pattern="^(energy|gradient|hessian)$",
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
# HESSIAN TOOL
# =============================================================================

@register_tool
class HessianTool(BaseTool[HessianToolInput, ToolOutput]):
    """
    MCP tool for Hessian matrix calculations.
    
    Computes the Hessian matrix (second derivative of energy with
    respect to nuclear coordinates).
    
    The Hessian is used for:
        - Vibrational frequency calculations
        - Thermochemistry
        - Characterizing stationary points
        - IRC calculations
    
    Returns:
        Hessian output including:
        - Energy at current geometry
        - Hessian matrix
        - Eigenvalues (related to frequencies)
    """
    
    name: ClassVar[str] = "calculate_hessian"
    description: ClassVar[str] = (
        "Calculate the Hessian matrix (second energy derivatives) of a molecule. "
        "Used for frequencies, thermochemistry, and characterizing stationary points."
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
            "dertype": {
                "type": "string",
                "description": "Derivative type (energy, gradient, hessian)",
                "default": "energy",
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
    
    def _execute(self, input_data: HessianToolInput) -> Result[ToolOutput]:
        """Execute Hessian calculation."""
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
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            mol_result = psi4.create_molecule(mol_string)
            if mol_result.is_failure:
                return Result.failure(mol_result.error)
            
            molecule = mol_result.value
            n_atoms = molecule.natom()
            
            # Set options
            options = {"basis": input_data.basis}
            if input_data.options:
                options.update(input_data.options)
            psi4.set_options(options)
            
            # Calculate Hessian
            hess_result = psi4.hessian(
                input_data.method,
                molecule=molecule,
                return_wfn=True,
            )
            
            if hess_result.is_failure:
                return Result.failure(hess_result.error)
            
            hessian, wfn = hess_result.value
            
            # Extract Hessian array
            hess_array = hessian.np.tolist()
            
            # Get energy
            energy = wfn.energy()
            
            # Calculate eigenvalues for characterization
            import numpy as np
            hess_np = np.array(hess_array)
            eigenvalues = np.linalg.eigvalsh(hess_np).tolist()
            
            # Count negative eigenvalues
            n_negative = sum(1 for ev in eigenvalues if ev < -1e-6)
            n_zero = sum(1 for ev in eigenvalues if abs(ev) < 1e-6)
            
            # Characterize stationary point
            if n_negative == 0:
                sp_type = "minimum"
            elif n_negative == 1:
                sp_type = "transition_state"
            else:
                sp_type = f"higher_order_saddle_point_{n_negative}"
            
            # Build response
            data = {
                "energy": energy,
                "energy_unit": "Hartree",
                "hessian": hess_array,
                "hessian_unit": "Hartree/Bohr^2",
                "eigenvalues": eigenvalues,
                "n_negative_eigenvalues": n_negative,
                "n_zero_eigenvalues": n_zero,
                "stationary_point_type": sp_type,
                "method": input_data.method,
                "basis": input_data.basis,
                "n_atoms": n_atoms,
                "hessian_size": f"{3*n_atoms}x{3*n_atoms}",
            }
            
            message = (
                f"Hessian calculation completed: {input_data.method}/{input_data.basis}\n"
                f"Energy: {energy:.10f} Hartree\n"
                f"Hessian size: {3*n_atoms}x{3*n_atoms}\n"
                f"Negative eigenvalues: {n_negative}\n"
                f"Stationary point type: {sp_type}"
            )
            
            # Cleanup
            psi4.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data,
            ))
            
        except Exception as e:
            logger.exception("Hessian calculation failed")
            return Result.failure(CalculationError(
                code="HESSIAN_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_hessian(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    dertype: str = "energy",
    memory: int = 2000,
    n_threads: int = 1,
    **options: Any,
) -> ToolOutput:
    """
    Calculate the Hessian matrix.
    
    Args:
        geometry: Molecular geometry string.
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        dertype: Derivative type for computation.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        **options: Additional Psi4 options.
        
    Returns:
        ToolOutput with Hessian results.
        
    Examples:
        >>> result = calculate_hessian(
        ...     geometry="O 0 0 0\\nH 0 0 0.96\\nH 0 0.96 0",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        >>> print(result.data["stationary_point_type"])
    """
    tool = HessianTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "dertype": dertype,
        "memory": memory,
        "n_threads": n_threads,
    }
    
    if options:
        input_data["options"] = options
    
    return tool.run(input_data)
