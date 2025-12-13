"""
Thermochemistry Calculation Tool.

MCP tool for computing thermodynamic properties from vibrational
frequencies and electronic structure data.

Key Functions:
    - calculate_thermochemistry: Convenience function
    
Key Classes:
    - ThermochemistryTool: MCP tool class
    - ThermochemistryToolInput: Input schema
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
from psi4_mcp.runners.frequency_runner import run_thermochemistry


logger = logging.getLogger(__name__)


# =============================================================================
# INPUT SCHEMA
# =============================================================================

class ThermochemistryToolInput(ToolInput):
    """
    Input schema for thermochemistry calculation tool.
    
    Attributes:
        frequencies: List of vibrational frequencies (cm^-1).
        electronic_energy: Electronic energy (Hartree).
        molecular_mass: Molecular mass (amu).
        multiplicity: Spin multiplicity.
        temperature: Temperature (K).
        pressure: Pressure (atm).
        is_linear: Whether molecule is linear.
        symmetry_number: Rotational symmetry number.
        moments_of_inertia: Principal moments of inertia (amu*Å^2).
    """
    
    frequencies: list[float] = Field(
        ...,
        description="Vibrational frequencies in cm^-1",
        min_length=1,
    )
    
    electronic_energy: float = Field(
        ...,
        description="Electronic energy in Hartree",
    )
    
    molecular_mass: float = Field(
        ...,
        description="Molecular mass in amu",
        gt=0,
    )
    
    multiplicity: int = Field(
        default=1,
        description="Spin multiplicity (2S+1)",
        ge=1,
    )
    
    temperature: float = Field(
        default=298.15,
        description="Temperature in K",
        gt=0,
    )
    
    pressure: float = Field(
        default=1.0,
        description="Pressure in atm",
        gt=0,
    )
    
    is_linear: bool = Field(
        default=False,
        description="Whether molecule is linear",
    )
    
    symmetry_number: int = Field(
        default=1,
        description="Rotational symmetry number",
        ge=1,
    )
    
    moments_of_inertia: Optional[list[float]] = Field(
        default=None,
        description="Principal moments of inertia in amu*Å^2",
    )


# =============================================================================
# THERMOCHEMISTRY TOOL
# =============================================================================

@register_tool
class ThermochemistryTool(BaseTool[ThermochemistryToolInput, ToolOutput]):
    """
    MCP tool for thermochemistry calculations.
    
    Computes thermodynamic properties from vibrational frequencies
    using the rigid rotor-harmonic oscillator (RRHO) approximation.
    
    Computed Properties:
        - Zero-point energy (ZPE)
        - Thermal energy
        - Enthalpy (H)
        - Entropy (S)
        - Gibbs free energy (G)
        - Heat capacities (Cv, Cp)
    
    Contributions:
        - Translational
        - Rotational
        - Vibrational
        - Electronic
    """
    
    name: ClassVar[str] = "calculate_thermochemistry"
    description: ClassVar[str] = (
        "Calculate thermodynamic properties from vibrational frequencies. "
        "Computes ZPE, enthalpy, entropy, Gibbs free energy, and heat capacities."
    )
    category: ClassVar[ToolCategory] = ToolCategory.VIBRATIONAL
    version: ClassVar[str] = "1.0.0"
    
    @classmethod
    def get_input_schema(cls) -> dict[str, Any]:
        """Get JSON schema for input validation."""
        return {
            "frequencies": {
                "type": "array",
                "items": {"type": "number"},
                "description": "Vibrational frequencies in cm^-1",
            },
            "electronic_energy": {
                "type": "number",
                "description": "Electronic energy in Hartree",
            },
            "molecular_mass": {
                "type": "number",
                "description": "Molecular mass in amu",
            },
            "temperature": {
                "type": "number",
                "description": "Temperature in K",
                "default": 298.15,
            },
            "pressure": {
                "type": "number",
                "description": "Pressure in atm",
                "default": 1.0,
            },
            "multiplicity": {
                "type": "integer",
                "description": "Spin multiplicity",
                "default": 1,
            },
            "is_linear": {
                "type": "boolean",
                "description": "Whether molecule is linear",
                "default": False,
            },
            "symmetry_number": {
                "type": "integer",
                "description": "Rotational symmetry number",
                "default": 1,
            },
        }
    
    def _execute(self, input_data: ThermochemistryToolInput) -> Result[ToolOutput]:
        """Execute thermochemistry calculation."""
        try:
            # Physical constants
            HARTREE_TO_KCAL = 627.5095
            HARTREE_TO_KJ = 2625.5
            CM_TO_HARTREE = 4.55634e-6
            BOLTZMANN_AU = 3.16683e-6  # Hartree/K
            GAS_CONSTANT = 8.31446  # J/(mol·K)
            
            T = input_data.temperature
            P = input_data.pressure
            mult = input_data.multiplicity
            
            # Filter out imaginary frequencies
            real_freqs = [f for f in input_data.frequencies if f > 0]
            
            # Zero-point energy
            zpe_hartree = 0.5 * sum(f * CM_TO_HARTREE for f in real_freqs)
            
            # Vibrational contributions
            e_vib = 0.0
            s_vib = 0.0
            cv_vib = 0.0
            
            for freq in real_freqs:
                theta = freq * CM_TO_HARTREE / BOLTZMANN_AU  # Vibrational temperature
                x = theta / T
                
                if x < 100:  # Avoid overflow
                    exp_x = __import__("math").exp(x)
                    # Vibrational energy (without ZPE)
                    e_vib += BOLTZMANN_AU * T * x / (exp_x - 1)
                    # Vibrational entropy
                    s_vib += BOLTZMANN_AU * (x / (exp_x - 1) - __import__("math").log(1 - 1/exp_x))
                    # Vibrational heat capacity
                    cv_vib += BOLTZMANN_AU * x**2 * exp_x / (exp_x - 1)**2
            
            # Translational contributions
            e_trans = 1.5 * BOLTZMANN_AU * T
            s_trans = BOLTZMANN_AU * (2.5 + __import__("math").log(
                (2 * __import__("math").pi * input_data.molecular_mass * 1836.15267 * 
                 BOLTZMANN_AU * T / (2 * __import__("math").pi))**1.5 / P
            ))
            cv_trans = 1.5 * BOLTZMANN_AU
            
            # Rotational contributions (simplified)
            if input_data.is_linear:
                e_rot = BOLTZMANN_AU * T
                cv_rot = BOLTZMANN_AU
                # s_rot simplified
                s_rot = BOLTZMANN_AU * 1.5
            else:
                e_rot = 1.5 * BOLTZMANN_AU * T
                cv_rot = 1.5 * BOLTZMANN_AU
                s_rot = BOLTZMANN_AU * 2.0
            
            # Electronic contribution
            e_elec = 0.0
            s_elec = BOLTZMANN_AU * __import__("math").log(mult)
            cv_elec = 0.0
            
            # Total thermal energy (Hartree)
            e_thermal = e_trans + e_rot + e_vib + e_elec + zpe_hartree
            
            # Enthalpy: H = E + RT (RT = PV for ideal gas)
            h = input_data.electronic_energy + e_thermal + BOLTZMANN_AU * T
            
            # Entropy (Hartree/K)
            s_total = s_trans + s_rot + s_vib + s_elec
            
            # Gibbs free energy: G = H - TS
            g = h - T * s_total
            
            # Heat capacities
            cv_total = cv_trans + cv_rot + cv_vib + cv_elec
            cp_total = cv_total + BOLTZMANN_AU  # Cp = Cv + R for ideal gas
            
            # Convert to standard units for output
            data = {
                "temperature": T,
                "temperature_unit": "K",
                "pressure": P,
                "pressure_unit": "atm",
                "electronic_energy": {
                    "hartree": input_data.electronic_energy,
                    "kcal_mol": input_data.electronic_energy * HARTREE_TO_KCAL,
                    "kJ_mol": input_data.electronic_energy * HARTREE_TO_KJ,
                },
                "zero_point_energy": {
                    "hartree": zpe_hartree,
                    "kcal_mol": zpe_hartree * HARTREE_TO_KCAL,
                    "kJ_mol": zpe_hartree * HARTREE_TO_KJ,
                },
                "thermal_energy": {
                    "hartree": e_thermal,
                    "kcal_mol": e_thermal * HARTREE_TO_KCAL,
                    "kJ_mol": e_thermal * HARTREE_TO_KJ,
                },
                "enthalpy": {
                    "hartree": h,
                    "kcal_mol": h * HARTREE_TO_KCAL,
                    "kJ_mol": h * HARTREE_TO_KJ,
                },
                "entropy": {
                    "hartree_per_K": s_total,
                    "cal_mol_K": s_total * HARTREE_TO_KCAL * 1000,
                    "J_mol_K": s_total * HARTREE_TO_KJ * 1000,
                },
                "gibbs_free_energy": {
                    "hartree": g,
                    "kcal_mol": g * HARTREE_TO_KCAL,
                    "kJ_mol": g * HARTREE_TO_KJ,
                },
                "heat_capacity_cv": {
                    "hartree_per_K": cv_total,
                    "cal_mol_K": cv_total * HARTREE_TO_KCAL * 1000,
                    "J_mol_K": cv_total * HARTREE_TO_KJ * 1000,
                },
                "heat_capacity_cp": {
                    "hartree_per_K": cp_total,
                    "cal_mol_K": cp_total * HARTREE_TO_KCAL * 1000,
                    "J_mol_K": cp_total * HARTREE_TO_KJ * 1000,
                },
                "n_frequencies": len(real_freqs),
                "multiplicity": mult,
            }
            
            message = (
                f"Thermochemistry calculation completed at T={T:.2f} K, P={P:.2f} atm\n"
                f"Zero-point energy: {zpe_hartree * HARTREE_TO_KCAL:.2f} kcal/mol\n"
                f"Enthalpy (H): {h * HARTREE_TO_KCAL:.2f} kcal/mol\n"
                f"Entropy (S): {s_total * HARTREE_TO_KCAL * 1000:.2f} cal/(mol·K)\n"
                f"Gibbs free energy (G): {g * HARTREE_TO_KCAL:.2f} kcal/mol"
            )
            
            return Result.success(ToolOutput(
                success=True,
                message=message,
                data=data,
            ))
            
        except Exception as e:
            logger.exception("Thermochemistry calculation failed")
            return Result.failure(CalculationError(
                code="THERMOCHEMISTRY_ERROR",
                message=str(e),
            ))


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def calculate_thermochemistry(
    frequencies: list[float],
    electronic_energy: float,
    molecular_mass: float,
    multiplicity: int = 1,
    temperature: float = 298.15,
    pressure: float = 1.0,
    is_linear: bool = False,
    symmetry_number: int = 1,
    **kwargs: Any,
) -> ToolOutput:
    """
    Calculate thermodynamic properties.
    
    Args:
        frequencies: Vibrational frequencies (cm^-1).
        electronic_energy: Electronic energy (Hartree).
        molecular_mass: Molecular mass (amu).
        multiplicity: Spin multiplicity.
        temperature: Temperature (K).
        pressure: Pressure (atm).
        is_linear: Whether molecule is linear.
        symmetry_number: Rotational symmetry number.
        
    Returns:
        ToolOutput with thermochemistry results.
        
    Examples:
        >>> result = calculate_thermochemistry(
        ...     frequencies=[1500, 3000, 3100],
        ...     electronic_energy=-76.0,
        ...     molecular_mass=18.015,
        ...     temperature=298.15
        ... )
    """
    tool = ThermochemistryTool()
    
    input_data = {
        "frequencies": frequencies,
        "electronic_energy": electronic_energy,
        "molecular_mass": molecular_mass,
        "multiplicity": multiplicity,
        "temperature": temperature,
        "pressure": pressure,
        "is_linear": is_linear,
        "symmetry_number": symmetry_number,
    }
    
    return tool.run(input_data)
