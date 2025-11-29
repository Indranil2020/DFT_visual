"""
Energy Calculation Output Models.

This module provides Pydantic models for representing energy calculation
results, including single-point energies, energy components, and
various energy decompositions.

Key Classes:
    - EnergyOutput: Primary energy result container
    - SCFEnergyOutput: SCF-specific energy details
    - CorrelationEnergyOutput: Post-HF correlation energies
    - DFTEnergyOutput: DFT-specific energy components
    - TotalEnergyOutput: Complete energy breakdown
"""

from typing import Any, Optional, Literal
from datetime import datetime
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel, CalculationOutput


# =============================================================================
# SCF ENERGY OUTPUT
# =============================================================================

class SCFEnergyComponents(Psi4BaseModel):
    """
    Detailed breakdown of SCF energy components.
    
    Attributes:
        one_electron: One-electron integrals energy.
        two_electron: Two-electron integrals energy.
        nuclear_repulsion: Nuclear repulsion energy.
        nuclear_attraction: Nuclear attraction energy.
        kinetic: Kinetic energy.
        coulomb: Coulomb (J) energy.
        exchange: Exchange (K) energy.
        total: Total SCF energy.
    """
    
    one_electron: Optional[float] = Field(
        default=None,
        description="One-electron energy in Hartree",
    )
    two_electron: Optional[float] = Field(
        default=None,
        description="Two-electron energy in Hartree",
    )
    nuclear_repulsion: float = Field(
        ...,
        description="Nuclear repulsion energy in Hartree",
    )
    nuclear_attraction: Optional[float] = Field(
        default=None,
        description="Nuclear attraction energy in Hartree",
    )
    kinetic: Optional[float] = Field(
        default=None,
        description="Kinetic energy in Hartree",
    )
    coulomb: Optional[float] = Field(
        default=None,
        description="Coulomb (J) energy in Hartree",
    )
    exchange: Optional[float] = Field(
        default=None,
        description="Exchange (K) energy in Hartree",
    )
    total: float = Field(
        ...,
        description="Total SCF energy in Hartree",
    )
    
    @property
    def electronic_energy(self) -> float:
        """Electronic energy (total minus nuclear repulsion)."""
        return self.total - self.nuclear_repulsion


class SCFConvergence(Psi4BaseModel):
    """
    SCF convergence information.
    
    Attributes:
        converged: Whether SCF converged.
        iterations: Number of iterations.
        final_energy: Final SCF energy.
        energy_change: Final energy change.
        density_change: Final density RMS change.
        orbital_gradient: Final orbital gradient.
        diis_error: Final DIIS error.
        level_shift: Level shift used (if any).
    """
    
    converged: bool = Field(
        ...,
        description="Whether SCF converged",
    )
    iterations: int = Field(
        ...,
        ge=0,
        description="Number of SCF iterations",
    )
    final_energy: float = Field(
        ...,
        description="Final SCF energy in Hartree",
    )
    energy_change: Optional[float] = Field(
        default=None,
        description="Final energy change",
    )
    density_change: Optional[float] = Field(
        default=None,
        description="Final density RMS change",
    )
    orbital_gradient: Optional[float] = Field(
        default=None,
        description="Final orbital gradient",
    )
    diis_error: Optional[float] = Field(
        default=None,
        description="Final DIIS error",
    )
    level_shift: Optional[float] = Field(
        default=None,
        description="Level shift used",
    )


class SCFEnergyOutput(Psi4BaseModel):
    """
    Complete SCF energy calculation output.
    
    Attributes:
        energy: Total SCF energy.
        components: Energy component breakdown.
        convergence: Convergence information.
        reference: Reference type used (RHF, UHF, etc.).
        n_basis_functions: Number of basis functions.
        n_alpha: Number of alpha electrons.
        n_beta: Number of beta electrons.
        homo_energy: HOMO orbital energy.
        lumo_energy: LUMO orbital energy.
        homo_lumo_gap: HOMO-LUMO gap in eV.
        s2: <S^2> expectation value (for open-shell).
        s2_expected: Expected <S^2> value.
    """
    
    energy: float = Field(
        ...,
        description="Total SCF energy in Hartree",
    )
    components: Optional[SCFEnergyComponents] = Field(
        default=None,
        description="Energy component breakdown",
    )
    convergence: Optional[SCFConvergence] = Field(
        default=None,
        description="Convergence information",
    )
    reference: str = Field(
        default="rhf",
        description="Reference type (rhf, uhf, rohf, rks, uks)",
    )
    n_basis_functions: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of basis functions",
    )
    n_alpha: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of alpha electrons",
    )
    n_beta: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of beta electrons",
    )
    homo_energy: Optional[float] = Field(
        default=None,
        description="HOMO orbital energy in Hartree",
    )
    lumo_energy: Optional[float] = Field(
        default=None,
        description="LUMO orbital energy in Hartree",
    )
    homo_lumo_gap: Optional[float] = Field(
        default=None,
        description="HOMO-LUMO gap in eV",
    )
    s2: Optional[float] = Field(
        default=None,
        ge=0,
        description="<S^2> expectation value",
    )
    s2_expected: Optional[float] = Field(
        default=None,
        ge=0,
        description="Expected <S^2> = S(S+1)",
    )
    
    @property
    def spin_contamination(self) -> Optional[float]:
        """Spin contamination: <S^2> - S(S+1)."""
        if self.s2 is not None and self.s2_expected is not None:
            return self.s2 - self.s2_expected
        return None
    
    @property
    def is_unrestricted(self) -> bool:
        """Check if calculation used unrestricted reference."""
        return self.reference.lower() in ("uhf", "uks")


# =============================================================================
# CORRELATION ENERGY OUTPUT
# =============================================================================

class MP2EnergyComponents(Psi4BaseModel):
    """
    MP2 energy component breakdown.
    
    Attributes:
        same_spin: Same-spin (SS) correlation energy.
        opposite_spin: Opposite-spin (OS) correlation energy.
        total_correlation: Total MP2 correlation energy.
        singles: Singles contribution (usually zero for canonical MP2).
        scs_correlation: SCS-MP2 correlation energy.
    """
    
    same_spin: Optional[float] = Field(
        default=None,
        description="Same-spin correlation energy",
    )
    opposite_spin: Optional[float] = Field(
        default=None,
        description="Opposite-spin correlation energy",
    )
    total_correlation: float = Field(
        ...,
        description="Total MP2 correlation energy",
    )
    singles: Optional[float] = Field(
        default=None,
        description="Singles contribution",
    )
    scs_correlation: Optional[float] = Field(
        default=None,
        description="SCS-MP2 correlation energy",
    )


class CCEnergyComponents(Psi4BaseModel):
    """
    Coupled cluster energy component breakdown.
    
    Attributes:
        singles: Singles (T1) contribution.
        doubles: Doubles (T2) contribution.
        triples: Triples (T) contribution (perturbative).
        total_correlation: Total CC correlation energy.
        t1_diagnostic: T1 diagnostic value.
        d1_diagnostic: D1 diagnostic value.
        largest_t1: Largest T1 amplitude.
        largest_t2: Largest T2 amplitude.
    """
    
    singles: Optional[float] = Field(
        default=None,
        description="Singles contribution",
    )
    doubles: Optional[float] = Field(
        default=None,
        description="Doubles contribution",
    )
    triples: Optional[float] = Field(
        default=None,
        description="Perturbative triples contribution",
    )
    total_correlation: float = Field(
        ...,
        description="Total CC correlation energy",
    )
    t1_diagnostic: Optional[float] = Field(
        default=None,
        ge=0,
        description="T1 diagnostic",
    )
    d1_diagnostic: Optional[float] = Field(
        default=None,
        ge=0,
        description="D1 diagnostic",
    )
    largest_t1: Optional[float] = Field(
        default=None,
        description="Largest T1 amplitude",
    )
    largest_t2: Optional[float] = Field(
        default=None,
        description="Largest T2 amplitude",
    )
    
    @property
    def is_single_reference_reliable(self) -> bool:
        """Check if T1 diagnostic suggests single-reference is reliable."""
        if self.t1_diagnostic is None:
            return True  # Assume OK if not computed
        return self.t1_diagnostic < 0.02  # Standard threshold


class CorrelationConvergence(Psi4BaseModel):
    """
    Correlation method convergence information.
    
    Attributes:
        converged: Whether iteration converged.
        iterations: Number of iterations.
        final_energy_change: Final energy change.
        final_residual: Final residual norm.
        max_iterations: Maximum iterations allowed.
    """
    
    converged: bool = Field(
        ...,
        description="Whether converged",
    )
    iterations: int = Field(
        ...,
        ge=0,
        description="Number of iterations",
    )
    final_energy_change: Optional[float] = Field(
        default=None,
        description="Final energy change",
    )
    final_residual: Optional[float] = Field(
        default=None,
        description="Final residual norm",
    )
    max_iterations: Optional[int] = Field(
        default=None,
        description="Maximum iterations",
    )


class CorrelationEnergyOutput(Psi4BaseModel):
    """
    Post-Hartree-Fock correlation energy output.
    
    Attributes:
        method: Correlation method name.
        reference_energy: Reference (SCF) energy.
        correlation_energy: Correlation energy.
        total_energy: Total energy (reference + correlation).
        mp2_components: MP2 energy breakdown (if applicable).
        cc_components: CC energy breakdown (if applicable).
        convergence: Convergence information.
        frozen_core: Whether core orbitals were frozen.
        n_frozen_core: Number of frozen core orbitals.
        n_frozen_virtual: Number of frozen virtual orbitals.
    """
    
    method: str = Field(
        ...,
        description="Correlation method",
    )
    reference_energy: float = Field(
        ...,
        description="Reference (SCF) energy in Hartree",
    )
    correlation_energy: float = Field(
        ...,
        description="Correlation energy in Hartree",
    )
    total_energy: float = Field(
        ...,
        description="Total energy in Hartree",
    )
    mp2_components: Optional[MP2EnergyComponents] = Field(
        default=None,
        description="MP2 energy components",
    )
    cc_components: Optional[CCEnergyComponents] = Field(
        default=None,
        description="Coupled cluster components",
    )
    convergence: Optional[CorrelationConvergence] = Field(
        default=None,
        description="Convergence information",
    )
    frozen_core: bool = Field(
        default=True,
        description="Whether core was frozen",
    )
    n_frozen_core: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of frozen core orbitals",
    )
    n_frozen_virtual: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of frozen virtual orbitals",
    )
    
    @model_validator(mode="after")
    def validate_total_energy(self) -> "CorrelationEnergyOutput":
        """Validate total energy consistency."""
        computed_total = self.reference_energy + self.correlation_energy
        if abs(computed_total - self.total_energy) > 1e-8:
            # Auto-correct small inconsistencies
            object.__setattr__(self, 'total_energy', computed_total)
        return self


# =============================================================================
# DFT ENERGY OUTPUT
# =============================================================================

class DFTEnergyComponents(Psi4BaseModel):
    """
    DFT-specific energy component breakdown.
    
    Attributes:
        exchange: Exchange energy.
        correlation: Correlation energy.
        exchange_correlation: Combined XC energy.
        exact_exchange: Exact (HF) exchange contribution.
        kinetic: Kinetic energy.
        nuclear_repulsion: Nuclear repulsion energy.
        dispersion: Dispersion correction energy.
        nlc: Non-local correlation energy.
        total: Total DFT energy.
    """
    
    exchange: Optional[float] = Field(
        default=None,
        description="Exchange energy",
    )
    correlation: Optional[float] = Field(
        default=None,
        description="Correlation energy",
    )
    exchange_correlation: Optional[float] = Field(
        default=None,
        description="Combined XC energy",
    )
    exact_exchange: Optional[float] = Field(
        default=None,
        description="Exact exchange contribution",
    )
    kinetic: Optional[float] = Field(
        default=None,
        description="Kinetic energy",
    )
    nuclear_repulsion: float = Field(
        ...,
        description="Nuclear repulsion energy",
    )
    dispersion: Optional[float] = Field(
        default=None,
        description="Dispersion correction",
    )
    nlc: Optional[float] = Field(
        default=None,
        description="Non-local correlation energy",
    )
    total: float = Field(
        ...,
        description="Total DFT energy",
    )


class DFTEnergyOutput(Psi4BaseModel):
    """
    Complete DFT energy calculation output.
    
    Attributes:
        energy: Total DFT energy.
        functional: DFT functional used.
        components: Energy component breakdown.
        convergence: SCF convergence info.
        dispersion_correction: Dispersion correction type used.
        dispersion_energy: Dispersion energy.
        grid_points: Number of DFT grid points.
        xc_grid: XC integration grid specification.
    """
    
    energy: float = Field(
        ...,
        description="Total DFT energy in Hartree",
    )
    functional: str = Field(
        ...,
        description="DFT functional name",
    )
    components: Optional[DFTEnergyComponents] = Field(
        default=None,
        description="Energy components",
    )
    convergence: Optional[SCFConvergence] = Field(
        default=None,
        description="SCF convergence",
    )
    dispersion_correction: Optional[str] = Field(
        default=None,
        description="Dispersion correction type (D3, D4, etc.)",
    )
    dispersion_energy: Optional[float] = Field(
        default=None,
        description="Dispersion energy in Hartree",
    )
    grid_points: Optional[int] = Field(
        default=None,
        ge=0,
        description="Number of DFT grid points",
    )
    xc_grid: Optional[str] = Field(
        default=None,
        description="XC grid specification",
    )


# =============================================================================
# TOTAL ENERGY OUTPUT
# =============================================================================

class TotalEnergyOutput(CalculationOutput):
    """
    Complete energy calculation output combining all components.
    
    Attributes:
        total_energy: Final total energy.
        scf_energy: SCF/DFT energy.
        correlation_energy: Correlation energy (if post-HF).
        nuclear_repulsion: Nuclear repulsion energy.
        dispersion_energy: Dispersion correction.
        solvation_energy: Solvation energy.
        relativistic_correction: Relativistic correction.
        zpve: Zero-point vibrational energy.
        thermal_correction: Thermal correction to energy.
        scf_output: Detailed SCF output.
        dft_output: Detailed DFT output.
        correlation_output: Detailed correlation output.
        molecular_formula: Molecular formula.
        point_group: Point group symmetry.
    """
    
    total_energy: float = Field(
        ...,
        description="Final total energy in Hartree",
    )
    scf_energy: Optional[float] = Field(
        default=None,
        description="SCF energy in Hartree",
    )
    correlation_energy: Optional[float] = Field(
        default=None,
        description="Correlation energy in Hartree",
    )
    nuclear_repulsion: Optional[float] = Field(
        default=None,
        description="Nuclear repulsion energy",
    )
    dispersion_energy: Optional[float] = Field(
        default=None,
        description="Dispersion correction energy",
    )
    solvation_energy: Optional[float] = Field(
        default=None,
        description="Solvation energy",
    )
    relativistic_correction: Optional[float] = Field(
        default=None,
        description="Relativistic correction",
    )
    zpve: Optional[float] = Field(
        default=None,
        description="Zero-point vibrational energy",
    )
    thermal_correction: Optional[float] = Field(
        default=None,
        description="Thermal correction to energy",
    )
    scf_output: Optional[SCFEnergyOutput] = Field(
        default=None,
        description="Detailed SCF output",
    )
    dft_output: Optional[DFTEnergyOutput] = Field(
        default=None,
        description="Detailed DFT output",
    )
    correlation_output: Optional[CorrelationEnergyOutput] = Field(
        default=None,
        description="Detailed correlation output",
    )
    molecular_formula: Optional[str] = Field(
        default=None,
        description="Molecular formula",
    )
    point_group: Optional[str] = Field(
        default=None,
        description="Point group symmetry",
    )
    
    @property
    def energy_with_zpve(self) -> Optional[float]:
        """Total energy including ZPVE correction."""
        if self.zpve is not None:
            return self.total_energy + self.zpve
        return None
    
    @property
    def energy_with_thermal(self) -> Optional[float]:
        """Total energy including thermal correction."""
        if self.thermal_correction is not None:
            return self.total_energy + self.thermal_correction
        return None


# =============================================================================
# RELATIVE ENERGY CALCULATIONS
# =============================================================================

class RelativeEnergy(Psi4BaseModel):
    """
    Relative energy between structures/species.
    
    Attributes:
        name: Name/identifier of the species.
        absolute_energy: Absolute energy in Hartree.
        relative_energy_hartree: Relative energy in Hartree.
        relative_energy_kcal_mol: Relative energy in kcal/mol.
        relative_energy_kj_mol: Relative energy in kJ/mol.
        relative_energy_ev: Relative energy in eV.
        relative_energy_cm_inv: Relative energy in cm^-1.
        is_reference: Whether this is the reference structure.
    """
    
    name: str = Field(
        ...,
        description="Structure name",
    )
    absolute_energy: float = Field(
        ...,
        description="Absolute energy in Hartree",
    )
    relative_energy_hartree: float = Field(
        default=0.0,
        description="Relative energy in Hartree",
    )
    relative_energy_kcal_mol: float = Field(
        default=0.0,
        description="Relative energy in kcal/mol",
    )
    relative_energy_kj_mol: float = Field(
        default=0.0,
        description="Relative energy in kJ/mol",
    )
    relative_energy_ev: float = Field(
        default=0.0,
        description="Relative energy in eV",
    )
    relative_energy_cm_inv: float = Field(
        default=0.0,
        description="Relative energy in cm^-1",
    )
    is_reference: bool = Field(
        default=False,
        description="Is this the reference structure",
    )


class RelativeEnergyOutput(Psi4BaseModel):
    """
    Collection of relative energies.
    
    Attributes:
        method: Calculation method.
        basis: Basis set.
        reference_name: Name of reference structure.
        reference_energy: Reference energy in Hartree.
        species: List of species with relative energies.
    """
    
    method: str = Field(
        ...,
        description="Calculation method",
    )
    basis: str = Field(
        ...,
        description="Basis set",
    )
    reference_name: str = Field(
        ...,
        description="Reference structure name",
    )
    reference_energy: float = Field(
        ...,
        description="Reference energy in Hartree",
    )
    species: list[RelativeEnergy] = Field(
        ...,
        min_length=1,
        description="List of species",
    )
    
    @classmethod
    def from_energies(
        cls,
        energies: dict[str, float],
        method: str,
        basis: str,
        reference: Optional[str] = None,
    ) -> "RelativeEnergyOutput":
        """
        Create from dictionary of name -> energy pairs.
        
        Args:
            energies: Dictionary mapping names to energies in Hartree.
            method: Calculation method.
            basis: Basis set.
            reference: Reference structure name (lowest energy if None).
        """
        from psi4_mcp.utils.helpers.units import (
            HARTREE_TO_KCAL_MOL,
            HARTREE_TO_KJ_MOL,
            HARTREE_TO_EV,
            HARTREE_TO_CM_INV,
        )
        
        # Determine reference
        if reference is None:
            reference = min(energies.keys(), key=lambda k: energies[k])
        
        ref_energy = energies[reference]
        
        species = []
        for name, energy in sorted(energies.items(), key=lambda x: x[1]):
            delta = energy - ref_energy
            species.append(RelativeEnergy(
                name=name,
                absolute_energy=energy,
                relative_energy_hartree=delta,
                relative_energy_kcal_mol=delta * HARTREE_TO_KCAL_MOL,
                relative_energy_kj_mol=delta * HARTREE_TO_KJ_MOL,
                relative_energy_ev=delta * HARTREE_TO_EV,
                relative_energy_cm_inv=delta * HARTREE_TO_CM_INV,
                is_reference=(name == reference),
            ))
        
        return cls(
            method=method,
            basis=basis,
            reference_name=reference,
            reference_energy=ref_energy,
            species=species,
        )
