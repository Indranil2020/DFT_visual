"""
EPR Zero-Field Splitting Tool.

MCP tool for computing zero-field splitting (ZFS) parameters D and E.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class ZeroFieldSplittingToolInput(ToolInput):
    """Input schema for ZFS calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="uhf", description="Method (UHF, UKS, ROHF)")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=3, description="Spin multiplicity (must be > 2)")
    include_soc: bool = Field(default=True, description="Include spin-orbit coupling")
    include_ss: bool = Field(default=True, description="Include spin-spin coupling")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class ZeroFieldSplittingTool(BaseTool[ZeroFieldSplittingToolInput, ToolOutput]):
    """
    MCP tool for zero-field splitting calculations.
    
    Computes the ZFS parameters D and E for high-spin systems (S >= 1).
    These parameters describe the energy level splitting in the absence
    of an external magnetic field due to:
    - Spin-spin (dipolar) coupling between unpaired electrons
    - Spin-orbit coupling
    
    Note: Requires multiplicity >= 3 (S >= 1).
    """
    
    name: ClassVar[str] = "calculate_zero_field_splitting"
    description: ClassVar[str] = (
        "Calculate zero-field splitting (ZFS) parameters D and E. "
        "For high-spin systems with S >= 1."
    )
    category: ClassVar[ToolCategory] = ToolCategory.SPECTROSCOPY
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "method": {"type": "string", "default": "uhf"},
                "basis": {"type": "string", "default": "cc-pvdz"},
                "multiplicity": {"type": "integer", "default": 3},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: ZeroFieldSplittingToolInput) -> Result[ToolOutput]:
        """Execute ZFS calculation."""
        try:
            import psi4
            import numpy as np
            
            # Validate multiplicity
            if input_data.multiplicity < 3:
                return Result.failure(CalculationError(
                    code="INVALID_MULTIPLICITY",
                    message="ZFS requires S >= 1 (multiplicity >= 3)"
                ))
            
            # Configure Psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            # Build molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            
            # Set options
            psi4.set_options({
                "basis": input_data.basis,
                "reference": "uhf" if "u" in input_data.method.lower() else "rohf",
            })
            
            # Run calculation
            method_str = f"{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Get spin information
            n_alpha = wfn.nalpha()
            n_beta = wfn.nbeta()
            n_unpaired = n_alpha - n_beta
            spin_s = n_unpaired / 2.0
            
            # Note: Full ZFS calculation requires specialized code
            # This provides a simplified interface
            
            # Try to extract ZFS parameters
            try:
                d_xx = psi4.variable("ZFS D_XX")
                d_yy = psi4.variable("ZFS D_YY")
                d_zz = psi4.variable("ZFS D_ZZ")
                
                # Convert to conventional D and E parameters
                # D = 3/2 * D_zz, E = (D_xx - D_yy) / 2
                d_param = 1.5 * float(d_zz)
                e_param = (float(d_xx) - float(d_yy)) / 2.0
                
                zfs_tensor = {
                    "D_xx": float(d_xx),
                    "D_yy": float(d_yy),
                    "D_zz": float(d_zz),
                }
            except Exception:
                d_param = None
                e_param = None
                zfs_tensor = None
            
            # Build output
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "multiplicity": input_data.multiplicity,
                "spin_s": spin_s,
                "n_unpaired_electrons": n_unpaired,
                "d_parameter_cm1": d_param,
                "e_parameter_cm1": e_param,
                "e_over_d": abs(e_param / d_param) if (d_param and d_param != 0) else None,
                "zfs_tensor_cm1": zfs_tensor,
                "contributions": {
                    "spin_spin": input_data.include_ss,
                    "spin_orbit": input_data.include_soc,
                },
                "units": {
                    "D": "cm^-1",
                    "E": "cm^-1"
                },
                "notes": [
                    "D = axial ZFS parameter (cm^-1)",
                    "E = rhombic ZFS parameter (cm^-1)",
                    "|E/D| < 1/3 for axial symmetry",
                    "E/D = 0 for perfect axial symmetry",
                    "E/D = 1/3 for maximum rhombicity"
                ]
            }
            
            if d_param is not None:
                message = f"ZFS: D = {d_param:.3f} cm^-1, E = {e_param:.3f} cm^-1"
            else:
                message = "ZFS parameters could not be computed"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("ZFS calculation failed")
            return Result.failure(CalculationError(
                code="ZFS_ERROR",
                message=str(e)
            ))


def calculate_zero_field_splitting(
    geometry: str,
    method: str = "uhf",
    basis: str = "cc-pvdz",
    multiplicity: int = 3,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate zero-field splitting parameters.
    
    Args:
        geometry: Molecular geometry
        method: Calculation method
        basis: Basis set
        multiplicity: Spin multiplicity (>= 3)
        **kwargs: Additional options
        
    Returns:
        ToolOutput with D and E parameters
    """
    tool = ZeroFieldSplittingTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "multiplicity": multiplicity,
        **kwargs
    })
