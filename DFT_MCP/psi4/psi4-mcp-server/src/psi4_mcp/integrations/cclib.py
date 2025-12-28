"""
cclib Integration for Psi4 MCP Server.

Provides parsing capabilities using cclib for output file analysis.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path


class CclibInterface:
    """Interface for cclib integration."""
    
    def __init__(self):
        """Initialize cclib interface."""
        self._cclib_available = self._check_cclib()
    
    def _check_cclib(self) -> bool:
        """Check if cclib is available."""
        try:
            import cclib
            return True
        except ImportError:
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if cclib is available."""
        return self._cclib_available
    
    def parse_output(self, output_path: str) -> Optional[Dict[str, Any]]:
        """
        Parse a quantum chemistry output file.
        
        Args:
            output_path: Path to output file
            
        Returns:
            Dictionary of parsed data or None if parsing fails
        """
        if not self._cclib_available:
            raise ImportError("cclib is not installed")
        
        import cclib
        
        path = Path(output_path)
        if not path.exists():
            return None
        
        parser = cclib.io.ccread(str(path))
        
        if parser is None:
            return None
        
        # Extract common data
        data = {}
        
        # Energy
        if hasattr(parser, "scfenergies") and len(parser.scfenergies) > 0:
            data["scf_energies"] = parser.scfenergies.tolist()
            data["final_scf_energy"] = float(parser.scfenergies[-1])
        
        # Geometry
        if hasattr(parser, "atomcoords") and len(parser.atomcoords) > 0:
            data["coordinates"] = parser.atomcoords[-1].tolist()
            data["n_geometries"] = len(parser.atomcoords)
        
        if hasattr(parser, "atomnos"):
            data["atomic_numbers"] = parser.atomnos.tolist()
        
        # Molecular orbitals
        if hasattr(parser, "moenergies"):
            data["orbital_energies"] = [e.tolist() for e in parser.moenergies]
        
        if hasattr(parser, "homos"):
            data["homo_indices"] = parser.homos.tolist()
        
        # Frequencies
        if hasattr(parser, "vibfreqs"):
            data["frequencies"] = parser.vibfreqs.tolist()
        
        if hasattr(parser, "vibirs"):
            data["ir_intensities"] = parser.vibirs.tolist()
        
        # Mulliken charges
        if hasattr(parser, "atomcharges") and "mulliken" in parser.atomcharges:
            data["mulliken_charges"] = parser.atomcharges["mulliken"].tolist()
        
        # Dipole moment
        if hasattr(parser, "moments"):
            data["dipole_moment"] = parser.moments[1].tolist() if len(parser.moments) > 1 else None
        
        # Metadata
        if hasattr(parser, "metadata"):
            data["metadata"] = dict(parser.metadata)
        
        return data
    
    def parse_string(self, output_string: str) -> Optional[Dict[str, Any]]:
        """
        Parse quantum chemistry output from string.
        
        Args:
            output_string: Output file contents
            
        Returns:
            Dictionary of parsed data or None if parsing fails
        """
        if not self._cclib_available:
            raise ImportError("cclib is not installed")
        
        import cclib
        from io import StringIO
        
        # cclib requires a file-like object
        parser = cclib.io.ccread(StringIO(output_string))
        
        if parser is None:
            return None
        
        # Use same extraction as parse_output
        return self._extract_data(parser)
    
    def _extract_data(self, parser: Any) -> Dict[str, Any]:
        """Extract data from cclib parser object."""
        data = {}
        
        if hasattr(parser, "scfenergies") and len(parser.scfenergies) > 0:
            data["scf_energies"] = parser.scfenergies.tolist()
            data["final_scf_energy"] = float(parser.scfenergies[-1])
        
        if hasattr(parser, "atomcoords") and len(parser.atomcoords) > 0:
            data["coordinates"] = parser.atomcoords[-1].tolist()
        
        if hasattr(parser, "atomnos"):
            data["atomic_numbers"] = parser.atomnos.tolist()
        
        if hasattr(parser, "moenergies"):
            data["orbital_energies"] = [e.tolist() for e in parser.moenergies]
        
        if hasattr(parser, "vibfreqs"):
            data["frequencies"] = parser.vibfreqs.tolist()
        
        return data


# Global interface instance
_cclib_interface: Optional[CclibInterface] = None


def get_cclib_interface() -> CclibInterface:
    """Get the global cclib interface."""
    global _cclib_interface
    if _cclib_interface is None:
        _cclib_interface = CclibInterface()
    return _cclib_interface


def parse_output_file(output_path: str) -> Optional[Dict[str, Any]]:
    """Parse a quantum chemistry output file."""
    interface = get_cclib_interface()
    return interface.parse_output(output_path)


def is_cclib_available() -> bool:
    """Check if cclib is available."""
    interface = get_cclib_interface()
    return interface.is_available
