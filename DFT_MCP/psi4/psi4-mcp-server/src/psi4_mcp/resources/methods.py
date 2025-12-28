"""Methods Resource - Comprehensive quantum chemistry method information."""

from typing import Optional, Dict, Any, List
from psi4_mcp.resources.base_resource import BaseResource, register_resource

METHODS: Dict[str, Dict[str, Any]] = {
    # Hartree-Fock
    "hf": {
        "name": "Hartree-Fock",
        "type": "wavefunction",
        "category": "scf",
        "scaling": "O(N^4)",
        "accuracy": "baseline",
        "correlation": False,
        "multireference": False,
        "description": "Self-consistent field, mean-field approximation",
        "variants": ["rhf", "uhf", "rohf"],
        "strengths": ["fast", "variational", "size-consistent"],
        "weaknesses": ["no correlation", "poor for open-shell"],
        "recommended_for": ["initial geometry", "large systems", "baseline"],
        "basis_recommendation": "cc-pvdz or larger"
    },
    
    # DFT
    "b3lyp": {
        "name": "B3LYP",
        "type": "dft",
        "category": "hybrid-gga",
        "scaling": "O(N^3-N^4)",
        "accuracy": "good",
        "correlation": True,
        "multireference": False,
        "hf_exchange": 20,
        "description": "Becke 3-parameter Lee-Yang-Parr hybrid functional",
        "strengths": ["good geometry", "well-tested", "fast"],
        "weaknesses": ["poor for dispersion", "CT states"],
        "recommended_for": ["geometry", "frequencies", "general DFT"],
        "basis_recommendation": "def2-TZVP or 6-31G*"
    },
    "pbe": {
        "name": "PBE",
        "type": "dft",
        "category": "gga",
        "scaling": "O(N^3)",
        "accuracy": "good",
        "correlation": True,
        "hf_exchange": 0,
        "description": "Perdew-Burke-Ernzerhof GGA functional",
        "strengths": ["no empirical parameters", "good for solids"],
        "weaknesses": ["no HF exchange", "underestimates gaps"],
        "recommended_for": ["solids", "metals", "general DFT"],
        "basis_recommendation": "def2-TZVP"
    },
    "pbe0": {
        "name": "PBE0",
        "type": "dft",
        "category": "hybrid-gga",
        "scaling": "O(N^4)",
        "accuracy": "good",
        "correlation": True,
        "hf_exchange": 25,
        "description": "PBE with 25% HF exchange",
        "strengths": ["good thermochemistry", "balanced"],
        "weaknesses": ["slightly more expensive than PBE"],
        "recommended_for": ["thermochemistry", "barriers"],
        "basis_recommendation": "def2-TZVP"
    },
    "m06-2x": {
        "name": "M06-2X",
        "type": "dft",
        "category": "meta-hybrid-gga",
        "scaling": "O(N^4)",
        "accuracy": "good",
        "correlation": True,
        "hf_exchange": 54,
        "description": "Minnesota functional with 54% HF exchange",
        "strengths": ["good for main-group", "noncovalent"],
        "weaknesses": ["many parameters", "grid-sensitive"],
        "recommended_for": ["thermochemistry", "kinetics", "noncovalent"],
        "basis_recommendation": "def2-TZVP"
    },
    "wb97x-d": {
        "name": "ωB97X-D",
        "type": "dft",
        "category": "range-separated-hybrid",
        "scaling": "O(N^4)",
        "accuracy": "very good",
        "correlation": True,
        "hf_exchange": "range-separated",
        "dispersion": "D2",
        "description": "Range-separated hybrid with dispersion",
        "strengths": ["good for CT states", "dispersion included"],
        "weaknesses": ["more expensive"],
        "recommended_for": ["excited states", "noncovalent", "CT"],
        "basis_recommendation": "def2-TZVP or aug-cc-pVDZ"
    },
    "cam-b3lyp": {
        "name": "CAM-B3LYP",
        "type": "dft",
        "category": "range-separated-hybrid",
        "scaling": "O(N^4)",
        "accuracy": "good",
        "correlation": True,
        "hf_exchange": "range-separated (19-65%)",
        "description": "Coulomb-attenuated B3LYP",
        "strengths": ["good for CT states", "Rydberg states"],
        "weaknesses": ["more expensive than B3LYP"],
        "recommended_for": ["excited states", "charge transfer"],
        "basis_recommendation": "aug-cc-pVTZ"
    },
    
    # MP2
    "mp2": {
        "name": "MP2",
        "type": "wavefunction",
        "category": "perturbation",
        "scaling": "O(N^5)",
        "accuracy": "good",
        "correlation": True,
        "multireference": False,
        "description": "Second-order Møller-Plesset perturbation theory",
        "strengths": ["captures ~80-90% correlation", "size-consistent"],
        "weaknesses": ["overestimates dispersion", "fails for metals"],
        "recommended_for": ["correlation energy", "noncovalent", "geometry"],
        "basis_recommendation": "cc-pVTZ"
    },
    "df-mp2": {
        "name": "DF-MP2",
        "type": "wavefunction",
        "category": "perturbation",
        "scaling": "O(N^4-N^5)",
        "accuracy": "good",
        "correlation": True,
        "description": "Density-fitted MP2 (much faster)",
        "strengths": ["fast", "nearly identical to MP2"],
        "weaknesses": ["requires auxiliary basis"],
        "recommended_for": ["large molecules", "quick MP2"],
        "basis_recommendation": "cc-pVTZ with cc-pVTZ-RI"
    },
    "scs-mp2": {
        "name": "SCS-MP2",
        "type": "wavefunction",
        "category": "perturbation",
        "scaling": "O(N^5)",
        "accuracy": "very good",
        "correlation": True,
        "description": "Spin-component scaled MP2",
        "strengths": ["improved accuracy over MP2"],
        "weaknesses": ["empirical scaling"],
        "recommended_for": ["noncovalent", "reaction energies"],
        "basis_recommendation": "cc-pVTZ"
    },
    
    # Coupled Cluster
    "ccsd": {
        "name": "CCSD",
        "type": "wavefunction",
        "category": "coupled-cluster",
        "scaling": "O(N^6)",
        "accuracy": "high",
        "correlation": True,
        "multireference": False,
        "description": "Coupled cluster with singles and doubles",
        "strengths": ["high accuracy", "size-extensive"],
        "weaknesses": ["expensive", "poor for multireference"],
        "recommended_for": ["accurate energies", "small molecules"],
        "basis_recommendation": "cc-pVTZ or larger"
    },
    "ccsd(t)": {
        "name": "CCSD(T)",
        "type": "wavefunction",
        "category": "coupled-cluster",
        "scaling": "O(N^7)",
        "accuracy": "very high (gold standard)",
        "correlation": True,
        "multireference": False,
        "description": "CCSD with perturbative triples",
        "strengths": ["gold standard accuracy (~1 kJ/mol)", "benchmark quality"],
        "weaknesses": ["very expensive", "needs large basis"],
        "recommended_for": ["benchmark", "thermochemistry", "barrier heights"],
        "basis_recommendation": "cc-pVTZ or CBS extrapolation"
    },
    "eom-ccsd": {
        "name": "EOM-CCSD",
        "type": "wavefunction",
        "category": "coupled-cluster",
        "scaling": "O(N^6)",
        "accuracy": "high",
        "correlation": True,
        "description": "Equation-of-motion CCSD for excited states",
        "variants": ["eom-ccsd-ee", "eom-ccsd-ip", "eom-ccsd-ea"],
        "strengths": ["accurate excited states", "size-intensive"],
        "weaknesses": ["expensive", "requires good reference"],
        "recommended_for": ["excited states", "ionization", "electron affinity"],
        "basis_recommendation": "aug-cc-pVTZ"
    },
    
    # CI
    "cisd": {
        "name": "CISD",
        "type": "wavefunction",
        "category": "ci",
        "scaling": "O(N^6)",
        "accuracy": "medium",
        "correlation": True,
        "multireference": False,
        "description": "Configuration interaction singles and doubles",
        "strengths": ["variational", "simple"],
        "weaknesses": ["not size-extensive", "less accurate than CC"],
        "recommended_for": ["comparison", "small systems"],
        "basis_recommendation": "cc-pVDZ"
    },
    "fci": {
        "name": "FCI",
        "type": "wavefunction",
        "category": "ci",
        "scaling": "exponential",
        "accuracy": "exact (within basis)",
        "correlation": True,
        "multireference": True,
        "description": "Full configuration interaction - exact solution",
        "strengths": ["exact within basis set", "handles all correlation"],
        "weaknesses": ["exponential scaling", "only tiny systems"],
        "recommended_for": ["benchmark", "validation", "small systems"],
        "basis_recommendation": "small basis only"
    },
    
    # Multireference
    "casscf": {
        "name": "CASSCF",
        "type": "wavefunction",
        "category": "mcscf",
        "scaling": "exponential in active space",
        "accuracy": "good for static correlation",
        "correlation": "static only",
        "multireference": True,
        "description": "Complete active space SCF",
        "strengths": ["handles multireference", "bond breaking"],
        "weaknesses": ["no dynamic correlation", "active space choice"],
        "recommended_for": ["bond breaking", "transition metals", "excited states"],
        "basis_recommendation": "cc-pVDZ for geometry, cc-pVTZ for energy"
    },
    "caspt2": {
        "name": "CASPT2",
        "type": "wavefunction",
        "category": "mcscf+pt",
        "scaling": "O(N^5) + CAS",
        "accuracy": "high",
        "correlation": True,
        "multireference": True,
        "description": "CASSCF with PT2 dynamic correlation",
        "strengths": ["good for excited states", "handles MR"],
        "weaknesses": ["intruder states", "active space"],
        "recommended_for": ["excited states", "transition metals"],
        "basis_recommendation": "ANO or cc-pVTZ"
    },
    
    # SAPT
    "sapt0": {
        "name": "SAPT0",
        "type": "sapt",
        "category": "intermolecular",
        "scaling": "O(N^5)",
        "accuracy": "good",
        "description": "Zeroth-order SAPT with HF monomers",
        "strengths": ["physical decomposition", "fast"],
        "weaknesses": ["limited accuracy"],
        "recommended_for": ["noncovalent analysis", "large dimers"],
        "basis_recommendation": "jun-cc-pVDZ"
    },
    "sapt2+": {
        "name": "SAPT2+",
        "type": "sapt",
        "category": "intermolecular",
        "scaling": "O(N^5)",
        "accuracy": "high",
        "description": "Second-order SAPT with improved dispersion",
        "strengths": ["accurate", "physical insight"],
        "weaknesses": ["more expensive"],
        "recommended_for": ["accurate noncovalent", "interaction analysis"],
        "basis_recommendation": "aug-cc-pVDZ"
    },
    
    # TD-DFT
    "tddft": {
        "name": "TD-DFT",
        "type": "response",
        "category": "excited-states",
        "scaling": "O(N^4)",
        "accuracy": "good for valence",
        "description": "Time-dependent DFT for excited states",
        "strengths": ["fast", "good for valence states"],
        "weaknesses": ["poor for CT/Rydberg with pure functionals"],
        "recommended_for": ["absorption spectra", "excited states"],
        "basis_recommendation": "def2-TZVP or aug-cc-pVDZ"
    },
    "adc2": {
        "name": "ADC(2)",
        "type": "response",
        "category": "excited-states",
        "scaling": "O(N^5)",
        "accuracy": "good",
        "description": "Algebraic diagrammatic construction",
        "strengths": ["size-consistent", "balanced accuracy"],
        "weaknesses": ["more expensive than TD-DFT"],
        "recommended_for": ["excited states", "UV-Vis"],
        "basis_recommendation": "cc-pVTZ"
    },
}


@register_resource
class MethodResource(BaseResource):
    """Resource providing method information."""
    
    name = "methods"
    description = "Comprehensive quantum chemistry method information"
    
    def get(self, subpath: Optional[str] = None) -> str:
        if subpath is None:
            summary = {
                "total": len(METHODS),
                "categories": {},
                "methods": list(METHODS.keys())
            }
            for method, info in METHODS.items():
                cat = info.get("category", "other")
                if cat not in summary["categories"]:
                    summary["categories"][cat] = []
                summary["categories"][cat].append(method)
            return self.to_json(summary)
        
        method = subpath.lower().replace("-", "").replace("(", "").replace(")", "")
        # Try exact match first
        if method in METHODS:
            return self.to_json(METHODS[method])
        
        # Try normalized versions
        for key, info in METHODS.items():
            if key.replace("-", "").replace("(", "").replace(")", "") == method:
                return self.to_json(info)
        
        return self.to_json({
            "error": f"Method '{subpath}' not found",
            "available": list(METHODS.keys())
        })
    
    def recommend(self, task: str, system_size: str = "medium", 
                  accuracy: str = "medium") -> List[str]:
        """Recommend methods for a task."""
        recommendations = []
        
        scaling_limit = {
            "small": "O(N^7)",
            "medium": "O(N^5)",
            "large": "O(N^4)"
        }.get(system_size, "O(N^5)")
        
        for name, info in METHODS.items():
            if task in info.get("recommended_for", []):
                recommendations.append(name)
        
        return recommendations[:5]
