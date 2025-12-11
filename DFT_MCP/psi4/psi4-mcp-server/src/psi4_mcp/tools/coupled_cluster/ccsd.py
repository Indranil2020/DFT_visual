"""
CCSD (Coupled Cluster Singles and Doubles) Tool.

MCP tool for CCSD calculations.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class CCSDToolInput(ToolInput):
    """Input schema for CCSD calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    freeze_core: bool = Field(default=True, description="Freeze core orbitals")
    convergence: float = Field(default=1e-7, description="Amplitude convergence")
    max_iterations: int = Field(default=50, description="Maximum iterations")
    df: bool = Field(default=False, description="Use density fitting")
    memory: int = Field(default=4000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class CCSDTool(BaseTool[CCSDToolInput, ToolOutput]):
    """
    MCP tool for CCSD calculations.
    
    CCSD (Coupled Cluster Singles and Doubles) includes single and double
    excitations iteratively. Provides good correlation energy recovery.
    
    Scaling: O(N^6)
    Accuracy: ~1-2 kcal/mol for reaction energies
    """
    
    name: ClassVar[str] = "calculate_ccsd"
    description: ClassVar[str] = (
        "Calculate energy using CCSD (Coupled Cluster Singles and Doubles). "
        "O(N^6) scaling, good accuracy for single-reference systems."
    )
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATED
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "basis": {"type": "string", "default": "cc-pvdz"},
                "freeze_core": {"type": "boolean", "default": True},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: CCSDToolInput) -> Result[ToolOutput]:
        """Execute CCSD calculation."""
        try:
            import psi4
            
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            
            psi4.set_options({
                "basis": input_data.basis,
                "freeze_core": input_data.freeze_core,
                "r_convergence": input_data.convergence,
                "maxiter": input_data.max_iterations,
            })
            
            method = "df-ccsd" if input_data.df else "ccsd"
            energy, wfn = psi4.energy(f"{method}/{input_data.basis}", return_wfn=True, molecule=molecule)
            
            # Extract components
            hf_energy = psi4.variable("HF TOTAL ENERGY")
            ccsd_corr = psi4.variable("CCSD CORRELATION ENERGY")
            
            # Get T1 diagnostic for multireference character
            try:
                t1_diag = psi4.variable("CCSD T1 DIAGNOSTIC")
            except Exception:
                t1_diag = None
            
            data = {
                "total_energy": float(energy),
                "hf_energy": float(hf_energy),
                "correlation_energy": float(ccsd_corr),
                "t1_diagnostic": float(t1_diag) if t1_diag else None,
                "multireference_warning": float(t1_diag) > 0.02 if t1_diag else None,
                "basis": input_data.basis,
                "method": "DF-CCSD" if input_data.df else "CCSD",
                "freeze_core": input_data.freeze_core,
                "units": {"energy": "hartree"}
            }
            
            message = f"CCSD: E = {energy:.10f} Hartree"
            if t1_diag and float(t1_diag) > 0.02:
                message += f" (T1={t1_diag:.4f}, multireference character!)"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("CCSD calculation failed")
            return Result.failure(CalculationError(code="CCSD_ERROR", message=str(e)))


def calculate_ccsd(geometry: str, basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate CCSD energy."""
    return CCSDTool().run({"geometry": geometry, "basis": basis, **kwargs})
