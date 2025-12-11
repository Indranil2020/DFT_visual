"""
Energy Calculation Input Models.

This module provides Pydantic models for specifying energy calculation
inputs, including single-point energies, relative energies, and
various method-specific configurations.

Key Classes:
    - EnergyInput: Basic energy calculation input
    - SCFInput: SCF-specific input
    - DFTInput: DFT-specific input
    - CorrelationInput: Post-HF correlation input
    - CompositeInput: Composite method input (G4, CBS, etc.)
"""

from typing import Any, Optional, Literal, Union
from pydantic import Field, field_validator, model_validator

from psi4_mcp.models.base import Psi4BaseModel, CalculationInput
from psi4_mcp.models.options import (
    SCFOptions,
    DFTOptions,
    CorrelationOptions,
    SolvationOptions,
    CalculationOptions,
)


# =============================================================================
# MOLECULE INPUT
# =============================================================================

class MoleculeInput(Psi4BaseModel):
    """
    Molecule specification for calculations.
    
    Can be provided as XYZ string, Psi4 string, or structured data.
    
    Attributes:
        geometry: Geometry as string (XYZ or Psi4 format).
        charge: Molecular charge.
        multiplicity: Spin multiplicity (2S+1).
        units: Coordinate units.
        name: Molecule name.
        symmetry: Point group symmetry (or 'c1' for no symmetry).
        no_reorient: Disable geometry reorientation.
        no_com: Disable center of mass translation.
    """
    
    geometry: str = Field(
        ...,
        min_length=1,
        description="Geometry string (XYZ or Psi4 format)",
    )
    charge: int = Field(
        default=0,
        description="Molecular charge",
    )
    multiplicity: int = Field(
        default=1,
        ge=1,
        description="Spin multiplicity (2S+1)",
    )
    units: Literal["angstrom", "bohr"] = Field(
        default="angstrom",
        description="Coordinate units",
    )
    name: Optional[str] = Field(
        default=None,
        description="Molecule name",
    )
    symmetry: Optional[str] = Field(
        default="c1",
        description="Point group symmetry",
    )
    no_reorient: bool = Field(
        default=True,
        description="Disable reorientation",
    )
    no_com: bool = Field(
        default=True,
        description="Disable COM translation",
    )
    
    def to_psi4_string(self) -> str:
        """Convert to Psi4 molecule specification string."""
        lines = []
        
        # Check if geometry already has charge/multiplicity
        first_line = self.geometry.strip().split('\n')[0].strip()
        has_charge_mult = len(first_line.split()) == 2 and \
                          first_line.split()[0].lstrip('-').isdigit()
        
        if not has_charge_mult:
            lines.append(f"{self.charge} {self.multiplicity}")
        
        lines.append(self.geometry.strip())
        
        # Add options
        lines.append(f"units {self.units}")
        if self.no_reorient:
            lines.append("noreorient")
        if self.no_com:
            lines.append("nocom")
        if self.symmetry:
            lines.append(f"symmetry {self.symmetry}")
        
        return "\n".join(lines)


# =============================================================================
# BASIC ENERGY INPUT
# =============================================================================

class EnergyInput(CalculationInput):
    """
    Basic energy calculation input.
    
    Attributes:
        molecule: Molecule specification.
        method: Calculation method.
        basis: Basis set.
        reference: Reference wavefunction type.
        return_wavefunction: Return wavefunction object.
        properties: Properties to compute along with energy.
        dertype: Derivative type to compute (0=energy, 1=gradient, 2=hessian).
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    return_wavefunction: bool = Field(
        default=True,
        description="Return wavefunction object",
    )
    properties: list[str] = Field(
        default_factory=list,
        description="Properties to compute",
    )
    dertype: int = Field(
        default=0,
        ge=0,
        le=2,
        description="Derivative type (0=energy, 1=grad, 2=hess)",
    )
    
    @field_validator("properties")
    @classmethod
    def validate_properties(cls, v: list[str]) -> list[str]:
        """Validate property names."""
        valid_props = {
            "dipole", "quadrupole", "mulliken_charges", "lowdin_charges",
            "wiberg_bond_indices", "mayer_bond_indices", "no_occupations",
            "grid_esp", "grid_field", "mbis_charges", "mbis_volume_ratios",
        }
        for prop in v:
            if prop.lower() not in valid_props:
                # Allow unknown properties (Psi4 may support more)
                pass
        return [p.lower() for p in v]


# =============================================================================
# SCF INPUT
# =============================================================================

class SCFInput(EnergyInput):
    """
    SCF (Hartree-Fock or DFT) calculation input.
    
    Attributes:
        scf_options: SCF-specific options.
        stability_analysis: Perform stability analysis.
        save_orbitals: Save molecular orbitals to file.
        orbital_file: Filename for orbital output.
    """
    
    scf_options: SCFOptions = Field(
        default_factory=SCFOptions,
        description="SCF options",
    )
    stability_analysis: bool = Field(
        default=False,
        description="Perform stability analysis",
    )
    save_orbitals: bool = Field(
        default=False,
        description="Save orbitals to file",
    )
    orbital_file: Optional[str] = Field(
        default=None,
        description="Orbital filename",
    )
    
    def __init__(self, **data: Any) -> None:
        if "method" not in data:
            data["method"] = "hf"
        super().__init__(**data)
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = self.scf_options.to_psi4_options()
        opts.update(self.options)
        
        if self.stability_analysis:
            opts["stability_analysis"] = "check"
        
        return opts


# =============================================================================
# DFT INPUT
# =============================================================================

class DFTInput(EnergyInput):
    """
    DFT calculation input.
    
    Attributes:
        functional: DFT functional name.
        scf_options: SCF options.
        dft_options: DFT-specific options.
        dispersion: Dispersion correction type.
        grid: DFT integration grid.
    """
    
    functional: str = Field(
        default="b3lyp",
        description="DFT functional",
    )
    scf_options: SCFOptions = Field(
        default_factory=SCFOptions,
        description="SCF options",
    )
    dft_options: DFTOptions = Field(
        default_factory=DFTOptions,
        description="DFT options",
    )
    dispersion: Optional[str] = Field(
        default=None,
        description="Dispersion correction (d3, d3bj, d4)",
    )
    grid: str = Field(
        default="default",
        description="DFT grid (coarse, default, fine, ultrafine)",
    )
    
    def __init__(self, **data: Any) -> None:
        # Set method to functional
        if "functional" in data:
            data["method"] = data["functional"]
        elif "method" not in data:
            data["method"] = "b3lyp"
        super().__init__(**data)
    
    @model_validator(mode="after")
    def sync_functional(self) -> "DFTInput":
        """Sync functional with method."""
        if self.method != self.functional:
            object.__setattr__(self, 'method', self.functional)
        return self
    
    @field_validator("functional")
    @classmethod
    def validate_functional(cls, v: str) -> str:
        """Normalize functional name."""
        return v.lower().strip().replace("_", "-")
    
    @field_validator("dispersion")
    @classmethod
    def validate_dispersion(cls, v: Optional[str]) -> Optional[str]:
        """Validate dispersion correction."""
        if v is None:
            return None
        valid = {"d2", "d3", "d3bj", "d3m", "d3mbj", "d4", "nl"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid dispersion: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = self.scf_options.to_psi4_options()
        opts.update(self.dft_options.to_psi4_options())
        opts.update(self.options)
        
        # Set DFT-specific reference
        if self.scf_options.reference in ("rhf", "uhf", "rohf"):
            ref_map = {"rhf": "rks", "uhf": "uks", "rohf": "roks"}
            opts["reference"] = ref_map.get(
                self.scf_options.reference, 
                self.scf_options.reference
            )
        
        return opts
    
    def get_method_string(self) -> str:
        """Get full method string including dispersion."""
        if self.dispersion:
            return f"{self.functional}-{self.dispersion}"
        return self.functional


# =============================================================================
# CORRELATION INPUT
# =============================================================================

class MP2Input(EnergyInput):
    """
    MP2 calculation input.
    
    Attributes:
        correlation_options: Correlation method options.
        mp2_type: MP2 algorithm type.
        scs: Use spin-component-scaled MP2.
        scs_ps: SCS opposite-spin scaling factor.
        scs_pt: SCS same-spin scaling factor.
        sos: Use scaled opposite-spin MP2.
        nat_orbs: Compute natural orbitals.
    """
    
    correlation_options: CorrelationOptions = Field(
        default_factory=CorrelationOptions,
        description="Correlation options",
    )
    mp2_type: str = Field(
        default="df",
        description="MP2 type (conv, df, cd)",
    )
    scs: bool = Field(
        default=False,
        description="Use SCS-MP2",
    )
    scs_ps: float = Field(
        default=1.2,
        description="SCS opposite-spin factor",
    )
    scs_pt: float = Field(
        default=0.33333333,
        description="SCS same-spin factor",
    )
    sos: bool = Field(
        default=False,
        description="Use SOS-MP2",
    )
    nat_orbs: bool = Field(
        default=False,
        description="Compute natural orbitals",
    )
    
    def __init__(self, **data: Any) -> None:
        if "method" not in data:
            data["method"] = "mp2"
        super().__init__(**data)
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = self.correlation_options.to_psi4_options()
        opts["mp2_type"] = self.mp2_type
        opts.update(self.options)
        
        if self.scs:
            opts["mp2_os_scale"] = self.scs_ps
            opts["mp2_ss_scale"] = self.scs_pt
        elif self.sos:
            opts["mp2_os_scale"] = 1.3
            opts["mp2_ss_scale"] = 0.0
        
        if self.nat_orbs:
            opts["nat_orbs"] = True
        
        return opts


class CoupledClusterInput(EnergyInput):
    """
    Coupled cluster calculation input.
    
    Attributes:
        cc_method: CC method (ccsd, ccsd(t), cc2, cc3).
        correlation_options: Correlation options.
        cc_type: CC algorithm type.
        local: Use local correlation.
        pno: Use PNO approximation.
        t1_diagnostic: Compute T1 diagnostic.
        brueckner: Use Brueckner orbitals.
    """
    
    cc_method: str = Field(
        default="ccsd(t)",
        description="CC method",
    )
    correlation_options: CorrelationOptions = Field(
        default_factory=CorrelationOptions,
        description="Correlation options",
    )
    cc_type: str = Field(
        default="conv",
        description="CC type (conv, df, cd)",
    )
    local: bool = Field(
        default=False,
        description="Use local correlation",
    )
    pno: bool = Field(
        default=False,
        description="Use PNO approximation",
    )
    t1_diagnostic: bool = Field(
        default=True,
        description="Compute T1 diagnostic",
    )
    brueckner: bool = Field(
        default=False,
        description="Use Brueckner orbitals",
    )
    
    def __init__(self, **data: Any) -> None:
        if "method" not in data:
            data["method"] = data.get("cc_method", "ccsd(t)")
        super().__init__(**data)
    
    @field_validator("cc_method")
    @classmethod
    def validate_cc_method(cls, v: str) -> str:
        """Validate CC method."""
        valid = {
            "ccsd", "ccsd(t)", "cc2", "cc3", "ccsdt", "ccsdt(q)",
            "bccd", "bccd(t)", "a-ccsd(t)", "eom-ccsd",
        }
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid CC method: {v}. Must be one of {valid}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts = self.correlation_options.to_psi4_options()
        opts["cc_type"] = self.cc_type
        opts.update(self.options)
        
        if self.brueckner:
            # Modify method to Brueckner variant
            pass
        
        return opts


class CIInput(EnergyInput):
    """
    Configuration Interaction calculation input.
    
    Attributes:
        ci_method: CI method (cisd, fci, casci, etc.).
        correlation_options: Correlation options.
        num_roots: Number of CI roots.
        active_space: Active space specification [n_electrons, n_orbitals].
        active_orbitals: Specific orbital indices for active space.
    """
    
    ci_method: str = Field(
        default="cisd",
        description="CI method",
    )
    correlation_options: CorrelationOptions = Field(
        default_factory=CorrelationOptions,
        description="Correlation options",
    )
    num_roots: int = Field(
        default=1,
        ge=1,
        description="Number of CI roots",
    )
    active_space: Optional[list[int]] = Field(
        default=None,
        description="Active space [n_elec, n_orb]",
    )
    active_orbitals: Optional[list[int]] = Field(
        default=None,
        description="Active orbital indices",
    )
    
    def __init__(self, **data: Any) -> None:
        if "method" not in data:
            data["method"] = data.get("ci_method", "cisd")
        super().__init__(**data)
    
    @field_validator("ci_method")
    @classmethod
    def validate_ci_method(cls, v: str) -> str:
        """Validate CI method."""
        valid = {"cis", "cisd", "cisdt", "cisdtq", "fci", "casci", "detci"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid CI method: {v}. Must be one of {valid}")
        return normalized


# =============================================================================
# COMPOSITE METHOD INPUT
# =============================================================================

class CompositeInput(Psi4BaseModel):
    """
    Composite method calculation input (G4, CBS, etc.).
    
    Attributes:
        molecule: Molecule specification.
        composite_method: Composite method name.
        cbs_components: CBS extrapolation components.
        empirical_corrections: Apply empirical corrections.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    composite_method: str = Field(
        default="cbs",
        description="Composite method (g3, g4, cbs, w1, etc.)",
    )
    cbs_components: Optional[dict[str, Any]] = Field(
        default=None,
        description="CBS extrapolation components",
    )
    empirical_corrections: bool = Field(
        default=True,
        description="Apply empirical corrections",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Number of threads",
    )
    
    @field_validator("composite_method")
    @classmethod
    def validate_composite_method(cls, v: str) -> str:
        """Validate composite method."""
        valid = {
            "g1", "g2", "g2mp2", "g3", "g3b3", "g3mp2", "g3mp2b3",
            "g4", "g4mp2",
            "cbs", "cbs-4", "cbs-qb3", "cbs-q", "cbs-apno",
            "w1", "w2",
        }
        normalized = v.lower().strip().replace("_", "-")
        if normalized not in valid:
            raise ValueError(f"Invalid composite method: {v}")
        return normalized


class CBSInput(Psi4BaseModel):
    """
    Complete Basis Set extrapolation input.
    
    Attributes:
        molecule: Molecule specification.
        scf_basis: Basis sets for SCF extrapolation.
        corl_basis: Basis sets for correlation extrapolation.
        scf_scheme: SCF extrapolation scheme.
        corl_scheme: Correlation extrapolation scheme.
        corl_method: Correlation method.
        delta_method: Method for delta correction.
        delta_basis: Basis for delta correction.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    scf_basis: list[str] = Field(
        default_factory=lambda: ["cc-pvtz", "cc-pvqz"],
        description="SCF extrapolation bases",
    )
    corl_basis: list[str] = Field(
        default_factory=lambda: ["cc-pvtz", "cc-pvqz"],
        description="Correlation extrapolation bases",
    )
    scf_scheme: str = Field(
        default="scf_xtpl_helgaker_3",
        description="SCF extrapolation scheme",
    )
    corl_scheme: str = Field(
        default="corl_xtpl_helgaker_2",
        description="Correlation extrapolation scheme",
    )
    corl_method: str = Field(
        default="mp2",
        description="Correlation method",
    )
    delta_method: Optional[str] = Field(
        default=None,
        description="Delta correction method",
    )
    delta_basis: Optional[str] = Field(
        default=None,
        description="Delta correction basis",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Number of threads",
    )


# =============================================================================
# RELATIVE ENERGY INPUT
# =============================================================================

class RelativeEnergyInput(Psi4BaseModel):
    """
    Relative energy calculation input for multiple structures.
    
    Attributes:
        structures: Dictionary of name -> geometry string.
        method: Calculation method.
        basis: Basis set.
        reference_structure: Name of reference structure.
        include_zpve: Include zero-point vibrational energy.
        include_thermal: Include thermal corrections.
        temperature: Temperature for thermal corrections.
    """
    
    structures: dict[str, str] = Field(
        ...,
        min_length=2,
        description="Name -> geometry mapping",
    )
    method: str = Field(
        default="b3lyp",
        description="Calculation method",
    )
    basis: str = Field(
        default="def2-tzvp",
        description="Basis set",
    )
    reference_structure: Optional[str] = Field(
        default=None,
        description="Reference structure name",
    )
    include_zpve: bool = Field(
        default=False,
        description="Include ZPVE corrections",
    )
    include_thermal: bool = Field(
        default=False,
        description="Include thermal corrections",
    )
    temperature: float = Field(
        default=298.15,
        gt=0,
        description="Temperature in K",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Number of threads",
    )
    
    def get_molecule_inputs(self) -> dict[str, MoleculeInput]:
        """Convert structures to MoleculeInput objects."""
        return {
            name: MoleculeInput(geometry=geom)
            for name, geom in self.structures.items()
        }


# =============================================================================
# SOLVATION INPUT
# =============================================================================

class SolvatedEnergyInput(EnergyInput):
    """
    Energy calculation with implicit solvation.
    
    Attributes:
        solvation: Solvation model options.
        solvent: Solvent name.
        epsilon: Dielectric constant override.
    """
    
    solvation: SolvationOptions = Field(
        default_factory=lambda: SolvationOptions(pcm=True),
        description="Solvation options",
    )
    solvent: str = Field(
        default="water",
        description="Solvent name",
    )
    epsilon: Optional[float] = Field(
        default=None,
        gt=1.0,
        description="Dielectric constant",
    )
    
    @model_validator(mode="after")
    def sync_solvent(self) -> "SolvatedEnergyInput":
        """Sync solvent settings."""
        if self.solvation.solvent != self.solvent:
            new_solvation = SolvationOptions(
                pcm=self.solvation.pcm,
                solvent=self.solvent,
                epsilon=self.epsilon or self.solvation.epsilon,
                probe_radius=self.solvation.probe_radius,
                cavity_type=self.solvation.cavity_type,
            )
            object.__setattr__(self, 'solvation', new_solvation)
        return self
