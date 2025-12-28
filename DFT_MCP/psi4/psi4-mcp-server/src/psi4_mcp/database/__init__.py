"""
Database Module for Psi4 MCP Server.

Provides persistent storage for calculation results, molecules,
and other data.
"""

from psi4_mcp.database.schema import (
    Base,
    Molecule,
    Calculation,
    Result,
    BasisSetRecord,
)
from psi4_mcp.database.manager import DatabaseManager, get_database_manager
from psi4_mcp.database.queries import (
    get_molecule_by_name,
    get_calculations_for_molecule,
    search_results,
)

__all__ = [
    "Base",
    "Molecule",
    "Calculation",
    "Result",
    "BasisSetRecord",
    "DatabaseManager",
    "get_database_manager",
    "get_molecule_by_name",
    "get_calculations_for_molecule",
    "search_results",
]
