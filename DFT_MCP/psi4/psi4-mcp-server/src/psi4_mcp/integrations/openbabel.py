"""
OpenBabel Integration for Psi4 MCP Server.

Provides format conversion and molecular manipulation via OpenBabel.
"""

from typing import Any, Dict, List, Optional, Tuple


class OpenBabelInterface:
    """Interface for OpenBabel integration."""
    
    def __init__(self):
        """Initialize OpenBabel interface."""
        self._openbabel_available = self._check_openbabel()
    
    def _check_openbabel(self) -> bool:
        """Check if OpenBabel is available."""
        try:
            from openbabel import openbabel
            return True
        except ImportError:
            try:
                import openbabel
                return True
            except ImportError:
                return False
    
    @property
    def is_available(self) -> bool:
        """Check if OpenBabel is available."""
        return self._openbabel_available
    
    def convert_format(
        self,
        input_data: str,
        input_format: str,
        output_format: str,
    ) -> Optional[str]:
        """
        Convert between molecular formats.
        
        Args:
            input_data: Input molecular data
            input_format: Input format (xyz, mol2, pdb, smi, etc.)
            output_format: Output format
            
        Returns:
            Converted data or None
        """
        if not self._openbabel_available:
            raise ImportError("OpenBabel is not installed")
        
        try:
            from openbabel import openbabel as ob
        except ImportError:
            import openbabel as ob
        
        # Create converter
        conv = ob.OBConversion()
        conv.SetInAndOutFormats(input_format, output_format)
        
        # Create molecule
        mol = ob.OBMol()
        
        # Read input
        if not conv.ReadString(mol, input_data):
            return None
        
        # Write output
        return conv.WriteString(mol)
    
    def smiles_to_xyz(self, smiles: str, optimize: bool = True) -> Optional[str]:
        """
        Convert SMILES to XYZ format.
        
        Args:
            smiles: SMILES string
            optimize: Whether to optimize 3D geometry
            
        Returns:
            XYZ format string or None
        """
        if not self._openbabel_available:
            raise ImportError("OpenBabel is not installed")
        
        try:
            from openbabel import openbabel as ob
            from openbabel import pybel
        except ImportError:
            import openbabel as ob
            import pybel
        
        # Parse SMILES
        mol = pybel.readstring("smi", smiles)
        
        # Generate 3D coordinates
        mol.make3D()
        
        # Optionally optimize
        if optimize:
            mol.localopt()
        
        return mol.write("xyz")
    
    def xyz_to_smiles(self, xyz: str) -> Optional[str]:
        """
        Convert XYZ to SMILES.
        
        Args:
            xyz: XYZ format string
            
        Returns:
            SMILES string or None
        """
        if not self._openbabel_available:
            raise ImportError("OpenBabel is not installed")
        
        try:
            from openbabel import pybel
        except ImportError:
            import pybel
        
        mol = pybel.readstring("xyz", xyz)
        return mol.write("smi").strip()
    
    def calculate_formula(self, input_data: str, input_format: str) -> Optional[str]:
        """
        Calculate molecular formula.
        
        Args:
            input_data: Molecular data
            input_format: Input format
            
        Returns:
            Molecular formula or None
        """
        if not self._openbabel_available:
            raise ImportError("OpenBabel is not installed")
        
        try:
            from openbabel import pybel
        except ImportError:
            import pybel
        
        mol = pybel.readstring(input_format, input_data)
        return mol.formula
    
    def calculate_molecular_weight(self, input_data: str, input_format: str) -> Optional[float]:
        """
        Calculate molecular weight.
        
        Args:
            input_data: Molecular data
            input_format: Input format
            
        Returns:
            Molecular weight in g/mol or None
        """
        if not self._openbabel_available:
            raise ImportError("OpenBabel is not installed")
        
        try:
            from openbabel import pybel
        except ImportError:
            import pybel
        
        mol = pybel.readstring(input_format, input_data)
        return mol.molwt
    
    def add_hydrogens(self, input_data: str, input_format: str) -> Optional[str]:
        """
        Add hydrogens to molecule.
        
        Args:
            input_data: Molecular data
            input_format: Input format
            
        Returns:
            Modified molecule in same format
        """
        if not self._openbabel_available:
            raise ImportError("OpenBabel is not installed")
        
        try:
            from openbabel import pybel
        except ImportError:
            import pybel
        
        mol = pybel.readstring(input_format, input_data)
        mol.addh()
        return mol.write(input_format)
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get list of supported formats.
        
        Returns:
            Dictionary with 'input' and 'output' format lists
        """
        if not self._openbabel_available:
            return {"input": [], "output": []}
        
        try:
            from openbabel import openbabel as ob
        except ImportError:
            import openbabel as ob
        
        conv = ob.OBConversion()
        
        return {
            "input": list(conv.GetSupportedInputFormat()),
            "output": list(conv.GetSupportedOutputFormat()),
        }


# Global interface instance
_openbabel_interface: Optional[OpenBabelInterface] = None


def get_openbabel_interface() -> OpenBabelInterface:
    """Get the global OpenBabel interface."""
    global _openbabel_interface
    if _openbabel_interface is None:
        _openbabel_interface = OpenBabelInterface()
    return _openbabel_interface


def convert_format(
    input_data: str,
    input_format: str,
    output_format: str,
) -> Optional[str]:
    """Convert between molecular formats."""
    interface = get_openbabel_interface()
    return interface.convert_format(input_data, input_format, output_format)


def smiles_to_xyz(smiles: str, optimize: bool = True) -> Optional[str]:
    """Convert SMILES to XYZ."""
    interface = get_openbabel_interface()
    return interface.smiles_to_xyz(smiles, optimize)


def is_openbabel_available() -> bool:
    """Check if OpenBabel is available."""
    interface = get_openbabel_interface()
    return interface.is_available
