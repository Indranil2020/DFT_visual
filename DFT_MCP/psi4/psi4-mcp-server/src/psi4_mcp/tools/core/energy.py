"""
Energy Calculation Tool.

MCP tool for computing single-point energies using various quantum
chemistry methods (HF, DFT, MP2, CCSD, etc.).

Key Functions:
    - calculate_energy: Convenience function for energy calculations
    
Key Classes:
    - EnergyTool: MCP tool class for energy calculations
    - EnergyToolInput: Input schema for energy tool
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
from psi4_mcp.models.calculations.energy import EnergyInput, MoleculeInput
from psi4_mcp.models.outputs.energy import TotalEnergyOutput
from psi4_mcp.runners.energy_runner import EnergyRunner, run_energy
from psi4_mcp.runners.base_runner import RunnerConfig


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class EnergyToolInput(ToolInput):
    """
    Input schema for energy calculation tool.
    
    Attributes:
        geometry: Molecular geometry (XYZ or Psi4 format).
        method: Calculation method (hf, b3lyp, mp2, ccsd, etc.).
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        reference: Reference wavefunction (rhf, uhf, rohf).
        memory: Memory limit in MB.
        n_threads: Number of threads.
        options: Additional Psi4 options.
    """
    
    geometry: str = Field(
        ...,
        description="Molecular geometry in XYZ or Psi4 format",
        examples=[
            "O 0.0 0.0 0.0\nH 0.0 0.0 0.96\nH 0.0 0.96 0.0",
            "H 0.0 0.0 0.0\nH 0.0 0.0 0.74",
        ],
    )
    
    method: str = Field(
        default="hf",
        description="Calculation method",
        examples=["hf", "b3lyp", "mp2", "ccsd", "ccsd(t)"],
    )
    
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set",
        examples=["sto-3g", "6-31g*", "cc-pvdz", "cc-pvtz", "def2-tzvp"],
    )
    
    charge: int = Field(
        default=0,
        description="Molecular charge",
        ge=-10,
        le=10,
    )
    
    multiplicity: int = Field(
        default=1,
        description="Spin multiplicity (2S+1)",
        ge=1,
        le=10,
    )
    
    reference: Optional[str] = Field(
        default=None,
        description="Reference wavefunction type",
        examples=["rhf", "uhf", "rohf", "rks", "uks"],
    )
    
    memory: int = Field(
        default=2000,
        description="Memory limit in MB",
        ge=100,
        le=500000,
    )
    
    n_threads: int = Field(
        default=1,
        description="Number of threads",
        ge=1,
        le=256,
    )
    
    options: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional Psi4 options",
    )


# =============================================================================
# ENERGY TOOL
# =============================================================================

@register_tool
class EnergyTool(BaseTool[EnergyToolInput, ToolOutput]):
    """
    MCP tool for single-point energy calculations.
    
    Computes the electronic energy of a molecule using various
    quantum chemistry methods including HF, DFT, MP2, and coupled cluster.
    
    Supported Methods:
        - Hartree-Fock (hf, rhf, uhf, rohf)
        - DFT (b3lyp, pbe, m06-2x, wb97x-d, etc.)
        - MP2, MP3, MP4
        - CCSD, CCSD(T), CC2, CC3
        - CISD, FCI
    
    Returns:
        Energy output including:
        - Total electronic energy
        - SCF energy components
        - Correlation energy (if applicable)
        - Nuclear repulsion energy
    
    Example:
        >>> result = calculate_energy(
        ...     geometry="O 0 0 0\\nH 0 0 0.96\\nH 0 0.96 0",
        ...     method="b3lyp",
        ...     basis="def2-tzvp"
        ... )
    """
    
    # Class-level metadata
    name: ClassVar[str] = "calculate_energy"
    description: ClassVar[str] = (
        "Calculate the electronic energy of a molecule using quantum chemistry methods. "
        "Supports HF, DFT, MP2, CCSD, and many other methods."
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
                "description": "Calculation method (hf, b3lyp, mp2, ccsd, etc.)",
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
            "reference": {
                "type": "string",
                "description": "Reference wavefunction type (rhf, uhf, rohf)",
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
            "options": {
                "type": "object",
                "description": "Additional Psi4 options",
            },
        }
    
    def _execute(self, input_data: EnergyToolInput) -> Result[ToolOutput]:
        """Execute energy calculation."""
        try:
            # Build options dictionary
            options = input_data.options or {}
            if input_data.reference:
                options["reference"] = input_data.reference
            
            # Run energy calculation using runner
            result = run_energy(
                geometry=input_data.geometry,
                method=input_data.method,
                basis=input_data.basis,
                charge=input_data.charge,
                multiplicity=input_data.multiplicity,
                memory=input_data.memory,
                n_threads=input_data.n_threads,
                **options,
            )
            
            if result.is_failure:
                return Result.failure(result.error)
            
            # Extract output data
            energy_output = result.value
            
            # Build response data
            data = {
                "total_energy": energy_output.total_energy,
                "total_energy_unit": "Hartree",
                "method": input_data.method,
                "basis": input_data.basis,
            }
            
            # Add optional components
            if energy_output.scf_output:
                data["scf_energy"] = energy_output.scf_output.total_energy
                if energy_output.scf_output.components:
                    data["nuclear_repulsion"] = energy_output.scf_output.components.nuclear_repulsion
            
            if energy_output.correlation_output:
                data["correlation_energy"] = energy_output.correlation_output.correlation_energy
            
            if energy_output.dft_output:
                data["dft_functional"] = energy_output.dft_output.functional
                if energy_output.dft_output.components:
                    data["xc_energy"] = energy_output.dft_output.components.exchange_correlation
            
            if energy_output.molecular_formula:
                data["molecular_formula"] = energy_output.molecular_formula
            
            if energy_output.point_group:
                data["point_group"] = energy_output.point_group
            
            # Create success message
            message = (
                f"Energy calculation completed: {input_data.method}/{input_data.basis}\n"
                f"Total energy: {energy_output.total_energy:.10f} Hartree"
            )
            
            output = ToolOutput(
                success=True,
                message=message,
                data=data,
            )
            
            return Result.success(output)
            
        except Exception as e:
            logger.exception("Energy calculation failed")
            return Result.failure(CalculationError(
                code="ENERGY_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_energy(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    reference: Optional[str] = None,
    memory: int = 2000,
    n_threads: int = 1,
    **options: Any,
) -> ToolOutput:
    """
    Calculate single-point energy.
    
    This is the main convenience function for energy calculations.
    
    Args:
        geometry: Molecular geometry string (XYZ or Psi4 format).
        method: Calculation method (hf, b3lyp, mp2, ccsd, etc.).
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity (2S+1).
        reference: Reference wavefunction type.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        **options: Additional Psi4 options.
        
    Returns:
        ToolOutput with energy calculation results.
        
    Examples:
        >>> # Basic HF calculation
        >>> result = calculate_energy(
        ...     geometry="H 0 0 0\\nH 0 0 0.74",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        
        >>> # DFT with B3LYP
        >>> result = calculate_energy(
        ...     geometry="O 0 0 0\\nH 0 0 0.96\\nH 0 0.96 0",
        ...     method="b3lyp",
        ...     basis="def2-tzvp"
        ... )
        
        >>> # MP2 calculation
        >>> result = calculate_energy(
        ...     geometry="C 0 0 0\\nO 0 0 1.128",
        ...     method="mp2",
        ...     basis="cc-pvtz"
        ... )
    """
    tool = EnergyTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "memory": memory,
        "n_threads": n_threads,
    }
    
    if reference:
        input_data["reference"] = reference
    
    if options:
        input_data["options"] = options
    
    return tool.run(input_data)


# =============================================================================
# SPECIALIZED ENERGY FUNCTIONS
# =============================================================================

def calculate_hf_energy(
    geometry: str,
    basis: str = "cc-pvdz",
    reference: str = "rhf",
    **kwargs: Any,
) -> ToolOutput:
    """Calculate Hartree-Fock energy."""
    return calculate_energy(
        geometry=geometry,
        method=reference,
        basis=basis,
        reference=reference,
        **kwargs,
    )


def calculate_dft_energy(
    geometry: str,
    functional: str = "b3lyp",
    basis: str = "def2-tzvp",
    dispersion: Optional[str] = None,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate DFT energy."""
    method = functional
    if dispersion:
        method = f"{functional}-{dispersion}"
    
    return calculate_energy(
        geometry=geometry,
        method=method,
        basis=basis,
        **kwargs,
    )


def calculate_mp2_energy(
    geometry: str,
    basis: str = "cc-pvtz",
    frozen_core: bool = True,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate MP2 energy."""
    options = kwargs.pop("options", {}) or {}
    options["freeze_core"] = frozen_core
    
    return calculate_energy(
        geometry=geometry,
        method="mp2",
        basis=basis,
        options=options,
        **kwargs,
    )


def calculate_ccsd_energy(
    geometry: str,
    basis: str = "cc-pvdz",
    frozen_core: bool = True,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate CCSD energy."""
    options = kwargs.pop("options", {}) or {}
    options["freeze_core"] = frozen_core
    
    return calculate_energy(
        geometry=geometry,
        method="ccsd",
        basis=basis,
        options=options,
        **kwargs,
    )


def calculate_ccsd_t_energy(
    geometry: str,
    basis: str = "cc-pvdz",
    frozen_core: bool = True,
    **kwargs: Any,
) -> ToolOutput:
    """Calculate CCSD(T) energy."""
    options = kwargs.pop("options", {}) or {}
    options["freeze_core"] = frozen_core
    
    return calculate_energy(
        geometry=geometry,
        method="ccsd(t)",
        basis=basis,
        options=options,
        **kwargs,
    )
