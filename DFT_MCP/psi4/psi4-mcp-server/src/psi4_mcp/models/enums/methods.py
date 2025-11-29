"""
Quantum Chemistry Method Enumerations.

This module defines comprehensive enumerations for all quantum chemistry
methods supported by Psi4. Methods are categorized by their theoretical
foundation and computational characteristics.

Categories:
    - Hartree-Fock methods
    - Density Functional Theory (DFT)
    - Møller-Plesset Perturbation Theory
    - Coupled Cluster methods
    - Configuration Interaction
    - Multi-reference methods
    - Symmetry-Adapted Perturbation Theory (SAPT)
    - Time-Dependent methods
"""

from enum import Enum
from typing import Final


class MethodCategory(str, Enum):
    """
    High-level categorization of quantum chemistry methods.
    
    Attributes:
        HF: Hartree-Fock and related mean-field methods
        DFT: Density Functional Theory methods
        PERTURBATION: Perturbation theory methods (MPn)
        COUPLED_CLUSTER: Coupled cluster methods
        CI: Configuration Interaction methods
        MCSCF: Multi-configurational SCF methods
        SAPT: Symmetry-Adapted Perturbation Theory
        TDDFT: Time-dependent DFT
        COMPOSITE: Composite methods (Gn, CBS, etc.)
        SEMIEMPIRICAL: Semi-empirical methods
    """
    HF = "hf"
    DFT = "dft"
    PERTURBATION = "perturbation"
    COUPLED_CLUSTER = "coupled_cluster"
    CI = "configuration_interaction"
    MCSCF = "mcscf"
    SAPT = "sapt"
    TDDFT = "tddft"
    COMPOSITE = "composite"
    SEMIEMPIRICAL = "semiempirical"


class HFMethod(str, Enum):
    """
    Hartree-Fock and related methods.
    
    Attributes:
        HF: Standard Hartree-Fock
        SCF: Self-Consistent Field (alias for HF)
    """
    HF = "hf"
    SCF = "scf"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return "scf"


class DFTFunctionalType(str, Enum):
    """
    Classification of DFT exchange-correlation functionals.
    
    Attributes:
        LDA: Local Density Approximation
        GGA: Generalized Gradient Approximation
        META_GGA: Meta-GGA (includes kinetic energy density)
        HYBRID: Hybrid functionals (GGA + exact exchange)
        META_HYBRID: Meta-hybrid functionals
        RANGE_SEPARATED: Range-separated hybrid functionals
        DOUBLE_HYBRID: Double-hybrid functionals (hybrid + PT2)
    """
    LDA = "lda"
    GGA = "gga"
    META_GGA = "meta_gga"
    HYBRID = "hybrid"
    META_HYBRID = "meta_hybrid"
    RANGE_SEPARATED = "range_separated"
    DOUBLE_HYBRID = "double_hybrid"


class DFTFunctional(str, Enum):
    """
    Comprehensive enumeration of DFT functionals supported by Psi4.
    
    Organized by functional type (LDA, GGA, hybrid, etc.).
    """
    # LDA Functionals
    SVWN = "svwn"
    SVWN5 = "svwn5"
    SPW92 = "spw92"
    
    # GGA Functionals
    BLYP = "blyp"
    BP86 = "bp86"
    PBE = "pbe"
    REVPBE = "revpbe"
    RPBE = "rpbe"
    PW91 = "pw91"
    SOGGA = "sogga"
    SOGGA11 = "sogga11"
    N12 = "n12"
    GAM = "gam"
    
    # Meta-GGA Functionals
    TPSS = "tpss"
    REVTPSS = "revtpss"
    M06_L = "m06-l"
    M11_L = "m11-l"
    MN12_L = "mn12-l"
    MN15_L = "mn15-l"
    SCAN = "scan"
    REVSCAN = "revscan"
    R2SCAN = "r2scan"
    
    # Hybrid GGA Functionals
    B3LYP = "b3lyp"
    B3LYP5 = "b3lyp5"
    B3PW91 = "b3pw91"
    B3P86 = "b3p86"
    PBE0 = "pbe0"
    B97 = "b97"
    B97_1 = "b97-1"
    B97_2 = "b97-2"
    B97_3 = "b97-3"
    SOGGA11_X = "sogga11-x"
    PBE50 = "pbe50"
    BHHLYP = "bhhlyp"
    B1LYP = "b1lyp"
    B5050LYP = "b5050lyp"
    
    # Meta-Hybrid Functionals
    M05 = "m05"
    M05_2X = "m05-2x"
    M06 = "m06"
    M06_2X = "m06-2x"
    M06_HF = "m06-hf"
    M08_HX = "m08-hx"
    M08_SO = "m08-so"
    M11 = "m11"
    MN12_SX = "mn12-sx"
    MN15 = "mn15"
    TPSSh = "tpssh"
    REVTPSSH = "revtpssh"
    SCAN0 = "scan0"
    
    # Range-Separated Hybrid Functionals
    WB97 = "wb97"
    WB97X = "wb97x"
    WB97X_D = "wb97x-d"
    WB97X_D3 = "wb97x-d3"
    WB97X_D3BJ = "wb97x-d3bj"
    WB97M_D3BJ = "wb97m-d3bj"
    WB97X_V = "wb97x-v"
    WB97M_V = "wb97m-v"
    CAM_B3LYP = "cam-b3lyp"
    LC_WPBE = "lc-wpbe"
    LC_BLYP = "lc-blyp"
    LRC_WPBE = "lrc-wpbe"
    LRC_WPBEH = "lrc-wpbeh"
    
    # Double-Hybrid Functionals
    B2PLYP = "b2plyp"
    B2PLYP_D3 = "b2plyp-d3"
    B2GPPLYP = "b2gpplyp"
    PWPB95 = "pwpb95"
    PWPB95_D3 = "pwpb95-d3"
    DSD_PBEP86 = "dsd-pbep86"
    DSD_PBEP86_D3BJ = "dsd-pbep86-d3bj"
    DSD_BLYP = "dsd-blyp"
    DSD_BLYP_D3BJ = "dsd-blyp-d3bj"
    
    @classmethod
    def from_string(cls, value: str) -> "DFTFunctional":
        """
        Create a DFTFunctional from a string (case-insensitive).
        
        Args:
            value: String name of the functional.
            
        Returns:
            Corresponding DFTFunctional enum, or B3LYP if not found.
        """
        normalized = value.lower().strip().replace("_", "-")
        for member in cls:
            if member.value == normalized:
                return member
        # Default to B3LYP
        return cls.B3LYP
    
    def get_type(self) -> DFTFunctionalType:
        """Get the functional type classification."""
        lda = {self.SVWN, self.SVWN5, self.SPW92}
        gga = {
            self.BLYP, self.BP86, self.PBE, self.REVPBE, self.RPBE,
            self.PW91, self.SOGGA, self.SOGGA11, self.N12, self.GAM
        }
        meta_gga = {
            self.TPSS, self.REVTPSS, self.M06_L, self.M11_L,
            self.MN12_L, self.MN15_L, self.SCAN, self.REVSCAN, self.R2SCAN
        }
        hybrid = {
            self.B3LYP, self.B3LYP5, self.B3PW91, self.B3P86, self.PBE0,
            self.B97, self.B97_1, self.B97_2, self.B97_3, self.SOGGA11_X,
            self.PBE50, self.BHHLYP, self.B1LYP, self.B5050LYP
        }
        meta_hybrid = {
            self.M05, self.M05_2X, self.M06, self.M06_2X, self.M06_HF,
            self.M08_HX, self.M08_SO, self.M11, self.MN12_SX, self.MN15,
            self.TPSSh, self.REVTPSSH, self.SCAN0
        }
        range_separated = {
            self.WB97, self.WB97X, self.WB97X_D, self.WB97X_D3, self.WB97X_D3BJ,
            self.WB97M_D3BJ, self.WB97X_V, self.WB97M_V, self.CAM_B3LYP,
            self.LC_WPBE, self.LC_BLYP, self.LRC_WPBE, self.LRC_WPBEH
        }
        double_hybrid = {
            self.B2PLYP, self.B2PLYP_D3, self.B2GPPLYP, self.PWPB95,
            self.PWPB95_D3, self.DSD_PBEP86, self.DSD_PBEP86_D3BJ,
            self.DSD_BLYP, self.DSD_BLYP_D3BJ
        }
        
        if self in lda:
            return DFTFunctionalType.LDA
        elif self in gga:
            return DFTFunctionalType.GGA
        elif self in meta_gga:
            return DFTFunctionalType.META_GGA
        elif self in hybrid:
            return DFTFunctionalType.HYBRID
        elif self in meta_hybrid:
            return DFTFunctionalType.META_HYBRID
        elif self in range_separated:
            return DFTFunctionalType.RANGE_SEPARATED
        elif self in double_hybrid:
            return DFTFunctionalType.DOUBLE_HYBRID
        else:
            return DFTFunctionalType.GGA
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


class PerturbationMethod(str, Enum):
    """
    Møller-Plesset perturbation theory methods.
    
    Attributes:
        MP2: Second-order Møller-Plesset
        SCS_MP2: Spin-Component Scaled MP2
        SOS_MP2: Scaled Opposite-Spin MP2
        MP2_5: MP2.5 (average of MP2 and MP3)
        MP3: Third-order Møller-Plesset
        MP4: Fourth-order Møller-Plesset
        MP4_SDQ: MP4 with singles, doubles, quadruples only
        ZAPT2: Z-averaged perturbation theory (for open shell)
        DF_MP2: Density-fitted MP2
        CD_MP2: Cholesky-decomposed MP2
    """
    MP2 = "mp2"
    SCS_MP2 = "scs-mp2"
    SOS_MP2 = "sos-mp2"
    MP2_5 = "mp2.5"
    MP3 = "mp3"
    MP4 = "mp4"
    MP4_SDQ = "mp4(sdq)"
    ZAPT2 = "zapt2"
    DF_MP2 = "df-mp2"
    CD_MP2 = "cd-mp2"
    OMP2 = "omp2"
    OMP2_5 = "omp2.5"
    OMP3 = "omp3"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


class CoupledClusterMethod(str, Enum):
    """
    Coupled cluster methods.
    
    These methods provide high-accuracy results by including electron
    correlation through cluster operators.
    
    Attributes:
        CCSD: Coupled Cluster Singles and Doubles
        CCSD_T: CCSD with perturbative triples correction
        CC2: Approximate coupled cluster with doubles
        CC3: Approximate coupled cluster with triples
        CCSDT: Full coupled cluster with triples
        CCSDT_Q: CCSDT with perturbative quadruples
        CCSDTQ: Full coupled cluster with quadruples
        BCCD: Brueckner coupled cluster doubles
        BCCD_T: BCCD with perturbative triples
        EOM_CCSD: Equation of Motion CCSD (excited states)
        EOM_CC2: Equation of Motion CC2
        EOM_CC3: Equation of Motion CC3
        LR_CCSD: Linear Response CCSD
        DLPNO_CCSD: Domain-based LPNO CCSD
        DLPNO_CCSD_T: DLPNO-CCSD(T)
    """
    CC2 = "cc2"
    CCSD = "ccsd"
    CCSD_T = "ccsd(t)"
    CC3 = "cc3"
    CCSDT = "ccsdt"
    CCSDT_Q = "ccsdt(q)"
    CCSDTQ = "ccsdtq"
    BCCD = "bccd"
    BCCD_T = "bccd(t)"
    A_CCSD_T = "a-ccsd(t)"
    EOM_CCSD = "eom-ccsd"
    EOM_CC2 = "eom-cc2"
    EOM_CC3 = "eom-cc3"
    LR_CCSD = "lr-ccsd"
    DLPNO_CCSD = "dlpno-ccsd"
    DLPNO_CCSD_T = "dlpno-ccsd(t)"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value
    
    def includes_triples(self) -> bool:
        """Check if method includes triple excitations."""
        triples_methods = {
            self.CCSD_T, self.CC3, self.CCSDT, self.CCSDT_Q,
            self.CCSDTQ, self.BCCD_T, self.A_CCSD_T,
            self.EOM_CC3, self.DLPNO_CCSD_T
        }
        return self in triples_methods


class CIMethod(str, Enum):
    """
    Configuration Interaction methods.
    
    Attributes:
        CIS: CI Singles (excited states only)
        CID: CI Doubles
        CISD: CI Singles and Doubles
        CISDT: CI Singles, Doubles, and Triples
        CISDTQ: CI with up to quadruple excitations
        FCI: Full Configuration Interaction
        DETCI: Determinant-based CI
        QCISD: Quadratic CISD
        QCISD_T: QCISD with perturbative triples
    """
    CIS = "cis"
    CID = "cid"
    CISD = "cisd"
    CISDT = "cisdt"
    CISDTQ = "cisdtq"
    FCI = "fci"
    DETCI = "detci"
    QCISD = "qcisd"
    QCISD_T = "qcisd(t)"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


class MCSCFMethod(str, Enum):
    """
    Multi-configurational SCF methods.
    
    Attributes:
        CASSCF: Complete Active Space SCF
        RASSCF: Restricted Active Space SCF
        DMRG_SCF: Density Matrix Renormalization Group SCF
        CASPT2: CASSCF + second-order perturbation
        NEVPT2: N-electron Valence PT2
        MRCI: Multi-reference CI
    """
    CASSCF = "casscf"
    RASSCF = "rasscf"
    DMRG_SCF = "dmrg-scf"
    CASPT2 = "caspt2"
    NEVPT2 = "nevpt2"
    MRCI = "mrci"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


class SAPTMethod(str, Enum):
    """
    Symmetry-Adapted Perturbation Theory methods.
    
    SAPT decomposes interaction energies into physically meaningful
    components: electrostatics, exchange, induction, and dispersion.
    
    Attributes:
        SAPT0: Zeroth-order SAPT (fast, moderate accuracy)
        SSAPT0: Scaled SAPT0
        SAPT2: Second-order SAPT
        SAPT2_PLUS: SAPT2+
        SAPT2_PLUS_3: SAPT2+(3)
        SAPT2_PLUS_DMP2: SAPT2+dMP2
        SAPT2_PLUS_3_DMP2: SAPT2+(3)dMP2
        SAPT_DFT: DFT-based SAPT
        F_SAPT: Functional group SAPT
        I_SAPT: Intramolecular SAPT
    """
    SAPT0 = "sapt0"
    SSAPT0 = "ssapt0"
    SAPT2 = "sapt2"
    SAPT2_PLUS = "sapt2+"
    SAPT2_PLUS_3 = "sapt2+(3)"
    SAPT2_PLUS_DMP2 = "sapt2+dmp2"
    SAPT2_PLUS_3_DMP2 = "sapt2+(3)dmp2"
    SAPT_DFT = "sapt(dft)"
    F_SAPT = "fisapt0"
    I_SAPT = "isapt"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


class TDDFTMethod(str, Enum):
    """
    Time-dependent and response theory methods.
    
    Attributes:
        TDDFT: Time-dependent DFT
        TDA: Tamm-Dancoff Approximation
        RPA: Random Phase Approximation
        TDHF: Time-dependent Hartree-Fock
        ADC1: Algebraic Diagrammatic Construction (1)
        ADC2: Algebraic Diagrammatic Construction (2)
        ADC2_X: Extended ADC(2)
        ADC3: Algebraic Diagrammatic Construction (3)
    """
    TDDFT = "tddft"
    TDA = "tda"
    RPA = "rpa"
    TDHF = "tdhf"
    ADC1 = "adc(1)"
    ADC2 = "adc(2)"
    ADC2_X = "adc(2)-x"
    ADC3 = "adc(3)"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


class CompositeMethod(str, Enum):
    """
    Composite thermochemistry methods.
    
    These methods combine multiple calculations with empirical corrections
    to achieve high accuracy for thermochemistry.
    
    Attributes:
        G1: Gaussian-1 theory
        G2: Gaussian-2 theory
        G2MP2: G2 with MP2 approximation
        G3: Gaussian-3 theory
        G3MP2: G3 with MP2 approximation
        G3MP2B3: G3(MP2)//B3LYP
        G4: Gaussian-4 theory
        G4MP2: G4 with MP2 approximation
        CBS_4: CBS-4 complete basis set
        CBS_Q: CBS-Q complete basis set
        CBS_QB3: CBS-QB3 complete basis set
        CBS_APNO: CBS-APNO complete basis set
        W1: Weizmann-1 theory
        W1BD: W1 with BDTQ
        W2: Weizmann-2 theory
    """
    G1 = "g1"
    G2 = "g2"
    G2MP2 = "g2mp2"
    G3 = "g3"
    G3MP2 = "g3mp2"
    G3MP2B3 = "g3mp2b3"
    G4 = "g4"
    G4MP2 = "g4mp2"
    CBS_4 = "cbs-4"
    CBS_Q = "cbs-q"
    CBS_QB3 = "cbs-qb3"
    CBS_APNO = "cbs-apno"
    W1 = "w1"
    W1BD = "w1bd"
    W2 = "w2"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value


# =============================================================================
# UNIFIED METHOD TYPE
# =============================================================================

class Method(str, Enum):
    """
    Unified enumeration of all quantum chemistry methods.
    
    This provides a single enumeration for all method types, making it
    easier to work with methods generically.
    """
    # HF
    HF = "hf"
    SCF = "scf"
    
    # Common DFT
    B3LYP = "b3lyp"
    PBE = "pbe"
    PBE0 = "pbe0"
    WB97X_D = "wb97x-d"
    M06_2X = "m06-2x"
    
    # Perturbation
    MP2 = "mp2"
    MP3 = "mp3"
    MP4 = "mp4"
    
    # Coupled Cluster
    CCSD = "ccsd"
    CCSD_T = "ccsd(t)"
    
    # CI
    CISD = "cisd"
    FCI = "fci"
    
    # MCSCF
    CASSCF = "casscf"
    
    # SAPT
    SAPT0 = "sapt0"
    SAPT2_PLUS = "sapt2+"
    
    # TDDFT
    TDDFT = "tddft"
    TDA = "tda"
    ADC2 = "adc(2)"
    
    def to_psi4_method(self) -> str:
        """Convert to Psi4 method string."""
        return self.value
    
    def get_category(self) -> MethodCategory:
        """Get the method category."""
        hf_methods = {self.HF, self.SCF}
        dft_methods = {self.B3LYP, self.PBE, self.PBE0, self.WB97X_D, self.M06_2X}
        pt_methods = {self.MP2, self.MP3, self.MP4}
        cc_methods = {self.CCSD, self.CCSD_T}
        ci_methods = {self.CISD, self.FCI}
        mcscf_methods = {self.CASSCF}
        sapt_methods = {self.SAPT0, self.SAPT2_PLUS}
        tddft_methods = {self.TDDFT, self.TDA, self.ADC2}
        
        if self in hf_methods:
            return MethodCategory.HF
        elif self in dft_methods:
            return MethodCategory.DFT
        elif self in pt_methods:
            return MethodCategory.PERTURBATION
        elif self in cc_methods:
            return MethodCategory.COUPLED_CLUSTER
        elif self in ci_methods:
            return MethodCategory.CI
        elif self in mcscf_methods:
            return MethodCategory.MCSCF
        elif self in sapt_methods:
            return MethodCategory.SAPT
        elif self in tddft_methods:
            return MethodCategory.TDDFT
        else:
            return MethodCategory.HF


# =============================================================================
# METHOD PROPERTIES AND METADATA
# =============================================================================

# Computational scaling (N = number of basis functions)
METHOD_SCALING: Final[dict[str, str]] = {
    "hf": "O(N^4)",
    "dft": "O(N^3-4)",
    "mp2": "O(N^5)",
    "mp3": "O(N^6)",
    "mp4": "O(N^7)",
    "ccsd": "O(N^6)",
    "ccsd(t)": "O(N^7)",
    "ccsdt": "O(N^8)",
    "cisd": "O(N^6)",
    "fci": "O(N!)",
    "casscf": "O(N^6-8)",
    "sapt0": "O(N^5)",
    "sapt2+": "O(N^5)",
    "tddft": "O(N^4)",
    "adc(2)": "O(N^5)",
}

# Typical accuracy (kcal/mol for reaction energies)
METHOD_ACCURACY: Final[dict[str, float]] = {
    "hf": 10.0,
    "b3lyp": 3.0,
    "pbe0": 2.5,
    "wb97x-d": 2.0,
    "mp2": 2.0,
    "ccsd": 1.0,
    "ccsd(t)": 0.5,
    "fci": 0.1,
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_dft_method(method_name: str) -> bool:
    """
    Check if a method name corresponds to a DFT calculation.
    
    Args:
        method_name: Name of the method (case-insensitive).
        
    Returns:
        True if this is a DFT method, False otherwise.
    """
    normalized = method_name.lower().strip()
    
    # Check if it's a known DFT functional
    for func in DFTFunctional:
        if func.value == normalized:
            return True
    
    # Check common DFT keywords
    dft_keywords = {"dft", "ks", "rks", "uks", "gks"}
    return normalized in dft_keywords


def is_post_hf_method(method_name: str) -> bool:
    """
    Check if a method is a post-Hartree-Fock correlation method.
    
    Args:
        method_name: Name of the method (case-insensitive).
        
    Returns:
        True if this is a post-HF method, False otherwise.
    """
    normalized = method_name.lower().strip()
    
    post_hf_prefixes = (
        "mp", "cc", "ci", "sapt", "adc", "fci", "qci", "bccd", "eom"
    )
    
    return any(normalized.startswith(prefix) for prefix in post_hf_prefixes)


def requires_reference(method_name: str) -> bool:
    """
    Check if a method requires a reference calculation first.
    
    Args:
        method_name: Name of the method (case-insensitive).
        
    Returns:
        True if the method requires a reference (SCF) calculation.
    """
    normalized = method_name.lower().strip()
    
    # Methods that don't require a separate reference
    self_consistent = {"hf", "scf", "dft"} | {f.value for f in DFTFunctional}
    
    return normalized not in self_consistent


def get_method_description(method_name: str) -> str:
    """
    Get a human-readable description of a method.
    
    Args:
        method_name: Name of the method.
        
    Returns:
        Description string.
    """
    descriptions: dict[str, str] = {
        "hf": "Hartree-Fock: Mean-field approximation, no electron correlation",
        "mp2": "Second-order Møller-Plesset: Perturbative correlation, O(N^5)",
        "ccsd": "Coupled Cluster Singles and Doubles: High accuracy, O(N^6)",
        "ccsd(t)": "CCSD with perturbative triples: Gold standard for thermochemistry",
        "b3lyp": "B3LYP: Popular hybrid functional, good general accuracy",
        "pbe0": "PBE0: Parameter-free hybrid, excellent for many properties",
        "wb97x-d": "ωB97X-D: Range-separated hybrid with dispersion, very versatile",
        "casscf": "Complete Active Space SCF: Multi-reference method for complex bonding",
        "sapt0": "SAPT0: Fast interaction energy decomposition",
        "tddft": "Time-Dependent DFT: Excited states within DFT framework",
    }
    
    normalized = method_name.lower().strip()
    return descriptions.get(normalized, f"Quantum chemistry method: {method_name}")
