"""
SAPT Calculation Input Models.

This module provides Pydantic models for specifying Symmetry-Adapted
Perturbation Theory (SAPT) calculations.

Key Classes:
    - SAPTInput: Basic SAPT calculation
    - SAPTMonomer: Monomer specification
    - FSAPTInput: F-SAPT calculation
    - ISAPTInput: I-SAPT calculation
"""

from typing import Any, Optional, Literal
from pydantic import Field, field_validator, model_validator

from psi4_mcp.models.base import Psi4BaseModel
from psi4_mcp.models.calculations.energy import MoleculeInput


# =============================================================================
# SAPT MONOMER
# =============================================================================

class SAPTMonomer(Psi4BaseModel):
    """
    SAPT monomer specification.
    
    Attributes:
        geometry: Monomer geometry string.
        charge: Monomer charge.
        multiplicity: Monomer multiplicity.
        name: Monomer name.
    """
    
    geometry: str = Field(
        ...,
        description="Monomer geometry",
    )
    charge: int = Field(
        default=0,
        description="Monomer charge",
    )
    multiplicity: int = Field(
        default=1,
        ge=1,
        description="Monomer multiplicity",
    )
    name: Optional[str] = Field(
        default=None,
        description="Monomer name",
    )


class SAPTDimer(Psi4BaseModel):
    """
    SAPT dimer specification (two monomers).
    
    Attributes:
        monomer_a: First monomer.
        monomer_b: Second monomer.
        dimer_charge: Total dimer charge.
        dimer_multiplicity: Total dimer multiplicity.
        units: Coordinate units.
    """
    
    monomer_a: SAPTMonomer = Field(
        ...,
        description="Monomer A",
    )
    monomer_b: SAPTMonomer = Field(
        ...,
        description="Monomer B",
    )
    dimer_charge: Optional[int] = Field(
        default=None,
        description="Dimer charge",
    )
    dimer_multiplicity: Optional[int] = Field(
        default=None,
        description="Dimer multiplicity",
    )
    units: Literal["angstrom", "bohr"] = Field(
        default="angstrom",
        description="Units",
    )
    
    @model_validator(mode="after")
    def compute_dimer_properties(self) -> "SAPTDimer":
        """Compute dimer charge and multiplicity."""
        if self.dimer_charge is None:
            charge = self.monomer_a.charge + self.monomer_b.charge
            object.__setattr__(self, 'dimer_charge', charge)
        
        if self.dimer_multiplicity is None:
            # For closed-shell monomers, dimer is singlet
            mult = 1
            object.__setattr__(self, 'dimer_multiplicity', mult)
        
        return self
    
    def to_psi4_string(self) -> str:
        """Convert to Psi4 molecule string with fragment separator."""
        lines = []
        
        # Dimer charge/multiplicity
        lines.append(f"{self.dimer_charge} {self.dimer_multiplicity}")
        
        # Monomer A
        if self.monomer_a.name:
            lines.append(f"# Monomer A: {self.monomer_a.name}")
        lines.append(self.monomer_a.geometry.strip())
        
        # Fragment separator
        lines.append("--")
        
        # Monomer B charge/multiplicity
        lines.append(f"{self.monomer_b.charge} {self.monomer_b.multiplicity}")
        
        # Monomer B
        if self.monomer_b.name:
            lines.append(f"# Monomer B: {self.monomer_b.name}")
        lines.append(self.monomer_b.geometry.strip())
        
        # Options
        lines.append(f"units {self.units}")
        lines.append("noreorient")
        lines.append("nocom")
        
        return "\n".join(lines)


# =============================================================================
# SAPT INPUT
# =============================================================================

class SAPTInput(Psi4BaseModel):
    """
    SAPT calculation input.
    
    Attributes:
        dimer: Dimer specification.
        sapt_level: SAPT level (sapt0, sapt2, sapt2+, etc.).
        basis: Basis set.
        df_basis_sapt: Density fitting basis for SAPT.
        df_basis_elst: DF basis for electrostatics.
        freeze_core: Freeze core electrons.
        print_level: Print verbosity.
        coupled_induction: Use coupled induction.
        exch_scale_alpha: Exchange scaling alpha.
        do_ind_exch: Include exchange-induction.
        do_disp_exch: Include exchange-dispersion.
    """
    
    dimer: SAPTDimer = Field(
        ...,
        description="Dimer specification",
    )
    sapt_level: str = Field(
        default="sapt0",
        description="SAPT level",
    )
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set",
    )
    df_basis_sapt: Optional[str] = Field(
        default=None,
        description="DF basis for SAPT",
    )
    df_basis_elst: Optional[str] = Field(
        default=None,
        description="DF basis for electrostatics",
    )
    freeze_core: bool = Field(
        default=True,
        description="Freeze core",
    )
    print_level: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Print level",
    )
    coupled_induction: bool = Field(
        default=False,
        description="Coupled induction",
    )
    exch_scale_alpha: bool = Field(
        default=False,
        description="Exchange scaling",
    )
    do_ind_exch: bool = Field(
        default=True,
        description="Include exchange-induction",
    )
    do_disp_exch: bool = Field(
        default=True,
        description="Include exchange-dispersion",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @field_validator("sapt_level")
    @classmethod
    def validate_sapt_level(cls, v: str) -> str:
        """Validate SAPT level."""
        valid = {
            "sapt0", "ssapt0", "sapt0-ct",
            "sapt2", "sapt2+", "sapt2+(3)", "sapt2+3",
            "sapt2+(ccd)", "sapt2+(3)(ccd)", "sapt2+3(ccd)",
            "sapt2+dmp2", "sapt2+(3)dmp2", "sapt2+3dmp2",
        }
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid SAPT level: {v}")
        return normalized
    
    def to_psi4_options(self) -> dict[str, Any]:
        """Convert to Psi4 options dictionary."""
        opts: dict[str, Any] = {
            "freeze_core": self.freeze_core,
            "print": self.print_level,
        }
        
        if self.df_basis_sapt:
            opts["df_basis_sapt"] = self.df_basis_sapt
        if self.df_basis_elst:
            opts["df_basis_elst"] = self.df_basis_elst
        
        if self.coupled_induction:
            opts["coupled_induction"] = True
        
        if self.exch_scale_alpha:
            opts["exch_scale_alpha"] = True
        
        opts["do_ind_exch"] = self.do_ind_exch
        opts["do_disp_exch"] = self.do_disp_exch
        
        return opts


# =============================================================================
# F-SAPT INPUT
# =============================================================================

class FSAPTFragment(Psi4BaseModel):
    """
    F-SAPT fragment definition.
    
    Attributes:
        atom_indices: Atom indices in fragment (1-indexed).
        name: Fragment name.
        functional_group: Functional group type.
    """
    
    atom_indices: list[int] = Field(
        ...,
        min_length=1,
        description="Atom indices (1-indexed)",
    )
    name: Optional[str] = Field(
        default=None,
        description="Fragment name",
    )
    functional_group: Optional[str] = Field(
        default=None,
        description="Functional group type",
    )


class FSAPTInput(Psi4BaseModel):
    """
    F-SAPT (Functional-group SAPT) calculation input.
    
    Attributes:
        dimer: Dimer specification.
        fragments_a: Fragments in monomer A.
        fragments_b: Fragments in monomer B.
        link_atoms_a: Link atoms for monomer A.
        link_atoms_b: Link atoms for monomer B.
        sapt_level: SAPT level.
        basis: Basis set.
        partition: Partitioning scheme.
    """
    
    dimer: SAPTDimer = Field(
        ...,
        description="Dimer specification",
    )
    fragments_a: list[FSAPTFragment] = Field(
        ...,
        min_length=1,
        description="Fragments in A",
    )
    fragments_b: list[FSAPTFragment] = Field(
        ...,
        min_length=1,
        description="Fragments in B",
    )
    link_atoms_a: list[int] = Field(
        default_factory=list,
        description="Link atoms A (1-indexed)",
    )
    link_atoms_b: list[int] = Field(
        default_factory=list,
        description="Link atoms B (1-indexed)",
    )
    sapt_level: str = Field(
        default="sapt0",
        description="SAPT level",
    )
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set",
    )
    partition: str = Field(
        default="atoms",
        description="Partitioning scheme",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @field_validator("partition")
    @classmethod
    def validate_partition(cls, v: str) -> str:
        """Validate partitioning scheme."""
        valid = {"atoms", "orbitals"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid partition: {v}")
        return normalized
    
    def get_fsapt_file_content(self) -> str:
        """Generate F-SAPT input file content."""
        lines = []
        
        # Monomer A fragments
        lines.append("# Monomer A Fragments")
        for i, frag in enumerate(self.fragments_a):
            name = frag.name or f"A{i+1}"
            indices = " ".join(str(idx) for idx in frag.atom_indices)
            lines.append(f"A_{name} {indices}")
        
        # Monomer A links
        if self.link_atoms_a:
            links = " ".join(str(idx) for idx in self.link_atoms_a)
            lines.append(f"A_Link {links}")
        
        # Monomer B fragments
        lines.append("# Monomer B Fragments")
        for i, frag in enumerate(self.fragments_b):
            name = frag.name or f"B{i+1}"
            indices = " ".join(str(idx) for idx in frag.atom_indices)
            lines.append(f"B_{name} {indices}")
        
        # Monomer B links
        if self.link_atoms_b:
            links = " ".join(str(idx) for idx in self.link_atoms_b)
            lines.append(f"B_Link {links}")
        
        return "\n".join(lines)


# =============================================================================
# I-SAPT INPUT
# =============================================================================

class ISAPTInput(Psi4BaseModel):
    """
    I-SAPT (Intramolecular SAPT) calculation input.
    
    For analyzing intramolecular non-covalent interactions.
    
    Attributes:
        molecule: Molecule with fragment definitions.
        fragment_atoms: List of atom indices for each fragment.
        link_atoms: Link atoms connecting fragments.
        sapt_level: SAPT level.
        basis: Basis set.
    """
    
    molecule: MoleculeInput = Field(
        ...,
        description="Molecule specification",
    )
    fragment_atoms: list[list[int]] = Field(
        ...,
        min_length=2,
        description="Atom indices per fragment",
    )
    link_atoms: list[int] = Field(
        default_factory=list,
        description="Link atoms (1-indexed)",
    )
    sapt_level: str = Field(
        default="sapt0",
        description="SAPT level",
    )
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @model_validator(mode="after")
    def validate_fragments(self) -> "ISAPTInput":
        """Validate fragment definitions."""
        if len(self.fragment_atoms) != 2:
            raise ValueError("I-SAPT requires exactly 2 fragments")
        return self


# =============================================================================
# SAPT SCAN INPUT
# =============================================================================

class SAPTScanInput(Psi4BaseModel):
    """
    SAPT energy scan along a coordinate.
    
    Attributes:
        monomer_a: Fixed monomer A.
        monomer_b: Monomer B to be displaced.
        scan_type: Type of scan (distance, angle).
        scan_values: Values to scan.
        scan_axis: Axis for displacement [x, y, z].
        sapt_level: SAPT level.
        basis: Basis set.
    """
    
    monomer_a: SAPTMonomer = Field(
        ...,
        description="Fixed monomer",
    )
    monomer_b: SAPTMonomer = Field(
        ...,
        description="Mobile monomer",
    )
    scan_type: Literal["distance", "angle", "dihedral"] = Field(
        default="distance",
        description="Scan type",
    )
    scan_values: list[float] = Field(
        ...,
        min_length=2,
        description="Values to scan",
    )
    scan_axis: list[float] = Field(
        default_factory=lambda: [0.0, 0.0, 1.0],
        description="Displacement axis",
    )
    sapt_level: str = Field(
        default="sapt0",
        description="SAPT level",
    )
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @property
    def n_points(self) -> int:
        """Number of scan points."""
        return len(self.scan_values)


# =============================================================================
# SUPERMOLECULAR INTERACTION ENERGY INPUT
# =============================================================================

class InteractionEnergyInput(Psi4BaseModel):
    """
    Supermolecular interaction energy calculation.
    
    Computes interaction energy as E_AB - E_A - E_B with optional
    counterpoise correction.
    
    Attributes:
        dimer: Dimer specification.
        method: Calculation method.
        basis: Basis set.
        counterpoise: Apply counterpoise correction.
        bsse_type: BSSE correction type.
        deformation: Include deformation energy.
    """
    
    dimer: SAPTDimer = Field(
        ...,
        description="Dimer specification",
    )
    method: str = Field(
        default="mp2",
        description="Calculation method",
    )
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set",
    )
    counterpoise: bool = Field(
        default=True,
        description="Apply CP correction",
    )
    bsse_type: Literal["cp", "nocp", "vmfc"] = Field(
        default="cp",
        description="BSSE type",
    )
    deformation: bool = Field(
        default=False,
        description="Include deformation energy",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )


# =============================================================================
# EDA INPUT (Energy Decomposition Analysis)
# =============================================================================

class EDAInput(Psi4BaseModel):
    """
    Energy Decomposition Analysis input.
    
    Attributes:
        dimer: Dimer specification.
        method: EDA method (sapt, almo, etc.).
        basis: Basis set.
        decomposition: Decomposition scheme.
        include_ct: Include charge transfer.
        include_pol: Include polarization.
    """
    
    dimer: SAPTDimer = Field(
        ...,
        description="Dimer specification",
    )
    method: str = Field(
        default="sapt0",
        description="EDA method",
    )
    basis: str = Field(
        default="aug-cc-pvdz",
        description="Basis set",
    )
    decomposition: str = Field(
        default="sapt",
        description="Decomposition scheme",
    )
    include_ct: bool = Field(
        default=True,
        description="Include charge transfer",
    )
    include_pol: bool = Field(
        default=True,
        description="Include polarization",
    )
    memory: int = Field(
        default=4000,
        ge=100,
        description="Memory in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        description="Threads",
    )
    
    @field_validator("decomposition")
    @classmethod
    def validate_decomposition(cls, v: str) -> str:
        """Validate decomposition scheme."""
        valid = {"sapt", "almo", "eda", "lmo-eda", "gks-eda"}
        normalized = v.lower().strip()
        if normalized not in valid:
            raise ValueError(f"Invalid decomposition: {v}")
        return normalized
