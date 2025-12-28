"""Basis Set Resource - Comprehensive basis set information."""

from typing import Optional, Dict, Any, List
from psi4_mcp.resources.base_resource import BaseResource, register_resource

# Complete basis set database
BASIS_SETS: Dict[str, Dict[str, Any]] = {
    # Minimal basis
    "sto-3g": {
        "name": "STO-3G",
        "type": "minimal",
        "zeta": 1,
        "polarization": False,
        "diffuse": False,
        "elements": "H-Kr",
        "description": "Minimal basis for testing only",
        "accuracy": "very low",
        "cost": "very low",
        "recommended_for": ["testing", "initial guess"],
        "citation": "Hehre, Stewart, Pople, JCP 1969"
    },
    
    # Pople basis sets
    "3-21g": {
        "name": "3-21G",
        "type": "split-valence",
        "zeta": 2,
        "polarization": False,
        "diffuse": False,
        "elements": "H-Cs",
        "description": "Split-valence double-zeta",
        "accuracy": "low",
        "cost": "low",
        "recommended_for": ["quick estimates", "large systems"],
        "citation": "Binkley, Pople, Hehre, JACS 1980"
    },
    "6-31g": {
        "name": "6-31G",
        "type": "split-valence",
        "zeta": 2,
        "polarization": False,
        "diffuse": False,
        "elements": "H-Zn",
        "description": "Split-valence double-zeta",
        "accuracy": "low-medium",
        "cost": "low",
        "recommended_for": ["geometry optimization", "DFT"],
        "citation": "Ditchfield, Hehre, Pople, JCP 1971"
    },
    "6-31g*": {
        "name": "6-31G(d)",
        "type": "split-valence+polarization",
        "zeta": 2,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Zn",
        "description": "6-31G with d polarization on heavy atoms",
        "accuracy": "medium",
        "cost": "low-medium",
        "recommended_for": ["geometry", "frequencies", "DFT"],
        "citation": "Hariharan, Pople, TCA 1973"
    },
    "6-31+g*": {
        "name": "6-31+G(d)",
        "type": "split-valence+polarization+diffuse",
        "zeta": 2,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Zn",
        "description": "6-31G(d) with diffuse functions on heavy atoms",
        "accuracy": "medium",
        "cost": "medium",
        "recommended_for": ["anions", "excited states", "polarizability"],
        "citation": "Clark et al., JCC 1983"
    },
    "6-311g**": {
        "name": "6-311G(d,p)",
        "type": "triple-zeta+polarization",
        "zeta": 3,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Br",
        "description": "Triple-zeta with polarization",
        "accuracy": "medium-high",
        "cost": "medium",
        "recommended_for": ["accurate geometry", "energetics"],
        "citation": "Krishnan et al., JCP 1980"
    },
    "6-311++g**": {
        "name": "6-311++G(d,p)",
        "type": "triple-zeta+polarization+diffuse",
        "zeta": 3,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Br",
        "description": "Triple-zeta with polarization and diffuse",
        "accuracy": "high",
        "cost": "medium-high",
        "recommended_for": ["anions", "H-bonding", "excited states"],
        "citation": "Krishnan et al., JCP 1980"
    },
    
    # Dunning correlation-consistent
    "cc-pvdz": {
        "name": "cc-pVDZ",
        "type": "correlation-consistent",
        "zeta": 2,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Ar, Ca-Kr",
        "description": "Correlation-consistent polarized valence double-zeta",
        "accuracy": "medium",
        "cost": "medium",
        "recommended_for": ["correlated methods", "MP2", "CCSD"],
        "citation": "Dunning, JCP 1989"
    },
    "cc-pvtz": {
        "name": "cc-pVTZ",
        "type": "correlation-consistent",
        "zeta": 3,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Ar, Ca-Kr",
        "description": "Correlation-consistent polarized valence triple-zeta",
        "accuracy": "high",
        "cost": "high",
        "recommended_for": ["accurate energies", "CCSD(T)"],
        "citation": "Dunning, JCP 1989"
    },
    "cc-pvqz": {
        "name": "cc-pVQZ",
        "type": "correlation-consistent",
        "zeta": 4,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Ar, Ca-Kr",
        "description": "Correlation-consistent polarized valence quadruple-zeta",
        "accuracy": "very high",
        "cost": "very high",
        "recommended_for": ["benchmark", "CBS extrapolation"],
        "citation": "Dunning, JCP 1989"
    },
    "aug-cc-pvdz": {
        "name": "aug-cc-pVDZ",
        "type": "augmented correlation-consistent",
        "zeta": 2,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Ar, Ca-Kr",
        "description": "Augmented cc-pVDZ with diffuse functions",
        "accuracy": "medium-high",
        "cost": "medium-high",
        "recommended_for": ["anions", "SAPT", "excited states", "polarizability"],
        "citation": "Kendall, Dunning, Harrison, JCP 1992"
    },
    "aug-cc-pvtz": {
        "name": "aug-cc-pVTZ",
        "type": "augmented correlation-consistent",
        "zeta": 3,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Ar, Ca-Kr",
        "description": "Augmented cc-pVTZ with diffuse functions",
        "accuracy": "high",
        "cost": "high",
        "recommended_for": ["accurate anions", "properties", "SAPT"],
        "citation": "Kendall, Dunning, Harrison, JCP 1992"
    },
    "aug-cc-pvqz": {
        "name": "aug-cc-pVQZ",
        "type": "augmented correlation-consistent",
        "zeta": 4,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Ar, Ca-Kr",
        "description": "Augmented cc-pVQZ with diffuse functions",
        "accuracy": "very high",
        "cost": "very high",
        "recommended_for": ["benchmark anions", "CBS extrapolation"],
        "citation": "Kendall, Dunning, Harrison, JCP 1992"
    },
    
    # Core-valence
    "cc-pcvdz": {
        "name": "cc-pCVDZ",
        "type": "core-valence",
        "zeta": 2,
        "polarization": True,
        "diffuse": False,
        "elements": "Li-Ar",
        "description": "Core-valence cc-pVDZ for core correlation",
        "accuracy": "medium",
        "cost": "high",
        "recommended_for": ["core correlation", "NMR"],
        "citation": "Woon, Dunning, JCP 1995"
    },
    "cc-pcvtz": {
        "name": "cc-pCVTZ",
        "type": "core-valence",
        "zeta": 3,
        "polarization": True,
        "diffuse": False,
        "elements": "Li-Ar",
        "description": "Core-valence cc-pVTZ for core correlation",
        "accuracy": "high",
        "cost": "very high",
        "recommended_for": ["accurate core correlation", "NMR shielding"],
        "citation": "Woon, Dunning, JCP 1995"
    },
    
    # Karlsruhe def2 family
    "def2-svp": {
        "name": "def2-SVP",
        "type": "split-valence+polarization",
        "zeta": 2,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Rn",
        "description": "Karlsruhe split-valence polarization",
        "accuracy": "medium",
        "cost": "low-medium",
        "recommended_for": ["DFT geometry", "large molecules"],
        "citation": "Weigend, Ahlrichs, PCCP 2005"
    },
    "def2-svpd": {
        "name": "def2-SVPD",
        "type": "split-valence+polarization+diffuse",
        "zeta": 2,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Rn",
        "description": "def2-SVP with diffuse functions",
        "accuracy": "medium",
        "cost": "medium",
        "recommended_for": ["anions with DFT", "response properties"],
        "citation": "Rappoport, Furche, JCP 2010"
    },
    "def2-tzvp": {
        "name": "def2-TZVP",
        "type": "triple-zeta+polarization",
        "zeta": 3,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Rn",
        "description": "Karlsruhe triple-zeta polarization",
        "accuracy": "high",
        "cost": "medium-high",
        "recommended_for": ["DFT production", "accurate geometry"],
        "citation": "Weigend, Ahlrichs, PCCP 2005"
    },
    "def2-tzvpd": {
        "name": "def2-TZVPD",
        "type": "triple-zeta+polarization+diffuse",
        "zeta": 3,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Rn",
        "description": "def2-TZVP with diffuse functions",
        "accuracy": "high",
        "cost": "high",
        "recommended_for": ["response properties", "excited states"],
        "citation": "Rappoport, Furche, JCP 2010"
    },
    "def2-tzvpp": {
        "name": "def2-TZVPP",
        "type": "triple-zeta+2polarization",
        "zeta": 3,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Rn",
        "description": "def2-TZVP with extra polarization",
        "accuracy": "high",
        "cost": "high",
        "recommended_for": ["correlated calculations"],
        "citation": "Weigend, Ahlrichs, PCCP 2005"
    },
    "def2-qzvp": {
        "name": "def2-QZVP",
        "type": "quadruple-zeta+polarization",
        "zeta": 4,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Rn",
        "description": "Karlsruhe quadruple-zeta polarization",
        "accuracy": "very high",
        "cost": "very high",
        "recommended_for": ["benchmark", "CBS limit"],
        "citation": "Weigend, Ahlrichs, PCCP 2005"
    },
    
    # SAPT-specific
    "jun-cc-pvdz": {
        "name": "jun-cc-pVDZ",
        "type": "calendar basis",
        "zeta": 2,
        "polarization": True,
        "diffuse": "partial",
        "elements": "H-Ar",
        "description": "Truncated aug-cc-pVDZ for SAPT",
        "accuracy": "medium",
        "cost": "medium",
        "recommended_for": ["SAPT0", "large dimers"],
        "citation": "Papajak et al., JCTC 2011"
    },
    "aug-cc-pvdz-jkfit": {
        "name": "aug-cc-pVDZ-JKFIT",
        "type": "auxiliary",
        "zeta": 2,
        "polarization": True,
        "diffuse": True,
        "elements": "H-Ar",
        "description": "JK fitting basis for aug-cc-pVDZ",
        "accuracy": "N/A (auxiliary)",
        "cost": "N/A",
        "recommended_for": ["density fitting SCF"],
        "citation": "Weigend, PCCP 2002"
    },
    "cc-pvdz-ri": {
        "name": "cc-pVDZ-RI",
        "type": "auxiliary",
        "zeta": 2,
        "polarization": True,
        "diffuse": False,
        "elements": "H-Ar",
        "description": "RI fitting basis for cc-pVDZ",
        "accuracy": "N/A (auxiliary)",
        "cost": "N/A",
        "recommended_for": ["DF-MP2", "RI methods"],
        "citation": "Weigend, Köhn, Hättig, JCP 2002"
    },
}


@register_resource
class BasisSetResource(BaseResource):
    """Resource providing basis set information."""
    
    name = "basis_sets"
    description = "Comprehensive basis set information including recommendations"
    
    def get(self, subpath: Optional[str] = None) -> str:
        if subpath is None:
            # Return summary of all basis sets
            summary = {
                "total": len(BASIS_SETS),
                "categories": {
                    "minimal": [k for k, v in BASIS_SETS.items() if v["type"] == "minimal"],
                    "split-valence": [k for k, v in BASIS_SETS.items() if "split-valence" in v["type"]],
                    "correlation-consistent": [k for k, v in BASIS_SETS.items() if "correlation-consistent" in v["type"]],
                    "karlsruhe": [k for k, v in BASIS_SETS.items() if k.startswith("def2")],
                    "augmented": [k for k, v in BASIS_SETS.items() if k.startswith("aug-")],
                    "auxiliary": [k for k, v in BASIS_SETS.items() if v["type"] == "auxiliary"],
                },
                "basis_sets": list(BASIS_SETS.keys())
            }
            return self.to_json(summary)
        
        # Return specific basis set info
        basis = subpath.lower().replace("(", "").replace(")", "").replace(",", "")
        if basis in BASIS_SETS:
            return self.to_json(BASIS_SETS[basis])
        
        # Try to find similar
        similar = [k for k in BASIS_SETS.keys() if basis in k or k in basis]
        return self.to_json({
            "error": f"Basis set '{subpath}' not found",
            "similar": similar,
            "available": list(BASIS_SETS.keys())
        })
    
    def recommend(self, calculation_type: str, accuracy: str = "medium", 
                  has_anions: bool = False) -> List[str]:
        """Recommend basis sets for a calculation type."""
        recommendations = []
        
        for name, info in BASIS_SETS.items():
            if info.get("type") == "auxiliary":
                continue
            if has_anions and not info.get("diffuse"):
                continue
            if accuracy == "low" and info.get("zeta", 0) > 2:
                continue
            if accuracy == "high" and info.get("zeta", 0) < 3:
                continue
            if calculation_type in info.get("recommended_for", []):
                recommendations.append(name)
        
        return recommendations[:5]
