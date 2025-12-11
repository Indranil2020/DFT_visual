"""
CCSD(T) Tool - The Gold Standard.

MCP tool for CCSD(T) calculations - the "gold standard" of quantum chemistry.
"""

from typing import Any, ClassVar
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


class CCSD_T_ToolInput(ToolInput):
    """Input schema for CCSD(T) calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    freeze_core: bool = Field(default=True, description="Freeze core orbitals")
    convergence: float = Field(default=1e-7, description="Amplitude convergence")
    df: bool = Field(default=False, description="Use density fitting")
    memory: int = Field(default=8000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class CCSD_T_Tool(BaseTool[CCSD_T_ToolInput, ToolOutput]):
    """
    MCP tool for CCSD(T) calculations.
    
    CCSD(T) is the "gold standard" of quantum chemistry. It adds perturbative
    triples correction to CCSD, achieving very high accuracy.
    
    Scaling: O(N^7)
    Accuracy: ~0.5 kcal/mol for thermochemistry (with large basis)
    
    Use for:
    - Benchmark calculations
    - Accurate thermochemistry
    - Reference for other methods
    """
    
    name: ClassVar[str] = "calculate_ccsd_t"
    description: ClassVar[str] = (
        "Calculate energy using CCSD(T), the 'gold standard' of quantum chemistry. "
        "O(N^7) scaling, highest accuracy for single-reference systems."
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
    
    def _execute(self, input_data: CCSD_T_ToolInput) -> Result[ToolOutput]:
        """Execute CCSD(T) calculation."""
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
            })
            
            method = "df-ccsd(t)" if input_data.df else "ccsd(t)"
            energy, wfn = psi4.energy(f"{method}/{input_data.basis}", return_wfn=True, molecule=molecule)
            
            # Extract all components
            hf_energy = psi4.variable("HF TOTAL ENERGY")
            ccsd_corr = psi4.variable("CCSD CORRELATION ENERGY")
            ccsd_total = psi4.variable("CCSD TOTAL ENERGY")
            triples_corr = psi4.variable("(T) CORRECTION ENERGY")
            
            try:
                t1_diag = psi4.variable("CCSD T1 DIAGNOSTIC")
            except Exception:
                t1_diag = None
            
            data = {
                "ccsd_t_total_energy": float(energy),
                "ccsd_total_energy": float(ccsd_total),
                "hf_energy": float(hf_energy),
                "ccsd_correlation_energy": float(ccsd_corr),
                "triples_correction": float(triples_corr),
                "percent_triples": 100 * abs(float(triples_corr) / float(ccsd_corr)) if ccsd_corr else None,
                "t1_diagnostic": float(t1_diag) if t1_diag else None,
                "basis": input_data.basis,
                "method": "DF-CCSD(T)" if input_data.df else "CCSD(T)",
                "units": {"energy": "hartree"}
            }
            
            message = f"CCSD(T): E = {energy:.10f} Hartree, (T) = {triples_corr:.6f}"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(success=True, message=message, data=data))
            
        except Exception as e:
            logger.exception("CCSD(T) calculation failed")
            return Result.failure(CalculationError(code="CCSD_T_ERROR", message=str(e)))


def calculate_ccsd_t(geometry: str, basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate CCSD(T) energy - the gold standard."""
    return CCSD_T_Tool().run({"geometry": geometry, "basis": basis, **kwargs})
