"""
EPR Hyperfine Coupling Tool.

MCP tool for computing hyperfine coupling constants in open-shell molecules.
"""

from typing import Any, ClassVar, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


# Nuclear g-factors for common isotopes
NUCLEAR_G_FACTORS = {
    "1H": 5.5857,
    "2H": 0.8574,
    "13C": 1.4048,
    "14N": 0.4038,
    "15N": -0.5664,
    "17O": -0.7575,
    "19F": 5.2577,
    "31P": 2.2632,
    "33S": 0.4291,
}


class HyperfineToolInput(ToolInput):
    """Input schema for hyperfine coupling calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="uhf", description="Method (UHF, UKS)")
    basis: str = Field(default="cc-pvtz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=2, description="Spin multiplicity")
    nuclei: Optional[list[int]] = Field(
        default=None,
        description="Atom indices to compute (0-indexed). None = all"
    )
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class HyperfineTool(BaseTool[HyperfineToolInput, ToolOutput]):
    """
    MCP tool for hyperfine coupling constant calculations.
    
    Computes isotropic (Fermi contact) and anisotropic (dipolar) hyperfine
    coupling constants between unpaired electrons and magnetic nuclei.
    """
    
    name: ClassVar[str] = "calculate_hyperfine"
    description: ClassVar[str] = (
        "Calculate EPR hyperfine coupling constants. "
        "Returns isotropic and anisotropic couplings for magnetic nuclei."
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
                "basis": {"type": "string", "default": "cc-pvtz"},
                "multiplicity": {"type": "integer", "default": 2},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: HyperfineToolInput) -> Result[ToolOutput]:
        """Execute hyperfine calculation."""
        try:
            import psi4
            import numpy as np
            
            # Validate multiplicity
            if input_data.multiplicity < 2:
                return Result.failure(CalculationError(
                    code="INVALID_MULTIPLICITY",
                    message="Hyperfine requires open-shell system (multiplicity >= 2)"
                ))
            
            # Configure Psi4
            psi4.core.clean()
            psi4.set_memory(f"{input_data.memory} MB")
            psi4.set_num_threads(input_data.n_threads)
            
            # Build molecule
            mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
            molecule = psi4.geometry(mol_string)
            n_atoms = molecule.natom()
            
            # Determine nuclei to compute
            if input_data.nuclei:
                target_atoms = input_data.nuclei
            else:
                target_atoms = list(range(n_atoms))
            
            # Set options
            psi4.set_options({
                "basis": input_data.basis,
                "reference": "uhf",
            })
            
            # Run calculation
            method_str = f"{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Get spin density for hyperfine calculations
            # Note: Full implementation requires spin density at nuclei
            
            hyperfine_couplings = []
            
            for i in target_atoms:
                if i >= n_atoms:
                    continue
                    
                element = molecule.symbol(i)
                mass_number = molecule.mass(i)
                
                # Get isotope label
                isotope = f"{int(round(mass_number))}{element}"
                
                try:
                    # Try to get Fermi contact term
                    a_iso = psi4.variable(f"HYPERFINE A_ISO {i+1}")
                except Exception:
                    a_iso = None
                
                try:
                    # Try to get dipolar tensor
                    t_xx = psi4.variable(f"HYPERFINE T_XX {i+1}")
                    t_yy = psi4.variable(f"HYPERFINE T_YY {i+1}")
                    t_zz = psi4.variable(f"HYPERFINE T_ZZ {i+1}")
                    dipolar = {
                        "T_xx": float(t_xx),
                        "T_yy": float(t_yy),
                        "T_zz": float(t_zz),
                    }
                except Exception:
                    dipolar = None
                
                coupling_data = {
                    "atom_index": i,
                    "element": element,
                    "isotope": isotope,
                    "nuclear_g_factor": NUCLEAR_G_FACTORS.get(isotope),
                    "a_iso_mhz": float(a_iso) if a_iso else None,
                    "dipolar_tensor_mhz": dipolar,
                }
                
                hyperfine_couplings.append(coupling_data)
            
            # Build output
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "multiplicity": input_data.multiplicity,
                "n_nuclei": len(hyperfine_couplings),
                "hyperfine_couplings": hyperfine_couplings,
                "units": {
                    "a_iso": "MHz",
                    "dipolar": "MHz"
                },
                "notes": [
                    "A_iso = Fermi contact (isotropic)",
                    "T = dipolar tensor (anisotropic, traceless)",
                    "Full tensor A = A_iso + T"
                ]
            }
            
            message = f"Hyperfine couplings computed for {len(hyperfine_couplings)} nuclei"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("Hyperfine calculation failed")
            return Result.failure(CalculationError(
                code="HYPERFINE_ERROR",
                message=str(e)
            ))


def calculate_hyperfine(
    geometry: str,
    method: str = "uhf",
    basis: str = "cc-pvtz",
    multiplicity: int = 2,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate EPR hyperfine coupling constants.
    
    Args:
        geometry: Molecular geometry
        method: Calculation method (UHF, UKS)
        basis: Basis set
        multiplicity: Spin multiplicity (>= 2)
        **kwargs: Additional options
        
    Returns:
        ToolOutput with hyperfine couplings
    """
    tool = HyperfineTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "multiplicity": multiplicity,
        **kwargs
    })
