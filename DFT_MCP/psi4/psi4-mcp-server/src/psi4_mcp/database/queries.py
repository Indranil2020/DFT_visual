"""
Database Query Helpers for Psi4 MCP Server.

Provides convenient query functions for common database operations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from psi4_mcp.database.manager import get_database_manager
from psi4_mcp.database.schema import (
    Molecule,
    Calculation,
    Result,
    BasisSetRecord,
    CalculationType,
    CalculationStatus,
)


def get_molecule_by_name(name: str) -> Optional[Molecule]:
    """Get a molecule by name."""
    db = get_database_manager()
    return db.get_molecule_by_name(name)


def get_molecule_by_formula(formula: str) -> List[Molecule]:
    """Get all molecules with a given formula."""
    db = get_database_manager()
    return db.search_molecules(formula=formula)


def get_calculations_for_molecule(
    molecule_id: str,
    calculation_type: Optional[str] = None,
) -> List[Calculation]:
    """Get all calculations for a molecule."""
    db = get_database_manager()
    
    calc_type = None
    if calculation_type:
        calc_type = CalculationType(calculation_type)
    
    return db.get_calculations_for_molecule(molecule_id, calc_type)


def search_results(
    result_type: Optional[str] = None,
    molecule_name: Optional[str] = None,
    method: Optional[str] = None,
    basis: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search results with various filters."""
    db = get_database_manager()
    
    # Get base results
    results = db.search_results(result_type=result_type)
    
    # If no additional filters, return as dicts
    if not molecule_name and not method and not basis:
        return [r.to_dict() for r in results]
    
    # Need to filter by calculation properties
    filtered = []
    
    for result in results:
        calculation = db.get_calculation(result.calculation_id)
        if calculation is None:
            continue
        
        if method and calculation.method.lower() != method.lower():
            continue
        if basis and calculation.basis.lower() != basis.lower():
            continue
        
        if molecule_name:
            molecule = db.get_molecule(calculation.molecule_id)
            if molecule is None or molecule_name.lower() not in molecule.name.lower():
                continue
        
        filtered.append({
            "result": result.to_dict(),
            "calculation": calculation.to_dict(),
        })
    
    return filtered


def get_latest_energy(molecule_id: str, method: str, basis: str) -> Optional[float]:
    """Get the latest energy for a molecule/method/basis combination."""
    db = get_database_manager()
    
    calculations = db.get_calculations_for_molecule(
        molecule_id,
        CalculationType.ENERGY,
    )
    
    # Filter by method and basis
    matching = [
        c for c in calculations
        if c.method.lower() == method.lower() and c.basis.lower() == basis.lower()
        and c.status == CalculationStatus.COMPLETED
    ]
    
    if not matching:
        return None
    
    # Get the most recent
    latest = max(matching, key=lambda c: c.completed_at or datetime.min)
    
    # Get energy result
    results = db.get_results_for_calculation(latest.id)
    for result in results:
        if result.result_type == "energy":
            return result.value
    
    return None


def get_optimized_geometry(molecule_id: str, method: str, basis: str) -> Optional[str]:
    """Get the optimized geometry for a molecule."""
    db = get_database_manager()
    
    calculations = db.get_calculations_for_molecule(
        molecule_id,
        CalculationType.OPTIMIZATION,
    )
    
    # Filter by method and basis
    matching = [
        c for c in calculations
        if c.method.lower() == method.lower() and c.basis.lower() == basis.lower()
        and c.status == CalculationStatus.COMPLETED
    ]
    
    if not matching:
        return None
    
    # Get the most recent
    latest = max(matching, key=lambda c: c.completed_at or datetime.min)
    
    # Get geometry result
    results = db.get_results_for_calculation(latest.id)
    for result in results:
        if result.result_type == "optimized_geometry":
            return result.value
    
    return None


def get_frequencies(molecule_id: str, method: str, basis: str) -> Optional[List[float]]:
    """Get vibrational frequencies for a molecule."""
    db = get_database_manager()
    
    calculations = db.get_calculations_for_molecule(
        molecule_id,
        CalculationType.FREQUENCY,
    )
    
    # Filter by method and basis
    matching = [
        c for c in calculations
        if c.method.lower() == method.lower() and c.basis.lower() == basis.lower()
        and c.status == CalculationStatus.COMPLETED
    ]
    
    if not matching:
        return None
    
    # Get the most recent
    latest = max(matching, key=lambda c: c.completed_at or datetime.min)
    
    # Get frequency result
    results = db.get_results_for_calculation(latest.id)
    for result in results:
        if result.result_type == "frequencies":
            return result.value
    
    return None


def find_similar_calculations(
    molecule_id: str,
    calculation_type: CalculationType,
    method: str,
) -> List[Tuple[Calculation, str]]:
    """Find similar calculations with different basis sets."""
    db = get_database_manager()
    
    all_calculations = db.get_calculations_for_molecule(molecule_id, calculation_type)
    
    similar = []
    for calc in all_calculations:
        if calc.method.lower() == method.lower():
            similar.append((calc, calc.basis))
    
    return similar


def get_calculation_history(
    molecule_id: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Get calculation history for a molecule."""
    db = get_database_manager()
    
    molecule = db.get_molecule(molecule_id)
    if molecule is None:
        return []
    
    # Get all calculations
    calculations = []
    for calc_type in CalculationType:
        calculations.extend(db.get_calculations_for_molecule(molecule_id, calc_type))
    
    # Sort by creation date
    calculations.sort(key=lambda c: c.created_at, reverse=True)
    
    # Limit results
    calculations = calculations[:limit]
    
    # Format history
    history = []
    for calc in calculations:
        results = db.get_results_for_calculation(calc.id)
        
        history.append({
            "calculation": calc.to_dict(),
            "results": [r.to_dict() for r in results],
        })
    
    return history


def get_recent_calculations(hours: int = 24) -> List[Calculation]:
    """Get calculations from the last N hours."""
    db = get_database_manager()
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Get all calculations (inefficient but simple)
    all_calcs = []
    for mol_id in [m["id"] for m in db.export_all().get("molecules", [])]:
        all_calcs.extend(db.get_calculations_for_molecule(mol_id))
    
    # Filter by date
    recent = [c for c in all_calcs if c.created_at > cutoff]
    
    return sorted(recent, key=lambda c: c.created_at, reverse=True)


def count_calculations_by_status() -> Dict[str, int]:
    """Count calculations by status."""
    db = get_database_manager()
    
    counts = {status.value: 0 for status in CalculationStatus}
    
    all_calcs = db.export_all().get("calculations", [])
    for calc in all_calcs:
        status = calc.get("status", "unknown")
        if status in counts:
            counts[status] += 1
    
    return counts


def count_calculations_by_method() -> Dict[str, int]:
    """Count calculations by method."""
    db = get_database_manager()
    
    counts: Dict[str, int] = {}
    
    all_calcs = db.export_all().get("calculations", [])
    for calc in all_calcs:
        method = calc.get("method", "unknown")
        counts[method] = counts.get(method, 0) + 1
    
    return counts


def purge_old_results(days: int = 30) -> int:
    """Remove results older than N days."""
    db = get_database_manager()
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    results = db.export_all().get("results", [])
    original_count = len(results)
    
    filtered = [
        r for r in results
        if datetime.fromisoformat(r["created_at"]) > cutoff
    ]
    
    db._write_collection("results", filtered)
    
    return original_count - len(filtered)
