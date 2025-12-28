"""Common Molecules Resource."""

from typing import Optional, Dict, Any
from psi4_mcp.resources.base_resource import BaseResource, register_resource

MOLECULES: Dict[str, Dict[str, Any]] = {
    "water": {
        "formula": "H2O",
        "name": "Water",
        "atoms": 3,
        "electrons": 10,
        "geometry": """O  0.000000  0.000000  0.117369
H  0.000000  0.757463 -0.469476
H  0.000000 -0.757463 -0.469476""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "C2v",
        "notes": "Standard test molecule"
    },
    "methane": {
        "formula": "CH4",
        "name": "Methane",
        "atoms": 5,
        "electrons": 10,
        "geometry": """C  0.000000  0.000000  0.000000
H  0.629118  0.629118  0.629118
H -0.629118 -0.629118  0.629118
H -0.629118  0.629118 -0.629118
H  0.629118 -0.629118 -0.629118""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "Td"
    },
    "ammonia": {
        "formula": "NH3",
        "name": "Ammonia",
        "atoms": 4,
        "electrons": 10,
        "geometry": """N  0.000000  0.000000  0.116489
H  0.000000  0.939731 -0.271807
H  0.813797 -0.469865 -0.271807
H -0.813797 -0.469865 -0.271807""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "C3v"
    },
    "ethane": {
        "formula": "C2H6",
        "name": "Ethane",
        "atoms": 8,
        "electrons": 18,
        "geometry": """C  0.000000  0.000000  0.762935
C  0.000000  0.000000 -0.762935
H  1.018818  0.000000  1.157534
H -0.509409  0.882283  1.157534
H -0.509409 -0.882283  1.157534
H -1.018818  0.000000 -1.157534
H  0.509409 -0.882283 -1.157534
H  0.509409  0.882283 -1.157534""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "D3d"
    },
    "ethylene": {
        "formula": "C2H4",
        "name": "Ethylene",
        "atoms": 6,
        "electrons": 16,
        "geometry": """C  0.000000  0.000000  0.666805
C  0.000000  0.000000 -0.666805
H  0.000000  0.922683  1.237657
H  0.000000 -0.922683  1.237657
H  0.000000 -0.922683 -1.237657
H  0.000000  0.922683 -1.237657""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "D2h"
    },
    "benzene": {
        "formula": "C6H6",
        "name": "Benzene",
        "atoms": 12,
        "electrons": 42,
        "geometry": """C  1.391500  0.000000  0.000000
C  0.695750  1.204946  0.000000
C -0.695750  1.204946  0.000000
C -1.391500  0.000000  0.000000
C -0.695750 -1.204946  0.000000
C  0.695750 -1.204946  0.000000
H  2.471500  0.000000  0.000000
H  1.235750  2.140354  0.000000
H -1.235750  2.140354  0.000000
H -2.471500  0.000000  0.000000
H -1.235750 -2.140354  0.000000
H  1.235750 -2.140354  0.000000""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "D6h"
    },
    "formaldehyde": {
        "formula": "CH2O",
        "name": "Formaldehyde",
        "atoms": 4,
        "electrons": 16,
        "geometry": """O  0.000000  0.000000  1.203962
C  0.000000  0.000000  0.000000
H  0.000000  0.943102 -0.584079
H  0.000000 -0.943102 -0.584079""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "C2v",
        "notes": "Good test for excited states (n->pi*)"
    },
    "hydrogen_fluoride": {
        "formula": "HF",
        "name": "Hydrogen Fluoride",
        "atoms": 2,
        "electrons": 10,
        "geometry": """H  0.000000  0.000000  0.000000
F  0.000000  0.000000  0.917085""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "Cv"
    },
    "carbon_monoxide": {
        "formula": "CO",
        "name": "Carbon Monoxide",
        "atoms": 2,
        "electrons": 14,
        "geometry": """C  0.000000  0.000000  0.000000
O  0.000000  0.000000  1.128323""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "Cv"
    },
    "nitrogen": {
        "formula": "N2",
        "name": "Dinitrogen",
        "atoms": 2,
        "electrons": 14,
        "geometry": """N  0.000000  0.000000  0.000000
N  0.000000  0.000000  1.097600""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "Dh",
        "notes": "Triple bond test"
    },
    "hydrogen_peroxide": {
        "formula": "H2O2",
        "name": "Hydrogen Peroxide",
        "atoms": 4,
        "electrons": 18,
        "geometry": """O  0.000000  0.727403 -0.053633
O  0.000000 -0.727403 -0.053633
H  0.797867  0.895669  0.428933
H -0.797867 -0.895669  0.428933""",
        "charge": 0,
        "multiplicity": 1,
        "point_group": "C2"
    },
    "water_dimer": {
        "formula": "(H2O)2",
        "name": "Water Dimer",
        "atoms": 6,
        "electrons": 20,
        "geometry": """O -1.551007 -0.114520  0.000000
H -1.934259  0.762503  0.000000
H -0.599677  0.040712  0.000000
--
O  1.350625  0.111469  0.000000
H  1.680398 -0.373741 -0.758561
H  1.680398 -0.373741  0.758561""",
        "charge": 0,
        "multiplicity": 1,
        "notes": "Standard SAPT test system"
    },
}


@register_resource
class MoleculeResource(BaseResource):
    """Resource providing common molecule geometries."""
    
    name = "molecules"
    description = "Library of common molecule geometries"
    
    def get(self, subpath: Optional[str] = None) -> str:
        if subpath is None:
            return self.to_json({
                "total": len(MOLECULES),
                "molecules": {k: {"formula": v["formula"], "atoms": v["atoms"]} 
                             for k, v in MOLECULES.items()}
            })
        
        key = subpath.lower().replace(" ", "_").replace("-", "_")
        if key in MOLECULES:
            return self.to_json(MOLECULES[key])
        
        # Search by formula
        for name, mol in MOLECULES.items():
            if mol["formula"].lower() == subpath.lower():
                return self.to_json(mol)
        
        return self.to_json({
            "error": f"Molecule '{subpath}' not found",
            "available": list(MOLECULES.keys())
        })
