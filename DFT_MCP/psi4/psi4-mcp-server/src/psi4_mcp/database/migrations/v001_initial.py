"""
Initial Database Migration (v001).

Creates the initial database schema.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


MIGRATION_VERSION = "001"
MIGRATION_NAME = "initial"


def get_migration_info() -> Dict[str, Any]:
    """Get migration information."""
    return {
        "version": MIGRATION_VERSION,
        "name": MIGRATION_NAME,
        "description": "Initial database schema creation",
        "created_at": "2024-01-01T00:00:00Z",
    }


def migrate_v001(db_path: str) -> bool:
    """
    Run the initial migration.
    
    Creates the initial database structure:
    - molecules.json
    - calculations.json
    - results.json
    - basis_sets.json
    - migrations.json (tracks applied migrations)
    
    Args:
        db_path: Path to database directory
        
    Returns:
        True if migration successful, False otherwise
    """
    db_dir = Path(db_path)
    
    # Create database directory if needed
    db_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize collection files
    collections = {
        "molecules": [],
        "calculations": [],
        "results": [],
        "basis_sets": [],
    }
    
    for name, initial_data in collections.items():
        file_path = db_dir / f"{name}.json"
        if not file_path.exists():
            with open(file_path, "w") as f:
                json.dump(initial_data, f, indent=2)
    
    # Track migration
    migrations_file = db_dir / "migrations.json"
    
    if migrations_file.exists():
        with open(migrations_file, "r") as f:
            migrations = json.load(f)
    else:
        migrations = {"applied": []}
    
    # Check if already applied
    for m in migrations["applied"]:
        if m["version"] == MIGRATION_VERSION:
            return True  # Already applied
    
    # Record migration
    migrations["applied"].append({
        "version": MIGRATION_VERSION,
        "name": MIGRATION_NAME,
        "applied_at": datetime.utcnow().isoformat(),
    })
    
    with open(migrations_file, "w") as f:
        json.dump(migrations, f, indent=2)
    
    # Seed initial basis sets
    seed_initial_basis_sets(db_dir)
    
    return True


def seed_initial_basis_sets(db_dir: Path) -> None:
    """Seed initial basis set data."""
    basis_sets_file = db_dir / "basis_sets.json"
    
    initial_basis_sets = [
        {
            "id": "basis_sto3g",
            "name": "sto-3g",
            "description": "Minimal basis set (3 Gaussians per STO)",
            "elements": ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"],
            "family": "STO",
            "reference": "Hehre, Stewart, Pople, JCP 1969",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "basis_631g",
            "name": "6-31g",
            "description": "Split-valence double-zeta basis",
            "elements": ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"],
            "family": "Pople",
            "reference": "Ditchfield, Hehre, Pople, JCP 1971",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "basis_631gs",
            "name": "6-31g*",
            "description": "6-31G with polarization on heavy atoms",
            "elements": ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"],
            "family": "Pople",
            "reference": "Hariharan, Pople, Theor. Chim. Acta 1973",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "basis_ccpvdz",
            "name": "cc-pvdz",
            "description": "Correlation-consistent polarized valence double-zeta",
            "elements": ["H", "He", "B", "C", "N", "O", "F", "Ne", "Al", "Si", "P", "S", "Cl", "Ar"],
            "family": "Dunning",
            "reference": "Dunning, JCP 1989",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "basis_ccpvtz",
            "name": "cc-pvtz",
            "description": "Correlation-consistent polarized valence triple-zeta",
            "elements": ["H", "He", "B", "C", "N", "O", "F", "Ne", "Al", "Si", "P", "S", "Cl", "Ar"],
            "family": "Dunning",
            "reference": "Dunning, JCP 1989",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "basis_def2svp",
            "name": "def2-svp",
            "description": "Split-valence polarization basis",
            "elements": ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", 
                        "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
                        "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"],
            "family": "Karlsruhe",
            "reference": "Weigend, Ahlrichs, PCCP 2005",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": "basis_def2tzvp",
            "name": "def2-tzvp",
            "description": "Triple-zeta valence polarization basis",
            "elements": ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
                        "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
                        "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn"],
            "family": "Karlsruhe",
            "reference": "Weigend, Ahlrichs, PCCP 2005",
            "data": {},
            "created_at": datetime.utcnow().isoformat(),
        },
    ]
    
    with open(basis_sets_file, "w") as f:
        json.dump(initial_basis_sets, f, indent=2)


def rollback_v001(db_path: str) -> bool:
    """
    Rollback the initial migration.
    
    Note: This will delete all data!
    
    Args:
        db_path: Path to database directory
        
    Returns:
        True if rollback successful, False otherwise
    """
    db_dir = Path(db_path)
    
    if not db_dir.exists():
        return True
    
    # Remove collection files
    for name in ["molecules", "calculations", "results", "basis_sets"]:
        file_path = db_dir / f"{name}.json"
        if file_path.exists():
            os.remove(file_path)
    
    # Update migrations record
    migrations_file = db_dir / "migrations.json"
    
    if migrations_file.exists():
        with open(migrations_file, "r") as f:
            migrations = json.load(f)
        
        migrations["applied"] = [
            m for m in migrations["applied"]
            if m["version"] != MIGRATION_VERSION
        ]
        
        with open(migrations_file, "w") as f:
            json.dump(migrations, f, indent=2)
    
    return True


def check_migration_status(db_path: str) -> Dict[str, Any]:
    """
    Check migration status.
    
    Returns:
        Migration status information
    """
    db_dir = Path(db_path)
    migrations_file = db_dir / "migrations.json"
    
    if not migrations_file.exists():
        return {
            "applied": False,
            "version": None,
            "needs_migration": True,
        }
    
    with open(migrations_file, "r") as f:
        migrations = json.load(f)
    
    for m in migrations["applied"]:
        if m["version"] == MIGRATION_VERSION:
            return {
                "applied": True,
                "version": MIGRATION_VERSION,
                "applied_at": m.get("applied_at"),
                "needs_migration": False,
            }
    
    return {
        "applied": False,
        "version": None,
        "needs_migration": True,
    }
