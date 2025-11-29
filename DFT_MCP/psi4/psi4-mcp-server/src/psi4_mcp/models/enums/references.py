"""
Reference Wavefunction Type Enumerations.

This module defines enumerations for reference wavefunction types used in
quantum chemistry calculations. The reference determines how electrons are
treated in terms of spin and orbital occupations.

Reference Types:
    - RHF: Restricted Hartree-Fock (closed-shell singlets)
    - UHF: Unrestricted Hartree-Fock (open-shell, broken symmetry)
    - ROHF: Restricted Open-shell Hartree-Fock (open-shell with spin restriction)
    - RKS: Restricted Kohn-Sham DFT
    - UKS: Unrestricted Kohn-Sham DFT
    - CUHF: Constrained UHF
"""

from enum import Enum
from typing import Final


class ReferenceType(str, Enum):
    """
    Enumeration of reference wavefunction types.
    
    The reference type determines how electrons are distributed among
    spatial and spin orbitals in the calculation.
    
    Attributes:
        RHF: Restricted Hartree-Fock. Alpha and beta electrons share
             the same spatial orbitals. Used for closed-shell singlets.
        UHF: Unrestricted Hartree-Fock. Alpha and beta electrons have
             independent spatial orbitals. Used for open-shell systems
             or when spin symmetry breaking is desired.
        ROHF: Restricted Open-shell Hartree-Fock. Doubly occupied orbitals
              are shared between alpha and beta, but singly occupied
              orbitals are treated separately.
        RKS: Restricted Kohn-Sham. DFT equivalent of RHF.
        UKS: Unrestricted Kohn-Sham. DFT equivalent of UHF.
        CUHF: Constrained UHF. UHF with additional constraints.
        GHF: Generalized Hartree-Fock. Allows mixing of alpha and beta spins.
        GKS: Generalized Kohn-Sham. DFT equivalent of GHF.
    """
    RHF = "rhf"
    UHF = "uhf"
    ROHF = "rohf"
    RKS = "rks"
    UKS = "uks"
    CUHF = "cuhf"
    GHF = "ghf"
    GKS = "gks"
    
    @classmethod
    def from_string(cls, value: str) -> "ReferenceType":
        """
        Create a ReferenceType from a string (case-insensitive).
        
        Args:
            value: String representation of the reference type.
            
        Returns:
            Corresponding ReferenceType enum value.
            Returns RHF if the value is not recognized.
        """
        normalized = value.lower().strip()
        for member in cls:
            if member.value == normalized:
                return member
        # Default to RHF for unrecognized values
        return cls.RHF
    
    def is_restricted(self) -> bool:
        """Check if this reference type is spin-restricted."""
        return self in (ReferenceType.RHF, ReferenceType.RKS, ReferenceType.ROHF)
    
    def is_unrestricted(self) -> bool:
        """Check if this reference type is spin-unrestricted."""
        return self in (ReferenceType.UHF, ReferenceType.UKS, ReferenceType.CUHF)
    
    def is_generalized(self) -> bool:
        """Check if this reference type is generalized (GHF/GKS)."""
        return self in (ReferenceType.GHF, ReferenceType.GKS)
    
    def is_dft(self) -> bool:
        """Check if this reference type is a DFT reference (KS)."""
        return self in (ReferenceType.RKS, ReferenceType.UKS, ReferenceType.GKS)
    
    def is_hf(self) -> bool:
        """Check if this reference type is a Hartree-Fock reference."""
        return self in (
            ReferenceType.RHF, 
            ReferenceType.UHF, 
            ReferenceType.ROHF, 
            ReferenceType.CUHF,
            ReferenceType.GHF
        )
    
    def get_description(self) -> str:
        """Get a human-readable description of the reference type."""
        descriptions: dict[ReferenceType, str] = {
            ReferenceType.RHF: "Restricted Hartree-Fock",
            ReferenceType.UHF: "Unrestricted Hartree-Fock",
            ReferenceType.ROHF: "Restricted Open-shell Hartree-Fock",
            ReferenceType.RKS: "Restricted Kohn-Sham DFT",
            ReferenceType.UKS: "Unrestricted Kohn-Sham DFT",
            ReferenceType.CUHF: "Constrained Unrestricted Hartree-Fock",
            ReferenceType.GHF: "Generalized Hartree-Fock",
            ReferenceType.GKS: "Generalized Kohn-Sham DFT",
        }
        return descriptions.get(self, "Unknown reference type")
    
    def to_psi4_string(self) -> str:
        """Convert to Psi4-compatible reference string."""
        return self.value.upper()


class SpinMultiplicity(int, Enum):
    """
    Common spin multiplicities in quantum chemistry.
    
    The spin multiplicity is 2S + 1, where S is the total spin quantum number.
    
    Attributes:
        SINGLET: S = 0, 2S + 1 = 1 (all electrons paired)
        DOUBLET: S = 1/2, 2S + 1 = 2 (one unpaired electron)
        TRIPLET: S = 1, 2S + 1 = 3 (two unpaired electrons)
        QUARTET: S = 3/2, 2S + 1 = 4 (three unpaired electrons)
        QUINTET: S = 2, 2S + 1 = 5 (four unpaired electrons)
        SEXTET: S = 5/2, 2S + 1 = 6 (five unpaired electrons)
        SEPTET: S = 3, 2S + 1 = 7 (six unpaired electrons)
    """
    SINGLET = 1
    DOUBLET = 2
    TRIPLET = 3
    QUARTET = 4
    QUINTET = 5
    SEXTET = 6
    SEPTET = 7
    OCTET = 8
    NONET = 9
    
    @classmethod
    def from_unpaired_electrons(cls, n_unpaired: int) -> "SpinMultiplicity":
        """
        Create SpinMultiplicity from number of unpaired electrons.
        
        Args:
            n_unpaired: Number of unpaired electrons.
            
        Returns:
            Corresponding SpinMultiplicity enum value.
        """
        multiplicity = n_unpaired + 1
        for member in cls:
            if member.value == multiplicity:
                return member
        # Return the integer value if not a named member
        return cls.SINGLET
    
    def get_unpaired_electrons(self) -> int:
        """Get the number of unpaired electrons for this multiplicity."""
        return self.value - 1
    
    def get_total_spin(self) -> float:
        """Get the total spin quantum number S."""
        return (self.value - 1) / 2.0
    
    def get_ms_values(self) -> list[float]:
        """Get all possible M_S values for this multiplicity."""
        s = self.get_total_spin()
        return [s - i for i in range(self.value)]
    
    def get_name(self) -> str:
        """Get the name of the spin multiplicity."""
        names: dict[int, str] = {
            1: "singlet",
            2: "doublet", 
            3: "triplet",
            4: "quartet",
            5: "quintet",
            6: "sextet",
            7: "septet",
            8: "octet",
            9: "nonet",
        }
        return names.get(self.value, f"{self.value}-et")


class OrbitalOccupation(str, Enum):
    """
    Orbital occupation types for electronic structure calculations.
    
    Attributes:
        AUFBAU: Standard aufbau filling (lowest energy first)
        FERMI: Fermi-Dirac smearing for metals/difficult cases
        FRACTIONAL: Fractional occupation numbers
        MOM: Maximum Overlap Method for excited states
        FIXED: Fixed occupation (user-specified)
    """
    AUFBAU = "aufbau"
    FERMI = "fermi"
    FRACTIONAL = "fractional"
    MOM = "mom"
    FIXED = "fixed"
    
    def get_description(self) -> str:
        """Get a human-readable description of the occupation type."""
        descriptions: dict[OrbitalOccupation, str] = {
            OrbitalOccupation.AUFBAU: "Standard aufbau principle (lowest energy first)",
            OrbitalOccupation.FERMI: "Fermi-Dirac smearing for metallic/difficult systems",
            OrbitalOccupation.FRACTIONAL: "Fractional occupation numbers",
            OrbitalOccupation.MOM: "Maximum Overlap Method for excited state SCF",
            OrbitalOccupation.FIXED: "Fixed user-specified occupation",
        }
        return descriptions.get(self, "Unknown occupation type")


class SpinState(str, Enum):
    """
    Spin state classifications for molecular systems.
    
    Attributes:
        CLOSED_SHELL: All electrons paired (singlet ground state)
        OPEN_SHELL: One or more unpaired electrons
        HIGH_SPIN: Maximum number of unpaired electrons for given configuration
        LOW_SPIN: Minimum number of unpaired electrons for given configuration
        INTERMEDIATE_SPIN: Between high and low spin
    """
    CLOSED_SHELL = "closed_shell"
    OPEN_SHELL = "open_shell"
    HIGH_SPIN = "high_spin"
    LOW_SPIN = "low_spin"
    INTERMEDIATE_SPIN = "intermediate_spin"
    
    @classmethod
    def from_multiplicity_and_electrons(
        cls, 
        multiplicity: int, 
        n_electrons: int
    ) -> "SpinState":
        """
        Determine spin state from multiplicity and electron count.
        
        Args:
            multiplicity: Spin multiplicity (2S + 1).
            n_electrons: Total number of electrons.
            
        Returns:
            The appropriate SpinState classification.
        """
        if multiplicity == 1:
            return cls.CLOSED_SHELL
        
        # For open shell, need to determine if high/low spin
        # This is a simplified heuristic
        n_unpaired = multiplicity - 1
        max_unpaired = n_electrons  # Theoretical maximum
        
        if n_unpaired == 0:
            return cls.CLOSED_SHELL
        elif n_unpaired >= max_unpaired // 2:
            return cls.HIGH_SPIN
        else:
            return cls.LOW_SPIN


# =============================================================================
# COMPATIBILITY MAPPINGS
# =============================================================================

# Mapping from reference type to compatible methods
REFERENCE_METHOD_COMPATIBILITY: Final[dict[ReferenceType, frozenset[str]]] = {
    ReferenceType.RHF: frozenset({
        "hf", "mp2", "mp3", "mp4", "ccsd", "ccsd(t)", "ccsdt", "cisd",
        "fci", "casscf", "rasscf", "sapt", "adc"
    }),
    ReferenceType.UHF: frozenset({
        "hf", "mp2", "ccsd", "ccsd(t)", "cisd"
    }),
    ReferenceType.ROHF: frozenset({
        "hf", "mp2", "ccsd", "cisd", "casscf", "rasscf"
    }),
    ReferenceType.RKS: frozenset({
        "dft", "tddft", "mp2", "sapt"
    }),
    ReferenceType.UKS: frozenset({
        "dft", "tddft", "mp2"
    }),
    ReferenceType.CUHF: frozenset({
        "hf"
    }),
    ReferenceType.GHF: frozenset({
        "hf"
    }),
    ReferenceType.GKS: frozenset({
        "dft"
    }),
}


# Default reference for each scenario
DEFAULT_REFERENCES: Final[dict[str, ReferenceType]] = {
    "closed_shell_hf": ReferenceType.RHF,
    "open_shell_hf": ReferenceType.UHF,
    "closed_shell_dft": ReferenceType.RKS,
    "open_shell_dft": ReferenceType.UKS,
    "transition_metal": ReferenceType.UKS,
    "radical": ReferenceType.UHF,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def suggest_reference(
    n_electrons: int,
    multiplicity: int,
    is_dft: bool = False
) -> ReferenceType:
    """
    Suggest an appropriate reference type based on system properties.
    
    Args:
        n_electrons: Total number of electrons in the system.
        multiplicity: Spin multiplicity (2S + 1).
        is_dft: Whether this is a DFT calculation.
        
    Returns:
        Recommended ReferenceType for the calculation.
    """
    # Closed shell (singlet with even electrons)
    is_closed_shell = (multiplicity == 1) and (n_electrons % 2 == 0)
    
    if is_dft:
        if is_closed_shell:
            return ReferenceType.RKS
        else:
            return ReferenceType.UKS
    else:
        if is_closed_shell:
            return ReferenceType.RHF
        else:
            # For open shell, ROHF is more physically meaningful but
            # UHF is more flexible. Default to UHF.
            return ReferenceType.UHF


def validate_multiplicity_electrons(multiplicity: int, n_electrons: int) -> bool:
    """
    Check if a multiplicity is valid for a given number of electrons.
    
    The number of unpaired electrons (multiplicity - 1) cannot exceed
    the total number of electrons, and both must have the same parity.
    
    Args:
        multiplicity: Spin multiplicity (2S + 1), must be positive integer.
        n_electrons: Total number of electrons, must be non-negative.
        
    Returns:
        True if the combination is physically valid, False otherwise.
    """
    if multiplicity < 1:
        return False
    if n_electrons < 0:
        return False
    
    n_unpaired = multiplicity - 1
    
    # Cannot have more unpaired electrons than total electrons
    if n_unpaired > n_electrons:
        return False
    
    # Parity check: n_unpaired and n_electrons must have same parity
    # (both odd or both even)
    if (n_unpaired % 2) != (n_electrons % 2):
        return False
    
    return True


def get_n_alpha_beta(n_electrons: int, multiplicity: int) -> tuple[int, int]:
    """
    Calculate the number of alpha and beta electrons.
    
    Args:
        n_electrons: Total number of electrons.
        multiplicity: Spin multiplicity (2S + 1).
        
    Returns:
        Tuple of (n_alpha, n_beta) electrons.
        Returns (0, 0) if the combination is invalid.
    """
    if not validate_multiplicity_electrons(multiplicity, n_electrons):
        return (0, 0)
    
    n_unpaired = multiplicity - 1
    n_paired = n_electrons - n_unpaired
    
    # Paired electrons are split evenly between alpha and beta
    n_beta = n_paired // 2
    n_alpha = n_beta + n_unpaired
    
    return (n_alpha, n_beta)
