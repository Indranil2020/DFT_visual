"""
Literature Resources for Psi4 MCP Server.

Provides access to literature references, citations, and publication data
for computational chemistry methods and basis sets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class PublicationType(str, Enum):
    """Types of publications."""
    JOURNAL_ARTICLE = "article"
    BOOK = "book"
    BOOK_CHAPTER = "inbook"
    CONFERENCE = "conference"
    THESIS = "thesis"
    PREPRINT = "preprint"
    SOFTWARE = "software"
    WEBSITE = "website"


@dataclass
class Author:
    """Author information."""
    last_name: str
    first_name: str
    middle_name: str = ""
    orcid: str = ""
    
    def format_name(self, style: str = "apa") -> str:
        """Format author name."""
        if style == "apa":
            initials = self.first_name[0] + "."
            if self.middle_name:
                initials += " " + self.middle_name[0] + "."
            return f"{self.last_name}, {initials}"
        elif style == "bibtex":
            return f"{self.last_name}, {self.first_name}"
        return f"{self.first_name} {self.last_name}"


@dataclass
class Citation:
    """Citation information for a publication."""
    key: str
    title: str
    authors: List[Author]
    year: int
    publication_type: PublicationType = PublicationType.JOURNAL_ARTICLE
    journal: str = ""
    volume: str = ""
    pages: str = ""
    doi: str = ""
    url: str = ""
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    publisher: str = ""
    
    def format_apa(self) -> str:
        """Format citation in APA style."""
        author_str = ", ".join(a.format_name("apa") for a in self.authors[:3])
        if len(self.authors) > 3:
            author_str += ", et al."
        
        base = f"{author_str} ({self.year}). {self.title}."
        
        if self.journal:
            base += f" {self.journal}"
            if self.volume:
                base += f", {self.volume}"
            if self.pages:
                base += f", {self.pages}"
            base += "."
        
        if self.doi:
            base += f" https://doi.org/{self.doi}"
        
        return base
    
    def format_bibtex(self) -> str:
        """Format citation in BibTeX."""
        entry_type = self.publication_type.value
        authors = " and ".join(a.format_name("bibtex") for a in self.authors)
        
        lines = [f"@{entry_type}{{{self.key},"]
        lines.append(f"  author = {{{authors}}},")
        lines.append(f"  title = {{{self.title}}},")
        lines.append(f"  year = {{{self.year}}},")
        
        if self.journal:
            lines.append(f"  journal = {{{self.journal}}},")
        if self.volume:
            lines.append(f"  volume = {{{self.volume}}},")
        if self.pages:
            lines.append(f"  pages = {{{self.pages}}},")
        if self.doi:
            lines.append(f"  doi = {{{self.doi}}},")
        
        lines.append("}")
        return "\n".join(lines)


class LiteratureDatabase:
    """Database of literature references."""
    
    def __init__(self):
        self._citations: Dict[str, Citation] = {}
        self._method_citations: Dict[str, List[str]] = {}
        self._basis_citations: Dict[str, List[str]] = {}
        self._load_default_citations()
    
    def _load_default_citations(self) -> None:
        """Load default citations for common methods."""
        # Psi4 citation
        self.add_citation(Citation(
            key="psi4_2020",
            title="Psi4 1.4: Open-Source Software for High-Throughput Quantum Chemistry",
            authors=[
                Author("Smith", "Daniel", "G. A."),
                Author("Burns", "Lori", "A."),
                Author("Simmonett", "Andrew", "C."),
            ],
            year=2020,
            journal="J. Chem. Phys.",
            volume="152",
            pages="184108",
            doi="10.1063/5.0006002",
        ))
        
        # B3LYP citation
        self.add_citation(Citation(
            key="b3lyp_1993",
            title="Density-functional thermochemistry. III. The role of exact exchange",
            authors=[
                Author("Becke", "Axel", "D."),
            ],
            year=1993,
            journal="J. Chem. Phys.",
            volume="98",
            pages="5648-5652",
            doi="10.1063/1.464913",
        ))
        self._method_citations["b3lyp"] = ["b3lyp_1993"]
        
        # CCSD(T) citation
        self.add_citation(Citation(
            key="ccsd_t_1989",
            title="A fifth-order perturbation comparison of electron correlation theories",
            authors=[
                Author("Raghavachari", "Krishnan"),
                Author("Trucks", "Gary", "W."),
                Author("Pople", "John", "A."),
                Author("Head-Gordon", "Martin"),
            ],
            year=1989,
            journal="Chem. Phys. Lett.",
            volume="157",
            pages="479-483",
            doi="10.1016/S0009-2614(89)87395-6",
        ))
        self._method_citations["ccsd(t)"] = ["ccsd_t_1989"]
        
        # cc-pVXZ basis sets
        self.add_citation(Citation(
            key="dunning_1989",
            title="Gaussian basis sets for use in correlated molecular calculations. I.",
            authors=[
                Author("Dunning", "Thom", "H."),
            ],
            year=1989,
            journal="J. Chem. Phys.",
            volume="90",
            pages="1007-1023",
            doi="10.1063/1.456153",
        ))
        for basis in ["cc-pvdz", "cc-pvtz", "cc-pvqz", "cc-pv5z"]:
            self._basis_citations[basis] = ["dunning_1989"]
        
        # def2 basis sets
        self.add_citation(Citation(
            key="weigend_2005",
            title="Balanced basis sets of split valence, triple zeta valence and quadruple zeta valence quality",
            authors=[
                Author("Weigend", "Florian"),
                Author("Ahlrichs", "Reinhart"),
            ],
            year=2005,
            journal="Phys. Chem. Chem. Phys.",
            volume="7",
            pages="3297-3305",
            doi="10.1039/B508541A",
        ))
        for basis in ["def2-svp", "def2-tzvp", "def2-qzvp"]:
            self._basis_citations[basis] = ["weigend_2005"]
        
        # MP2 citation
        self.add_citation(Citation(
            key="mp2_1934",
            title="Note on an Approximation Treatment for Many-Electron Systems",
            authors=[
                Author("Møller", "Chr."),
                Author("Plesset", "Milton", "S."),
            ],
            year=1934,
            journal="Phys. Rev.",
            volume="46",
            pages="618-622",
            doi="10.1103/PhysRev.46.618",
        ))
        self._method_citations["mp2"] = ["mp2_1934"]
        
        # SAPT citation
        self.add_citation(Citation(
            key="sapt_1994",
            title="Perturbation Theory Approach to Intermolecular Potential Energy Surfaces",
            authors=[
                Author("Jeziorski", "Bogumil"),
                Author("Moszynski", "Robert"),
                Author("Szalewicz", "Krzysztof"),
            ],
            year=1994,
            journal="Chem. Rev.",
            volume="94",
            pages="1887-1930",
            doi="10.1021/cr00031a008",
        ))
        self._method_citations["sapt"] = ["sapt_1994"]
    
    def add_citation(self, citation: Citation) -> None:
        """Add a citation to the database."""
        self._citations[citation.key] = citation
    
    def get_citation(self, key: str) -> Optional[Citation]:
        """Get citation by key."""
        return self._citations.get(key)
    
    def get_method_citations(self, method: str) -> List[Citation]:
        """Get citations for a method."""
        method_lower = method.lower()
        keys = self._method_citations.get(method_lower, [])
        return [self._citations[k] for k in keys if k in self._citations]
    
    def get_basis_citations(self, basis: str) -> List[Citation]:
        """Get citations for a basis set."""
        basis_lower = basis.lower()
        keys = self._basis_citations.get(basis_lower, [])
        return [self._citations[k] for k in keys if k in self._citations]
    
    def search(self, query: str) -> List[Citation]:
        """Search citations by title, author, or keywords."""
        query_lower = query.lower()
        results = []
        
        for citation in self._citations.values():
            if query_lower in citation.title.lower():
                results.append(citation)
                continue
            
            for author in citation.authors:
                if query_lower in author.last_name.lower():
                    results.append(citation)
                    break
            
            for keyword in citation.keywords:
                if query_lower in keyword.lower():
                    results.append(citation)
                    break
        
        return results
    
    def export_bibtex(self, keys: Optional[List[str]] = None) -> str:
        """Export citations as BibTeX."""
        if keys is None:
            keys = list(self._citations.keys())
        
        entries = []
        for key in keys:
            if key in self._citations:
                entries.append(self._citations[key].format_bibtex())
        
        return "\n\n".join(entries)
    
    def list_all(self) -> List[Citation]:
        """List all citations."""
        return list(self._citations.values())


# Global database instance
_literature_db: Optional[LiteratureDatabase] = None


def get_literature_database() -> LiteratureDatabase:
    """Get the global literature database."""
    global _literature_db
    if _literature_db is None:
        _literature_db = LiteratureDatabase()
    return _literature_db


def get_method_citation(method: str, format: str = "apa") -> str:
    """Get formatted citation for a method."""
    db = get_literature_database()
    citations = db.get_method_citations(method)
    
    if not citations:
        return f"No citation found for method: {method}"
    
    if format == "bibtex":
        return "\n\n".join(c.format_bibtex() for c in citations)
    return "\n".join(c.format_apa() for c in citations)


def get_basis_citation(basis: str, format: str = "apa") -> str:
    """Get formatted citation for a basis set."""
    db = get_literature_database()
    citations = db.get_basis_citations(basis)
    
    if not citations:
        return f"No citation found for basis set: {basis}"
    
    if format == "bibtex":
        return "\n\n".join(c.format_bibtex() for c in citations)
    return "\n".join(c.format_apa() for c in citations)


def get_psi4_citation(format: str = "apa") -> str:
    """Get Psi4 citation."""
    db = get_literature_database()
    citation = db.get_citation("psi4_2020")
    
    if citation is None:
        return "Psi4 citation not found"
    
    if format == "bibtex":
        return citation.format_bibtex()
    return citation.format_apa()
