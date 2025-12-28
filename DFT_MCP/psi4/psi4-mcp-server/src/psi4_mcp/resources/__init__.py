"""
Psi4 MCP Resources Package.

Provides access to basis sets, methods, functionals, reference molecules,
literature references, benchmarks, and tutorials.
"""

from psi4_mcp.resources.base_resource import BaseResource, RESOURCE_REGISTRY
from psi4_mcp.resources.basis_sets import BasisSetResource
from psi4_mcp.resources.methods import MethodResource
from psi4_mcp.resources.functionals import FunctionalResource
from psi4_mcp.resources.molecules import MoleculeResource
from psi4_mcp.resources.elements import ElementResource
from psi4_mcp.resources.literature import (
    LiteratureDatabase,
    get_literature_database,
    get_method_citation,
    get_basis_citation,
    get_psi4_citation,
)
from psi4_mcp.resources.benchmarks import (
    BenchmarkDatabase,
    get_benchmark_database,
    get_s22_reference,
    calculate_mae,
    calculate_rmse,
)
from psi4_mcp.resources.tutorials import (
    TutorialDatabase,
    get_tutorial_database,
    get_tutorial,
    list_beginner_tutorials,
)

__all__ = [
    "BaseResource", "RESOURCE_REGISTRY",
    "BasisSetResource", "MethodResource", "FunctionalResource",
    "MoleculeResource", "ElementResource",
    "LiteratureDatabase", "get_literature_database",
    "get_method_citation", "get_basis_citation", "get_psi4_citation",
    "BenchmarkDatabase", "get_benchmark_database",
    "get_s22_reference", "calculate_mae", "calculate_rmse",
    "TutorialDatabase", "get_tutorial_database",
    "get_tutorial", "list_beginner_tutorials",
]
