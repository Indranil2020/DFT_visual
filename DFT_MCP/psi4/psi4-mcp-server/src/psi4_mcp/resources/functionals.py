"""DFT Functionals Resource."""

from typing import Optional, Dict, Any
from psi4_mcp.resources.base_resource import BaseResource, register_resource

FUNCTIONALS: Dict[str, Dict[str, Any]] = {
    # LDA
    "svwn": {"name": "SVWN", "type": "LDA", "hf_exchange": 0, "dispersion": None},
    "svwn5": {"name": "SVWN5", "type": "LDA", "hf_exchange": 0, "dispersion": None},
    
    # GGA
    "blyp": {"name": "BLYP", "type": "GGA", "hf_exchange": 0, "dispersion": None},
    "bp86": {"name": "BP86", "type": "GGA", "hf_exchange": 0, "dispersion": None},
    "pbe": {"name": "PBE", "type": "GGA", "hf_exchange": 0, "dispersion": None},
    "pw91": {"name": "PW91", "type": "GGA", "hf_exchange": 0, "dispersion": None},
    
    # Meta-GGA
    "tpss": {"name": "TPSS", "type": "meta-GGA", "hf_exchange": 0, "dispersion": None},
    "m06-l": {"name": "M06-L", "type": "meta-GGA", "hf_exchange": 0, "dispersion": None},
    "scan": {"name": "SCAN", "type": "meta-GGA", "hf_exchange": 0, "dispersion": None},
    
    # Hybrid GGA
    "b3lyp": {"name": "B3LYP", "type": "hybrid-GGA", "hf_exchange": 20, "dispersion": None},
    "b3lyp5": {"name": "B3LYP5", "type": "hybrid-GGA", "hf_exchange": 20, "dispersion": None},
    "pbe0": {"name": "PBE0", "type": "hybrid-GGA", "hf_exchange": 25, "dispersion": None},
    "b97": {"name": "B97", "type": "hybrid-GGA", "hf_exchange": 21, "dispersion": None},
    
    # Hybrid meta-GGA
    "m06": {"name": "M06", "type": "hybrid-meta-GGA", "hf_exchange": 27, "dispersion": None},
    "m06-2x": {"name": "M06-2X", "type": "hybrid-meta-GGA", "hf_exchange": 54, "dispersion": None},
    "m06-hf": {"name": "M06-HF", "type": "hybrid-meta-GGA", "hf_exchange": 100, "dispersion": None},
    "tpssh": {"name": "TPSSh", "type": "hybrid-meta-GGA", "hf_exchange": 10, "dispersion": None},
    
    # Range-separated
    "cam-b3lyp": {"name": "CAM-B3LYP", "type": "RSH", "hf_exchange": "19-65%", "omega": 0.33},
    "lc-wpbe": {"name": "LC-ωPBE", "type": "RSH", "hf_exchange": "0-100%", "omega": 0.40},
    "wb97": {"name": "ωB97", "type": "RSH", "hf_exchange": "0-100%", "omega": 0.40},
    "wb97x": {"name": "ωB97X", "type": "RSH", "hf_exchange": "16-100%", "omega": 0.30},
    "wb97x-d": {"name": "ωB97X-D", "type": "RSH+D", "hf_exchange": "22-100%", "omega": 0.20, "dispersion": "D2"},
    "wb97x-d3": {"name": "ωB97X-D3", "type": "RSH+D", "hf_exchange": "var", "dispersion": "D3"},
    
    # Double-hybrid
    "b2plyp": {"name": "B2PLYP", "type": "double-hybrid", "hf_exchange": 53, "mp2_correlation": 27},
    "b2gpplyp": {"name": "B2GP-PLYP", "type": "double-hybrid", "hf_exchange": 65, "mp2_correlation": 36},
    "dsd-pbep86": {"name": "DSD-PBEP86", "type": "double-hybrid", "hf_exchange": 68, "mp2_correlation": "spin-scaled"},
    
    # With dispersion
    "b3lyp-d3": {"name": "B3LYP-D3", "type": "hybrid-GGA+D", "hf_exchange": 20, "dispersion": "D3"},
    "b3lyp-d3bj": {"name": "B3LYP-D3(BJ)", "type": "hybrid-GGA+D", "hf_exchange": 20, "dispersion": "D3BJ"},
    "pbe-d3": {"name": "PBE-D3", "type": "GGA+D", "hf_exchange": 0, "dispersion": "D3"},
    "pbe0-d3": {"name": "PBE0-D3", "type": "hybrid-GGA+D", "hf_exchange": 25, "dispersion": "D3"},
}


@register_resource
class FunctionalResource(BaseResource):
    """Resource providing DFT functional information."""
    
    name = "functionals"
    description = "DFT functional catalog with properties"
    
    def get(self, subpath: Optional[str] = None) -> str:
        if subpath is None:
            by_type = {}
            for name, info in FUNCTIONALS.items():
                ftype = info.get("type", "other")
                if ftype not in by_type:
                    by_type[ftype] = []
                by_type[ftype].append(name)
            return self.to_json({
                "total": len(FUNCTIONALS),
                "by_type": by_type,
                "all": list(FUNCTIONALS.keys())
            })
        
        key = subpath.lower().replace("-", "").replace("(", "").replace(")", "")
        for fname, info in FUNCTIONALS.items():
            if fname.replace("-", "").replace("(", "").replace(")", "") == key:
                return self.to_json(info)
        
        return self.to_json({"error": f"Functional '{subpath}' not found"})
