"""
MCP Resource Models.

Pydantic models for MCP resources that provide reference information:
    - Basis set information
    - Method information
    - Molecule libraries
    - Benchmark data
    - Literature references
"""

from typing import Any, Optional, Literal
from pydantic import Field, HttpUrl
from enum import Enum

from psi4_mcp.models.base import BaseModel


# =============================================================================
# RESOURCE ENUMS
# =============================================================================

class ResourceType(str, Enum):
    """Types of MCP resources."""
    BASIS_SET = "basis_set"
    METHOD = "method"
    FUNCTIONAL = "functional"
    MOLECULE = "molecule"
    BENCHMARK = "benchmark"
    LITERATURE = "literature"
    TUTORIAL = "tutorial"


class ResourceCategory(str, Enum):
    """Resource categories for organization."""
    REFERENCE = "reference"
    DATA = "data"
    EDUCATION = "education"
    EXAMPLES = "examples"


# =============================================================================
# BASE RESOURCE MODEL
# =============================================================================

class Resource(BaseModel):
    """
    Base MCP resource model.
    
    Resources provide read-only reference information that LLMs can
    query to make informed decisions about calculations.
    
    Attributes:
        uri: Unique resource identifier (psi4://type/name).
        name: Human-readable resource name.
        description: Detailed description.
        resource_type: Type classification.
        category: Category for organization.
        tags: Searchable tags.
        metadata: Additional metadata.
    """
    
    uri: str = Field(description="Unique resource URI")
    name: str = Field(description="Resource name")
    description: str = Field(description="Resource description")
    resource_type: ResourceType = Field(description="Resource type")
    category: ResourceCategory = Field(default=ResourceCategory.REFERENCE)
    tags: list[str] = Field(default_factory=list, description="Searchable tags")
    metadata: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# BASIS SET RESOURCES
# =============================================================================

class BasisSetResource(Resource):
    """
    Basis set information resource.
    
    Provides detailed information about basis sets including:
    - Contraction scheme
    - Supported elements
    - Recommended use cases
    - References
    """
    
    resource_type: ResourceType = ResourceType.BASIS_SET
    
    # Basis set specifics
    basis_name: str = Field(description="Basis set name in Psi4 format")
    family: str = Field(description="Basis set family (dunning, pople, etc.)")
    zeta: Optional[str] = Field(default=None, description="Zeta level (DZ, TZ, QZ)")
    polarization: bool = Field(default=False, description="Has polarization functions")
    diffuse: bool = Field(default=False, description="Has diffuse functions")
    supported_elements: list[str] = Field(
        default_factory=list,
        description="Elements with parameters"
    )
    n_functions_h: Optional[int] = Field(default=None, description="Functions for H")
    n_functions_c: Optional[int] = Field(default=None, description="Functions for C")
    recommended_for: list[str] = Field(
        default_factory=list,
        description="Recommended use cases"
    )
    not_recommended_for: list[str] = Field(
        default_factory=list,
        description="Not recommended use cases"
    )
    reference: Optional[str] = Field(default=None, description="Literature reference")
    doi: Optional[str] = Field(default=None, description="DOI for reference")


class BasisSetListResource(Resource):
    """List of available basis sets."""
    resource_type: ResourceType = ResourceType.BASIS_SET
    basis_sets: list[BasisSetResource] = Field(default_factory=list)


# =============================================================================
# METHOD RESOURCES
# =============================================================================

class MethodResource(Resource):
    """
    Computational method information resource.
    
    Provides detailed information about quantum chemistry methods.
    """
    
    resource_type: ResourceType = ResourceType.METHOD
    
    # Method specifics
    method_name: str = Field(description="Method name")
    method_type: Literal["hf", "dft", "mp", "cc", "ci", "mcscf", "other"] = Field(
        description="Method type category"
    )
    scaling: str = Field(description="Computational scaling (e.g., O(N^4))")
    accuracy_description: str = Field(description="Typical accuracy description")
    recommended_basis: list[str] = Field(
        default_factory=list,
        description="Recommended basis sets"
    )
    strengths: list[str] = Field(default_factory=list, description="Method strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Method weaknesses")
    typical_error_kcal: Optional[float] = Field(
        default=None,
        description="Typical error in kcal/mol"
    )
    supports_gradient: bool = Field(default=True)
    supports_hessian: bool = Field(default=True)
    supports_excited_states: bool = Field(default=False)
    reference: Optional[str] = Field(default=None)


class FunctionalResource(Resource):
    """
    DFT functional information resource.
    """
    
    resource_type: ResourceType = ResourceType.FUNCTIONAL
    
    # Functional specifics
    functional_name: str = Field(description="Functional name")
    rung: Literal["lda", "gga", "meta-gga", "hybrid", "double-hybrid"] = Field(
        description="Jacob's ladder rung"
    )
    hf_exchange: Optional[float] = Field(default=None, description="% HF exchange")
    dispersion_correction: Optional[str] = Field(
        default=None, description="Built-in dispersion"
    )
    recommended_for: list[str] = Field(default_factory=list)
    not_recommended_for: list[str] = Field(default_factory=list)


# =============================================================================
# MOLECULE RESOURCES
# =============================================================================

class MoleculeResource(Resource):
    """
    Reference molecule information.
    """
    
    resource_type: ResourceType = ResourceType.MOLECULE
    
    # Molecule specifics
    molecular_formula: str = Field(description="Molecular formula")
    name: str = Field(description="Common name")
    iupac_name: Optional[str] = Field(default=None)
    smiles: Optional[str] = Field(default=None, description="SMILES string")
    inchi: Optional[str] = Field(default=None, description="InChI string")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    point_group: Optional[str] = Field(default=None)
    geometry_xyz: Optional[str] = Field(default=None, description="XYZ geometry")
    source: Optional[str] = Field(default=None, description="Geometry source")


class MoleculeLibraryResource(Resource):
    """Collection of reference molecules."""
    resource_type: ResourceType = ResourceType.MOLECULE
    molecules: list[MoleculeResource] = Field(default_factory=list)


# =============================================================================
# BENCHMARK RESOURCES
# =============================================================================

class BenchmarkDataPoint(BaseModel):
    """Single benchmark data point."""
    system: str = Field(description="System name/identifier")
    property_name: str = Field(description="Property computed")
    reference_value: float = Field(description="Reference value")
    reference_unit: str = Field(description="Unit of reference value")
    reference_source: str = Field(description="Source (e.g., CCSD(T)/CBS)")
    computed_values: dict[str, float] = Field(
        default_factory=dict,
        description="Computed values by method"
    )


class BenchmarkResource(Resource):
    """
    Benchmark dataset resource.
    
    Contains reference data for validating computational methods.
    """
    
    resource_type: ResourceType = ResourceType.BENCHMARK
    
    # Benchmark specifics
    benchmark_name: str = Field(description="Benchmark set name")
    benchmark_type: Literal[
        "thermochemistry", "barrier_heights", "noncovalent",
        "geometry", "reaction_energy", "other"
    ] = Field(description="Type of benchmark")
    n_systems: int = Field(description="Number of systems")
    property_type: str = Field(description="Property being benchmarked")
    reference_level: str = Field(description="Reference level of theory")
    data_points: list[BenchmarkDataPoint] = Field(default_factory=list)
    publication: Optional[str] = Field(default=None)
    doi: Optional[str] = Field(default=None)


# =============================================================================
# LITERATURE RESOURCES
# =============================================================================

class LiteratureResource(Resource):
    """
    Literature reference resource.
    """
    
    resource_type: ResourceType = ResourceType.LITERATURE
    
    # Citation info
    authors: list[str] = Field(default_factory=list)
    title: str = Field(description="Publication title")
    journal: Optional[str] = Field(default=None)
    year: Optional[int] = Field(default=None)
    volume: Optional[str] = Field(default=None)
    pages: Optional[str] = Field(default=None)
    doi: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    
    def to_citation(self) -> str:
        """Format as citation string."""
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        
        parts = [authors_str, f'"{self.title}"']
        if self.journal:
            parts.append(self.journal)
        if self.volume:
            parts.append(self.volume)
        if self.pages:
            parts.append(self.pages)
        if self.year:
            parts.append(f"({self.year})")
        
        return ", ".join(parts)


# =============================================================================
# TUTORIAL RESOURCES
# =============================================================================

class TutorialResource(Resource):
    """
    Tutorial/educational resource.
    """
    
    resource_type: ResourceType = ResourceType.TUTORIAL
    category: ResourceCategory = ResourceCategory.EDUCATION
    
    # Tutorial specifics
    title: str = Field(description="Tutorial title")
    difficulty: Literal["beginner", "intermediate", "advanced"] = Field(
        default="beginner"
    )
    topics: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    content: str = Field(description="Tutorial content (markdown)")
    examples: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Example code/inputs"
    )


# =============================================================================
# RESOURCE REGISTRY
# =============================================================================

class ResourceRegistry(BaseModel):
    """
    Registry of all available resources.
    
    Provides methods for resource discovery and retrieval.
    """
    
    resources: dict[str, Resource] = Field(
        default_factory=dict,
        description="URI -> Resource mapping"
    )
    
    def register(self, resource: Resource) -> None:
        """Register a resource."""
        self.resources[resource.uri] = resource
    
    def get(self, uri: str) -> Optional[Resource]:
        """Get resource by URI."""
        return self.resources.get(uri)
    
    def list_by_type(self, resource_type: ResourceType) -> list[Resource]:
        """List resources by type."""
        return [r for r in self.resources.values() if r.resource_type == resource_type]
    
    def search(self, query: str) -> list[Resource]:
        """Search resources by name/description/tags."""
        query_lower = query.lower()
        results = []
        for resource in self.resources.values():
            if (query_lower in resource.name.lower() or
                query_lower in resource.description.lower() or
                any(query_lower in tag.lower() for tag in resource.tags)):
                results.append(resource)
        return results
