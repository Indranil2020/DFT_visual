"""
Database Schema for Psi4 MCP Server.

Defines the data models for persistent storage using dataclasses.
This is a lightweight implementation that doesn't require SQLAlchemy.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json
import hashlib


class CalculationType(str, Enum):
    """Types of calculations."""
    ENERGY = "energy"
    OPTIMIZATION = "optimization"
    FREQUENCY = "frequency"
    PROPERTY = "property"
    TDDFT = "tddft"
    SAPT = "sapt"
    COUPLED_CLUSTER = "coupled_cluster"


class CalculationStatus(str, Enum):
    """Calculation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Base class marker for ORM-like behavior
class Base:
    """Base class for all database models."""
    pass


@dataclass
class Molecule(Base):
    """Molecule record in database."""
    id: str
    name: str
    formula: str
    geometry: str
    charge: int = 0
    multiplicity: int = 1
    smiles: str = ""
    inchi: str = ""
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_geometry(
        cls,
        geometry: str,
        name: str = "",
        charge: int = 0,
        multiplicity: int = 1,
    ) -> "Molecule":
        """Create molecule from geometry string."""
        # Generate ID from geometry hash
        geom_hash = hashlib.md5(geometry.encode()).hexdigest()[:12]
        mol_id = f"mol_{geom_hash}"
        
        # Extract formula
        formula = cls._extract_formula(geometry)
        
        return cls(
            id=mol_id,
            name=name or formula,
            formula=formula,
            geometry=geometry,
            charge=charge,
            multiplicity=multiplicity,
        )
    
    @staticmethod
    def _extract_formula(geometry: str) -> str:
        """Extract molecular formula from geometry."""
        elements: Dict[str, int] = {}
        
        for line in geometry.strip().split("\n"):
            parts = line.split()
            if len(parts) >= 4:
                elem = parts[0]
                elements[elem] = elements.get(elem, 0) + 1
        
        # Format formula (C first, then H, then alphabetical)
        formula_parts = []
        
        if "C" in elements:
            count = elements.pop("C")
            formula_parts.append(f"C{count}" if count > 1 else "C")
        
        if "H" in elements:
            count = elements.pop("H")
            formula_parts.append(f"H{count}" if count > 1 else "H")
        
        for elem in sorted(elements.keys()):
            count = elements[elem]
            formula_parts.append(f"{elem}{count}" if count > 1 else elem)
        
        return "".join(formula_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "formula": self.formula,
            "geometry": self.geometry,
            "charge": self.charge,
            "multiplicity": self.multiplicity,
            "smiles": self.smiles,
            "inchi": self.inchi,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Molecule":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            formula=data["formula"],
            geometry=data["geometry"],
            charge=data.get("charge", 0),
            multiplicity=data.get("multiplicity", 1),
            smiles=data.get("smiles", ""),
            inchi=data.get("inchi", ""),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.utcnow(),
        )


@dataclass
class Calculation(Base):
    """Calculation record in database."""
    id: str
    molecule_id: str
    calculation_type: CalculationType
    method: str
    basis: str
    status: CalculationStatus = CalculationStatus.PENDING
    options: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        molecule_id: str,
        calculation_type: CalculationType,
        method: str,
        basis: str,
        options: Optional[Dict[str, Any]] = None,
    ) -> "Calculation":
        """Create a new calculation record."""
        calc_hash = hashlib.md5(
            f"{molecule_id}_{calculation_type}_{method}_{basis}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return cls(
            id=f"calc_{calc_hash}",
            molecule_id=molecule_id,
            calculation_type=calculation_type,
            method=method,
            basis=basis,
            options=options or {},
        )
    
    def start(self) -> None:
        """Mark calculation as started."""
        self.status = CalculationStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark calculation as completed."""
        self.status = CalculationStatus.COMPLETED
        self.completed_at = datetime.utcnow()
    
    def fail(self, error_message: str) -> None:
        """Mark calculation as failed."""
        self.status = CalculationStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "molecule_id": self.molecule_id,
            "calculation_type": self.calculation_type.value,
            "method": self.method,
            "basis": self.basis,
            "status": self.status.value,
            "options": self.options,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Calculation":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            molecule_id=data["molecule_id"],
            calculation_type=CalculationType(data["calculation_type"]),
            method=data["method"],
            basis=data["basis"],
            status=CalculationStatus(data["status"]),
            options=data.get("options", {}),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            error_message=data.get("error_message", ""),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
        )


@dataclass
class Result(Base):
    """Calculation result record in database."""
    id: str
    calculation_id: str
    result_type: str
    value: Any
    unit: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def create(
        cls,
        calculation_id: str,
        result_type: str,
        value: Any,
        unit: str = "",
    ) -> "Result":
        """Create a new result record."""
        result_hash = hashlib.md5(
            f"{calculation_id}_{result_type}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return cls(
            id=f"result_{result_hash}",
            calculation_id=calculation_id,
            result_type=result_type,
            value=value,
            unit=unit,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "calculation_id": self.calculation_id,
            "result_type": self.result_type,
            "value": self.value,
            "unit": self.unit,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Result":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            calculation_id=data["calculation_id"],
            result_type=data["result_type"],
            value=data["value"],
            unit=data.get("unit", ""),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
        )


@dataclass
class BasisSetRecord(Base):
    """Basis set record in database."""
    id: str
    name: str
    description: str = ""
    elements: List[str] = field(default_factory=list)
    family: str = ""
    reference: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "elements": self.elements,
            "family": self.family,
            "reference": self.reference,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BasisSetRecord":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            elements=data.get("elements", []),
            family=data.get("family", ""),
            reference=data.get("reference", ""),
            data=data.get("data", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
        )
