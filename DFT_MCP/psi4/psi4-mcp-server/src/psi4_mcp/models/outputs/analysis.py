"""
Wavefunction Analysis Output Models.

This module provides Pydantic models for representing various wavefunction
analysis results including density analysis, localized orbitals, and
topological analysis (AIM, ELF, etc.).

Key Classes:
    - DensityAnalysis: Electron density analysis
    - LocalizedOrbitals: Localized orbital information
    - AIMOutput: Atoms in Molecules analysis
    - ELFOutput: Electron Localization Function
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel


# =============================================================================
# ELECTRON DENSITY ANALYSIS
# =============================================================================

class CriticalPoint(Psi4BaseModel):
    """
    Critical point in electron density.
    
    Attributes:
        cp_type: Type of critical point (bcp, rcp, ccp, ncp).
        position: Position [x, y, z] in Bohr.
        density: Electron density at CP.
        gradient: Gradient magnitude at CP.
        laplacian: Laplacian of density at CP.
        ellipticity: Ellipticity (for BCPs).
        eigenvalues: Hessian eigenvalues.
        connected_atoms: Atoms connected by this CP (for BCPs).
    """
    
    cp_type: Literal["ncp", "bcp", "rcp", "ccp"] = Field(
        ...,
        description="Critical point type",
    )
    position: list[float] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Position [x, y, z]",
    )
    density: float = Field(
        ...,
        ge=0,
        description="Electron density",
    )
    gradient: Optional[float] = Field(
        default=None,
        ge=0,
        description="Gradient magnitude",
    )
    laplacian: Optional[float] = Field(
        default=None,
        description="Laplacian",
    )
    ellipticity: Optional[float] = Field(
        default=None,
        ge=0,
        description="Ellipticity",
    )
    eigenvalues: Optional[list[float]] = Field(
        default=None,
        description="Hessian eigenvalues",
    )
    connected_atoms: Optional[list[int]] = Field(
        default=None,
        description="Connected atom indices",
    )
    
    @property
    def is_bond_critical_point(self) -> bool:
        """Check if this is a bond critical point."""
        return self.cp_type == "bcp"
    
    @property
    def is_nuclear_critical_point(self) -> bool:
        """Check if this is a nuclear critical point."""
        return self.cp_type == "ncp"


class DensityGridPoint(Psi4BaseModel):
    """
    Electron density at a grid point.
    
    Attributes:
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        density: Electron density.
        gradient_x: X gradient component.
        gradient_y: Y gradient component.
        gradient_z: Z gradient component.
        laplacian: Laplacian of density.
    """
    
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    density: float = Field(..., ge=0, description="Density")
    gradient_x: Optional[float] = Field(default=None, description="Grad X")
    gradient_y: Optional[float] = Field(default=None, description="Grad Y")
    gradient_z: Optional[float] = Field(default=None, description="Grad Z")
    laplacian: Optional[float] = Field(default=None, description="Laplacian")


class DensityAnalysis(Psi4BaseModel):
    """
    Electron density analysis output.
    
    Attributes:
        n_electrons_integrated: Total electrons from integration.
        max_density: Maximum electron density.
        critical_points: List of critical points.
        grid_points: Density on a grid (if computed).
        total_charge: Total electronic charge.
        dipole_from_density: Dipole moment from density.
    """
    
    n_electrons_integrated: Optional[float] = Field(
        default=None,
        description="Integrated electrons",
    )
    max_density: Optional[float] = Field(
        default=None,
        ge=0,
        description="Maximum density",
    )
    critical_points: list[CriticalPoint] = Field(
        default_factory=list,
        description="Critical points",
    )
    grid_points: Optional[list[DensityGridPoint]] = Field(
        default=None,
        description="Grid density",
    )
    total_charge: Optional[float] = Field(
        default=None,
        description="Total charge",
    )
    dipole_from_density: Optional[list[float]] = Field(
        default=None,
        description="Dipole [x, y, z]",
    )
    
    def get_bond_critical_points(self) -> list[CriticalPoint]:
        """Get all bond critical points."""
        return [cp for cp in self.critical_points if cp.is_bond_critical_point]
    
    def get_cp_between_atoms(self, atom1: int, atom2: int) -> Optional[CriticalPoint]:
        """Get BCP between two atoms."""
        for cp in self.critical_points:
            if cp.connected_atoms and set(cp.connected_atoms) == {atom1, atom2}:
                return cp
        return None


# =============================================================================
# ATOMS IN MOLECULES (AIM)
# =============================================================================

class AIMAtom(Psi4BaseModel):
    """
    AIM basin properties for a single atom.
    
    Attributes:
        atom_index: Atom index.
        symbol: Element symbol.
        basin_charge: Integrated basin charge.
        basin_population: Basin electron population.
        basin_volume: Basin volume.
        localization_index: Localization index.
        delocalization_indices: Delocalization indices to other atoms.
        kinetic_energy: Basin kinetic energy.
        potential_energy: Basin potential energy.
    """
    
    atom_index: int = Field(..., ge=0, description="Atom index")
    symbol: str = Field(..., description="Element symbol")
    basin_charge: float = Field(..., description="Basin charge")
    basin_population: float = Field(..., ge=0, description="Population")
    basin_volume: Optional[float] = Field(default=None, ge=0, description="Volume")
    localization_index: Optional[float] = Field(default=None, description="LI")
    delocalization_indices: Optional[dict[int, float]] = Field(
        default=None,
        description="DI to other atoms",
    )
    kinetic_energy: Optional[float] = Field(default=None, description="KE")
    potential_energy: Optional[float] = Field(default=None, description="PE")


class AIMBond(Psi4BaseModel):
    """
    AIM bond properties.
    
    Attributes:
        atom1_index: First atom index.
        atom2_index: Second atom index.
        bcp: Bond critical point.
        delocalization_index: Delocalization index.
        bond_order: AIM bond order.
        bond_ellipticity: Bond ellipticity.
    """
    
    atom1_index: int = Field(..., ge=0, description="Atom 1")
    atom2_index: int = Field(..., ge=0, description="Atom 2")
    bcp: Optional[CriticalPoint] = Field(default=None, description="BCP")
    delocalization_index: Optional[float] = Field(default=None, description="DI")
    bond_order: Optional[float] = Field(default=None, ge=0, description="Bond order")
    bond_ellipticity: Optional[float] = Field(default=None, ge=0, description="Ellipticity")


class AIMOutput(Psi4BaseModel):
    """
    Complete Atoms in Molecules analysis output.
    
    Attributes:
        atoms: AIM atomic basin properties.
        bonds: AIM bond properties.
        critical_points: All critical points found.
        poincare_hopf_satisfied: Whether Poincare-Hopf rule is satisfied.
        total_basin_charge: Sum of basin charges.
    """
    
    atoms: list[AIMAtom] = Field(..., description="Atomic basins")
    bonds: list[AIMBond] = Field(default_factory=list, description="Bonds")
    critical_points: list[CriticalPoint] = Field(
        default_factory=list,
        description="Critical points",
    )
    poincare_hopf_satisfied: bool = Field(
        default=True,
        description="Poincare-Hopf satisfied",
    )
    total_basin_charge: Optional[float] = Field(
        default=None,
        description="Total basin charge",
    )
    
    def get_atom(self, index: int) -> Optional[AIMAtom]:
        """Get atom by index."""
        for atom in self.atoms:
            if atom.atom_index == index:
                return atom
        return None
    
    def get_bond(self, atom1: int, atom2: int) -> Optional[AIMBond]:
        """Get bond between two atoms."""
        for bond in self.bonds:
            if {bond.atom1_index, bond.atom2_index} == {atom1, atom2}:
                return bond
        return None


# =============================================================================
# ELECTRON LOCALIZATION FUNCTION (ELF)
# =============================================================================

class ELFBasin(Psi4BaseModel):
    """
    ELF basin data.
    
    Attributes:
        basin_type: Type of basin (core, valence, lone pair).
        attractor_position: Attractor position [x, y, z].
        population: Basin population.
        variance: Population variance.
        synaptic_order: Synaptic order (connectivity).
        connected_atoms: Connected atom indices.
    """
    
    basin_type: str = Field(..., description="Basin type")
    attractor_position: list[float] = Field(..., description="Attractor [x,y,z]")
    population: float = Field(..., ge=0, description="Population")
    variance: Optional[float] = Field(default=None, ge=0, description="Variance")
    synaptic_order: Optional[int] = Field(default=None, ge=0, description="Synaptic order")
    connected_atoms: Optional[list[int]] = Field(default=None, description="Connected atoms")
    
    @property
    def is_core(self) -> bool:
        """Check if this is a core basin."""
        return "core" in self.basin_type.lower()
    
    @property
    def is_lone_pair(self) -> bool:
        """Check if this is a lone pair basin."""
        return "lone" in self.basin_type.lower() or self.synaptic_order == 1


class ELFOutput(Psi4BaseModel):
    """
    Electron Localization Function analysis output.
    
    Attributes:
        basins: List of ELF basins.
        n_core_basins: Number of core basins.
        n_valence_basins: Number of valence basins.
        total_population: Total basin population.
        grid_data: ELF values on grid.
    """
    
    basins: list[ELFBasin] = Field(..., description="ELF basins")
    n_core_basins: Optional[int] = Field(default=None, ge=0, description="Core basins")
    n_valence_basins: Optional[int] = Field(default=None, ge=0, description="Valence basins")
    total_population: Optional[float] = Field(default=None, description="Total population")
    grid_data: Optional[list[list[float]]] = Field(default=None, description="Grid data")
    
    def get_lone_pairs(self) -> list[ELFBasin]:
        """Get lone pair basins."""
        return [b for b in self.basins if b.is_lone_pair]
    
    def get_bonding_basins(self) -> list[ELFBasin]:
        """Get bonding basins."""
        return [
            b for b in self.basins 
            if not b.is_core and not b.is_lone_pair
        ]


# =============================================================================
# LOCALIZED ORBITALS
# =============================================================================

class LocalizedOrbital(Psi4BaseModel):
    """
    Single localized molecular orbital.
    
    Attributes:
        index: Orbital index.
        energy: Orbital energy (if canonical).
        occupation: Occupation number.
        localization_index: Localization index.
        centroid: Orbital centroid [x, y, z].
        spread: Orbital spread (second moment).
        atom_contributions: Contribution from each atom.
        orbital_type: Type (core, bond, lone pair).
        connected_atoms: Atoms involved in this orbital.
    """
    
    index: int = Field(..., ge=0, description="Orbital index")
    energy: Optional[float] = Field(default=None, description="Energy")
    occupation: float = Field(default=2.0, ge=0, le=2, description="Occupation")
    localization_index: Optional[float] = Field(default=None, description="LI")
    centroid: Optional[list[float]] = Field(default=None, description="Centroid")
    spread: Optional[float] = Field(default=None, ge=0, description="Spread")
    atom_contributions: Optional[dict[int, float]] = Field(
        default=None,
        description="Atom contributions",
    )
    orbital_type: Optional[str] = Field(default=None, description="Type")
    connected_atoms: Optional[list[int]] = Field(default=None, description="Atoms")
    
    @property
    def is_core(self) -> bool:
        """Check if this is a core orbital."""
        if self.orbital_type:
            return "core" in self.orbital_type.lower()
        return False
    
    @property
    def is_lone_pair(self) -> bool:
        """Check if this is a lone pair orbital."""
        if self.orbital_type:
            return "lone" in self.orbital_type.lower()
        if self.connected_atoms:
            return len(self.connected_atoms) == 1
        return False
    
    @property
    def is_bonding(self) -> bool:
        """Check if this is a bonding orbital."""
        if self.orbital_type:
            return "bond" in self.orbital_type.lower()
        if self.connected_atoms:
            return len(self.connected_atoms) == 2
        return False


class LocalizedOrbitalsOutput(Psi4BaseModel):
    """
    Localized orbitals output.
    
    Attributes:
        method: Localization method (Boys, PM, IBO, etc.).
        orbitals: List of localized orbitals.
        n_core: Number of core orbitals.
        n_valence: Number of valence orbitals.
        total_spread: Total orbital spread.
        convergence: Whether localization converged.
        iterations: Number of iterations.
    """
    
    method: str = Field(..., description="Localization method")
    orbitals: list[LocalizedOrbital] = Field(..., description="Orbitals")
    n_core: Optional[int] = Field(default=None, ge=0, description="Core orbitals")
    n_valence: Optional[int] = Field(default=None, ge=0, description="Valence orbitals")
    total_spread: Optional[float] = Field(default=None, ge=0, description="Total spread")
    convergence: bool = Field(default=True, description="Converged")
    iterations: Optional[int] = Field(default=None, ge=0, description="Iterations")
    
    def get_core_orbitals(self) -> list[LocalizedOrbital]:
        """Get core orbitals."""
        return [o for o in self.orbitals if o.is_core]
    
    def get_lone_pairs(self) -> list[LocalizedOrbital]:
        """Get lone pair orbitals."""
        return [o for o in self.orbitals if o.is_lone_pair]
    
    def get_bonding_orbitals(self) -> list[LocalizedOrbital]:
        """Get bonding orbitals."""
        return [o for o in self.orbitals if o.is_bonding]


# =============================================================================
# SPIN DENSITY ANALYSIS
# =============================================================================

class SpinDensityAnalysis(Psi4BaseModel):
    """
    Spin density analysis output.
    
    Attributes:
        n_unpaired_electrons: Number of unpaired electrons.
        spin_populations: Spin population on each atom.
        total_spin: Total spin.
        s2_value: <S^2> expectation value.
        spin_contamination: Spin contamination.
        spin_density_max: Maximum spin density.
    """
    
    n_unpaired_electrons: int = Field(..., ge=0, description="Unpaired electrons")
    spin_populations: dict[int, float] = Field(..., description="Atom spin populations")
    total_spin: float = Field(..., ge=0, description="Total spin S")
    s2_value: Optional[float] = Field(default=None, ge=0, description="<S^2>")
    spin_contamination: Optional[float] = Field(default=None, description="Contamination")
    spin_density_max: Optional[float] = Field(default=None, description="Max density")
    
    def get_alpha_atoms(self, threshold: float = 0.1) -> list[int]:
        """Get atoms with significant positive spin density."""
        return [
            atom for atom, pop in self.spin_populations.items() 
            if pop > threshold
        ]
    
    def get_beta_atoms(self, threshold: float = 0.1) -> list[int]:
        """Get atoms with significant negative spin density."""
        return [
            atom for atom, pop in self.spin_populations.items() 
            if pop < -threshold
        ]


# =============================================================================
# FUKUI FUNCTIONS
# =============================================================================

class FukuiFunctions(Psi4BaseModel):
    """
    Fukui function analysis output.
    
    Attributes:
        f_plus: Nucleophilic attack susceptibility (per atom).
        f_minus: Electrophilic attack susceptibility (per atom).
        f_zero: Radical attack susceptibility (per atom).
        dual_descriptor: Dual descriptor (f+ - f-).
        local_softness_plus: Local softness s+.
        local_softness_minus: Local softness s-.
    """
    
    f_plus: dict[int, float] = Field(..., description="f+ per atom")
    f_minus: dict[int, float] = Field(..., description="f- per atom")
    f_zero: Optional[dict[int, float]] = Field(default=None, description="f0 per atom")
    dual_descriptor: Optional[dict[int, float]] = Field(
        default=None,
        description="Dual descriptor",
    )
    local_softness_plus: Optional[dict[int, float]] = Field(
        default=None,
        description="s+ per atom",
    )
    local_softness_minus: Optional[dict[int, float]] = Field(
        default=None,
        description="s- per atom",
    )
    
    @model_validator(mode="after")
    def compute_f_zero(self) -> "FukuiFunctions":
        """Compute f0 if not provided."""
        if self.f_zero is None and self.f_plus and self.f_minus:
            f_zero = {
                atom: 0.5 * (self.f_plus.get(atom, 0) + self.f_minus.get(atom, 0))
                for atom in set(self.f_plus.keys()) | set(self.f_minus.keys())
            }
            object.__setattr__(self, 'f_zero', f_zero)
        return self
    
    def get_nucleophilic_sites(self, threshold: float = 0.1) -> list[int]:
        """Get atoms susceptible to nucleophilic attack."""
        return [atom for atom, val in self.f_plus.items() if val > threshold]
    
    def get_electrophilic_sites(self, threshold: float = 0.1) -> list[int]:
        """Get atoms susceptible to electrophilic attack."""
        return [atom for atom, val in self.f_minus.items() if val > threshold]
