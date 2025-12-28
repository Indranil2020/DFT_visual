"""
ASE (Atomic Simulation Environment) Integration.

Provides conversion between ASE Atoms objects and Psi4 molecules.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np


class ASEInterface:
    """Interface for ASE integration."""
    
    def __init__(self):
        """Initialize ASE interface."""
        self._ase_available = self._check_ase()
    
    def _check_ase(self) -> bool:
        """Check if ASE is available."""
        try:
            import ase
            return True
        except ImportError:
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if ASE is available."""
        return self._ase_available
    
    def atoms_to_geometry(self, atoms: Any) -> Tuple[List[str], np.ndarray]:
        """
        Convert ASE Atoms to geometry data.
        
        Args:
            atoms: ASE Atoms object
            
        Returns:
            Tuple of (element symbols, coordinates in Angstrom)
        """
        if not self._ase_available:
            raise ImportError("ASE is not installed")
        
        symbols = list(atoms.get_chemical_symbols())
        positions = atoms.get_positions()  # Already in Angstrom
        
        return symbols, positions
    
    def atoms_to_psi4_string(
        self,
        atoms: Any,
        charge: int = 0,
        multiplicity: int = 1,
    ) -> str:
        """
        Convert ASE Atoms to Psi4 geometry string.
        
        Args:
            atoms: ASE Atoms object
            charge: Molecular charge
            multiplicity: Spin multiplicity
            
        Returns:
            Psi4-format geometry string
        """
        symbols, positions = self.atoms_to_geometry(atoms)
        
        lines = [f"{charge} {multiplicity}"]
        
        for symbol, (x, y, z) in zip(symbols, positions):
            lines.append(f"{symbol:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
        
        return "\n".join(lines)
    
    def geometry_to_atoms(
        self,
        symbols: List[str],
        positions: np.ndarray,
    ) -> Any:
        """
        Convert geometry data to ASE Atoms.
        
        Args:
            symbols: Element symbols
            positions: Coordinates in Angstrom
            
        Returns:
            ASE Atoms object
        """
        if not self._ase_available:
            raise ImportError("ASE is not installed")
        
        from ase import Atoms
        return Atoms(symbols=symbols, positions=positions)
    
    def psi4_string_to_atoms(self, geometry: str) -> Any:
        """
        Convert Psi4 geometry string to ASE Atoms.
        
        Args:
            geometry: Psi4-format geometry string
            
        Returns:
            ASE Atoms object
        """
        if not self._ase_available:
            raise ImportError("ASE is not installed")
        
        from ase import Atoms
        
        symbols = []
        positions = []
        
        lines = geometry.strip().split("\n")
        
        # Skip charge/multiplicity line if present
        start_idx = 0
        first_parts = lines[0].split()
        if len(first_parts) == 2:
            try:
                int(first_parts[0])
                int(first_parts[1])
                start_idx = 1
            except ValueError:
                pass
        
        for line in lines[start_idx:]:
            parts = line.split()
            if len(parts) >= 4:
                symbol = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                
                symbols.append(symbol)
                positions.append([x, y, z])
        
        return Atoms(symbols=symbols, positions=positions)


# Global interface instance
_ase_interface: Optional[ASEInterface] = None


def get_ase_interface() -> ASEInterface:
    """Get the global ASE interface."""
    global _ase_interface
    if _ase_interface is None:
        _ase_interface = ASEInterface()
    return _ase_interface


def ase_to_psi4(
    atoms: Any,
    charge: int = 0,
    multiplicity: int = 1,
) -> str:
    """
    Convert ASE Atoms to Psi4 geometry string.
    
    Args:
        atoms: ASE Atoms object
        charge: Molecular charge
        multiplicity: Spin multiplicity
        
    Returns:
        Psi4-format geometry string
    """
    interface = get_ase_interface()
    return interface.atoms_to_psi4_string(atoms, charge, multiplicity)


def psi4_to_ase(geometry: str) -> Any:
    """
    Convert Psi4 geometry string to ASE Atoms.
    
    Args:
        geometry: Psi4-format geometry string
        
    Returns:
        ASE Atoms object
    """
    interface = get_ase_interface()
    return interface.psi4_string_to_atoms(geometry)


def is_ase_available() -> bool:
    """Check if ASE is available."""
    interface = get_ase_interface()
    return interface.is_available
