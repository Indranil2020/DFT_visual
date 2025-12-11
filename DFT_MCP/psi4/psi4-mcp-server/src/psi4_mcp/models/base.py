"""
Base Pydantic Models for Psi4 MCP Server.

This module provides the foundation Pydantic models used throughout the
Psi4 MCP server. These base classes define common fields, validators,
and serialization behavior.

Key Base Classes:
    - Psi4BaseModel: Base for all Psi4 MCP models
    - CalculationInput: Base for calculation input specifications
    - CalculationOutput: Base for calculation results
    - ResourceModel: Base for MCP resource representations
"""

from typing import Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from collections import Counter


# =============================================================================
# BASE MODEL CONFIGURATION
# =============================================================================

class Psi4BaseModel(BaseModel):
    """
    Base model for all Psi4 MCP data structures.
    
    Provides consistent configuration and common functionality across
    all models in the system.
    
    Features:
        - Immutable by default (frozen=False for flexibility)
        - Extra fields forbidden to catch typos
        - Validation on assignment
        - Custom JSON serialization
    """
    
    model_config = ConfigDict(
        extra="ignore",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary, excluding None values."""
        return self.model_dump(exclude_none=True)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert model to JSON string."""
        return self.model_dump_json(indent=indent, exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Psi4BaseModel":
        """Create model from dictionary."""
        return cls.model_validate(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Psi4BaseModel":
        """Create model from JSON string."""
        return cls.model_validate_json(json_str)


class StrictModel(Psi4BaseModel):
    """Strict model that forbids extra fields."""
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        populate_by_name=True,
    )


# =============================================================================
# CALCULATION BASE MODELS
# =============================================================================

class CalculationInput(Psi4BaseModel):
    """
    Base model for calculation input specifications.
    
    Attributes:
        method: The quantum chemistry method to use.
        basis: The basis set to use.
        reference: Reference wavefunction type (rhf, uhf, rohf).
        memory: Memory allocation in MB.
        n_threads: Number of CPU threads to use.
        options: Additional Psi4 options as key-value pairs.
    """
    
    method: str = Field(
        default="hf",
        description="Quantum chemistry method (e.g., hf, b3lyp, mp2, ccsd)",
    )
    basis: str = Field(
        default="cc-pvdz",
        description="Basis set name",
    )
    reference: str = Field(
        default="rhf",
        description="Reference wavefunction type (rhf, uhf, rohf)",
    )
    memory: int = Field(
        default=2000,
        ge=100,
        le=1000000,
        description="Memory allocation in MB",
    )
    n_threads: int = Field(
        default=1,
        ge=1,
        le=256,
        description="Number of CPU threads",
    )
    options: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Psi4 options",
    )
    
    @field_validator("method")
    @classmethod
    def normalize_method(cls, v: str) -> str:
        """Normalize method name to lowercase."""
        return v.lower().strip()
    
    @field_validator("basis")
    @classmethod
    def normalize_basis(cls, v: str) -> str:
        """Normalize basis set name to lowercase."""
        return v.lower().strip()
    
    @field_validator("reference")
    @classmethod
    def validate_reference(cls, v: str) -> str:
        """Validate and normalize reference type."""
        normalized = v.lower().strip()
        valid_refs = {"rhf", "uhf", "rohf", "rks", "uks", "cuhf", "ghf", "gks"}
        if normalized not in valid_refs:
            raise ValueError(f"Invalid reference type: {v}. Must be one of {valid_refs}")
        return normalized


class CalculationOutput(Psi4BaseModel):
    """
    Base model for calculation output/results.
    
    Attributes:
        success: Whether the calculation completed successfully.
        method: The method that was used.
        basis: The basis set that was used.
        energy: The primary energy result (if applicable).
        error_message: Error message if calculation failed.
        wall_time: Wall clock time in seconds.
        cpu_time: CPU time in seconds.
        timestamp: When the calculation completed.
    """
    
    success: bool = Field(
        default=True,
        description="Whether the calculation succeeded",
    )
    method: str = Field(
        default="",
        description="Method used in calculation",
    )
    basis: str = Field(
        default="",
        description="Basis set used in calculation",
    )
    energy: Optional[float] = Field(
        default=None,
        description="Primary energy result in Hartree",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if calculation failed",
    )
    wall_time: Optional[float] = Field(
        default=None,
        ge=0,
        description="Wall clock time in seconds",
    )
    cpu_time: Optional[float] = Field(
        default=None,
        ge=0,
        description="CPU time in seconds",
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Calculation completion timestamp",
    )
    
    @model_validator(mode="after")
    def validate_output(self) -> "CalculationOutput":
        """Validate output consistency."""
        if not self.success and self.error_message is None:
            object.__setattr__(self, 'error_message', "Calculation failed")
        return self


# =============================================================================
# RESOURCE BASE MODELS
# =============================================================================

class ResourceModel(Psi4BaseModel):
    """
    Base model for MCP resource representations.
    
    Attributes:
        uri: Unique resource identifier.
        name: Human-readable name.
        description: Detailed description.
        mime_type: MIME type of the resource content.
    """
    
    uri: str = Field(..., description="Unique resource identifier")
    name: str = Field(..., description="Human-readable resource name")
    description: str = Field(default="", description="Detailed description")
    mime_type: str = Field(default="application/json", description="MIME type")


class ToolInput(Psi4BaseModel):
    """Base model for MCP tool inputs."""
    pass


class ToolOutput(Psi4BaseModel):
    """
    Base model for MCP tool outputs.
    
    Attributes:
        success: Whether the tool execution succeeded.
        message: Human-readable result message.
        data: The actual result data.
        error: Error information if failed.
    """
    
    success: bool = Field(default=True, description="Whether execution succeeded")
    message: str = Field(default="", description="Human-readable result message")
    data: Optional[dict[str, Any]] = Field(default=None, description="Result data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


# =============================================================================
# COORDINATE AND GEOMETRY TYPES
# =============================================================================

class Coordinate3D(Psi4BaseModel):
    """A 3D coordinate point."""
    
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    
    def to_tuple(self) -> tuple[float, float, float]:
        """Convert to tuple."""
        return (self.x, self.y, self.z)
    
    def to_list(self) -> list[float]:
        """Convert to list."""
        return [self.x, self.y, self.z]


class AtomSpec(Psi4BaseModel):
    """
    Specification for a single atom.
    
    Attributes:
        symbol: Element symbol (e.g., 'H', 'C', 'Fe').
        x: X coordinate.
        y: Y coordinate.
        z: Z coordinate.
        mass: Optional custom mass in AMU.
        charge: Optional partial charge.
        label: Optional atom label.
        ghost: Whether this is a ghost atom (Bq).
    """
    
    symbol: str = Field(..., min_length=1, max_length=3, description="Element symbol")
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    mass: Optional[float] = Field(default=None, gt=0, description="Custom mass in AMU")
    charge: Optional[float] = Field(default=None, description="Partial charge")
    label: Optional[str] = Field(default=None, description="Atom label")
    ghost: bool = Field(default=False, description="Ghost atom flag")
    
    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, v: str) -> str:
        """Normalize element symbol."""
        v = v.strip()
        if len(v) == 1:
            return v.upper()
        return v[0].upper() + v[1:].lower()


class MoleculeSpec(Psi4BaseModel):
    """
    Complete molecule specification.
    
    Attributes:
        atoms: List of atom specifications.
        charge: Total molecular charge.
        multiplicity: Spin multiplicity (2S+1).
        units: Coordinate units ('angstrom' or 'bohr').
        name: Optional molecule name.
        symmetry: Point group symmetry.
        no_reorient: Disable geometry reorientation.
        no_com: Disable center of mass translation.
    """
    
    atoms: list[AtomSpec] = Field(..., min_length=1, description="List of atoms")
    charge: int = Field(default=0, description="Total molecular charge")
    multiplicity: int = Field(default=1, ge=1, description="Spin multiplicity (2S+1)")
    units: Literal["angstrom", "bohr"] = Field(default="angstrom", description="Coordinate units")
    name: Optional[str] = Field(default=None, description="Molecule name")
    symmetry: Optional[str] = Field(default=None, description="Point group symmetry")
    no_reorient: bool = Field(default=True, description="Disable geometry reorientation")
    no_com: bool = Field(default=True, description="Disable center of mass translation")
    
    @property
    def n_atoms(self) -> int:
        """Number of atoms."""
        return len(self.atoms)
    
    @property
    def n_electrons(self) -> int:
        """Estimated number of electrons based on nuclear charges."""
        from psi4_mcp.utils.helpers.constants import get_atomic_number
        total_z = sum(
            get_atomic_number(atom.symbol) 
            for atom in self.atoms 
            if not atom.ghost
        )
        return total_z - self.charge
    
    @property
    def molecular_formula(self) -> str:
        """Generate molecular formula in Hill notation."""
        counts = Counter(atom.symbol for atom in self.atoms if not atom.ghost)
        
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
    
    def to_xyz_string(self) -> str:
        """Convert to XYZ format string."""
        lines = [str(self.n_atoms), self.name or self.molecular_formula]
        for atom in self.atoms:
            prefix = "@" if atom.ghost else ""
            lines.append(f"{prefix}{atom.symbol}  {atom.x:16.10f}  {atom.y:16.10f}  {atom.z:16.10f}")
        return "\n".join(lines)
    
    def to_psi4_string(self) -> str:
        """Convert to Psi4 molecule string."""
        lines = [f"{self.charge} {self.multiplicity}"]
        
        unit_str = "bohr" if self.units == "bohr" else "angstrom"
        lines.append(f"units {unit_str}")
        
        if self.no_reorient:
            lines.append("noreorient")
        if self.no_com:
            lines.append("nocom")
        if self.symmetry:
            lines.append(f"symmetry {self.symmetry}")
        
        for atom in self.atoms:
            prefix = "@" if atom.ghost else ""
            lines.append(f"{prefix}{atom.symbol}  {atom.x:16.10f}  {atom.y:16.10f}  {atom.z:16.10f}")
        
        return "\n".join(lines)
    
    @model_validator(mode="after")
    def validate_multiplicity(self) -> "MoleculeSpec":
        """Validate that multiplicity is compatible with electron count."""
        n_elec = self.n_electrons
        mult = self.multiplicity
        n_unpaired = mult - 1
        
        if (n_unpaired % 2) != (n_elec % 2):
            raise ValueError(
                f"Multiplicity {mult} is incompatible with {n_elec} electrons "
                f"(parity mismatch)"
            )
        
        if n_unpaired > n_elec:
            raise ValueError(
                f"Multiplicity {mult} requires {n_unpaired} unpaired electrons "
                f"but molecule only has {n_elec} electrons"
            )
        
        return self


# =============================================================================
# ENERGY AND PROPERTY TYPES
# =============================================================================

class EnergyComponents(Psi4BaseModel):
    """
    Breakdown of energy components.
    
    Attributes:
        total: Total energy in Hartree.
        nuclear_repulsion: Nuclear repulsion energy.
        one_electron: One-electron energy.
        two_electron: Two-electron energy.
        exchange_correlation: Exchange-correlation energy (DFT).
        correlation: Correlation energy (post-HF).
        dispersion: Dispersion correction.
        solvation: Solvation energy.
    """
    
    total: float = Field(..., description="Total energy in Hartree")
    nuclear_repulsion: Optional[float] = Field(default=None, description="Nuclear repulsion energy")
    one_electron: Optional[float] = Field(default=None, description="One-electron energy")
    two_electron: Optional[float] = Field(default=None, description="Two-electron energy")
    exchange_correlation: Optional[float] = Field(default=None, description="Exchange-correlation (DFT)")
    correlation: Optional[float] = Field(default=None, description="Correlation energy (post-HF)")
    dispersion: Optional[float] = Field(default=None, description="Dispersion correction")
    solvation: Optional[float] = Field(default=None, description="Solvation energy")


class DipoleMoment(Psi4BaseModel):
    """
    Electric dipole moment.
    
    Attributes:
        x: X component in Debye.
        y: Y component in Debye.
        z: Z component in Debye.
        total: Total magnitude in Debye.
    """
    
    x: float = Field(..., description="X component in Debye")
    y: float = Field(..., description="Y component in Debye")
    z: float = Field(..., description="Z component in Debye")
    total: Optional[float] = Field(default=None, description="Total magnitude in Debye")
    
    @model_validator(mode="after")
    def calculate_total(self) -> "DipoleMoment":
        """Calculate total magnitude if not provided."""
        if self.total is None:
            import math
            total = math.sqrt(self.x**2 + self.y**2 + self.z**2)
            object.__setattr__(self, 'total', total)
        return self


class OrbitalInfo(Psi4BaseModel):
    """
    Information about molecular orbitals.
    
    Attributes:
        n_alpha: Number of alpha electrons.
        n_beta: Number of beta electrons.
        n_basis: Number of basis functions.
        n_molecular: Number of molecular orbitals.
        homo_alpha: HOMO energy for alpha electrons.
        lumo_alpha: LUMO energy for alpha electrons.
        homo_beta: HOMO energy for beta electrons (if unrestricted).
        lumo_beta: LUMO energy for beta electrons (if unrestricted).
        homo_lumo_gap: HOMO-LUMO gap in eV.
    """
    
    n_alpha: int = Field(..., ge=0, description="Number of alpha electrons")
    n_beta: int = Field(..., ge=0, description="Number of beta electrons")
    n_basis: int = Field(..., ge=1, description="Number of basis functions")
    n_molecular: int = Field(..., ge=1, description="Number of molecular orbitals")
    homo_alpha: Optional[float] = Field(default=None, description="Alpha HOMO energy (Hartree)")
    lumo_alpha: Optional[float] = Field(default=None, description="Alpha LUMO energy (Hartree)")
    homo_beta: Optional[float] = Field(default=None, description="Beta HOMO energy (Hartree)")
    lumo_beta: Optional[float] = Field(default=None, description="Beta LUMO energy (Hartree)")
    homo_lumo_gap: Optional[float] = Field(default=None, description="HOMO-LUMO gap in eV")


class ConvergenceInfo(Psi4BaseModel):
    """
    Convergence information for iterative calculations.
    
    Attributes:
        converged: Whether the calculation converged.
        iterations: Number of iterations performed.
        final_energy_change: Final energy change.
        final_density_change: Final density matrix change.
        final_gradient_rms: Final RMS gradient (for geometry opt).
        final_gradient_max: Final maximum gradient (for geometry opt).
    """
    
    converged: bool = Field(..., description="Whether calculation converged")
    iterations: int = Field(..., ge=0, description="Number of iterations")
    final_energy_change: Optional[float] = Field(default=None, description="Final energy change")
    final_density_change: Optional[float] = Field(default=None, description="Final density change")
    final_gradient_rms: Optional[float] = Field(default=None, description="Final RMS gradient")
    final_gradient_max: Optional[float] = Field(default=None, description="Final max gradient")


# =============================================================================
# VERSION AND METADATA
# =============================================================================

class VersionInfo(Psi4BaseModel):
    """
    Version information for software components.
    
    Attributes:
        psi4: Psi4 version string.
        psi4_mcp: Psi4 MCP server version.
        python: Python version.
        numpy: NumPy version (if available).
    """
    
    psi4: Optional[str] = Field(default=None, description="Psi4 version")
    psi4_mcp: str = Field(..., description="Psi4 MCP server version")
    python: Optional[str] = Field(default=None, description="Python version")
    numpy: Optional[str] = Field(default=None, description="NumPy version")


class CalculationMetadataModel(Psi4BaseModel):
    """
    Metadata about a calculation.
    
    Attributes:
        method: Calculation method.
        basis: Basis set.
        reference: Reference wavefunction type.
        n_atoms: Number of atoms.
        n_electrons: Number of electrons.
        charge: Molecular charge.
        multiplicity: Spin multiplicity.
        point_group: Point group symmetry.
        n_basis_functions: Number of basis functions.
        n_molecular_orbitals: Number of molecular orbitals.
        timestamp: Calculation timestamp.
        wall_time: Wall clock time in seconds.
        cpu_time: CPU time in seconds.
        memory_used: Memory used in MB.
        hostname: Machine hostname.
        versions: Version information.
    """
    
    method: str = Field(..., description="Calculation method")
    basis: str = Field(..., description="Basis set")
    reference: str = Field(default="rhf", description="Reference type")
    n_atoms: int = Field(default=0, ge=0, description="Number of atoms")
    n_electrons: int = Field(default=0, ge=0, description="Number of electrons")
    charge: int = Field(default=0, description="Molecular charge")
    multiplicity: int = Field(default=1, ge=1, description="Spin multiplicity")
    point_group: Optional[str] = Field(default=None, description="Point group symmetry")
    n_basis_functions: Optional[int] = Field(default=None, ge=0, description="Basis functions")
    n_molecular_orbitals: Optional[int] = Field(default=None, ge=0, description="MOs")
    timestamp: Optional[datetime] = Field(default=None, description="Timestamp")
    wall_time: Optional[float] = Field(default=None, ge=0, description="Wall time (s)")
    cpu_time: Optional[float] = Field(default=None, ge=0, description="CPU time (s)")
    memory_used: Optional[float] = Field(default=None, ge=0, description="Memory (MB)")
    hostname: Optional[str] = Field(default=None, description="Machine hostname")
    versions: Optional[VersionInfo] = Field(default=None, description="Version info")


# Backward compatibility aliases
BaseInput = CalculationInput
BaseOutput = CalculationOutput
MoleculeInput = MoleculeSpec
