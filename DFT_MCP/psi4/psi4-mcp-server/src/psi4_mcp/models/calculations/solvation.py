"""
Solvation Calculation Models.

Pydantic models for implicit solvation calculations:
    - PCM (Polarizable Continuum Model)
    - CPCM (Conductor-like PCM)
    - IEF-PCM (Integral Equation Formalism)
    - SMD (Solvation Model based on Density)
    - ddCOSMO
"""

from typing import Any, Optional, Literal
from pydantic import Field

from psi4_mcp.models.base import BaseInput, BaseOutput
from psi4_mcp.models.molecules import MoleculeInput


# =============================================================================
# SOLVENT SPECIFICATIONS
# =============================================================================

class Solvent(BaseOutput):
    """
    Solvent specification.
    
    Attributes:
        name: Solvent name.
        dielectric: Dielectric constant (ε).
        optical_dielectric: Optical dielectric constant (ε∞).
        probe_radius: Solvent probe radius (Å).
    """
    
    name: str = Field(description="Solvent name")
    dielectric: float = Field(gt=1, description="Dielectric constant")
    optical_dielectric: Optional[float] = Field(
        default=None,
        description="Optical dielectric (for nonequilibrium)"
    )
    probe_radius: float = Field(default=1.4, gt=0, description="Probe radius (Å)")


# Common solvents
COMMON_SOLVENTS = {
    "water": Solvent(name="water", dielectric=78.39, optical_dielectric=1.78, probe_radius=1.4),
    "methanol": Solvent(name="methanol", dielectric=32.7, optical_dielectric=1.76, probe_radius=1.85),
    "ethanol": Solvent(name="ethanol", dielectric=24.55, optical_dielectric=1.85, probe_radius=2.18),
    "acetonitrile": Solvent(name="acetonitrile", dielectric=36.6, optical_dielectric=1.81, probe_radius=2.18),
    "dmso": Solvent(name="dmso", dielectric=46.7, optical_dielectric=2.02, probe_radius=2.455),
    "chloroform": Solvent(name="chloroform", dielectric=4.81, optical_dielectric=2.09, probe_radius=2.48),
    "thf": Solvent(name="thf", dielectric=7.58, optical_dielectric=1.97, probe_radius=2.52),
    "toluene": Solvent(name="toluene", dielectric=2.38, optical_dielectric=2.24, probe_radius=2.82),
    "hexane": Solvent(name="hexane", dielectric=1.88, optical_dielectric=1.89, probe_radius=2.99),
}


# =============================================================================
# SOLVATION INPUT MODELS
# =============================================================================

class SolvationInput(BaseInput):
    """
    Base input for solvation calculations.
    
    Attributes:
        molecule: Molecular specification.
        method: QM method.
        basis: Basis set name.
        solvent: Solvent specification.
        solvation_model: Solvation model to use.
    """
    
    molecule: MoleculeInput = Field(..., description="Molecular specification")
    method: str = Field(default="hf", description="Calculation method")
    basis: str = Field(default="cc-pvdz", description="Basis set")
    solvent: str | Solvent = Field(
        default="water",
        description="Solvent name or specification"
    )
    solvation_model: Literal["pcm", "cpcm", "iefpcm", "smd", "ddcosmo"] = Field(
        default="pcm",
        description="Solvation model"
    )
    
    def get_solvent(self) -> Solvent:
        """Get solvent specification."""
        if isinstance(self.solvent, Solvent):
            return self.solvent
        return COMMON_SOLVENTS.get(self.solvent.lower(), 
                                    Solvent(name=self.solvent, dielectric=78.39))
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        solvent = self.get_solvent()
        options = {
            "basis": self.basis,
            "pcm": True,
            "pcm_scf_type": "total",
        }
        return options


class PCMInput(SolvationInput):
    """
    PCM (Polarizable Continuum Model) input.
    
    Attributes:
        cavity_type: Cavity type (gepol, vdw).
        radii: Atomic radii set (bondi, uff).
        scaling: Radii scaling factor.
    """
    solvation_model: Literal["pcm"] = "pcm"
    cavity_type: Literal["gepol", "vdw", "ses", "sas"] = Field(
        default="gepol",
        description="Cavity type"
    )
    radii: Literal["bondi", "uff", "allinger"] = Field(
        default="bondi",
        description="Atomic radii set"
    )
    scaling: float = Field(default=1.2, gt=0, description="Radii scaling factor")


class CPCMInput(SolvationInput):
    """CPCM (Conductor-like PCM) input."""
    solvation_model: Literal["cpcm"] = "cpcm"


class IEFPCMInput(SolvationInput):
    """IEF-PCM input."""
    solvation_model: Literal["iefpcm"] = "iefpcm"


class SMDInput(SolvationInput):
    """
    SMD (Solvation Model based on Density) input.
    
    SMD includes nonelectrostatic contributions (cavitation,
    dispersion, solvent structure) in addition to electrostatics.
    """
    solvation_model: Literal["smd"] = "smd"
    # SMD uses specific cavity/dispersion parameters


class ddCOSMOInput(SolvationInput):
    """
    ddCOSMO (domain decomposition COSMO) input.
    
    Efficient COSMO implementation using domain decomposition.
    """
    solvation_model: Literal["ddcosmo"] = "ddcosmo"
    lmax: int = Field(default=10, ge=0, description="Max angular momentum")


# =============================================================================
# SOLVATION OUTPUT MODELS
# =============================================================================

class SolvationEnergy(BaseOutput):
    """Solvation energy decomposition."""
    total_solvation_energy: float = Field(description="Total solvation energy")
    electrostatic: float = Field(description="Electrostatic contribution")
    cavitation: Optional[float] = Field(default=None, description="Cavitation energy")
    dispersion: Optional[float] = Field(default=None, description="Dispersion energy")
    repulsion: Optional[float] = Field(default=None, description="Repulsion energy")
    solvent_structure: Optional[float] = Field(
        default=None, description="Solvent structure contribution"
    )
    unit: str = Field(default="kcal/mol")


class SolvationOutput(BaseOutput):
    """
    Solvation calculation output.
    
    Attributes:
        gas_phase_energy: Gas phase energy.
        solution_phase_energy: Solution phase energy.
        solvation_energy: Solvation free energy.
        energy_components: Decomposed energy contributions.
    """
    
    gas_phase_energy: Optional[float] = Field(
        default=None, description="Gas phase energy (Hartree)"
    )
    solution_phase_energy: float = Field(
        description="Solution phase energy (Hartree)"
    )
    solvation_energy: SolvationEnergy = Field(
        description="Solvation energy components"
    )
    solvent: str = Field(description="Solvent used")
    dielectric: float = Field(description="Dielectric constant")
    solvation_model: str = Field(description="Solvation model")
    method: str = Field(description="QM method")
    basis: str = Field(description="Basis set")
    
    @property
    def delta_g_solv(self) -> float:
        """Solvation free energy in kcal/mol."""
        return self.solvation_energy.total_solvation_energy


class PCMOutput(SolvationOutput):
    """PCM-specific output."""
    solvation_model: str = "PCM"
    cavity_surface_area: Optional[float] = Field(default=None, description="Å²")
    cavity_volume: Optional[float] = Field(default=None, description="Å³")


class SMDOutput(SolvationOutput):
    """SMD-specific output."""
    solvation_model: str = "SMD"
    # SMD has additional CDS (cavity-dispersion-solvent structure) terms
    cds_energy: Optional[float] = Field(default=None, description="CDS energy")
