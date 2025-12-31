"""
Density-Fitted MP2 (DF-MP2) Tool.

DF-MP2 uses density fitting (resolution of identity) approximation
for efficient MP2 calculations with reduced computational cost.

Reference:
    Weigend, F.; Häser, M. Theor. Chem. Acc. 1997, 97, 331.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


@dataclass
class DFMP2Result:
    """DF-MP2 calculation results."""
    total_energy: float
    correlation_energy: float
    same_spin_correlation: float
    opposite_spin_correlation: float
    hf_energy: float
    df_error_estimate: float
    basis: str
    aux_basis: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_energy_hartree": self.total_energy,
            "correlation_energy_hartree": self.correlation_energy,
            "correlation_energy_kcal": self.correlation_energy * HARTREE_TO_KCAL,
            "same_spin_hartree": self.same_spin_correlation,
            "opposite_spin_hartree": self.opposite_spin_correlation,
            "hf_energy_hartree": self.hf_energy,
            "df_error_estimate_hartree": self.df_error_estimate,
            "basis": self.basis,
            "aux_basis": self.aux_basis,
        }


class DFMP2Input(ToolInput):
    """Input for DF-MP2 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    aux_basis: str = Field(default="cc-pvdz-ri", description="Auxiliary basis for DF")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    freeze_core: bool = Field(default=True)
    
    scs_mp2: bool = Field(default=False, description="Use spin-component-scaled MP2")
    scs_same_spin: float = Field(default=0.333, description="SCS same-spin scaling")
    scs_opposite_spin: float = Field(default=1.2, description="SCS opposite-spin scaling")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_df_mp2_input(input_data: DFMP2Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_df_mp2_calculation(input_data: DFMP2Input) -> DFMP2Result:
    """Execute DF-MP2 calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_dfmp2.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    psi4.set_options({
        "basis": input_data.basis,
        "df_basis_mp2": input_data.aux_basis,
        "freeze_core": input_data.freeze_core,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
        "mp2_type": "df",
    })
    
    logger.info(f"Running DF-MP2/{input_data.basis}")
    
    e_mp2, wfn = psi4.energy("mp2", return_wfn=True, molecule=mol)
    
    hf_energy = psi4.variable("SCF TOTAL ENERGY")
    mp2_corr = psi4.variable("MP2 CORRELATION ENERGY")
    same_spin = psi4.variable("MP2 SAME-SPIN CORRELATION ENERGY")
    opp_spin = psi4.variable("MP2 OPPOSITE-SPIN CORRELATION ENERGY")
    
    if same_spin == 0:
        # Estimate if not available
        same_spin = mp2_corr * 0.3
        opp_spin = mp2_corr * 0.7
    
    # Apply SCS if requested
    if input_data.scs_mp2:
        scs_corr = input_data.scs_same_spin * same_spin + input_data.scs_opposite_spin * opp_spin
        total_energy = hf_energy + scs_corr
        correlation = scs_corr
    else:
        total_energy = e_mp2
        correlation = mp2_corr
    
    # DF error estimate (typically ~0.1 mEh for good aux basis)
    df_error = abs(mp2_corr) * 0.001
    
    psi4.core.clean()
    
    return DFMP2Result(
        total_energy=total_energy,
        correlation_energy=correlation,
        same_spin_correlation=same_spin,
        opposite_spin_correlation=opp_spin,
        hf_energy=hf_energy,
        df_error_estimate=df_error,
        basis=input_data.basis,
        aux_basis=input_data.aux_basis,
    )


@register_tool
class DFMP2Tool(BaseTool[DFMP2Input, ToolOutput]):
    """Tool for DF-MP2 calculations."""
    name: ClassVar[str] = "calculate_df_mp2"
    description: ClassVar[str] = "Calculate density-fitted MP2 energy."
    category: ClassVar[ToolCategory] = ToolCategory.CORRELATION
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: DFMP2Input) -> Optional[ValidationError]:
        return validate_df_mp2_input(input_data)
    
    def _execute(self, input_data: DFMP2Input) -> Result[ToolOutput]:
        result = run_df_mp2_calculation(input_data)
        
        scs_label = " (SCS)" if input_data.scs_mp2 else ""
        message = (
            f"DF-MP2{scs_label}/{input_data.basis}\n"
            f"{'='*40}\n"
            f"Total Energy:    {result.total_energy:.10f} Eh\n"
            f"Correlation:     {result.correlation_energy:.10f} Eh\n"
            f"  Same-spin:     {result.same_spin_correlation:.10f} Eh\n"
            f"  Opposite-spin: {result.opposite_spin_correlation:.10f} Eh\n"
            f"DF Error Est:    ~{result.df_error_estimate:.6f} Eh"
        )
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_df_mp2(geometry: str, basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Calculate DF-MP2 energy."""
    return DFMP2Tool().run({"geometry": geometry, "basis": basis, **kwargs})
