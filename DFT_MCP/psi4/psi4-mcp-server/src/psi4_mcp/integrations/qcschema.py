"""
QCSchema Integration for Psi4 MCP Server.

Provides conversion to/from QCSchema standard format.
QCSchema is the MolSSI standard for quantum chemistry data interchange.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
import json


@dataclass
class QCMolecule:
    """QCSchema molecule specification."""
    symbols: List[str]
    geometry: List[float]  # Flat list in Bohr
    molecular_charge: int = 0
    molecular_multiplicity: int = 1
    masses: Optional[List[float]] = None
    name: str = ""
    identifiers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = {
            "schema_name": "qcschema_molecule",
            "schema_version": 2,
            "symbols": self.symbols,
            "geometry": self.geometry,
            "molecular_charge": self.molecular_charge,
            "molecular_multiplicity": self.molecular_multiplicity,
        }
        if self.masses:
            d["masses"] = self.masses
        if self.name:
            d["name"] = self.name
        if self.identifiers:
            d["identifiers"] = self.identifiers
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QCMolecule":
        """Create from dictionary."""
        return cls(
            symbols=data["symbols"],
            geometry=data["geometry"],
            molecular_charge=data.get("molecular_charge", 0),
            molecular_multiplicity=data.get("molecular_multiplicity", 1),
            masses=data.get("masses"),
            name=data.get("name", ""),
            identifiers=data.get("identifiers", {}),
        )


@dataclass
class QCInput:
    """QCSchema input specification."""
    molecule: QCMolecule
    driver: str  # energy, gradient, hessian, properties
    model: Dict[str, str]  # method, basis
    keywords: Dict[str, Any] = field(default_factory=dict)
    protocols: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "schema_name": "qcschema_input",
            "schema_version": 1,
            "molecule": self.molecule.to_dict(),
            "driver": self.driver,
            "model": self.model,
            "keywords": self.keywords,
            "protocols": self.protocols,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QCInput":
        """Create from dictionary."""
        return cls(
            molecule=QCMolecule.from_dict(data["molecule"]),
            driver=data["driver"],
            model=data["model"],
            keywords=data.get("keywords", {}),
            protocols=data.get("protocols", {}),
        )


@dataclass
class QCResult:
    """QCSchema result specification."""
    input_data: QCInput
    success: bool
    return_result: Union[float, List[float], List[List[float]]]
    properties: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, str]] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = {
            "schema_name": "qcschema_output",
            "schema_version": 1,
            "input_data": self.input_data.to_dict(),
            "success": self.success,
            "return_result": self.return_result,
            "properties": self.properties,
            "provenance": self.provenance,
        }
        if self.error:
            d["error"] = self.error
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QCResult":
        """Create from dictionary."""
        return cls(
            input_data=QCInput.from_dict(data["input_data"]),
            success=data["success"],
            return_result=data["return_result"],
            properties=data.get("properties", {}),
            error=data.get("error"),
            provenance=data.get("provenance", {}),
        )


class QCSchemaInterface:
    """Interface for QCSchema conversion."""
    
    BOHR_TO_ANGSTROM = 0.529177210903
    ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM
    
    def geometry_to_qcschema(
        self,
        geometry: str,
        charge: int = 0,
        multiplicity: int = 1,
    ) -> QCMolecule:
        """
        Convert Psi4 geometry string to QCSchema molecule.
        
        Args:
            geometry: Psi4-format geometry (Angstrom)
            charge: Molecular charge
            multiplicity: Spin multiplicity
            
        Returns:
            QCMolecule object
        """
        symbols = []
        coords_bohr = []
        
        lines = geometry.strip().split("\n")
        
        # Skip charge/multiplicity line if present
        start_idx = 0
        first_parts = lines[0].split()
        if len(first_parts) == 2:
            try:
                int(first_parts[0])
                int(first_parts[1])
                start_idx = 1
            except ValueError:
                pass
        
        for line in lines[start_idx:]:
            parts = line.split()
            if len(parts) >= 4:
                symbols.append(parts[0])
                x = float(parts[1]) * self.ANGSTROM_TO_BOHR
                y = float(parts[2]) * self.ANGSTROM_TO_BOHR
                z = float(parts[3]) * self.ANGSTROM_TO_BOHR
                coords_bohr.extend([x, y, z])
        
        return QCMolecule(
            symbols=symbols,
            geometry=coords_bohr,
            molecular_charge=charge,
            molecular_multiplicity=multiplicity,
        )
    
    def qcschema_to_geometry(self, molecule: QCMolecule) -> str:
        """
        Convert QCSchema molecule to Psi4 geometry string.
        
        Args:
            molecule: QCMolecule object
            
        Returns:
            Psi4-format geometry (Angstrom)
        """
        lines = [f"{molecule.molecular_charge} {molecule.molecular_multiplicity}"]
        
        for i, symbol in enumerate(molecule.symbols):
            x = molecule.geometry[i * 3] * self.BOHR_TO_ANGSTROM
            y = molecule.geometry[i * 3 + 1] * self.BOHR_TO_ANGSTROM
            z = molecule.geometry[i * 3 + 2] * self.BOHR_TO_ANGSTROM
            lines.append(f"{symbol:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        
        return "\n".join(lines)
    
    def create_input(
        self,
        geometry: str,
        method: str,
        basis: str,
        driver: str = "energy",
        charge: int = 0,
        multiplicity: int = 1,
        keywords: Optional[Dict[str, Any]] = None,
    ) -> QCInput:
        """
        Create QCSchema input from Psi4 parameters.
        
        Args:
            geometry: Psi4-format geometry
            method: Computational method
            basis: Basis set
            driver: Calculation type (energy, gradient, hessian)
            charge: Molecular charge
            multiplicity: Spin multiplicity
            keywords: Additional keywords
            
        Returns:
            QCInput object
        """
        molecule = self.geometry_to_qcschema(geometry, charge, multiplicity)
        
        return QCInput(
            molecule=molecule,
            driver=driver,
            model={"method": method, "basis": basis},
            keywords=keywords or {},
        )
    
    def create_result(
        self,
        input_data: QCInput,
        energy: float,
        success: bool = True,
        properties: Optional[Dict[str, Any]] = None,
        gradient: Optional[List[float]] = None,
        hessian: Optional[List[List[float]]] = None,
    ) -> QCResult:
        """
        Create QCSchema result.
        
        Args:
            input_data: Original input
            energy: Computed energy (Hartree)
            success: Whether calculation succeeded
            properties: Additional properties
            gradient: Energy gradient (if computed)
            hessian: Energy Hessian (if computed)
            
        Returns:
            QCResult object
        """
        if input_data.driver == "gradient" and gradient is not None:
            return_result = gradient
        elif input_data.driver == "hessian" and hessian is not None:
            return_result = hessian
        else:
            return_result = energy
        
        props = properties or {}
        props["return_energy"] = energy
        
        return QCResult(
            input_data=input_data,
            success=success,
            return_result=return_result,
            properties=props,
            provenance={
                "creator": "psi4-mcp-server",
                "version": "1.0.0",
            },
        )
    
    def to_json(self, obj: Union[QCMolecule, QCInput, QCResult]) -> str:
        """Convert QCSchema object to JSON string."""
        return json.dumps(obj.to_dict(), indent=2)
    
    def from_json(self, json_str: str) -> Union[QCMolecule, QCInput, QCResult]:
        """Parse QCSchema object from JSON string."""
        data = json.loads(json_str)
        
        schema_name = data.get("schema_name", "")
        
        if schema_name == "qcschema_molecule":
            return QCMolecule.from_dict(data)
        elif schema_name == "qcschema_input":
            return QCInput.from_dict(data)
        elif schema_name == "qcschema_output":
            return QCResult.from_dict(data)
        
        raise ValueError(f"Unknown schema: {schema_name}")


# Global interface instance
_qcschema_interface: Optional[QCSchemaInterface] = None


def get_qcschema_interface() -> QCSchemaInterface:
    """Get the global QCSchema interface."""
    global _qcschema_interface
    if _qcschema_interface is None:
        _qcschema_interface = QCSchemaInterface()
    return _qcschema_interface


def to_qcschema(
    geometry: str,
    method: str,
    basis: str,
    driver: str = "energy",
    charge: int = 0,
    multiplicity: int = 1,
) -> Dict[str, Any]:
    """Convert Psi4 input to QCSchema format."""
    interface = get_qcschema_interface()
    qc_input = interface.create_input(geometry, method, basis, driver, charge, multiplicity)
    return qc_input.to_dict()


def from_qcschema(qcschema_input: Dict[str, Any]) -> Dict[str, Any]:
    """Convert QCSchema input to Psi4 format."""
    interface = get_qcschema_interface()
    
    qc_input = QCInput.from_dict(qcschema_input)
    geometry = interface.qcschema_to_geometry(qc_input.molecule)
    
    return {
        "geometry": geometry,
        "method": qc_input.model["method"],
        "basis": qc_input.model["basis"],
        "charge": qc_input.molecule.molecular_charge,
        "multiplicity": qc_input.molecule.molecular_multiplicity,
        "keywords": qc_input.keywords,
    }
