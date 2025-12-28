"""
Database Migrations for Psi4 MCP Server.

Handles schema migrations for the database.
"""

from psi4_mcp.database.migrations.v001_initial import migrate_v001

__all__ = ["migrate_v001"]
