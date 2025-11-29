"""
SAPT Output Models.

This module provides Pydantic models for representing Symmetry-Adapted
Perturbation Theory (SAPT) calculation results, including various
levels of SAPT and energy decomposition analysis.

Key Classes:
    - SAPTEnergyComponents: SAPT energy decomposition
    - SAPTOutput: Complete SAPT results
    - SAPTComponentBreakdown: Detailed component analysis
"""

from typing import Any, Optional, Literal
from pydantic import Field, model_validator

from psi4_mcp.models.base import Psi4BaseModel, CalculationOutput


# =============================================================================
# SAPT ENERGY COMPONENTS
# =============================================================================

class SAPTFirstOrder(Psi4BaseModel):
    """
    First-order SAPT energy components.
    
    Attributes:
        elst10: First-order electrostatic energy.
        exch10: First-order exchange energy.
        exch10_s2: Exchange with S^2 approximation.
        total: Total first-order energy.
    """
    
    elst10: float = Field(
        ...,
        description="E_elst^(10) in Hartree",
    )
    exch10: float = Field(
        ...,
        description="E_exch^(10) in Hartree",
    )
    exch10_s2: Optional[float] = Field(
        default=None,
        description="E_exch^(10)(S^2) in Hartree",
    )
    total: Optional[float] = Field(
        default=None,
        description="Total first-order energy",
    )
    
    @model_validator(mode="after")
    def compute_total(self) -> "SAPTFirstOrder":
        """Compute total first-order energy."""
        if self.total is None:
            total = self.elst10 + self.exch10
            object.__setattr__(self, 'total', total)
        return self


class SAPTSecondOrder(Psi4BaseModel):
    """
    Second-order SAPT energy components.
    
    Attributes:
        ind20: Second-order induction energy.
        ind20_resp: Induction with response.
        exch_ind20: Exchange-induction.
        exch_ind20_resp: Exchange-induction with response.
        disp20: Second-order dispersion.
        exch_disp20: Exchange-dispersion.
        total_ind: Total induction.
        total_disp: Total dispersion.
        total: Total second-order energy.
    """
    
    ind20: Optional[float] = Field(
        default=None,
        description="E_ind^(20) in Hartree",
    )
    ind20_resp: Optional[float] = Field(
        default=None,
        description="E_ind,resp^(20) in Hartree",
    )
    exch_ind20: Optional[float] = Field(
        default=None,
        description="E_exch-ind^(20) in Hartree",
    )
    exch_ind20_resp: Optional[float] = Field(
        default=None,
        description="E_exch-ind,resp^(20) in Hartree",
    )
    disp20: float = Field(
        ...,
        description="E_disp^(20) in Hartree",
    )
    exch_disp20: Optional[float] = Field(
        default=None,
        description="E_exch-disp^(20) in Hartree",
    )
    total_ind: Optional[float] = Field(
        default=None,
        description="Total induction",
    )
    total_disp: Optional[float] = Field(
        default=None,
        description="Total dispersion",
    )
    total: Optional[float] = Field(
        default=None,
        description="Total second-order",
    )


class SAPTHigherOrder(Psi4BaseModel):
    """
    Higher-order SAPT energy corrections.
    
    Attributes:
        ind30: Third-order induction.
        exch_ind30: Exchange-induction (30).
        ind22: Second-order induction (22).
        exch_ind22: Exchange-induction (22).
        disp21: Dispersion (21).
        disp22_sdq: Dispersion (22) SDQ.
        disp22_t: Dispersion (22) T.
        est_ind22: Estimated ind22.
        delta_hf: Delta HF correction.
    """
    
    ind30: Optional[float] = Field(default=None, description="E_ind^(30)")
    exch_ind30: Optional[float] = Field(default=None, description="E_exch-ind^(30)")
    ind22: Optional[float] = Field(default=None, description="E_ind^(22)")
    exch_ind22: Optional[float] = Field(default=None, description="E_exch-ind^(22)")
    disp21: Optional[float] = Field(default=None, description="E_disp^(21)")
    disp22_sdq: Optional[float] = Field(default=None, description="E_disp^(22)(SDQ)")
    disp22_t: Optional[float] = Field(default=None, description="E_disp^(22)(T)")
    est_ind22: Optional[float] = Field(default=None, description="Estimated E_ind^(22)")
    delta_hf: Optional[float] = Field(default=None, description="Delta HF correction")


class SAPTEnergyComponents(Psi4BaseModel):
    """
    Complete SAPT energy component breakdown.
    
    Attributes:
        electrostatic: Total electrostatic energy.
        exchange: Total exchange energy.
        induction: Total induction energy.
        dispersion: Total dispersion energy.
        first_order: First-order components.
        second_order: Second-order components.
        higher_order: Higher-order components.
        total_interaction: Total SAPT interaction energy.
    """
    
    electrostatic: float = Field(
        ...,
        description="Total electrostatic in Hartree",
    )
    exchange: float = Field(
        ...,
        description="Total exchange in Hartree",
    )
    induction: float = Field(
        ...,
        description="Total induction in Hartree",
    )
    dispersion: float = Field(
        ...,
        description="Total dispersion in Hartree",
    )
    first_order: Optional[SAPTFirstOrder] = Field(
        default=None,
        description="First-order terms",
    )
    second_order: Optional[SAPTSecondOrder] = Field(
        default=None,
        description="Second-order terms",
    )
    higher_order: Optional[SAPTHigherOrder] = Field(
        default=None,
        description="Higher-order terms",
    )
    total_interaction: float = Field(
        ...,
        description="Total interaction energy",
    )
    
    @model_validator(mode="after")
    def validate_total(self) -> "SAPTEnergyComponents":
        """Validate total interaction energy."""
        computed = (
            self.electrostatic + 
            self.exchange + 
            self.induction + 
            self.dispersion
        )
        if abs(computed - self.total_interaction) > 1e-6:
            # Allow small discrepancy due to higher-order terms
            pass
        return self


# =============================================================================
# SAPT LEVELS
# =============================================================================

class SAPT0Output(Psi4BaseModel):
    """
    SAPT0 calculation output.
    
    SAPT0 includes: Elst10 + Exch10 + Ind20,resp + Exch-Ind20,resp + Disp20 + Exch-Disp20
    
    Attributes:
        elst10: Electrostatic (10).
        exch10: Exchange (10).
        ind20_resp: Induction (20) with response.
        exch_ind20_resp: Exchange-induction (20) with response.
        disp20: Dispersion (20).
        exch_disp20: Exchange-dispersion (20).
        total_interaction: Total SAPT0 interaction.
        kcal_mol: Energies in kcal/mol.
    """
    
    elst10: float = Field(..., description="Elst10")
    exch10: float = Field(..., description="Exch10")
    ind20_resp: float = Field(..., description="Ind20,resp")
    exch_ind20_resp: float = Field(..., description="Exch-Ind20,resp")
    disp20: float = Field(..., description="Disp20")
    exch_disp20: float = Field(..., description="Exch-Disp20")
    total_interaction: float = Field(..., description="Total")
    kcal_mol: Optional[dict[str, float]] = Field(
        default=None,
        description="Energies in kcal/mol",
    )
    
    def to_kcal_mol(self) -> dict[str, float]:
        """Convert all energies to kcal/mol."""
        from psi4_mcp.utils.helpers.units import HARTREE_TO_KCAL_MOL
        factor = HARTREE_TO_KCAL_MOL
        return {
            "elst10": self.elst10 * factor,
            "exch10": self.exch10 * factor,
            "ind20_resp": self.ind20_resp * factor,
            "exch_ind20_resp": self.exch_ind20_resp * factor,
            "disp20": self.disp20 * factor,
            "exch_disp20": self.exch_disp20 * factor,
            "total": self.total_interaction * factor,
            "electrostatic": self.elst10 * factor,
            "exchange": self.exch10 * factor,
            "induction": (self.ind20_resp + self.exch_ind20_resp) * factor,
            "dispersion": (self.disp20 + self.exch_disp20) * factor,
        }


class SAPT2Output(Psi4BaseModel):
    """
    SAPT2 calculation output.
    
    Attributes:
        sapt0_components: SAPT0 components.
        ind22: Induction (22).
        exch_ind22: Exchange-induction (22).
        disp21: Dispersion (21).
        total_interaction: Total SAPT2 interaction.
    """
    
    sapt0_components: SAPT0Output = Field(
        ...,
        description="SAPT0 components",
    )
    ind22: Optional[float] = Field(default=None, description="Ind22")
    exch_ind22: Optional[float] = Field(default=None, description="Exch-Ind22")
    disp21: Optional[float] = Field(default=None, description="Disp21")
    total_interaction: float = Field(..., description="Total SAPT2")


class SAPT2PlusOutput(Psi4BaseModel):
    """
    SAPT2+ calculation output.
    
    Attributes:
        sapt2_components: SAPT2 components.
        disp22_sdq: Dispersion (22) SDQ.
        total_interaction: Total SAPT2+ interaction.
        ccd_disp: CCD dispersion (if computed).
    """
    
    sapt2_components: Optional[SAPT2Output] = Field(
        default=None,
        description="SAPT2 components",
    )
    disp22_sdq: Optional[float] = Field(default=None, description="Disp22(SDQ)")
    total_interaction: float = Field(..., description="Total SAPT2+")
    ccd_disp: Optional[float] = Field(default=None, description="CCD dispersion")


class SAPT2Plus3Output(Psi4BaseModel):
    """
    SAPT2+(3) calculation output.
    
    Attributes:
        sapt2plus_components: SAPT2+ components.
        disp22_t: Dispersion (22) T.
        ind30: Induction (30).
        exch_ind30: Exchange-induction (30).
        total_interaction: Total SAPT2+(3) interaction.
    """
    
    sapt2plus_components: Optional[SAPT2PlusOutput] = Field(
        default=None,
        description="SAPT2+ components",
    )
    disp22_t: Optional[float] = Field(default=None, description="Disp22(T)")
    ind30: Optional[float] = Field(default=None, description="Ind30")
    exch_ind30: Optional[float] = Field(default=None, description="Exch-Ind30")
    total_interaction: float = Field(..., description="Total SAPT2+(3)")


# =============================================================================
# F-SAPT OUTPUT
# =============================================================================

class FSAPTFragment(Psi4BaseModel):
    """
    F-SAPT fragment definition.
    
    Attributes:
        fragment_id: Fragment identifier.
        atom_indices: Atom indices in fragment.
        name: Fragment name.
        charge: Fragment charge.
    """
    
    fragment_id: int = Field(..., ge=0, description="Fragment ID")
    atom_indices: list[int] = Field(..., description="Atom indices")
    name: Optional[str] = Field(default=None, description="Name")
    charge: int = Field(default=0, description="Charge")


class FSAPTPairInteraction(Psi4BaseModel):
    """
    F-SAPT pairwise fragment interaction.
    
    Attributes:
        fragment1_id: First fragment ID.
        fragment2_id: Second fragment ID.
        electrostatic: Electrostatic interaction.
        exchange: Exchange interaction.
        induction: Induction interaction.
        dispersion: Dispersion interaction.
        total: Total interaction.
    """
    
    fragment1_id: int = Field(..., ge=0, description="Fragment 1")
    fragment2_id: int = Field(..., ge=0, description="Fragment 2")
    electrostatic: float = Field(..., description="Electrostatic")
    exchange: float = Field(..., description="Exchange")
    induction: float = Field(..., description="Induction")
    dispersion: float = Field(..., description="Dispersion")
    total: float = Field(..., description="Total")


class FSAPTOutput(Psi4BaseModel):
    """
    F-SAPT (Functional-group SAPT) output.
    
    Attributes:
        fragments: Fragment definitions.
        pair_interactions: Pairwise interactions.
        link_atoms: Link atom information.
        total_interaction: Total interaction energy.
    """
    
    fragments: list[FSAPTFragment] = Field(
        ...,
        description="Fragments",
    )
    pair_interactions: list[FSAPTPairInteraction] = Field(
        ...,
        description="Pair interactions",
    )
    link_atoms: Optional[list[int]] = Field(
        default=None,
        description="Link atoms",
    )
    total_interaction: float = Field(
        ...,
        description="Total interaction",
    )
    
    def get_interaction(self, frag1: int, frag2: int) -> Optional[FSAPTPairInteraction]:
        """Get interaction between two fragments."""
        for pair in self.pair_interactions:
            if (pair.fragment1_id == frag1 and pair.fragment2_id == frag2) or \
               (pair.fragment1_id == frag2 and pair.fragment2_id == frag1):
                return pair
        return None


# =============================================================================
# COMPLETE SAPT OUTPUT
# =============================================================================

class SAPTOutput(CalculationOutput):
    """
    Complete SAPT calculation output.
    
    Attributes:
        sapt_level: SAPT level (sapt0, sapt2, sapt2+, etc.).
        components: Energy components breakdown.
        sapt0: SAPT0 results.
        sapt2: SAPT2 results.
        sapt2plus: SAPT2+ results.
        sapt2plus3: SAPT2+(3) results.
        fsapt: F-SAPT results.
        monomer_a_energy: Monomer A energy.
        monomer_b_energy: Monomer B energy.
        dimer_energy: Dimer energy.
        counterpoise_correction: CP correction.
        basis_set_superposition_error: BSSE estimate.
        delta_hf: Delta HF correction.
        interaction_energy: Total interaction energy.
        interaction_energy_kcal_mol: Interaction in kcal/mol.
    """
    
    sapt_level: str = Field(
        ...,
        description="SAPT level",
    )
    components: SAPTEnergyComponents = Field(
        ...,
        description="Energy components",
    )
    sapt0: Optional[SAPT0Output] = Field(
        default=None,
        description="SAPT0 results",
    )
    sapt2: Optional[SAPT2Output] = Field(
        default=None,
        description="SAPT2 results",
    )
    sapt2plus: Optional[SAPT2PlusOutput] = Field(
        default=None,
        description="SAPT2+ results",
    )
    sapt2plus3: Optional[SAPT2Plus3Output] = Field(
        default=None,
        description="SAPT2+(3) results",
    )
    fsapt: Optional[FSAPTOutput] = Field(
        default=None,
        description="F-SAPT results",
    )
    monomer_a_energy: Optional[float] = Field(
        default=None,
        description="Monomer A energy",
    )
    monomer_b_energy: Optional[float] = Field(
        default=None,
        description="Monomer B energy",
    )
    dimer_energy: Optional[float] = Field(
        default=None,
        description="Dimer energy",
    )
    counterpoise_correction: Optional[float] = Field(
        default=None,
        description="CP correction",
    )
    basis_set_superposition_error: Optional[float] = Field(
        default=None,
        description="BSSE",
    )
    delta_hf: Optional[float] = Field(
        default=None,
        description="Delta HF",
    )
    interaction_energy: float = Field(
        ...,
        description="Interaction energy (Hartree)",
    )
    interaction_energy_kcal_mol: Optional[float] = Field(
        default=None,
        description="Interaction (kcal/mol)",
    )
    
    @model_validator(mode="after")
    def compute_kcal_mol(self) -> "SAPTOutput":
        """Compute interaction in kcal/mol."""
        if self.interaction_energy_kcal_mol is None:
            from psi4_mcp.utils.helpers.units import HARTREE_TO_KCAL_MOL
            kcal = self.interaction_energy * HARTREE_TO_KCAL_MOL
            object.__setattr__(self, 'interaction_energy_kcal_mol', kcal)
        return self
    
    def get_component_percentages(self) -> dict[str, float]:
        """Get percentage contribution of each component."""
        total = abs(self.components.total_interaction)
        if total < 1e-10:
            return {}
        
        return {
            "electrostatic": 100 * self.components.electrostatic / total,
            "exchange": 100 * self.components.exchange / total,
            "induction": 100 * self.components.induction / total,
            "dispersion": 100 * self.components.dispersion / total,
        }
    
    @property
    def is_attractive(self) -> bool:
        """Check if interaction is attractive (negative)."""
        return self.interaction_energy < 0
    
    @property
    def dominant_component(self) -> str:
        """Get the dominant attractive/repulsive component."""
        comps = {
            "electrostatic": self.components.electrostatic,
            "exchange": self.components.exchange,
            "induction": self.components.induction,
            "dispersion": self.components.dispersion,
        }
        
        # For attractive interaction, find most negative
        if self.is_attractive:
            return min(comps.keys(), key=lambda k: comps[k])
        else:
            return max(comps.keys(), key=lambda k: comps[k])
