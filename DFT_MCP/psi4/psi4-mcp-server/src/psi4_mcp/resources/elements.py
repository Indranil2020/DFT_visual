"""Element Properties Resource."""

from typing import Optional, Dict, Any
from psi4_mcp.resources.base_resource import BaseResource, register_resource

ELEMENTS: Dict[int, Dict[str, Any]] = {
    1: {"symbol": "H", "name": "Hydrogen", "mass": 1.008, "group": 1, "period": 1},
    2: {"symbol": "He", "name": "Helium", "mass": 4.003, "group": 18, "period": 1},
    3: {"symbol": "Li", "name": "Lithium", "mass": 6.941, "group": 1, "period": 2},
    4: {"symbol": "Be", "name": "Beryllium", "mass": 9.012, "group": 2, "period": 2},
    5: {"symbol": "B", "name": "Boron", "mass": 10.81, "group": 13, "period": 2},
    6: {"symbol": "C", "name": "Carbon", "mass": 12.01, "group": 14, "period": 2},
    7: {"symbol": "N", "name": "Nitrogen", "mass": 14.01, "group": 15, "period": 2},
    8: {"symbol": "O", "name": "Oxygen", "mass": 16.00, "group": 16, "period": 2},
    9: {"symbol": "F", "name": "Fluorine", "mass": 19.00, "group": 17, "period": 2},
    10: {"symbol": "Ne", "name": "Neon", "mass": 20.18, "group": 18, "period": 2},
    11: {"symbol": "Na", "name": "Sodium", "mass": 22.99, "group": 1, "period": 3},
    12: {"symbol": "Mg", "name": "Magnesium", "mass": 24.31, "group": 2, "period": 3},
    13: {"symbol": "Al", "name": "Aluminum", "mass": 26.98, "group": 13, "period": 3},
    14: {"symbol": "Si", "name": "Silicon", "mass": 28.09, "group": 14, "period": 3},
    15: {"symbol": "P", "name": "Phosphorus", "mass": 30.97, "group": 15, "period": 3},
    16: {"symbol": "S", "name": "Sulfur", "mass": 32.06, "group": 16, "period": 3},
    17: {"symbol": "Cl", "name": "Chlorine", "mass": 35.45, "group": 17, "period": 3},
    18: {"symbol": "Ar", "name": "Argon", "mass": 39.95, "group": 18, "period": 3},
    19: {"symbol": "K", "name": "Potassium", "mass": 39.10, "group": 1, "period": 4},
    20: {"symbol": "Ca", "name": "Calcium", "mass": 40.08, "group": 2, "period": 4},
    21: {"symbol": "Sc", "name": "Scandium", "mass": 44.96, "group": 3, "period": 4},
    22: {"symbol": "Ti", "name": "Titanium", "mass": 47.87, "group": 4, "period": 4},
    23: {"symbol": "V", "name": "Vanadium", "mass": 50.94, "group": 5, "period": 4},
    24: {"symbol": "Cr", "name": "Chromium", "mass": 52.00, "group": 6, "period": 4},
    25: {"symbol": "Mn", "name": "Manganese", "mass": 54.94, "group": 7, "period": 4},
    26: {"symbol": "Fe", "name": "Iron", "mass": 55.85, "group": 8, "period": 4},
    27: {"symbol": "Co", "name": "Cobalt", "mass": 58.93, "group": 9, "period": 4},
    28: {"symbol": "Ni", "name": "Nickel", "mass": 58.69, "group": 10, "period": 4},
    29: {"symbol": "Cu", "name": "Copper", "mass": 63.55, "group": 11, "period": 4},
    30: {"symbol": "Zn", "name": "Zinc", "mass": 65.38, "group": 12, "period": 4},
    31: {"symbol": "Ga", "name": "Gallium", "mass": 69.72, "group": 13, "period": 4},
    32: {"symbol": "Ge", "name": "Germanium", "mass": 72.63, "group": 14, "period": 4},
    33: {"symbol": "As", "name": "Arsenic", "mass": 74.92, "group": 15, "period": 4},
    34: {"symbol": "Se", "name": "Selenium", "mass": 78.97, "group": 16, "period": 4},
    35: {"symbol": "Br", "name": "Bromine", "mass": 79.90, "group": 17, "period": 4},
    36: {"symbol": "Kr", "name": "Krypton", "mass": 83.80, "group": 18, "period": 4},
    37: {"symbol": "Rb", "name": "Rubidium", "mass": 85.47, "group": 1, "period": 5},
    38: {"symbol": "Sr", "name": "Strontium", "mass": 87.62, "group": 2, "period": 5},
    39: {"symbol": "Y", "name": "Yttrium", "mass": 88.91, "group": 3, "period": 5},
    40: {"symbol": "Zr", "name": "Zirconium", "mass": 91.22, "group": 4, "period": 5},
    41: {"symbol": "Nb", "name": "Niobium", "mass": 92.91, "group": 5, "period": 5},
    42: {"symbol": "Mo", "name": "Molybdenum", "mass": 95.95, "group": 6, "period": 5},
    43: {"symbol": "Tc", "name": "Technetium", "mass": 98.00, "group": 7, "period": 5},
    44: {"symbol": "Ru", "name": "Ruthenium", "mass": 101.07, "group": 8, "period": 5},
    45: {"symbol": "Rh", "name": "Rhodium", "mass": 102.91, "group": 9, "period": 5},
    46: {"symbol": "Pd", "name": "Palladium", "mass": 106.42, "group": 10, "period": 5},
    47: {"symbol": "Ag", "name": "Silver", "mass": 107.87, "group": 11, "period": 5},
    48: {"symbol": "Cd", "name": "Cadmium", "mass": 112.41, "group": 12, "period": 5},
    49: {"symbol": "In", "name": "Indium", "mass": 114.82, "group": 13, "period": 5},
    50: {"symbol": "Sn", "name": "Tin", "mass": 118.71, "group": 14, "period": 5},
    51: {"symbol": "Sb", "name": "Antimony", "mass": 121.76, "group": 15, "period": 5},
    52: {"symbol": "Te", "name": "Tellurium", "mass": 127.60, "group": 16, "period": 5},
    53: {"symbol": "I", "name": "Iodine", "mass": 126.90, "group": 17, "period": 5},
    54: {"symbol": "Xe", "name": "Xenon", "mass": 131.29, "group": 18, "period": 5},
    55: {"symbol": "Cs", "name": "Cesium", "mass": 132.91, "group": 1, "period": 6},
    56: {"symbol": "Ba", "name": "Barium", "mass": 137.33, "group": 2, "period": 6},
    57: {"symbol": "La", "name": "Lanthanum", "mass": 138.91, "group": 3, "period": 6},
    58: {"symbol": "Ce", "name": "Cerium", "mass": 140.12, "group": None, "period": 6},
    59: {"symbol": "Pr", "name": "Praseodymium", "mass": 140.91, "group": None, "period": 6},
    60: {"symbol": "Nd", "name": "Neodymium", "mass": 144.24, "group": None, "period": 6},
    61: {"symbol": "Pm", "name": "Promethium", "mass": 145.00, "group": None, "period": 6},
    62: {"symbol": "Sm", "name": "Samarium", "mass": 150.36, "group": None, "period": 6},
    63: {"symbol": "Eu", "name": "Europium", "mass": 151.96, "group": None, "period": 6},
    64: {"symbol": "Gd", "name": "Gadolinium", "mass": 157.25, "group": None, "period": 6},
    65: {"symbol": "Tb", "name": "Terbium", "mass": 158.93, "group": None, "period": 6},
    66: {"symbol": "Dy", "name": "Dysprosium", "mass": 162.50, "group": None, "period": 6},
    67: {"symbol": "Ho", "name": "Holmium", "mass": 164.93, "group": None, "period": 6},
    68: {"symbol": "Er", "name": "Erbium", "mass": 167.26, "group": None, "period": 6},
    69: {"symbol": "Tm", "name": "Thulium", "mass": 168.93, "group": None, "period": 6},
    70: {"symbol": "Yb", "name": "Ytterbium", "mass": 173.05, "group": None, "period": 6},
    71: {"symbol": "Lu", "name": "Lutetium", "mass": 174.97, "group": 3, "period": 6},
    72: {"symbol": "Hf", "name": "Hafnium", "mass": 178.49, "group": 4, "period": 6},
    73: {"symbol": "Ta", "name": "Tantalum", "mass": 180.95, "group": 5, "period": 6},
    74: {"symbol": "W", "name": "Tungsten", "mass": 183.84, "group": 6, "period": 6},
    75: {"symbol": "Re", "name": "Rhenium", "mass": 186.21, "group": 7, "period": 6},
    76: {"symbol": "Os", "name": "Osmium", "mass": 190.23, "group": 8, "period": 6},
    77: {"symbol": "Ir", "name": "Iridium", "mass": 192.22, "group": 9, "period": 6},
    78: {"symbol": "Pt", "name": "Platinum", "mass": 195.08, "group": 10, "period": 6},
    79: {"symbol": "Au", "name": "Gold", "mass": 196.97, "group": 11, "period": 6},
    80: {"symbol": "Hg", "name": "Mercury", "mass": 200.59, "group": 12, "period": 6},
    81: {"symbol": "Tl", "name": "Thallium", "mass": 204.38, "group": 13, "period": 6},
    82: {"symbol": "Pb", "name": "Lead", "mass": 207.2, "group": 14, "period": 6},
    83: {"symbol": "Bi", "name": "Bismuth", "mass": 208.98, "group": 15, "period": 6},
    84: {"symbol": "Po", "name": "Polonium", "mass": 209.00, "group": 16, "period": 6},
    85: {"symbol": "At", "name": "Astatine", "mass": 210.00, "group": 17, "period": 6},
    86: {"symbol": "Rn", "name": "Radon", "mass": 222.00, "group": 18, "period": 6},
    87: {"symbol": "Fr", "name": "Francium", "mass": 223.00, "group": 1, "period": 7},
    88: {"symbol": "Ra", "name": "Radium", "mass": 226.00, "group": 2, "period": 7},
    89: {"symbol": "Ac", "name": "Actinium", "mass": 227.00, "group": 3, "period": 7},
    90: {"symbol": "Th", "name": "Thorium", "mass": 232.04, "group": None, "period": 7},
    91: {"symbol": "Pa", "name": "Protactinium", "mass": 231.04, "group": None, "period": 7},
    92: {"symbol": "U", "name": "Uranium", "mass": 238.03, "group": None, "period": 7},
    93: {"symbol": "Np", "name": "Neptunium", "mass": 237.00, "group": None, "period": 7},
    94: {"symbol": "Pu", "name": "Plutonium", "mass": 244.00, "group": None, "period": 7},
    95: {"symbol": "Am", "name": "Americium", "mass": 243.00, "group": None, "period": 7},
    96: {"symbol": "Cm", "name": "Curium", "mass": 247.00, "group": None, "period": 7},
    97: {"symbol": "Bk", "name": "Berkelium", "mass": 247.00, "group": None, "period": 7},
    98: {"symbol": "Cf", "name": "Californium", "mass": 251.00, "group": None, "period": 7},
    99: {"symbol": "Es", "name": "Einsteinium", "mass": 252.00, "group": None, "period": 7},
    100: {"symbol": "Fm", "name": "Fermium", "mass": 257.00, "group": None, "period": 7},
    101: {"symbol": "Md", "name": "Mendelevium", "mass": 258.00, "group": None, "period": 7},
    102: {"symbol": "No", "name": "Nobelium", "mass": 259.00, "group": None, "period": 7},
    103: {"symbol": "Lr", "name": "Lawrencium", "mass": 262.00, "group": None, "period": 7},
    104: {"symbol": "Rf", "name": "Rutherfordium", "mass": 267.00, "group": 4, "period": 7},
    105: {"symbol": "Db", "name": "Dubnium", "mass": 268.00, "group": 5, "period": 7},
    106: {"symbol": "Sg", "name": "Seaborgium", "mass": 271.00, "group": 6, "period": 7},
    107: {"symbol": "Bh", "name": "Bohrium", "mass": 272.00, "group": 7, "period": 7},
    108: {"symbol": "Hs", "name": "Hassium", "mass": 270.00, "group": 8, "period": 7},
    109: {"symbol": "Mt", "name": "Meitnerium", "mass": 276.00, "group": 9, "period": 7},
    110: {"symbol": "Ds", "name": "Darmstadtium", "mass": 281.00, "group": 10, "period": 7},
    111: {"symbol": "Rg", "name": "Roentgenium", "mass": 280.00, "group": 11, "period": 7},
    112: {"symbol": "Cn", "name": "Copernicium", "mass": 285.00, "group": 12, "period": 7},
    113: {"symbol": "Nh", "name": "Nihonium", "mass": 284.00, "group": 13, "period": 7},
    114: {"symbol": "Fl", "name": "Flerovium", "mass": 289.00, "group": 14, "period": 7},
    115: {"symbol": "Mc", "name": "Moscovium", "mass": 288.00, "group": 15, "period": 7},
    116: {"symbol": "Lv", "name": "Livermorium", "mass": 293.00, "group": 16, "period": 7},
    117: {"symbol": "Ts", "name": "Tennessine", "mass": 294.00, "group": 17, "period": 7},
    118: {"symbol": "Og", "name": "Oganesson", "mass": 294.00, "group": 18, "period": 7},
}


@register_resource
class ElementResource(BaseResource):
    """Resource providing element information."""

    name = "elements"
    description = "Periodic table element properties"

    def get(self, subpath: Optional[str] = None) -> str:
        if subpath is None:
            return self.to_json({
                "total": len(ELEMENTS),
                "elements": {v["symbol"]: v["name"] for v in ELEMENTS.values()}
            })

        # Check if subpath is an atomic number (integer string)
        if subpath.isdigit():
            z = int(subpath)
            if z in ELEMENTS:
                return self.to_json(ELEMENTS[z])

        # Try symbol or name
        for z, info in ELEMENTS.items():
            if info["symbol"].lower() == subpath.lower() or info["name"].lower() == subpath.lower():
                return self.to_json({**info, "atomic_number": z})

        return self.to_json({"error": f"Element '{subpath}' not found"})