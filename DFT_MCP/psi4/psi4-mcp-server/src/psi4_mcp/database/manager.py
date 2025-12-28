"""
Database Manager for Psi4 MCP Server.

Manages database connections and operations using JSON file storage.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from psi4_mcp.database.schema import (
    Base,
    Molecule,
    Calculation,
    Result,
    BasisSetRecord,
    CalculationType,
    CalculationStatus,
)

T = TypeVar("T", bound=Base)


class DatabaseManager:
    """Manages database operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager."""
        if db_path is None:
            db_path = os.path.expanduser("~/.psi4_mcp/database")
        
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize collection files
        self._collections = {
            "molecules": self.db_path / "molecules.json",
            "calculations": self.db_path / "calculations.json",
            "results": self.db_path / "results.json",
            "basis_sets": self.db_path / "basis_sets.json",
        }
        
        # Initialize empty collections if they don't exist
        for name, path in self._collections.items():
            if not path.exists():
                self._write_collection(name, [])
    
    def _read_collection(self, name: str) -> List[Dict[str, Any]]:
        """Read a collection from file."""
        path = self._collections[name]
        if not path.exists():
            return []
        
        with open(path, "r") as f:
            return json.load(f)
    
    def _write_collection(self, name: str, data: List[Dict[str, Any]]) -> None:
        """Write a collection to file."""
        path = self._collections[name]
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    # Molecule operations
    def add_molecule(self, molecule: Molecule) -> str:
        """Add a molecule to the database."""
        molecules = self._read_collection("molecules")
        
        # Check for duplicate
        for m in molecules:
            if m["id"] == molecule.id:
                # Update existing
                m.update(molecule.to_dict())
                self._write_collection("molecules", molecules)
                return molecule.id
        
        molecules.append(molecule.to_dict())
        self._write_collection("molecules", molecules)
        return molecule.id
    
    def get_molecule(self, molecule_id: str) -> Optional[Molecule]:
        """Get a molecule by ID."""
        molecules = self._read_collection("molecules")
        
        for m in molecules:
            if m["id"] == molecule_id:
                return Molecule.from_dict(m)
        
        return None
    
    def get_molecule_by_name(self, name: str) -> Optional[Molecule]:
        """Get a molecule by name."""
        molecules = self._read_collection("molecules")
        
        for m in molecules:
            if m["name"] == name:
                return Molecule.from_dict(m)
        
        return None
    
    def search_molecules(
        self,
        formula: Optional[str] = None,
        name_contains: Optional[str] = None,
    ) -> List[Molecule]:
        """Search molecules."""
        molecules = self._read_collection("molecules")
        results = []
        
        for m in molecules:
            if formula and m["formula"] != formula:
                continue
            if name_contains and name_contains.lower() not in m["name"].lower():
                continue
            results.append(Molecule.from_dict(m))
        
        return results
    
    def delete_molecule(self, molecule_id: str) -> bool:
        """Delete a molecule."""
        molecules = self._read_collection("molecules")
        original_len = len(molecules)
        
        molecules = [m for m in molecules if m["id"] != molecule_id]
        
        if len(molecules) < original_len:
            self._write_collection("molecules", molecules)
            return True
        
        return False
    
    # Calculation operations
    def add_calculation(self, calculation: Calculation) -> str:
        """Add a calculation to the database."""
        calculations = self._read_collection("calculations")
        calculations.append(calculation.to_dict())
        self._write_collection("calculations", calculations)
        return calculation.id
    
    def get_calculation(self, calculation_id: str) -> Optional[Calculation]:
        """Get a calculation by ID."""
        calculations = self._read_collection("calculations")
        
        for c in calculations:
            if c["id"] == calculation_id:
                return Calculation.from_dict(c)
        
        return None
    
    def get_calculations_for_molecule(
        self,
        molecule_id: str,
        calculation_type: Optional[CalculationType] = None,
    ) -> List[Calculation]:
        """Get calculations for a molecule."""
        calculations = self._read_collection("calculations")
        results = []
        
        for c in calculations:
            if c["molecule_id"] != molecule_id:
                continue
            if calculation_type and c["calculation_type"] != calculation_type.value:
                continue
            results.append(Calculation.from_dict(c))
        
        return results
    
    def update_calculation(self, calculation: Calculation) -> bool:
        """Update a calculation."""
        calculations = self._read_collection("calculations")
        
        for i, c in enumerate(calculations):
            if c["id"] == calculation.id:
                calculations[i] = calculation.to_dict()
                self._write_collection("calculations", calculations)
                return True
        
        return False
    
    def get_pending_calculations(self) -> List[Calculation]:
        """Get all pending calculations."""
        calculations = self._read_collection("calculations")
        return [
            Calculation.from_dict(c) for c in calculations
            if c["status"] == CalculationStatus.PENDING.value
        ]
    
    # Result operations
    def add_result(self, result: Result) -> str:
        """Add a result to the database."""
        results = self._read_collection("results")
        results.append(result.to_dict())
        self._write_collection("results", results)
        return result.id
    
    def get_result(self, result_id: str) -> Optional[Result]:
        """Get a result by ID."""
        results = self._read_collection("results")
        
        for r in results:
            if r["id"] == result_id:
                return Result.from_dict(r)
        
        return None
    
    def get_results_for_calculation(self, calculation_id: str) -> List[Result]:
        """Get results for a calculation."""
        results = self._read_collection("results")
        return [
            Result.from_dict(r) for r in results
            if r["calculation_id"] == calculation_id
        ]
    
    def search_results(
        self,
        result_type: Optional[str] = None,
        calculation_id: Optional[str] = None,
    ) -> List[Result]:
        """Search results."""
        results = self._read_collection("results")
        filtered = []
        
        for r in results:
            if result_type and r["result_type"] != result_type:
                continue
            if calculation_id and r["calculation_id"] != calculation_id:
                continue
            filtered.append(Result.from_dict(r))
        
        return filtered
    
    # Basis set operations
    def add_basis_set(self, basis_set: BasisSetRecord) -> str:
        """Add a basis set record."""
        basis_sets = self._read_collection("basis_sets")
        basis_sets.append(basis_set.to_dict())
        self._write_collection("basis_sets", basis_sets)
        return basis_set.id
    
    def get_basis_set(self, name: str) -> Optional[BasisSetRecord]:
        """Get a basis set by name."""
        basis_sets = self._read_collection("basis_sets")
        
        for b in basis_sets:
            if b["name"].lower() == name.lower():
                return BasisSetRecord.from_dict(b)
        
        return None
    
    def list_basis_sets(self) -> List[str]:
        """List all basis set names."""
        basis_sets = self._read_collection("basis_sets")
        return [b["name"] for b in basis_sets]
    
    # Utility methods
    def clear_all(self) -> None:
        """Clear all data (use with caution!)."""
        for name in self._collections:
            self._write_collection(name, [])
    
    def export_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export all data as a dictionary."""
        return {
            name: self._read_collection(name)
            for name in self._collections
        }
    
    def import_all(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Import data from a dictionary."""
        for name, records in data.items():
            if name in self._collections:
                self._write_collection(name, records)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get database statistics."""
        return {
            name: len(self._read_collection(name))
            for name in self._collections
        }


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager(db_path: Optional[str] = None) -> DatabaseManager:
    """Get the global database manager."""
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    
    return _db_manager


def reset_database_manager() -> None:
    """Reset the global database manager."""
    global _db_manager
    _db_manager = None
