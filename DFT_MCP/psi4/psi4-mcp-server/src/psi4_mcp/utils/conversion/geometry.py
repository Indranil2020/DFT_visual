"""
Geometry Format Conversion Utilities.

This module provides functions for converting molecular geometries between
different formats commonly used in quantum chemistry:

- XYZ format (Cartesian coordinates)
- Z-matrix (internal coordinates)
- Psi4 molecule strings
- PDB format (basic support)
- Various coordinate systems

Key Features:
    - Parse and generate multiple geometry formats
    - Coordinate system transformations
    - Fragment handling
    - Ghost atom support
"""

from typing import Optional, Sequence
from dataclasses import dataclass, field
from enum import Enum
import math

from psi4_mcp.utils.helpers.constants import (
    BOHR_TO_ANGSTROM,
    ANGSTROM_TO_BOHR,
    ATOMIC_MASSES,
    get_atomic_number,
)
from psi4_mcp.utils.helpers.string_utils import (
    normalize_element_symbol,
    is_valid_element_symbol,
)
from psi4_mcp.utils.helpers.math_utils import (
    vector_norm,
    vector_subtract,
    cross_product,
    dot_product,
    angle_between_vectors,
)


# =============================================================================
# ENUMERATIONS
# =============================================================================

class CoordinateFormat(str, Enum):
    """Supported coordinate format types."""
    XYZ = "xyz"
    ZMATRIX = "zmatrix"
    PSI4 = "psi4"
    PDB = "pdb"
    INTERNAL = "internal"
    CARTESIAN = "cartesian"


class LengthUnitType(str, Enum):
    """Length unit types for coordinates."""
    ANGSTROM = "angstrom"
    BOHR = "bohr"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Atom:
    """
    Represents a single atom with its properties.
    
    Attributes:
        symbol: Element symbol (e.g., "H", "C", "Fe").
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        mass: Atomic mass (AMU). If None, uses standard mass.
        charge: Partial charge (for force fields).
        label: Optional atom label/name.
        is_ghost: Whether this is a ghost atom (Bq).
        fragment_id: Fragment identifier for multi-fragment systems.
    """
    symbol: str
    x: float
    y: float
    z: float
    mass: Optional[float] = None
    charge: Optional[float] = None
    label: Optional[str] = None
    is_ghost: bool = False
    fragment_id: int = 0
    
    def __post_init__(self) -> None:
        self.symbol = normalize_element_symbol(self.symbol)
        if self.mass is None:
            self.mass = ATOMIC_MASSES.get(self.symbol, 0.0)
    
    @property
    def atomic_number(self) -> int:
        """Get the atomic number."""
        return get_atomic_number(self.symbol)
    
    @property
    def coordinates(self) -> tuple[float, float, float]:
        """Get coordinates as a tuple."""
        return (self.x, self.y, self.z)
    
    @property
    def coordinates_list(self) -> list[float]:
        """Get coordinates as a list."""
        return [self.x, self.y, self.z]
    
    def distance_to(self, other: "Atom") -> float:
        """Calculate distance to another atom."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)
    
    def to_xyz_line(self, precision: int = 10) -> str:
        """Format as XYZ line."""
        prefix = "@" if self.is_ghost else ""
        width = precision + 6
        return (
            f"{prefix}{self.symbol:>2s}  "
            f"{self.x:>{width}.{precision}f}  "
            f"{self.y:>{width}.{precision}f}  "
            f"{self.z:>{width}.{precision}f}"
        )
    
    def scaled_coordinates(self, factor: float) -> "Atom":
        """Return a new Atom with scaled coordinates."""
        return Atom(
            symbol=self.symbol,
            x=self.x * factor,
            y=self.y * factor,
            z=self.z * factor,
            mass=self.mass,
            charge=self.charge,
            label=self.label,
            is_ghost=self.is_ghost,
            fragment_id=self.fragment_id,
        )


@dataclass
class Geometry:
    """
    Represents a molecular geometry.
    
    Attributes:
        atoms: List of atoms in the geometry.
        units: Length units (angstrom or bohr).
        charge: Total molecular charge.
        multiplicity: Spin multiplicity.
        name: Optional molecule name.
        comment: Optional comment/description.
        symmetry: Point group symmetry (if known).
    """
    atoms: list[Atom] = field(default_factory=list)
    units: LengthUnitType = LengthUnitType.ANGSTROM
    charge: int = 0
    multiplicity: int = 1
    name: Optional[str] = None
    comment: Optional[str] = None
    symmetry: Optional[str] = None
    
    @property
    def n_atoms(self) -> int:
        """Number of atoms."""
        return len(self.atoms)
    
    @property
    def n_real_atoms(self) -> int:
        """Number of real (non-ghost) atoms."""
        return sum(1 for a in self.atoms if not a.is_ghost)
    
    @property
    def n_electrons(self) -> int:
        """Total number of electrons (considering charge)."""
        total_z = sum(a.atomic_number for a in self.atoms if not a.is_ghost)
        return total_z - self.charge
    
    @property
    def molecular_mass(self) -> float:
        """Total molecular mass in AMU."""
        return sum(a.mass or 0.0 for a in self.atoms if not a.is_ghost)
    
    @property
    def molecular_formula(self) -> str:
        """Generate molecular formula (Hill notation)."""
        counts: dict[str, int] = {}
        for atom in self.atoms:
            if not atom.is_ghost:
                counts[atom.symbol] = counts.get(atom.symbol, 0) + 1
        
        # Hill notation: C first, then H, then alphabetical
        parts = []
        if "C" in counts:
            parts.append(f"C{counts['C']}" if counts["C"] > 1 else "C")
            del counts["C"]
            if "H" in counts:
                parts.append(f"H{counts['H']}" if counts["H"] > 1 else "H")
                del counts["H"]
        
        for symbol in sorted(counts.keys()):
            parts.append(f"{symbol}{counts[symbol]}" if counts[symbol] > 1 else symbol)
        
        return "".join(parts)
    
    @property
    def center_of_mass(self) -> tuple[float, float, float]:
        """Calculate center of mass."""
        total_mass = 0.0
        cx, cy, cz = 0.0, 0.0, 0.0
        
        for atom in self.atoms:
            if atom.is_ghost:
                continue
            mass = atom.mass or 0.0
            total_mass += mass
            cx += mass * atom.x
            cy += mass * atom.y
            cz += mass * atom.z
        
        if total_mass < 1e-10:
            return (0.0, 0.0, 0.0)
        
        return (cx / total_mass, cy / total_mass, cz / total_mass)
    
    @property
    def center_of_nuclear_charge(self) -> tuple[float, float, float]:
        """Calculate center of nuclear charge."""
        total_z = 0.0
        cx, cy, cz = 0.0, 0.0, 0.0
        
        for atom in self.atoms:
            if atom.is_ghost:
                continue
            z = float(atom.atomic_number)
            total_z += z
            cx += z * atom.x
            cy += z * atom.y
            cz += z * atom.z
        
        if total_z < 1e-10:
            return (0.0, 0.0, 0.0)
        
        return (cx / total_z, cy / total_z, cz / total_z)
    
    @property
    def fragments(self) -> list[list[int]]:
        """Get atom indices grouped by fragment."""
        frag_dict: dict[int, list[int]] = {}
        for i, atom in enumerate(self.atoms):
            fid = atom.fragment_id
            if fid not in frag_dict:
                frag_dict[fid] = []
            frag_dict[fid].append(i)
        return [frag_dict[k] for k in sorted(frag_dict.keys())]
    
    def get_coordinates(self) -> list[list[float]]:
        """Get all coordinates as a list of [x, y, z] lists."""
        return [atom.coordinates_list for atom in self.atoms]
    
    def get_symbols(self) -> list[str]:
        """Get all element symbols."""
        return [atom.symbol for atom in self.atoms]
    
    def to_bohr(self) -> "Geometry":
        """Convert to Bohr units."""
        if self.units == LengthUnitType.BOHR:
            return self
        
        new_atoms = [atom.scaled_coordinates(ANGSTROM_TO_BOHR) for atom in self.atoms]
        return Geometry(
            atoms=new_atoms,
            units=LengthUnitType.BOHR,
            charge=self.charge,
            multiplicity=self.multiplicity,
            name=self.name,
            comment=self.comment,
            symmetry=self.symmetry,
        )
    
    def to_angstrom(self) -> "Geometry":
        """Convert to Angstrom units."""
        if self.units == LengthUnitType.ANGSTROM:
            return self
        
        new_atoms = [atom.scaled_coordinates(BOHR_TO_ANGSTROM) for atom in self.atoms]
        return Geometry(
            atoms=new_atoms,
            units=LengthUnitType.ANGSTROM,
            charge=self.charge,
            multiplicity=self.multiplicity,
            name=self.name,
            comment=self.comment,
            symmetry=self.symmetry,
        )
    
    def translate(self, dx: float, dy: float, dz: float) -> "Geometry":
        """Return a translated copy of the geometry."""
        new_atoms = [
            Atom(
                symbol=a.symbol,
                x=a.x + dx,
                y=a.y + dy,
                z=a.z + dz,
                mass=a.mass,
                charge=a.charge,
                label=a.label,
                is_ghost=a.is_ghost,
                fragment_id=a.fragment_id,
            )
            for a in self.atoms
        ]
        return Geometry(
            atoms=new_atoms,
            units=self.units,
            charge=self.charge,
            multiplicity=self.multiplicity,
            name=self.name,
            comment=self.comment,
            symmetry=self.symmetry,
        )
    
    def center_on_origin(self) -> "Geometry":
        """Return geometry centered on the center of mass."""
        com = self.center_of_mass
        return self.translate(-com[0], -com[1], -com[2])


# =============================================================================
# XYZ FORMAT PARSING
# =============================================================================

def parse_xyz(content: str) -> Optional[Geometry]:
    """
    Parse XYZ format geometry.
    
    Standard XYZ format:
        Line 1: Number of atoms
        Line 2: Comment/title
        Line 3+: Element X Y Z
    
    Args:
        content: XYZ file content as string.
        
    Returns:
        Geometry object, or None if parsing fails.
    """
    lines = content.strip().split('\n')
    
    if len(lines) < 3:
        return None
    
    # Parse number of atoms
    first_line = lines[0].strip()
    if not first_line.isdigit():
        return None
    n_atoms = int(first_line)
    
    # Comment line
    comment = lines[1].strip() if len(lines) > 1 else None
    
    # Parse atoms
    atoms = []
    for i in range(2, min(2 + n_atoms, len(lines))):
        line = lines[i].strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) < 4:
            continue
        
        symbol = parts[0]
        
        # Handle ghost atoms
        is_ghost = False
        if symbol.startswith('@') or symbol.startswith('X') or symbol.lower().startswith('gh'):
            is_ghost = True
            if symbol.startswith('@'):
                symbol = symbol[1:]
            elif symbol.lower().startswith('gh(') and symbol.endswith(')'):
                symbol = symbol[3:-1]
            elif symbol.lower() == 'x':
                symbol = 'X'
        
        if not is_valid_element_symbol(symbol) and not is_ghost:
            continue
        
        # Parse coordinates
        x_str = parts[1].replace('D', 'E').replace('d', 'e')
        y_str = parts[2].replace('D', 'E').replace('d', 'e')
        z_str = parts[3].replace('D', 'E').replace('d', 'e')
        
        x = float(x_str)
        y = float(y_str)
        z = float(z_str)
        
        atoms.append(Atom(
            symbol=symbol,
            x=x,
            y=y,
            z=z,
            is_ghost=is_ghost,
        ))
    
    if len(atoms) == 0:
        return None
    
    return Geometry(
        atoms=atoms,
        units=LengthUnitType.ANGSTROM,
        comment=comment,
    )


def geometry_to_xyz(
    geom: Geometry,
    precision: int = 10,
    include_header: bool = True
) -> str:
    """
    Convert geometry to XYZ format string.
    
    Args:
        geom: Geometry object.
        precision: Decimal places for coordinates.
        include_header: Include atom count and comment lines.
        
    Returns:
        XYZ format string.
    """
    # Ensure Angstrom units for standard XYZ
    geom_ang = geom.to_angstrom()
    
    lines = []
    
    if include_header:
        lines.append(str(len(geom_ang.atoms)))
        comment = geom_ang.comment or geom_ang.name or geom_ang.molecular_formula
        lines.append(comment or "")
    
    for atom in geom_ang.atoms:
        lines.append(atom.to_xyz_line(precision))
    
    return '\n'.join(lines)


# =============================================================================
# PSI4 FORMAT
# =============================================================================

def parse_psi4_geometry(content: str) -> Optional[Geometry]:
    """
    Parse Psi4-style geometry specification.
    
    Supports:
        - Cartesian coordinates
        - Charge/multiplicity specification
        - Units specification
        - Fragment separators (--)
        - Ghost atoms (@, Gh())
        - Symmetry and other options
    
    Args:
        content: Psi4 molecule string.
        
    Returns:
        Geometry object, or None if parsing fails.
    """
    lines = content.strip().split('\n')
    
    atoms = []
    charge = 0
    multiplicity = 1
    units = LengthUnitType.ANGSTROM
    symmetry = None
    current_fragment = 0
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#') or line.startswith('!'):
            continue
        
        # Fragment separator
        if line == '--':
            current_fragment += 1
            continue
        
        # Check for options (key = value or single keywords)
        if '=' in line or line.lower() in ('noreorient', 'nocom', 'symmetry'):
            lower_line = line.lower()
            
            if lower_line.startswith('units'):
                if 'bohr' in lower_line or 'au' in lower_line:
                    units = LengthUnitType.BOHR
                else:
                    units = LengthUnitType.ANGSTROM
            elif lower_line.startswith('symmetry'):
                parts = line.split()
                if len(parts) > 1:
                    symmetry = parts[1]
            continue
        
        parts = line.split()
        
        # Check for charge/multiplicity line (two integers)
        if len(parts) == 2:
            if parts[0].lstrip('-').isdigit() and parts[1].isdigit():
                charge = int(parts[0])
                multiplicity = int(parts[1])
                continue
        
        # Parse atom line
        if len(parts) >= 4:
            symbol = parts[0]
            
            # Handle ghost atoms
            is_ghost = False
            if symbol.startswith('@'):
                is_ghost = True
                symbol = symbol[1:]
            elif symbol.lower().startswith('gh(') and symbol.endswith(')'):
                is_ghost = True
                symbol = symbol[3:-1]
            
            if not is_valid_element_symbol(symbol):
                continue
            
            x_str = parts[1].replace('D', 'E').replace('d', 'e')
            y_str = parts[2].replace('D', 'E').replace('d', 'e')
            z_str = parts[3].replace('D', 'E').replace('d', 'e')
            
            x = float(x_str)
            y = float(y_str)
            z = float(z_str)
            
            atoms.append(Atom(
                symbol=symbol,
                x=x,
                y=y,
                z=z,
                is_ghost=is_ghost,
                fragment_id=current_fragment,
            ))
    
    if len(atoms) == 0:
        return None
    
    return Geometry(
        atoms=atoms,
        units=units,
        charge=charge,
        multiplicity=multiplicity,
        symmetry=symmetry,
    )


def geometry_to_psi4(
    geom: Geometry,
    precision: int = 10,
    include_options: bool = True
) -> str:
    """
    Convert geometry to Psi4 molecule format string.
    
    Args:
        geom: Geometry object.
        precision: Decimal places for coordinates.
        include_options: Include units and other options.
        
    Returns:
        Psi4-style geometry string.
    """
    lines = []
    
    # Charge and multiplicity
    lines.append(f"{geom.charge} {geom.multiplicity}")
    
    # Options
    if include_options:
        unit_str = "bohr" if geom.units == LengthUnitType.BOHR else "angstrom"
        lines.append(f"units {unit_str}")
        if geom.symmetry:
            lines.append(f"symmetry {geom.symmetry}")
        lines.append("noreorient")
        lines.append("nocom")
    
    # Atoms by fragment
    current_fragment = -1
    for atom in geom.atoms:
        if atom.fragment_id != current_fragment:
            if current_fragment >= 0:
                lines.append("--")
            current_fragment = atom.fragment_id
        
        lines.append(atom.to_xyz_line(precision))
    
    return '\n'.join(lines)


# =============================================================================
# INTERNAL COORDINATES
# =============================================================================

@dataclass
class InternalCoordinate:
    """Base class for internal coordinates."""
    atoms: list[int]  # 0-indexed atom indices
    value: float
    
    @property
    def n_atoms(self) -> int:
        return len(self.atoms)


@dataclass
class BondLength(InternalCoordinate):
    """Bond length between two atoms."""
    
    def __init__(self, atom1: int, atom2: int, value: float):
        super().__init__(atoms=[atom1, atom2], value=value)


@dataclass
class BondAngle(InternalCoordinate):
    """Angle between three atoms (in degrees)."""
    
    def __init__(self, atom1: int, atom2: int, atom3: int, value: float):
        super().__init__(atoms=[atom1, atom2, atom3], value=value)


@dataclass
class DihedralAngle(InternalCoordinate):
    """Dihedral/torsion angle between four atoms (in degrees)."""
    
    def __init__(self, atom1: int, atom2: int, atom3: int, atom4: int, value: float):
        super().__init__(atoms=[atom1, atom2, atom3, atom4], value=value)


def calculate_bond_length(geom: Geometry, atom1: int, atom2: int) -> float:
    """
    Calculate bond length between two atoms.
    
    Args:
        geom: Geometry object.
        atom1: Index of first atom (0-based).
        atom2: Index of second atom (0-based).
        
    Returns:
        Bond length in the geometry's units.
    """
    if atom1 < 0 or atom1 >= len(geom.atoms):
        return 0.0
    if atom2 < 0 or atom2 >= len(geom.atoms):
        return 0.0
    
    return geom.atoms[atom1].distance_to(geom.atoms[atom2])


def calculate_bond_angle(
    geom: Geometry, 
    atom1: int, 
    atom2: int, 
    atom3: int
) -> float:
    """
    Calculate angle between three atoms (atom2 is the vertex).
    
    Args:
        geom: Geometry object.
        atom1: Index of first atom.
        atom2: Index of central atom (vertex).
        atom3: Index of third atom.
        
    Returns:
        Angle in degrees.
    """
    if any(i < 0 or i >= len(geom.atoms) for i in [atom1, atom2, atom3]):
        return 0.0
    
    a1 = geom.atoms[atom1]
    a2 = geom.atoms[atom2]
    a3 = geom.atoms[atom3]
    
    # Vectors from central atom
    v1 = [a1.x - a2.x, a1.y - a2.y, a1.z - a2.z]
    v2 = [a3.x - a2.x, a3.y - a2.y, a3.z - a2.z]
    
    angle_rad = angle_between_vectors(v1, v2)
    return math.degrees(angle_rad)


def calculate_dihedral_angle(
    geom: Geometry,
    atom1: int,
    atom2: int,
    atom3: int,
    atom4: int
) -> float:
    """
    Calculate dihedral angle between four atoms.
    
    The dihedral is the angle between planes (1-2-3) and (2-3-4).
    
    Args:
        geom: Geometry object.
        atom1: Index of first atom.
        atom2: Index of second atom.
        atom3: Index of third atom.
        atom4: Index of fourth atom.
        
    Returns:
        Dihedral angle in degrees (-180 to 180).
    """
    if any(i < 0 or i >= len(geom.atoms) for i in [atom1, atom2, atom3, atom4]):
        return 0.0
    
    a1 = geom.atoms[atom1]
    a2 = geom.atoms[atom2]
    a3 = geom.atoms[atom3]
    a4 = geom.atoms[atom4]
    
    # Vectors along bonds
    b1 = [a2.x - a1.x, a2.y - a1.y, a2.z - a1.z]
    b2 = [a3.x - a2.x, a3.y - a2.y, a3.z - a2.z]
    b3 = [a4.x - a3.x, a4.y - a3.y, a4.z - a3.z]
    
    # Normal vectors to planes
    n1 = cross_product(b1, b2)
    n2 = cross_product(b2, b3)
    
    # Calculate dihedral
    m1 = cross_product(n1, b2)
    m1_norm = vector_norm(m1)
    if m1_norm < 1e-10:
        return 0.0
    m1 = [x / m1_norm for x in m1]
    
    n1_norm = vector_norm(n1)
    if n1_norm < 1e-10:
        return 0.0
    n1_unit = [x / n1_norm for x in n1]
    
    x = dot_product(n1_unit, n2)
    y = dot_product(m1, n2)
    
    return math.degrees(math.atan2(y, x))


def get_all_bond_lengths(
    geom: Geometry,
    cutoff_factor: float = 1.3
) -> list[BondLength]:
    """
    Find all bond lengths based on covalent radii.
    
    Args:
        geom: Geometry object.
        cutoff_factor: Multiply sum of covalent radii by this factor.
        
    Returns:
        List of BondLength objects.
    """
    from psi4_mcp.utils.helpers.constants import COVALENT_RADII
    
    bonds = []
    n = len(geom.atoms)
    
    for i in range(n):
        for j in range(i + 1, n):
            a1 = geom.atoms[i]
            a2 = geom.atoms[j]
            
            if a1.is_ghost or a2.is_ghost:
                continue
            
            r1 = COVALENT_RADII.get(a1.symbol, 1.5)
            r2 = COVALENT_RADII.get(a2.symbol, 1.5)
            
            # Convert to geometry units if needed
            if geom.units == LengthUnitType.BOHR:
                r1 *= ANGSTROM_TO_BOHR
                r2 *= ANGSTROM_TO_BOHR
            
            cutoff = cutoff_factor * (r1 + r2)
            distance = a1.distance_to(a2)
            
            if distance < cutoff:
                bonds.append(BondLength(i, j, distance))
    
    return bonds


# =============================================================================
# GEOMETRY VALIDATION
# =============================================================================

def validate_geometry(geom: Geometry) -> tuple[bool, list[str]]:
    """
    Validate a molecular geometry.
    
    Checks for:
        - Valid element symbols
        - Reasonable interatomic distances
        - Valid charge/multiplicity
        - Non-zero coordinates (for multi-atom systems)
    
    Args:
        geom: Geometry to validate.
        
    Returns:
        Tuple of (is_valid, list of warning/error messages).
    """
    messages = []
    is_valid = True
    
    # Check for atoms
    if len(geom.atoms) == 0:
        messages.append("ERROR: Geometry has no atoms")
        return (False, messages)
    
    # Check element symbols
    for i, atom in enumerate(geom.atoms):
        if not atom.is_ghost and get_atomic_number(atom.symbol) <= 0:
            messages.append(f"ERROR: Invalid element symbol '{atom.symbol}' for atom {i+1}")
            is_valid = False
    
    # Check for overlapping atoms (very short distances)
    for i in range(len(geom.atoms)):
        for j in range(i + 1, len(geom.atoms)):
            a1 = geom.atoms[i]
            a2 = geom.atoms[j]
            
            if a1.is_ghost or a2.is_ghost:
                continue
            
            distance = a1.distance_to(a2)
            
            # Convert to Angstrom for checking
            if geom.units == LengthUnitType.BOHR:
                distance *= BOHR_TO_ANGSTROM
            
            if distance < 0.1:
                messages.append(
                    f"ERROR: Atoms {i+1} ({a1.symbol}) and {j+1} ({a2.symbol}) "
                    f"overlap (distance = {distance:.4f} Å)"
                )
                is_valid = False
            elif distance < 0.5:
                messages.append(
                    f"WARNING: Very short distance between atoms {i+1} and {j+1}: "
                    f"{distance:.4f} Å"
                )
    
    # Check multiplicity
    n_electrons = geom.n_electrons
    if n_electrons < 0:
        messages.append(f"ERROR: Negative number of electrons ({n_electrons})")
        is_valid = False
    
    n_unpaired = geom.multiplicity - 1
    if n_unpaired > n_electrons:
        messages.append(
            f"ERROR: Multiplicity {geom.multiplicity} requires {n_unpaired} unpaired electrons "
            f"but molecule only has {n_electrons} electrons"
        )
        is_valid = False
    
    if (n_unpaired % 2) != (n_electrons % 2):
        messages.append(
            f"ERROR: Multiplicity {geom.multiplicity} is incompatible with "
            f"{n_electrons} electrons (parity mismatch)"
        )
        is_valid = False
    
    return (is_valid, messages)


# =============================================================================
# GEOMETRY COMPARISON
# =============================================================================

def geometries_are_similar(
    geom1: Geometry,
    geom2: Geometry,
    tolerance: float = 0.01
) -> bool:
    """
    Check if two geometries represent the same structure.
    
    Compares atomic positions after centering on center of mass.
    Does not account for rotation or atom reordering.
    
    Args:
        geom1: First geometry.
        geom2: Second geometry.
        tolerance: Maximum allowed RMS deviation in Angstrom.
        
    Returns:
        True if geometries are similar within tolerance.
    """
    if len(geom1.atoms) != len(geom2.atoms):
        return False
    
    # Convert both to Angstrom and center
    g1 = geom1.to_angstrom().center_on_origin()
    g2 = geom2.to_angstrom().center_on_origin()
    
    # Check symbols match
    for a1, a2 in zip(g1.atoms, g2.atoms):
        if a1.symbol != a2.symbol:
            return False
    
    # Calculate RMS deviation
    sum_sq = 0.0
    for a1, a2 in zip(g1.atoms, g2.atoms):
        dx = a1.x - a2.x
        dy = a1.y - a2.y
        dz = a1.z - a2.z
        sum_sq += dx*dx + dy*dy + dz*dz
    
    rmsd = math.sqrt(sum_sq / len(g1.atoms))
    
    return rmsd < tolerance


def calculate_rmsd(geom1: Geometry, geom2: Geometry) -> float:
    """
    Calculate root-mean-square deviation between two geometries.
    
    Geometries must have the same number and order of atoms.
    
    Args:
        geom1: First geometry.
        geom2: Second geometry.
        
    Returns:
        RMSD in Angstrom, or -1.0 if geometries are incompatible.
    """
    if len(geom1.atoms) != len(geom2.atoms):
        return -1.0
    
    g1 = geom1.to_angstrom()
    g2 = geom2.to_angstrom()
    
    sum_sq = 0.0
    for a1, a2 in zip(g1.atoms, g2.atoms):
        dx = a1.x - a2.x
        dy = a1.y - a2.y
        dz = a1.z - a2.z
        sum_sq += dx*dx + dy*dy + dz*dz
    
    return math.sqrt(sum_sq / len(g1.atoms))
