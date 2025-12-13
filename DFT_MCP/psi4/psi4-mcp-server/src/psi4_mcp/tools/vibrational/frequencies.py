"""
Frequency Calculation Tool.

MCP tool for computing harmonic vibrational frequencies and
related spectroscopic properties.

Key Functions:
    - calculate_frequencies: Convenience function for frequency calculations
    
Key Classes:
    - FrequencyTool: MCP tool class for frequency calculations
    - FrequencyToolInput: Input schema for frequency tool
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
from psi4_mcp.runners.frequency_runner import FrequencyRunner, run_frequencies
from psi4_mcp.runners.base_runner import RunnerConfig


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class FrequencyToolInput(ToolInput):
    """
    Input schema for frequency calculation tool.
    
    Attributes:
        geometry: Molecular geometry (XYZ or Psi4 format).
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        temperature: Temperature for thermochemistry (K).
        pressure: Pressure for thermochemistry (atm).
        scale_factor: Frequency scaling factor.
        compute_ir: Compute IR intensities.
        compute_raman: Compute Raman activities.
        compute_thermo: Compute thermochemistry.
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
    
    temperature: float = Field(
        default=298.15,
        description="Temperature for thermochemistry (K)",
        gt=0,
    )
    
    pressure: float = Field(
        default=1.0,
        description="Pressure for thermochemistry (atm)",
        gt=0,
    )
    
    scale_factor: float = Field(
        default=1.0,
        description="Frequency scaling factor",
        gt=0,
        le=2.0,
    )
    
    compute_ir: bool = Field(
        default=True,
        description="Compute IR intensities",
    )
    
    compute_raman: bool = Field(
        default=False,
        description="Compute Raman activities",
    )
    
    compute_thermo: bool = Field(
        default=True,
        description="Compute thermochemistry",
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
# FREQUENCY TOOL
# =============================================================================

@register_tool
class FrequencyTool(BaseTool[FrequencyToolInput, ToolOutput]):
    """
    MCP tool for vibrational frequency calculations.
    
    Computes harmonic vibrational frequencies and optionally
    IR intensities, Raman activities, and thermochemistry.
    
    The tool can characterize stationary points:
        - All real frequencies → minimum
        - One imaginary frequency → transition state
        - Multiple imaginary → higher-order saddle point
    
    Returns:
        Frequency output including:
        - List of vibrational frequencies (cm^-1)
        - IR intensities (km/mol)
        - Raman activities (Å^4/amu)
        - Zero-point energy
        - Thermodynamic quantities
    """
    
    name: ClassVar[str] = "calculate_frequencies"
    description: ClassVar[str] = (
        "Calculate harmonic vibrational frequencies, IR/Raman intensities, "
        "and thermochemistry. Use to characterize stationary points and "
        "compute thermodynamic properties."
    )
    category: ClassVar[ToolCategory] = ToolCategory.VIBRATIONAL
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
            "temperature": {
                "type": "number",
                "description": "Temperature for thermochemistry (K)",
                "default": 298.15,
            },
            "pressure": {
                "type": "number",
                "description": "Pressure for thermochemistry (atm)",
                "default": 1.0,
            },
            "scale_factor": {
                "type": "number",
                "description": "Frequency scaling factor",
                "default": 1.0,
            },
            "compute_thermo": {
                "type": "boolean",
                "description": "Compute thermochemistry",
                "default": True,
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
    
    def _execute(self, input_data: FrequencyToolInput) -> Result[ToolOutput]:
        """Execute frequency calculation."""
        try:
            # Run frequency calculation
            result = run_frequencies(
                geometry=input_data.geometry,
                method=input_data.method,
                basis=input_data.basis,
                charge=input_data.charge,
                multiplicity=input_data.multiplicity,
                temperature=input_data.temperature,
                pressure=input_data.pressure,
                scale_factor=input_data.scale_factor,
                memory=input_data.memory,
                n_threads=input_data.n_threads,
            )
            
            if result.is_failure:
                return Result.failure(result.error)
            
            freq_output = result.value
            
            # Extract frequencies
            frequencies = []
            ir_intensities = []
            
            for mode in freq_output.modes:
                frequencies.append(mode.frequency)
                if mode.ir_intensity is not None:
                    ir_intensities.append(mode.ir_intensity)
            
            # Build response data
            data = {
                "electronic_energy": freq_output.electronic_energy,
                "zero_point_energy": freq_output.zero_point_energy,
                "zero_point_corrected_energy": freq_output.zero_point_corrected_energy,
                "energy_unit": "Hartree",
                "frequencies": frequencies,
                "frequency_unit": "cm^-1",
                "n_modes": len(frequencies),
                "n_imaginary": freq_output.summary.n_imaginary if freq_output.summary else 0,
                "is_minimum": freq_output.is_minimum,
                "is_transition_state": freq_output.is_transition_state,
                "method": input_data.method,
                "basis": input_data.basis,
                "temperature": input_data.temperature,
            }
            
            if ir_intensities:
                data["ir_intensities"] = ir_intensities
                data["ir_intensity_unit"] = "km/mol"
            
            # Add thermochemistry if computed
            if freq_output.thermodynamics and input_data.compute_thermo:
                thermo = freq_output.thermodynamics
                data["thermochemistry"] = {
                    "temperature": thermo.temperature,
                    "pressure": thermo.pressure,
                    "internal_energy": thermo.internal_energy,
                    "enthalpy": thermo.enthalpy,
                    "entropy": thermo.entropy,
                    "gibbs_free_energy": thermo.gibbs_free_energy,
                    "heat_capacity_cv": thermo.heat_capacity_cv,
                    "heat_capacity_cp": thermo.heat_capacity_cp,
                }
            
            # Characterize stationary point
            if freq_output.is_minimum:
                sp_type = "minimum (all real frequencies)"
            elif freq_output.is_transition_state:
                sp_type = "transition state (one imaginary frequency)"
            else:
                n_imag = freq_output.summary.n_imaginary if freq_output.summary else 0
                sp_type = f"higher-order saddle point ({n_imag} imaginary frequencies)"
            
            data["stationary_point_type"] = sp_type
            
            # Create message
            message = (
                f"Frequency calculation completed: {input_data.method}/{input_data.basis}\n"
                f"Electronic energy: {freq_output.electronic_energy:.10f} Hartree\n"
                f"Zero-point energy: {freq_output.zero_point_energy:.6f} Hartree\n"
                f"Number of modes: {len(frequencies)}\n"
                f"Stationary point: {sp_type}"
            )
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data,
            ))
            
        except Exception as e:
            logger.exception("Frequency calculation failed")
            return Result.failure(CalculationError(
                code="FREQUENCY_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_frequencies(
    geometry: str,
    method: str = "hf",
    basis: str = "cc-pvdz",
    charge: int = 0,
    multiplicity: int = 1,
    temperature: float = 298.15,
    pressure: float = 1.0,
    scale_factor: float = 1.0,
    compute_thermo: bool = True,
    memory: int = 2000,
    n_threads: int = 1,
    **options: Any,
) -> ToolOutput:
    """
    Calculate vibrational frequencies.
    
    Args:
        geometry: Molecular geometry string.
        method: Calculation method.
        basis: Basis set name.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        temperature: Temperature for thermochemistry (K).
        pressure: Pressure for thermochemistry (atm).
        scale_factor: Frequency scaling factor.
        compute_thermo: Compute thermochemistry.
        memory: Memory limit in MB.
        n_threads: Number of threads.
        **options: Additional Psi4 options.
        
    Returns:
        ToolOutput with frequency results.
        
    Examples:
        >>> result = calculate_frequencies(
        ...     geometry="O 0 0 0\\nH 0 0 0.96\\nH 0 0.96 0",
        ...     method="hf",
        ...     basis="cc-pvdz"
        ... )
        >>> print(result.data["frequencies"])
    """
    tool = FrequencyTool()
    
    input_data = {
        "geometry": geometry,
        "method": method,
        "basis": basis,
        "charge": charge,
        "multiplicity": multiplicity,
        "temperature": temperature,
        "pressure": pressure,
        "scale_factor": scale_factor,
        "compute_thermo": compute_thermo,
        "memory": memory,
        "n_threads": n_threads,
    }
    
    if options:
        input_data["options"] = options
    
    return tool.run(input_data)
