"""
Psi4 MCP Prompts Package.

Provides prompt templates for method selection, workflows,
troubleshooting, and educational content.
"""

from psi4_mcp.prompts.base_prompt import BasePrompt, PROMPT_REGISTRY
from psi4_mcp.prompts.methods import (
    MethodSelector,
    get_method_selector,
    recommend_method,
    get_method_info,
    format_recommendation,
)
from psi4_mcp.prompts.troubleshooting import (
    TroubleshootingDatabase,
    get_troubleshooting_database,
    diagnose_problem,
    get_scf_convergence_help,
    format_troubleshooting_guide,
)

__all__ = [
    "BasePrompt", "PROMPT_REGISTRY",
    "MethodSelector", "get_method_selector",
    "recommend_method", "get_method_info", "format_recommendation",
    "TroubleshootingDatabase", "get_troubleshooting_database",
    "diagnose_problem", "get_scf_convergence_help", "format_troubleshooting_guide",
]
