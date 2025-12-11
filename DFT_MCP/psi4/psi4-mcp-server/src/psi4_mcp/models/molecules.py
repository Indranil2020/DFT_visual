"""
Molecule Data Models for Psi4 MCP Server.

This module provides comprehensive data models for representing molecules
and molecular systems in quantum chemistry calculations.

Key Classes:
    - Molecule: Full molecular representation
    - Fragment: Molecular fragment for SAPT/EDA calculations
    - MolecularSystem: Multi-molecule system
    - GeometrySpec: Geometry specification from various formats
"""

from typing import Any, Optional, Literal, Union, Sequence
from pydantic import Field, field_validator, model_validator
from collections import Counter
import math

from psi4_mcp.models.base import (
    Psi4BaseModel,
    AtomSpec,
    MoleculeSpec,
    Coordinate3D,
)
from psi4_mcp.utils.helpers.constants import (
    ATOMIC_NUMBERS,
    ATOMIC_MASSES,
    COVALENT_RADII,
    get_atomic_number,
    get_atomic_mass,
)


# =============================================================================
# ATOM MODELS
# =============================================================================

class AtomicPosition(Psi4BaseModel):
    """
    Complete atomic position with all relevant properties.
    
    Attributes:
        symbol: Element symbol.
        atomic_number: Atomic number (Z).
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        mass: Atomic mass in AMU.
        label: Atom label/name.
        is_ghost: Ghost atom flag.
        fragment_id: Fragment identifier.
        basis_set: Per-atom basis set override.
    """
    
    symbol: str = Field(..., min_length=1, max_length=3, description="Element symbol")
    atomic_number: int = Field(default=0, ge=0, le=118, description="Atomic number")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    mass: Optional[float] = Field(default=None, gt=0, description="Atomic mass in AMU")
    label: Optional[str] = Field(default=None, description="Atom label")
    is_ghost: bool = Field(default=False, description="Ghost atom flag")
    fragment_id: int = Field(default=0, ge=0, description="Fragment ID")
    basis_set: Optional[str] = Field(default=None, description="Per-atom basis set")
    
    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """Normalize element symbol."""
        v = v.strip()
        if len(v) == 1:
            return v.upper()
        return v[0].upper() + v[1:].lower()
    
    @model_validator(mode="after")
    def set_defaults(self) -> "AtomicPosition":
        """Set default atomic number and mass from symbol."""
        if self.atomic_number == 0 and not self.is_ghost:
            z = get_atomic_number(self.symbol)
            object.__setattr__(self, 'atomic_number', z)
        
        if self.mass is None and not self.is_ghost:
            mass = get_atomic_mass(self.symbol)
            if mass > 0:
                object.__setattr__(self, 'mass', mass)
        
        return self
    
    @property
    def coordinates(self) -> tuple[float, float, float]:
        """Get coordinates as tuple."""
        return (self.x, self.y, self.z)
    
    @property
    def coordinates_list(self) -> list[float]:
        """Get coordinates as list."""
        return [self.x, self.y, self.z]
    
    def distance_to(self, other: "AtomicPosition") -> float:
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


# =============================================================================
# MOLECULE MODEL
# =============================================================================

class Molecule(Psi4BaseModel):
    """
    Complete molecular representation for quantum chemistry calculations.
    
    Attributes:
        atoms: List of atomic positions.
        charge: Total molecular charge.
        multiplicity: Spin multiplicity (2S+1).
        units: Coordinate units.
        name: Molecule name.
        comment: Description or comment.
        symmetry: Point group symmetry.
        no_reorient: Disable geometry reorientation.
        no_com: Disable center of mass translation.
        fix_orientation: Fix molecular orientation.
        fragments: Fragment definitions for SAPT/EDA.
    """
    
    atoms: list[AtomicPosition] = Field(
        ..., 
        min_length=1, 
        description="List of atoms"
    )
    charge: int = Field(default=0, description="Total molecular charge")
    multiplicity: int = Field(default=1, ge=1, description="Spin multiplicity (2S+1)")
    units: Literal["angstrom", "bohr"] = Field(
        default="angstrom", 
        description="Coordinate units"
    )
    name: Optional[str] = Field(default=None, description="Molecule name")
    comment: Optional[str] = Field(default=None, description="Description/comment")
    symmetry: Optional[str] = Field(default=None, description="Point group symmetry")
    no_reorient: bool = Field(default=True, description="Disable reorientation")
    no_com: bool = Field(default=True, description="Disable COM translation")
    fix_orientation: bool = Field(default=False, description="Fix orientation")
    fragments: Optional[list[list[int]]] = Field(
        default=None, 
        description="Fragment atom indices"
    )
    
    # ==========================================================================
    # PROPERTIES
    # ==========================================================================
    
    @property
    def n_atoms(self) -> int:
        """Number of atoms (including ghost atoms)."""
        return len(self.atoms)
    
    @property
    def n_real_atoms(self) -> int:
        """Number of real (non-ghost) atoms."""
        return sum(1 for a in self.atoms if not a.is_ghost)
    
    @property
    def n_electrons(self) -> int:
        """Number of electrons."""
        total_z = sum(a.atomic_number for a in self.atoms if not a.is_ghost)
        return total_z - self.charge
    
    @property
    def n_alpha(self) -> int:
        """Number of alpha electrons."""
        n_unpaired = self.multiplicity - 1
        n_paired = self.n_electrons - n_unpaired
        return n_paired // 2 + n_unpaired
    
    @property
    def n_beta(self) -> int:
        """Number of beta electrons."""
        n_unpaired = self.multiplicity - 1
        n_paired = self.n_electrons - n_unpaired
        return n_paired // 2
    
    @property
    def total_mass(self) -> float:
        """Total molecular mass in AMU."""
        return sum(a.mass or 0.0 for a in self.atoms if not a.is_ghost)
    
    @property
    def total_nuclear_charge(self) -> int:
        """Total nuclear charge."""
        return sum(a.atomic_number for a in self.atoms if not a.is_ghost)
    
    @property
    def molecular_formula(self) -> str:
        """Molecular formula in Hill notation."""
        counts = Counter(a.symbol for a in self.atoms if not a.is_ghost)
        
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
        """Center of mass coordinates."""
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
        """Center of nuclear charge coordinates."""
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
    def element_counts(self) -> dict[str, int]:
        """Count of each element type."""
        return dict(Counter(a.symbol for a in self.atoms if not a.is_ghost))
    
    @property
    def unique_elements(self) -> list[str]:
        """List of unique element types."""
        return sorted(set(a.symbol for a in self.atoms if not a.is_ghost))
    
    @property
    def is_closed_shell(self) -> bool:
        """Check if molecule has closed-shell electronic structure."""
        return self.multiplicity == 1
    
    @property
    def is_linear(self) -> bool:
        """Check if molecule appears linear (heuristic)."""
        if self.n_real_atoms <= 2:
            return True
        
        # Check if all atoms are approximately collinear
        real_atoms = [a for a in self.atoms if not a.is_ghost]
        if len(real_atoms) < 3:
            return True
        
        # Get two vectors from first atom
        v1 = [
            real_atoms[1].x - real_atoms[0].x,
            real_atoms[1].y - real_atoms[0].y,
            real_atoms[1].z - real_atoms[0].z,
        ]
        
        v1_norm = math.sqrt(sum(x*x for x in v1))
        if v1_norm < 1e-10:
            return True
        v1 = [x / v1_norm for x in v1]
        
        # Check all other atoms
        for atom in real_atoms[2:]:
            v2 = [
                atom.x - real_atoms[0].x,
                atom.y - real_atoms[0].y,
                atom.z - real_atoms[0].z,
            ]
            v2_norm = math.sqrt(sum(x*x for x in v2))
            if v2_norm < 1e-10:
                continue
            v2 = [x / v2_norm for x in v2]
            
            # Check if parallel or antiparallel
            dot = abs(sum(a*b for a, b in zip(v1, v2)))
            if dot < 0.999:  # Not collinear
                return False
        
        return True
    
    # ==========================================================================
    # METHODS
    # ==========================================================================
    
    def get_coordinates(self) -> list[list[float]]:
        """Get all coordinates as list of [x, y, z] lists."""
        return [a.coordinates_list for a in self.atoms]
    
    def get_symbols(self) -> list[str]:
        """Get all element symbols."""
        return [a.symbol for a in self.atoms]
    
    def get_masses(self) -> list[float]:
        """Get all atomic masses."""
        return [a.mass or get_atomic_mass(a.symbol) for a in self.atoms]
    
    def get_nuclear_charges(self) -> list[int]:
        """Get all nuclear charges."""
        return [a.atomic_number for a in self.atoms]
    
    def get_fragment_atoms(self, fragment_id: int) -> list[AtomicPosition]:
        """Get atoms belonging to a specific fragment."""
        return [a for a in self.atoms if a.fragment_id == fragment_id]
    
    def distance(self, atom1: int, atom2: int) -> float:
        """Calculate distance between two atoms by index."""
        if atom1 < 0 or atom1 >= self.n_atoms:
            return 0.0
        if atom2 < 0 or atom2 >= self.n_atoms:
            return 0.0
        return self.atoms[atom1].distance_to(self.atoms[atom2])
    
    def angle(self, atom1: int, atom2: int, atom3: int) -> float:
        """Calculate angle (in degrees) with atom2 as vertex."""
        if any(i < 0 or i >= self.n_atoms for i in [atom1, atom2, atom3]):
            return 0.0
        
        a1, a2, a3 = self.atoms[atom1], self.atoms[atom2], self.atoms[atom3]
        
        v1 = [a1.x - a2.x, a1.y - a2.y, a1.z - a2.z]
        v2 = [a3.x - a2.x, a3.y - a2.y, a3.z - a2.z]
        
        dot = sum(a*b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(x*x for x in v1))
        mag2 = math.sqrt(sum(x*x for x in v2))
        
        if mag1 < 1e-10 or mag2 < 1e-10:
            return 0.0
        
        cos_angle = dot / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        
        return math.degrees(math.acos(cos_angle))
    
    def dihedral(self, atom1: int, atom2: int, atom3: int, atom4: int) -> float:
        """Calculate dihedral angle (in degrees) for four atoms."""
        if any(i < 0 or i >= self.n_atoms for i in [atom1, atom2, atom3, atom4]):
            return 0.0
        
        a1 = self.atoms[atom1]
        a2 = self.atoms[atom2]
        a3 = self.atoms[atom3]
        a4 = self.atoms[atom4]
        
        # Vectors
        b1 = [a2.x - a1.x, a2.y - a1.y, a2.z - a1.z]
        b2 = [a3.x - a2.x, a3.y - a2.y, a3.z - a2.z]
        b3 = [a4.x - a3.x, a4.y - a3.y, a4.z - a3.z]
        
        # Cross products
        def cross(v1: list[float], v2: list[float]) -> list[float]:
            return [
                v1[1]*v2[2] - v1[2]*v2[1],
                v1[2]*v2[0] - v1[0]*v2[2],
                v1[0]*v2[1] - v1[1]*v2[0]
            ]
        
        n1 = cross(b1, b2)
        n2 = cross(b2, b3)
        m1 = cross(n1, b2)
        
        b2_norm = math.sqrt(sum(x*x for x in b2))
        if b2_norm < 1e-10:
            return 0.0
        m1 = [x / b2_norm for x in m1]
        
        n1_norm = math.sqrt(sum(x*x for x in n1))
        if n1_norm < 1e-10:
            return 0.0
        n1 = [x / n1_norm for x in n1]
        
        x = sum(a*b for a, b in zip(n1, n2))
        y = sum(a*b for a, b in zip(m1, n2))
        
        return math.degrees(math.atan2(y, x))
    
    # ==========================================================================
    # CONVERSION METHODS
    # ==========================================================================
    
    def to_xyz_string(self, precision: int = 10) -> str:
        """Convert to XYZ format string."""
        lines = [str(self.n_atoms)]
        lines.append(self.comment or self.name or self.molecular_formula)
        
        for atom in self.atoms:
            lines.append(atom.to_xyz_line(precision))
        
        return "\n".join(lines)
    
    def to_psi4_string(self, precision: int = 10) -> str:
        """Convert to Psi4 molecule specification string."""
        lines = []
        
        # Charge and multiplicity
        lines.append(f"{self.charge} {self.multiplicity}")
        
        # Units
        lines.append(f"units {self.units}")
        
        # Options
        if self.no_reorient:
            lines.append("noreorient")
        if self.no_com:
            lines.append("nocom")
        if self.fix_orientation:
            lines.append("fix_orientation")
        if self.symmetry:
            lines.append(f"symmetry {self.symmetry}")
        
        # Atoms with fragment separators
        current_fragment = -1
        for atom in self.atoms:
            if atom.fragment_id != current_fragment:
                if current_fragment >= 0:
                    lines.append("--")
                current_fragment = atom.fragment_id
            
            lines.append(atom.to_xyz_line(precision))
        
        return "\n".join(lines)
    
    def to_qcschema(self) -> dict[str, Any]:
        """Convert to QCSchema Molecule format."""
        symbols = []
        geometry = []  # Flat list of coordinates in Bohr
        masses = []
        
        # Conversion factor
        from psi4_mcp.utils.helpers.constants import ANGSTROM_TO_BOHR
        factor = ANGSTROM_TO_BOHR if self.units == "angstrom" else 1.0
        
        for atom in self.atoms:
            if atom.is_ghost:
                continue  # QCSchema doesn't support ghost atoms directly
            symbols.append(atom.symbol)
            geometry.extend([
                atom.x * factor,
                atom.y * factor,
                atom.z * factor
            ])
            masses.append(atom.mass or get_atomic_mass(atom.symbol))
        
        return {
            "schema_name": "qcschema_molecule",
            "schema_version": 2,
            "symbols": symbols,
            "geometry": geometry,
            "masses": masses,
            "molecular_charge": self.charge,
            "molecular_multiplicity": self.multiplicity,
            "name": self.name or self.molecular_formula,
        }
    
    @classmethod
    def from_xyz_string(cls, xyz_string: str, charge: int = 0, multiplicity: int = 1) -> "Molecule":
        """Create Molecule from XYZ format string."""
        lines = xyz_string.strip().split("\n")
        
        # Skip header lines (count and comment)
        start_idx = 0
        if lines and lines[0].strip().isdigit():
            start_idx = 2
        elif len(lines) > 1 and lines[1].strip().isdigit():
            start_idx = 3
        
        comment = lines[1].strip() if len(lines) > 1 and start_idx >= 2 else None
        
        atoms = []
        for line in lines[start_idx:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 4:
                continue
            
            symbol = parts[0]
            is_ghost = False
            if symbol.startswith("@"):
                is_ghost = True
                symbol = symbol[1:]
            elif symbol.lower().startswith("gh("):
                is_ghost = True
                symbol = symbol[3:-1] if symbol.endswith(")") else symbol[3:]
            
            x = float(parts[1].replace('D', 'E').replace('d', 'e'))
            y = float(parts[2].replace('D', 'E').replace('d', 'e'))
            z = float(parts[3].replace('D', 'E').replace('d', 'e'))
            
            atoms.append(AtomicPosition(
                symbol=symbol,
                x=x,
                y=y,
                z=z,
                is_ghost=is_ghost,
            ))
        
        return cls(
            atoms=atoms,
            charge=charge,
            multiplicity=multiplicity,
            comment=comment,
            units="angstrom",
        )
    
    @classmethod
    def from_psi4_string(cls, psi4_string: str) -> "Molecule":
        """Create Molecule from Psi4 molecule specification string."""
        lines = psi4_string.strip().split("\n")
        
        atoms = []
        charge = 0
        multiplicity = 1
        units: Literal["angstrom", "bohr"] = "angstrom"
        symmetry = None
        no_reorient = False
        no_com = False
        fix_orientation = False
        current_fragment = 0
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith("#") or line.startswith("!"):
                continue
            
            if line == "--":
                current_fragment += 1
                continue
            
            lower_line = line.lower()
            
            # Parse options
            if "=" in lower_line or lower_line in ("noreorient", "nocom", "fix_orientation"):
                if "units" in lower_line:
                    if "bohr" in lower_line or "au" in lower_line:
                        units = "bohr"
                    else:
                        units = "angstrom"
                elif "symmetry" in lower_line:
                    parts = line.split()
                    if len(parts) > 1:
                        symmetry = parts[1]
                elif lower_line == "noreorient":
                    no_reorient = True
                elif lower_line == "nocom":
                    no_com = True
                elif lower_line == "fix_orientation":
                    fix_orientation = True
                continue
            
            parts = line.split()
            
            # Check for charge/multiplicity
            if len(parts) == 2:
                if parts[0].lstrip('-').isdigit() and parts[1].isdigit():
                    charge = int(parts[0])
                    multiplicity = int(parts[1])
                    continue
            
            # Parse atom line
            if len(parts) >= 4:
                symbol = parts[0]
                is_ghost = False
                if symbol.startswith("@"):
                    is_ghost = True
                    symbol = symbol[1:]
                elif symbol.lower().startswith("gh("):
                    is_ghost = True
                    symbol = symbol[3:-1] if symbol.endswith(")") else symbol[3:]
                
                x = float(parts[1].replace('D', 'E').replace('d', 'e'))
                y = float(parts[2].replace('D', 'E').replace('d', 'e'))
                z = float(parts[3].replace('D', 'E').replace('d', 'e'))
                
                atoms.append(AtomicPosition(
                    symbol=symbol,
                    x=x,
                    y=y,
                    z=z,
                    is_ghost=is_ghost,
                    fragment_id=current_fragment,
                ))
        
        return cls(
            atoms=atoms,
            charge=charge,
            multiplicity=multiplicity,
            units=units,
            symmetry=symmetry,
            no_reorient=no_reorient,
            no_com=no_com,
            fix_orientation=fix_orientation,
        )
    
    @classmethod
    def from_qcschema(cls, qcschema: dict[str, Any]) -> "Molecule":
        """Create Molecule from QCSchema Molecule dictionary."""
        from psi4_mcp.utils.helpers.constants import BOHR_TO_ANGSTROM
        
        symbols = qcschema.get("symbols", [])
        geometry = qcschema.get("geometry", [])  # Flat list in Bohr
        masses = qcschema.get("masses", [])
        charge = qcschema.get("molecular_charge", 0)
        multiplicity = qcschema.get("molecular_multiplicity", 1)
        name = qcschema.get("name")
        
        atoms = []
        for i, symbol in enumerate(symbols):
            x = geometry[3*i] * BOHR_TO_ANGSTROM
            y = geometry[3*i + 1] * BOHR_TO_ANGSTROM
            z = geometry[3*i + 2] * BOHR_TO_ANGSTROM
            mass = masses[i] if i < len(masses) else None
            
            atoms.append(AtomicPosition(
                symbol=symbol,
                x=x,
                y=y,
                z=z,
                mass=mass,
            ))
        
        return cls(
            atoms=atoms,
            charge=charge,
            multiplicity=multiplicity,
            name=name,
            units="angstrom",
        )
    
    # ==========================================================================
    # VALIDATION
    # ==========================================================================
    
    @model_validator(mode="after")
    def validate_molecule(self) -> "Molecule":
        """Validate molecule consistency."""
        n_elec = self.n_electrons
        mult = self.multiplicity
        n_unpaired = mult - 1
        
        # Check parity
        if (n_unpaired % 2) != (n_elec % 2):
            raise ValueError(
                f"Multiplicity {mult} is incompatible with {n_elec} electrons "
                f"(parity mismatch)"
            )
        
        # Check enough electrons
        if n_unpaired > n_elec:
            raise ValueError(
                f"Multiplicity {mult} requires {n_unpaired} unpaired electrons "
                f"but molecule only has {n_elec} electrons"
            )
        
        return self


# =============================================================================
# MOLECULAR SYSTEM
# =============================================================================

class MolecularSystem(Psi4BaseModel):
    """
    A system containing multiple molecules or fragments.
    
    Useful for interaction energy calculations, SAPT, etc.
    
    Attributes:
        molecules: List of molecules in the system.
        name: System name.
        description: System description.
    """
    
    molecules: list[Molecule] = Field(..., min_length=1, description="Molecules")
    name: Optional[str] = Field(default=None, description="System name")
    description: Optional[str] = Field(default=None, description="Description")
    
    @property
    def n_molecules(self) -> int:
        """Number of molecules."""
        return len(self.molecules)
    
    @property
    def n_total_atoms(self) -> int:
        """Total number of atoms across all molecules."""
        return sum(mol.n_atoms for mol in self.molecules)
    
    @property
    def n_total_electrons(self) -> int:
        """Total number of electrons across all molecules."""
        return sum(mol.n_electrons for mol in self.molecules)
    
    @property
    def total_charge(self) -> int:
        """Total system charge."""
        return sum(mol.charge for mol in self.molecules)
    
    def to_combined_molecule(self, overall_multiplicity: Optional[int] = None) -> Molecule:
        """
        Combine all molecules into a single Molecule with fragments.
        
        Args:
            overall_multiplicity: Multiplicity for combined system.
                If None, uses sum of (mult-1) + 1.
        
        Returns:
            Combined Molecule with fragment information.
        """
        all_atoms = []
        fragment_defs = []
        current_idx = 0
        
        for frag_id, mol in enumerate(self.molecules):
            frag_indices = []
            for atom in mol.atoms:
                new_atom = AtomicPosition(
                    symbol=atom.symbol,
                    atomic_number=atom.atomic_number,
                    x=atom.x,
                    y=atom.y,
                    z=atom.z,
                    mass=atom.mass,
                    label=atom.label,
                    is_ghost=atom.is_ghost,
                    fragment_id=frag_id,
                    basis_set=atom.basis_set,
                )
                all_atoms.append(new_atom)
                frag_indices.append(current_idx)
                current_idx += 1
            fragment_defs.append(frag_indices)
        
        total_charge = self.total_charge
        
        if overall_multiplicity is None:
            # Estimate: sum of unpaired electrons + 1
            total_unpaired = sum(mol.multiplicity - 1 for mol in self.molecules)
            overall_multiplicity = total_unpaired + 1
        
        # Ensure units are consistent (use first molecule's units)
        units = self.molecules[0].units
        
        return Molecule(
            atoms=all_atoms,
            charge=total_charge,
            multiplicity=overall_multiplicity,
            units=units,
            name=self.name,
            fragments=fragment_defs,
        )


# Backward compatibility aliases
MoleculeInput = Molecule
MoleculeSpec = Molecule
AtomSpec = AtomicPosition
