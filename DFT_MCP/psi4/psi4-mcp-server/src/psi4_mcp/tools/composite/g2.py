"""
G2 (Gaussian-2) Composite Method Tool.

G2 theory improves on G1 with larger basis sets and additional corrections.

Reference:
    Curtiss, L.A.; Raghavachari, K.; Trucks, G.W.; Pople, J.A.
    J. Chem. Phys. 1991, 94, 7221-7230.
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
class G2Result:
    """G2 calculation results."""
    e_0: float
    e_qcisd_t: float
    delta_e_mp2: float
    delta_e_hlc: float
    zpve: float
    optimized_geometry: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "e_0_hartree": self.e_0, "e_0_kcal": self.e_0 * HARTREE_TO_KCAL,
            "components": {
                "e_qcisd_t": self.e_qcisd_t, "delta_e_mp2": self.delta_e_mp2,
                "delta_e_hlc": self.delta_e_hlc, "zpve": self.zpve,
            },
            "optimized_geometry": self.optimized_geometry,
        }


class G2Input(ToolInput):
    """Input for G2 calculation."""
    geometry: str = Field(..., description="Molecular geometry")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    scale_factor: float = Field(default=0.8929)
    memory: int = Field(default=8000)
    n_threads: int = Field(default=1)


def validate_g2_input(input_data: G2Input) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def run_g2_calculation(input_data: G2Input) -> G2Result:
    """Execute G2 composite calculation."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_g2.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    ref = "rhf" if input_data.multiplicity == 1 else "uhf"
    
    # MP2(full)/6-31G* geometry optimization
    psi4.set_options({"basis": "6-31G*", "freeze_core": False, "reference": ref})
    psi4.optimize("mp2/6-31G*", molecule=mol)
    optimized_geometry = mol.save_string_xyz()
    
    # HF/6-31G* frequencies
    psi4.set_options({"basis": "6-31G*"})
    e_freq, freq_wfn = psi4.frequency("hf/6-31G*", molecule=mol, return_wfn=True)
    frequencies = freq_wfn.frequency_analysis['omega'].to_array().tolist()
    zpve = sum(f for f in frequencies if f > 0) * 0.5 * input_data.scale_factor * 4.556335e-6
    
    # QCISD(T)/6-311G** base energy
    psi4.set_options({"basis": "6-311G**", "freeze_core": True})
    e_qcisd_t = psi4.energy("ccsd(t)/6-311G**", molecule=mol)
    
    # MP2 correction for larger basis
    psi4.set_options({"basis": "6-311+G(3df,2p)", "freeze_core": True})
    e_mp2_large = psi4.energy("mp2/6-311+G(3df,2p)", molecule=mol)
    psi4.set_options({"basis": "6-311G**"})
    e_mp2_small = psi4.energy("mp2/6-311G**", molecule=mol)
    
    delta_e_mp2 = e_mp2_large - e_mp2_small
    
    # Higher-level correction
    n_electrons = mol.nelectron()
    n_unpaired = input_data.multiplicity - 1
    n_pairs = (n_electrons - n_unpaired) // 2
    delta_e_hlc = -0.00481 * n_pairs - 0.00019 * n_unpaired
    
    e_0 = e_qcisd_t + delta_e_mp2 + delta_e_hlc + zpve
    
    psi4.core.clean()
    
    return G2Result(e_0=e_0, e_qcisd_t=e_qcisd_t, delta_e_mp2=delta_e_mp2,
                   delta_e_hlc=delta_e_hlc, zpve=zpve, optimized_geometry=optimized_geometry)


@register_tool
class G2Tool(BaseTool[G2Input, ToolOutput]):
    """Tool for G2 composite calculations."""
    name: ClassVar[str] = "calculate_g2"
    description: ClassVar[str] = "Calculate G2 composite energy."
    category: ClassVar[ToolCategory] = ToolCategory.COMPOSITE
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: G2Input) -> Optional[ValidationError]:
        return validate_g2_input(input_data)
    
    def _execute(self, input_data: G2Input) -> Result[ToolOutput]:
        result = run_g2_calculation(input_data)
        message = f"G2 Energy: {result.e_0:.10f} Eh ({result.e_0 * HARTREE_TO_KCAL:.2f} kcal/mol)"
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def calculate_g2(geometry: str, charge: int = 0, multiplicity: int = 1, **kwargs: Any) -> ToolOutput:
    """Calculate G2 composite energy."""
    return G2Tool().run({"geometry": geometry, "charge": charge, "multiplicity": multiplicity, **kwargs})
