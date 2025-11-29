"""
Molecular Orbital and Population Analysis Output Models.

This module provides Pydantic models for representing molecular orbital
data, orbital energies, population analyses, and related electronic
structure information.

Key Classes:
    - MolecularOrbital: Single orbital data
    - OrbitalSet: Complete set of orbitals
    - PopulationAnalysis: Charge and population data
    - BondOrderAnalysis: Bond order information
    - NBOOutput: Natural Bond Orbital analysis
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel


# =============================================================================
# MOLECULAR ORBITALS
# =============================================================================

class MolecularOrbital(Psi4BaseModel):
    """
    Data for a single molecular orbital.
    
    Attributes:
        index: Orbital index (0-indexed).
        energy: Orbital energy in Hartree.
        energy_ev: Orbital energy in eV.
        occupation: Occupation number (0, 1, or 2).
        symmetry: Symmetry label (irrep).
        orbital_type: Type (core, valence, virtual, etc.).
        is_occupied: Whether orbital is occupied.
        coefficients: MO coefficients in AO basis.
        atom_contributions: Contribution from each atom (percent).
        ao_contributions: Contribution from each AO type.
    """
    
    index: int = Field(
        ...,
        ge=0,
        description="Orbital index (0-indexed)",
    )
    energy: float = Field(
        ...,
        description="Orbital energy in Hartree",
    )
    energy_ev: Optional[float] = Field(
        default=None,
        description="Orbital energy in eV",
    )
    occupation: float = Field(
        default=0.0,
        ge=0,
        le=2,
        description="Occupation number",
    )
    symmetry: Optional[str] = Field(
        default=None,
        description="Symmetry label",
    )
    orbital_type: Optional[str] = Field(
        default=None,
        description="Orbital type (core, valence, virtual)",
    )
    is_occupied: bool = Field(
        default=False,
        description="Whether occupied",
    )
    coefficients: Optional[list[float]] = Field(
        default=None,
        description="MO coefficients",
    )
    atom_contributions: Optional[dict[int, float]] = Field(
        default=None,
        description="Atom contributions (percent)",
    )
    ao_contributions: Optional[dict[str, float]] = Field(
        default=None,
        description="AO type contributions",
    )
    
    @model_validator(mode="after")
    def compute_energy_ev(self) -> "MolecularOrbital":
        """Compute energy in eV if not provided."""
        if self.energy_ev is None:
            from psi4_mcp.utils.helpers.units import HARTREE_TO_EV
            ev = self.energy * HARTREE_TO_EV
            object.__setattr__(self, 'energy_ev', ev)
        return self
    
    @model_validator(mode="after")
    def determine_occupied(self) -> "MolecularOrbital":
        """Determine if occupied from occupation number."""
        occupied = self.occupation > 0.5
        if occupied != self.is_occupied:
            object.__setattr__(self, 'is_occupied', occupied)
        return self


class OrbitalSet(Psi4BaseModel):
    """
    Complete set of molecular orbitals (alpha or beta).
    
    Attributes:
        spin: Spin type (alpha, beta, or restricted).
        orbitals: List of molecular orbitals.
        n_occupied: Number of occupied orbitals.
        n_virtual: Number of virtual orbitals.
        n_basis: Number of basis functions.
        homo_index: Index of HOMO.
        lumo_index: Index of LUMO.
        homo_energy: HOMO energy in Hartree.
        lumo_energy: LUMO energy in Hartree.
        homo_lumo_gap: HOMO-LUMO gap in eV.
    """
    
    spin: Literal["alpha", "beta", "restricted"] = Field(
        default="restricted",
        description="Spin type",
    )
    orbitals: list[MolecularOrbital] = Field(
        ...,
        description="Molecular orbitals",
    )
    n_occupied: int = Field(
        ...,
        ge=0,
        description="Number of occupied orbitals",
    )
    n_virtual: int = Field(
        ...,
        ge=0,
        description="Number of virtual orbitals",
    )
    n_basis: int = Field(
        ...,
        ge=1,
        description="Number of basis functions",
    )
    homo_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="HOMO index",
    )
    lumo_index: Optional[int] = Field(
        default=None,
        ge=0,
        description="LUMO index",
    )
    homo_energy: Optional[float] = Field(
        default=None,
        description="HOMO energy in Hartree",
    )
    lumo_energy: Optional[float] = Field(
        default=None,
        description="LUMO energy in Hartree",
    )
    homo_lumo_gap: Optional[float] = Field(
        default=None,
        description="HOMO-LUMO gap in eV",
    )
    
    @model_validator(mode="after")
    def compute_homo_lumo(self) -> "OrbitalSet":
        """Compute HOMO/LUMO info if not provided."""
        if self.homo_index is None and self.n_occupied > 0:
            homo_idx = self.n_occupied - 1
            object.__setattr__(self, 'homo_index', homo_idx)
        
        if self.lumo_index is None and self.n_occupied < len(self.orbitals):
            lumo_idx = self.n_occupied
            object.__setattr__(self, 'lumo_index', lumo_idx)
        
        if self.homo_index is not None and self.homo_energy is None:
            if self.homo_index < len(self.orbitals):
                energy = self.orbitals[self.homo_index].energy
                object.__setattr__(self, 'homo_energy', energy)
        
        if self.lumo_index is not None and self.lumo_energy is None:
            if self.lumo_index < len(self.orbitals):
                energy = self.orbitals[self.lumo_index].energy
                object.__setattr__(self, 'lumo_energy', energy)
        
        if self.homo_lumo_gap is None:
            if self.homo_energy is not None and self.lumo_energy is not None:
                from psi4_mcp.utils.helpers.units import HARTREE_TO_EV
                gap = (self.lumo_energy - self.homo_energy) * HARTREE_TO_EV
                object.__setattr__(self, 'homo_lumo_gap', gap)
        
        return self
    
    def get_orbital(self, index: int) -> Optional[MolecularOrbital]:
        """Get orbital by index."""
        for orb in self.orbitals:
            if orb.index == index:
                return orb
        return None
    
    def get_occupied(self) -> list[MolecularOrbital]:
        """Get all occupied orbitals."""
        return [o for o in self.orbitals if o.is_occupied]
    
    def get_virtual(self) -> list[MolecularOrbital]:
        """Get all virtual orbitals."""
        return [o for o in self.orbitals if not o.is_occupied]
    
    def get_energies(self) -> list[float]:
        """Get list of orbital energies."""
        return [o.energy for o in self.orbitals]


class OrbitalOutput(Psi4BaseModel):
    """
    Complete orbital information output.
    
    Attributes:
        alpha: Alpha orbital set.
        beta: Beta orbital set (if unrestricted).
        is_restricted: Whether calculation was restricted.
        n_electrons: Total number of electrons.
        n_alpha: Number of alpha electrons.
        n_beta: Number of beta electrons.
        overlap_matrix: Overlap matrix S.
        density_matrix_alpha: Alpha density matrix.
        density_matrix_beta: Beta density matrix.
    """
    
    alpha: OrbitalSet = Field(
        ...,
        description="Alpha orbitals",
    )
    beta: Optional[OrbitalSet] = Field(
        default=None,
        description="Beta orbitals",
    )
    is_restricted: bool = Field(
        default=True,
        description="Whether restricted",
    )
    n_electrons: int = Field(
        ...,
        ge=0,
        description="Total electrons",
    )
    n_alpha: int = Field(
        ...,
        ge=0,
        description="Alpha electrons",
    )
    n_beta: int = Field(
        ...,
        ge=0,
        description="Beta electrons",
    )
    overlap_matrix: Optional[list[list[float]]] = Field(
        default=None,
        description="Overlap matrix",
    )
    density_matrix_alpha: Optional[list[list[float]]] = Field(
        default=None,
        description="Alpha density matrix",
    )
    density_matrix_beta: Optional[list[list[float]]] = Field(
        default=None,
        description="Beta density matrix",
    )


# =============================================================================
# POPULATION ANALYSIS
# =============================================================================

class AtomicCharge(Psi4BaseModel):
    """
    Atomic charge for a single atom.
    
    Attributes:
        atom_index: Atom index (0-indexed).
        symbol: Element symbol.
        mulliken: Mulliken charge.
        lowdin: Löwdin charge.
        npa: Natural Population Analysis charge.
        esp: Electrostatic potential-derived charge.
        hirshfeld: Hirshfeld charge.
        cm5: CM5 charge.
        mbis: MBIS charge.
    """
    
    atom_index: int = Field(
        ...,
        ge=0,
        description="Atom index",
    )
    symbol: str = Field(
        ...,
        description="Element symbol",
    )
    mulliken: Optional[float] = Field(
        default=None,
        description="Mulliken charge",
    )
    lowdin: Optional[float] = Field(
        default=None,
        description="Löwdin charge",
    )
    npa: Optional[float] = Field(
        default=None,
        description="NPA charge",
    )
    esp: Optional[float] = Field(
        default=None,
        description="ESP charge",
    )
    hirshfeld: Optional[float] = Field(
        default=None,
        description="Hirshfeld charge",
    )
    cm5: Optional[float] = Field(
        default=None,
        description="CM5 charge",
    )
    mbis: Optional[float] = Field(
        default=None,
        description="MBIS charge",
    )
    
    def get_charge(self, method: str) -> Optional[float]:
        """Get charge by method name."""
        method_lower = method.lower()
        if method_lower == "mulliken":
            return self.mulliken
        elif method_lower in ("lowdin", "löwdin"):
            return self.lowdin
        elif method_lower == "npa":
            return self.npa
        elif method_lower == "esp":
            return self.esp
        elif method_lower == "hirshfeld":
            return self.hirshfeld
        elif method_lower == "cm5":
            return self.cm5
        elif method_lower == "mbis":
            return self.mbis
        return None


class AtomicPopulation(Psi4BaseModel):
    """
    Atomic population (electrons) for a single atom.
    
    Attributes:
        atom_index: Atom index.
        symbol: Element symbol.
        total_population: Total electron population.
        alpha_population: Alpha electron population.
        beta_population: Beta electron population.
        spin_density: Spin density (alpha - beta).
        s_population: s orbital population.
        p_population: p orbital population.
        d_population: d orbital population.
        f_population: f orbital population.
    """
    
    atom_index: int = Field(
        ...,
        ge=0,
        description="Atom index",
    )
    symbol: str = Field(
        ...,
        description="Element symbol",
    )
    total_population: float = Field(
        ...,
        description="Total population",
    )
    alpha_population: Optional[float] = Field(
        default=None,
        description="Alpha population",
    )
    beta_population: Optional[float] = Field(
        default=None,
        description="Beta population",
    )
    spin_density: Optional[float] = Field(
        default=None,
        description="Spin density",
    )
    s_population: Optional[float] = Field(
        default=None,
        description="s orbital population",
    )
    p_population: Optional[float] = Field(
        default=None,
        description="p orbital population",
    )
    d_population: Optional[float] = Field(
        default=None,
        description="d orbital population",
    )
    f_population: Optional[float] = Field(
        default=None,
        description="f orbital population",
    )


class PopulationAnalysis(Psi4BaseModel):
    """
    Complete population analysis output.
    
    Attributes:
        method: Population analysis method.
        charges: Atomic charges.
        populations: Atomic populations.
        dipole_moment: Dipole moment from charges.
        total_charge: Total molecular charge.
        spin_multiplicity: Spin multiplicity.
    """
    
    method: str = Field(
        ...,
        description="Analysis method",
    )
    charges: list[AtomicCharge] = Field(
        ...,
        description="Atomic charges",
    )
    populations: Optional[list[AtomicPopulation]] = Field(
        default=None,
        description="Atomic populations",
    )
    dipole_moment: Optional[list[float]] = Field(
        default=None,
        description="Dipole moment [x, y, z] in Debye",
    )
    total_charge: float = Field(
        default=0.0,
        description="Total charge",
    )
    spin_multiplicity: int = Field(
        default=1,
        ge=1,
        description="Spin multiplicity",
    )
    
    def get_charges_list(self, method: Optional[str] = None) -> list[float]:
        """Get list of charges."""
        if method is None:
            method = self.method
        return [c.get_charge(method) or 0.0 for c in self.charges]
    
    def get_total_charge(self, method: Optional[str] = None) -> float:
        """Get sum of charges (should equal formal charge)."""
        return sum(self.get_charges_list(method))


# =============================================================================
# BOND ORDER ANALYSIS
# =============================================================================

class BondOrder(Psi4BaseModel):
    """
    Bond order between two atoms.
    
    Attributes:
        atom1_index: First atom index.
        atom2_index: Second atom index.
        atom1_symbol: First atom symbol.
        atom2_symbol: Second atom symbol.
        wiberg: Wiberg bond order.
        mayer: Mayer bond order.
        nbo: NBO bond order.
        fuzzy: Fuzzy bond order.
    """
    
    atom1_index: int = Field(
        ...,
        ge=0,
        description="First atom index",
    )
    atom2_index: int = Field(
        ...,
        ge=0,
        description="Second atom index",
    )
    atom1_symbol: str = Field(
        ...,
        description="First atom symbol",
    )
    atom2_symbol: str = Field(
        ...,
        description="Second atom symbol",
    )
    wiberg: Optional[float] = Field(
        default=None,
        ge=0,
        description="Wiberg bond order",
    )
    mayer: Optional[float] = Field(
        default=None,
        description="Mayer bond order",
    )
    nbo: Optional[float] = Field(
        default=None,
        ge=0,
        description="NBO bond order",
    )
    fuzzy: Optional[float] = Field(
        default=None,
        ge=0,
        description="Fuzzy bond order",
    )
    
    @property
    def atom_pair_string(self) -> str:
        """String representation of atom pair."""
        return f"{self.atom1_symbol}{self.atom1_index+1}-{self.atom2_symbol}{self.atom2_index+1}"


class BondOrderAnalysis(Psi4BaseModel):
    """
    Complete bond order analysis output.
    
    Attributes:
        method: Bond order method.
        bond_orders: List of bond orders.
        total_valences: Total valence for each atom.
        free_valences: Free valence for each atom.
    """
    
    method: str = Field(
        ...,
        description="Bond order method",
    )
    bond_orders: list[BondOrder] = Field(
        ...,
        description="Bond orders",
    )
    total_valences: Optional[list[float]] = Field(
        default=None,
        description="Total valences",
    )
    free_valences: Optional[list[float]] = Field(
        default=None,
        description="Free valences",
    )
    
    def get_bond_order(self, atom1: int, atom2: int) -> Optional[BondOrder]:
        """Get bond order between two atoms."""
        for bo in self.bond_orders:
            if (bo.atom1_index == atom1 and bo.atom2_index == atom2) or \
               (bo.atom1_index == atom2 and bo.atom2_index == atom1):
                return bo
        return None
    
    def get_bonds_to_atom(self, atom_index: int) -> list[BondOrder]:
        """Get all bonds involving a specific atom."""
        return [
            bo for bo in self.bond_orders
            if bo.atom1_index == atom_index or bo.atom2_index == atom_index
        ]


# =============================================================================
# NBO ANALYSIS
# =============================================================================

class NaturalBondOrbital(Psi4BaseModel):
    """
    Single Natural Bond Orbital.
    
    Attributes:
        index: NBO index.
        orbital_type: Type (BD, LP, CR, RY, BD*).
        atoms: Atoms involved.
        occupancy: Occupancy.
        energy: Energy in Hartree.
        composition: Hybrid composition.
    """
    
    index: int = Field(
        ...,
        ge=0,
        description="NBO index",
    )
    orbital_type: str = Field(
        ...,
        description="Orbital type (BD, LP, CR, RY, BD*)",
    )
    atoms: list[int] = Field(
        ...,
        description="Atom indices",
    )
    occupancy: float = Field(
        ...,
        ge=0,
        le=2,
        description="Occupancy",
    )
    energy: Optional[float] = Field(
        default=None,
        description="Energy in Hartree",
    )
    composition: Optional[dict[str, float]] = Field(
        default=None,
        description="Hybrid composition",
    )
    
    @property
    def is_bonding(self) -> bool:
        """Check if this is a bonding orbital."""
        return self.orbital_type in ("BD", "bd")
    
    @property
    def is_antibonding(self) -> bool:
        """Check if this is an antibonding orbital."""
        return self.orbital_type in ("BD*", "bd*")
    
    @property
    def is_lone_pair(self) -> bool:
        """Check if this is a lone pair."""
        return self.orbital_type in ("LP", "lp")


class NBOInteraction(Psi4BaseModel):
    """
    Donor-acceptor interaction from NBO analysis.
    
    Attributes:
        donor_nbo: Donor NBO index.
        acceptor_nbo: Acceptor NBO index.
        donor_type: Donor orbital type.
        acceptor_type: Acceptor orbital type.
        energy_kcal_mol: Interaction energy in kcal/mol.
        fock_element: Fock matrix element.
    """
    
    donor_nbo: int = Field(
        ...,
        description="Donor NBO index",
    )
    acceptor_nbo: int = Field(
        ...,
        description="Acceptor NBO index",
    )
    donor_type: str = Field(
        ...,
        description="Donor type",
    )
    acceptor_type: str = Field(
        ...,
        description="Acceptor type",
    )
    energy_kcal_mol: float = Field(
        ...,
        description="Energy in kcal/mol",
    )
    fock_element: Optional[float] = Field(
        default=None,
        description="Fock matrix element",
    )


class NaturalAtomicOrbital(Psi4BaseModel):
    """
    Natural Atomic Orbital data.
    
    Attributes:
        atom_index: Atom index.
        symbol: Element symbol.
        orbital_type: Orbital type (1s, 2s, 2p, etc.).
        occupancy: Occupancy.
        energy: Energy in Hartree.
    """
    
    atom_index: int = Field(
        ...,
        ge=0,
        description="Atom index",
    )
    symbol: str = Field(
        ...,
        description="Element symbol",
    )
    orbital_type: str = Field(
        ...,
        description="Orbital type",
    )
    occupancy: float = Field(
        ...,
        ge=0,
        description="Occupancy",
    )
    energy: Optional[float] = Field(
        default=None,
        description="Energy in Hartree",
    )


class NBOOutput(Psi4BaseModel):
    """
    Complete Natural Bond Orbital analysis output.
    
    Attributes:
        natural_charges: Natural (NPA) charges.
        natural_electron_config: Natural electron configurations.
        nbos: List of Natural Bond Orbitals.
        naos: List of Natural Atomic Orbitals.
        interactions: Donor-acceptor interactions.
        total_lewis: Total Lewis structure energy.
        total_non_lewis: Total non-Lewis energy.
        resonance_weight: Resonance structure weights.
    """
    
    natural_charges: list[AtomicCharge] = Field(
        ...,
        description="Natural charges",
    )
    natural_electron_config: Optional[list[str]] = Field(
        default=None,
        description="Natural electron configs",
    )
    nbos: list[NaturalBondOrbital] = Field(
        default_factory=list,
        description="Natural Bond Orbitals",
    )
    naos: Optional[list[NaturalAtomicOrbital]] = Field(
        default=None,
        description="Natural Atomic Orbitals",
    )
    interactions: list[NBOInteraction] = Field(
        default_factory=list,
        description="Donor-acceptor interactions",
    )
    total_lewis: Optional[float] = Field(
        default=None,
        description="Total Lewis energy",
    )
    total_non_lewis: Optional[float] = Field(
        default=None,
        description="Total non-Lewis energy",
    )
    resonance_weights: Optional[list[float]] = Field(
        default=None,
        description="Resonance weights",
    )
    
    def get_bonding_orbitals(self) -> list[NaturalBondOrbital]:
        """Get all bonding orbitals."""
        return [nbo for nbo in self.nbos if nbo.is_bonding]
    
    def get_lone_pairs(self) -> list[NaturalBondOrbital]:
        """Get all lone pairs."""
        return [nbo for nbo in self.nbos if nbo.is_lone_pair]
    
    def get_strong_interactions(self, threshold: float = 5.0) -> list[NBOInteraction]:
        """Get interactions above energy threshold (kcal/mol)."""
        return [i for i in self.interactions if i.energy_kcal_mol >= threshold]
