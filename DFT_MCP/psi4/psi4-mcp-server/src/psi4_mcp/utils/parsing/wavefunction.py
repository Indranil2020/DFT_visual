"""
Wavefunction Parser for Psi4 MCP Server.

Parses Psi4 wavefunction objects.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class WavefunctionData:
    """Extracted wavefunction data."""
    energy: float = 0.0
    method: str = ""
    basis: str = ""
    n_atoms: int = 0
    n_electrons: int = 0
    n_alpha: int = 0
    n_beta: int = 0
    n_basis: int = 0
    n_mo: int = 0
    multiplicity: int = 1
    charge: int = 0
    converged: bool = True
    orbital_energies: List[float] = field(default_factory=list)


class WavefunctionParser:
    """Parser for Psi4 wavefunction objects."""
    
    def parse(self, wfn: Any) -> WavefunctionData:
        """Parse a Psi4 wavefunction object."""
        data = WavefunctionData()
        
        # Basic info
        if hasattr(wfn, "energy"):
            data.energy = float(wfn.energy())
        
        if hasattr(wfn, "name"):
            data.method = str(wfn.name())
        
        # Molecule info
        if hasattr(wfn, "molecule"):
            mol = wfn.molecule()
            if hasattr(mol, "natom"):
                data.n_atoms = mol.natom()
            if hasattr(mol, "multiplicity"):
                data.multiplicity = mol.multiplicity()
            if hasattr(mol, "molecular_charge"):
                data.charge = int(mol.molecular_charge())
        
        # Electron counts
        if hasattr(wfn, "nalpha"):
            data.n_alpha = wfn.nalpha()
        if hasattr(wfn, "nbeta"):
            data.n_beta = wfn.nbeta()
        data.n_electrons = data.n_alpha + data.n_beta
        
        # Basis info
        if hasattr(wfn, "basisset"):
            basis = wfn.basisset()
            if hasattr(basis, "nbf"):
                data.n_basis = basis.nbf()
            if hasattr(basis, "name"):
                data.basis = basis.name()
        
        if hasattr(wfn, "nmo"):
            data.n_mo = wfn.nmo()
        
        # Orbital energies
        if hasattr(wfn, "epsilon_a"):
            eps = wfn.epsilon_a()
            if hasattr(eps, "np"):
                data.orbital_energies = [float(e) for e in eps.np]
        
        return data
    
    def extract_geometry(self, wfn: Any) -> Optional[Tuple[List[str], List[Tuple[float, float, float]]]]:
        """Extract geometry from wavefunction."""
        if not hasattr(wfn, "molecule"):
            return None
        
        mol = wfn.molecule()
        n_atoms = mol.natom() if hasattr(mol, "natom") else 0
        
        elements = []
        coords = []
        
        for i in range(n_atoms):
            if hasattr(mol, "symbol"):
                elements.append(mol.symbol(i))
            if hasattr(mol, "x") and hasattr(mol, "y") and hasattr(mol, "z"):
                coords.append((mol.x(i), mol.y(i), mol.z(i)))
        
        return elements, coords


def parse_wavefunction(wfn: Any) -> WavefunctionData:
    """Convenience function to parse wavefunction."""
    parser = WavefunctionParser()
    return parser.parse(wfn)
