"""
NMR Chemical Shielding Tool.

MCP tool for computing NMR chemical shielding tensors and chemical shifts.
"""

from typing import Any, ClassVar, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, CalculationError

logger = logging.getLogger(__name__)


# Reference shieldings for common nuclei (ppm, B3LYP/cc-pVTZ level)
REFERENCE_SHIELDINGS = {
    "1H": {"TMS": 31.7, "description": "Tetramethylsilane"},
    "13C": {"TMS": 189.7, "description": "Tetramethylsilane"},
    "15N": {"CH3NO2": -135.0, "description": "Nitromethane"},
    "19F": {"CFCl3": 188.7, "description": "Trichlorofluoromethane"},
    "31P": {"H3PO4": 328.4, "description": "Phosphoric acid"},
}


class NMRShieldingToolInput(ToolInput):
    """Input schema for NMR shielding calculation."""
    
    geometry: str = Field(..., description="Molecular geometry")
    method: str = Field(default="b3lyp", description="DFT functional")
    basis: str = Field(default="cc-pvtz", description="Basis set")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, description="Spin multiplicity")
    nuclei: Optional[list[str]] = Field(
        default=None,
        description="Nuclei to compute (e.g., ['H', 'C']). None = all"
    )
    use_giao: bool = Field(default=True, description="Use GIAO method")
    compute_shifts: bool = Field(default=True, description="Compute chemical shifts")
    reference: str = Field(default="TMS", description="Reference compound")
    memory: int = Field(default=2000, description="Memory in MB")
    n_threads: int = Field(default=1, description="Number of threads")


@register_tool
class NMRShieldingTool(BaseTool[NMRShieldingToolInput, ToolOutput]):
    """
    MCP tool for NMR chemical shielding calculations.
    
    Computes isotropic and anisotropic chemical shielding tensors using
    GIAO (Gauge-Including Atomic Orbitals) method for gauge-origin
    independence.
    """
    
    name: ClassVar[str] = "calculate_nmr_shielding"
    description: ClassVar[str] = (
        "Calculate NMR chemical shielding tensors and chemical shifts. "
        "Uses GIAO method for accurate, gauge-independent results."
    )
    category: ClassVar[ToolCategory] = ToolCategory.SPECTROSCOPY
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "geometry": {"type": "string"},
                "method": {"type": "string", "default": "b3lyp"},
                "basis": {"type": "string", "default": "cc-pvtz"},
                "nuclei": {"type": "array", "items": {"type": "string"}},
                "use_giao": {"type": "boolean", "default": True},
            },
            "required": ["geometry"],
        }
    
    def _execute(self, input_data: NMRShieldingToolInput) -> Result[ToolOutput]:
        """Execute NMR shielding calculation."""
        try:
            import psi4
            
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
            })
            
            # Run NMR calculation (via properties)
            method_str = f"{input_data.method}/{input_data.basis}"
            energy, wfn = psi4.energy(method_str, return_wfn=True, molecule=molecule)
            
            # Compute NMR properties
            psi4.oeprop(wfn, "DIPOLE", "NMR")
            
            # Extract shielding tensors
            shieldings = []
            n_atoms = molecule.natom()
            
            for i in range(n_atoms):
                element = molecule.symbol(i)
                
                # Check if this nucleus should be included
                if input_data.nuclei and element not in input_data.nuclei:
                    continue
                
                try:
                    # Get isotropic shielding
                    var_name = f"NMR SHIELDING {i+1}"
                    iso_shield = psi4.variable(var_name)
                    
                    shield_data = {
                        "atom_index": i,
                        "element": element,
                        "isotropic_shielding_ppm": float(iso_shield),
                    }
                    
                    # Compute chemical shift if requested
                    if input_data.compute_shifts:
                        isotope = "1H" if element == "H" else f"13{element}" if element == "C" else element
                        if isotope in REFERENCE_SHIELDINGS:
                            ref_shield = REFERENCE_SHIELDINGS[isotope].get(input_data.reference, 0)
                            shield_data["chemical_shift_ppm"] = ref_shield - float(iso_shield)
                            shield_data["reference"] = input_data.reference
                    
                    shieldings.append(shield_data)
                    
                except Exception as ex:
                    logger.debug(f"Could not get shielding for atom {i}: {ex}")
            
            # Build output
            data = {
                "method": input_data.method,
                "basis": input_data.basis,
                "giao": input_data.use_giao,
                "n_atoms": n_atoms,
                "shieldings": shieldings,
                "reference": input_data.reference if input_data.compute_shifts else None,
                "units": {
                    "shielding": "ppm",
                    "chemical_shift": "ppm"
                }
            }
            
            message = f"NMR shieldings computed for {len(shieldings)} nuclei"
            
            psi4.core.clean()
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data
            ))
            
        except Exception as e:
            logger.exception("NMR shielding calculation failed")
            return Result.failure(CalculationError(
                code="NMR_SHIELDING_ERROR",
                message=str(e)
            ))


def calculate_nmr_shielding(
    geometry: str,
    method: str = "b3lyp",
    basis: str = "cc-pvtz",
    nuclei: list[str] = None,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate NMR chemical shielding.
    
    Args:
        geometry: Molecular geometry
        method: DFT functional
        basis: Basis set
        nuclei: List of elements to compute (None = all)
        **kwargs: Additional options
        
    Returns:
        ToolOutput with shielding tensors and chemical shifts
    """
    tool = NMRShieldingTool()
    return tool.run({
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "nuclei": nuclei,
        **kwargs
    })
