"""
Scripts Module for Psi4 MCP Server.

Provides utility scripts for benchmarking, documentation generation,
dependency installation, and environment setup.
"""

from psi4_mcp.scripts.benchmark import run_benchmark
from psi4_mcp.scripts.setup_env import setup_environment

__all__ = [
    "run_benchmark",
    "setup_environment",
]
