"""
Basis Set Parser for Psi4 MCP Server.

Provides utilities for parsing and formatting basis set files
in various formats (Gaussian/GBS, NWChem, etc.).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import re

from psi4_mcp.utils.basis.generator import (
    BasisFunction,
    ContractedFunction,
    ShellType,
)


@dataclass
class ElementBasis:
    """Basis set data for a single element."""
    element: str
    functions: List[ContractedFunction] = field(default_factory=list)
    
    @property
    def n_functions(self) -> int:
        """Total number of contracted functions."""
        return len(self.functions)
    
    @property
    def n_primitives(self) -> int:
        """Total number of primitives."""
        return sum(f.num_primitives for f in self.functions)
    
    def add_function(self, func: ContractedFunction) -> None:
        """Add a contracted function to this element basis."""
        func.element = self.element
        self.functions.append(func)


@dataclass
class BasisSetData:
    """Complete basis set data for multiple elements."""
    name: str
    description: str = ""
    elements: Dict[str, ElementBasis] = field(default_factory=dict)
    
    @property
    def supported_elements(self) -> List[str]:
        """Get list of supported elements."""
        return list(self.elements.keys())
    
    def get_element_basis(self, element: str) -> Optional[ElementBasis]:
        """Get basis for a specific element."""
        return self.elements.get(element.capitalize())
    
    def add_element_basis(self, element_basis: ElementBasis) -> None:
        """Add basis data for an element."""
        self.elements[element_basis.element.capitalize()] = element_basis


def parse_gbs_file(content: str, name: str = "Unknown") -> BasisSetData:
    """
    Parse a Gaussian/GBS format basis set file.
    
    GBS format example:
    ****
    H     0
    S   3   1.00
          3.42525091           0.15432897
          0.62391373           0.53532814
          0.16885540           0.44463454
    ****
    
    Args:
        content: File content as string
        name: Name for the basis set
        
    Returns:
        BasisSetData object
    """
    basis_data = BasisSetData(name=name)
    
    lines = content.strip().split('\n')
    i = 0
    current_element: Optional[ElementBasis] = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('!') or line.startswith('#'):
            i += 1
            continue
        
        # Element separator
        if line == '****':
            if current_element is not None and current_element.functions:
                basis_data.add_element_basis(current_element)
            current_element = None
            i += 1
            continue
        
        # Element definition line: "H     0" or "C     0"
        element_match = re.match(r'^([A-Za-z]{1,2})\s+\d+', line)
        if element_match:
            element_symbol = element_match.group(1).capitalize()
            current_element = ElementBasis(element=element_symbol)
            i += 1
            continue
        
        # Shell definition line: "S   3   1.00"
        shell_match = re.match(r'^([SPDFGHI])\s+(\d+)\s+([\d.]+)', line, re.IGNORECASE)
        if shell_match and current_element is not None:
            shell_char = shell_match.group(1).lower()
            n_primitives = int(shell_match.group(2))
            
            shell_type = _parse_shell_type(shell_char)
            if shell_type is None:
                i += 1
                continue
            
            func = ContractedFunction(
                shell_type=shell_type,
                element=current_element.element
            )
            
            # Read primitives
            for _ in range(n_primitives):
                i += 1
                if i >= len(lines):
                    break
                prim_line = lines[i].strip()
                parts = prim_line.split()
                if len(parts) >= 2:
                    # Handle D notation (1.234D+01 -> 1.234e+01)
                    exp_str = parts[0].replace('D', 'E').replace('d', 'e')
                    coef_str = parts[1].replace('D', 'E').replace('d', 'e')
                    exp_val = float(exp_str)
                    coef_val = float(coef_str)
                    func.add_primitive(exp_val, coef_val)
            
            current_element.add_function(func)
            i += 1
            continue
        
        # SP shell (combined S and P)
        sp_match = re.match(r'^SP\s+(\d+)\s+([\d.]+)', line, re.IGNORECASE)
        if sp_match and current_element is not None:
            n_primitives = int(sp_match.group(1))
            
            s_func = ContractedFunction(
                shell_type=ShellType.S,
                element=current_element.element
            )
            p_func = ContractedFunction(
                shell_type=ShellType.P,
                element=current_element.element
            )
            
            for _ in range(n_primitives):
                i += 1
                if i >= len(lines):
                    break
                prim_line = lines[i].strip()
                parts = prim_line.split()
                if len(parts) >= 3:
                    exp_str = parts[0].replace('D', 'E').replace('d', 'e')
                    s_coef_str = parts[1].replace('D', 'E').replace('d', 'e')
                    p_coef_str = parts[2].replace('D', 'E').replace('d', 'e')
                    
                    exp_val = float(exp_str)
                    s_func.add_primitive(exp_val, float(s_coef_str))
                    p_func.add_primitive(exp_val, float(p_coef_str))
            
            current_element.add_function(s_func)
            current_element.add_function(p_func)
            i += 1
            continue
        
        i += 1
    
    # Add last element if present
    if current_element is not None and current_element.functions:
        basis_data.add_element_basis(current_element)
    
    return basis_data


def parse_nwchem_basis(content: str, name: str = "Unknown") -> BasisSetData:
    """
    Parse an NWChem format basis set file.
    
    NWChem format example:
    BASIS "ao basis" PRINT
    #BASIS SET: ...
    H    S
          3.42525091           0.15432897
          0.62391373           0.53532814
          0.16885540           0.44463454
    END
    
    Args:
        content: File content as string
        name: Name for the basis set
        
    Returns:
        BasisSetData object
    """
    basis_data = BasisSetData(name=name)
    
    lines = content.strip().split('\n')
    i = 0
    current_element: Optional[ElementBasis] = None
    current_function: Optional[ContractedFunction] = None
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip BASIS line, comments, and END
        if (line.upper().startswith('BASIS') or 
            line.startswith('#') or 
            line.upper() == 'END' or
            not line):
            i += 1
            continue
        
        # Element and shell line: "H    S" or "C    SP"
        elem_shell_match = re.match(r'^([A-Za-z]{1,2})\s+([SPDFGHI]+)', line, re.IGNORECASE)
        if elem_shell_match:
            # Save previous function
            if current_function is not None and current_element is not None:
                current_element.add_function(current_function)
            
            element = elem_shell_match.group(1).capitalize()
            shell_str = elem_shell_match.group(2).upper()
            
            # Get or create element basis
            if current_element is None or current_element.element != element:
                if current_element is not None:
                    basis_data.add_element_basis(current_element)
                current_element = ElementBasis(element=element)
            
            shell_type = _parse_shell_type(shell_str[0].lower())
            if shell_type:
                current_function = ContractedFunction(
                    shell_type=shell_type,
                    element=element
                )
            else:
                current_function = None
            
            i += 1
            continue
        
        # Exponent/coefficient line
        parts = line.split()
        if len(parts) >= 2 and current_function is not None:
            exp_str = parts[0].replace('D', 'E').replace('d', 'e')
            coef_str = parts[1].replace('D', 'E').replace('d', 'e')
            
            exp_val = _safe_float(exp_str)
            coef_val = _safe_float(coef_str)
            
            if exp_val is not None and coef_val is not None:
                current_function.add_primitive(exp_val, coef_val)
        
        i += 1
    
    # Add last function and element
    if current_function is not None and current_element is not None:
        current_element.add_function(current_function)
    if current_element is not None:
        basis_data.add_element_basis(current_element)
    
    return basis_data


def parse_gaussian_basis(content: str, name: str = "Unknown") -> BasisSetData:
    """
    Parse a Gaussian format basis set (same as GBS).
    
    Args:
        content: File content as string
        name: Name for the basis set
        
    Returns:
        BasisSetData object
    """
    return parse_gbs_file(content, name)


def format_gbs_output(basis_data: BasisSetData) -> str:
    """
    Format basis set data as GBS format.
    
    Args:
        basis_data: BasisSetData object
        
    Returns:
        GBS format string
    """
    lines = []
    lines.append(f"! {basis_data.name}")
    if basis_data.description:
        lines.append(f"! {basis_data.description}")
    lines.append("")
    
    for element, element_basis in sorted(basis_data.elements.items()):
        lines.append("****")
        lines.append(f"{element}     0")
        
        for func in element_basis.functions:
            shell_char = func.shell_type.value.upper()
            n_prims = func.num_primitives
            lines.append(f"{shell_char}   {n_prims}   1.00")
            
            for prim in func.primitives:
                lines.append(f"     {prim.exponent:18.10f}     {prim.coefficient:18.10f}")
        
    lines.append("****")
    
    return "\n".join(lines)


def format_nwchem_output(basis_data: BasisSetData) -> str:
    """
    Format basis set data as NWChem format.
    
    Args:
        basis_data: BasisSetData object
        
    Returns:
        NWChem format string
    """
    lines = []
    lines.append(f'BASIS "ao basis" PRINT')
    lines.append(f"# {basis_data.name}")
    if basis_data.description:
        lines.append(f"# {basis_data.description}")
    
    for element, element_basis in sorted(basis_data.elements.items()):
        for func in element_basis.functions:
            shell_char = func.shell_type.value.upper()
            lines.append(f"{element}    {shell_char}")
            
            for prim in func.primitives:
                lines.append(f"     {prim.exponent:18.10f}     {prim.coefficient:18.10f}")
    
    lines.append("END")
    
    return "\n".join(lines)


def _parse_shell_type(char: str) -> Optional[ShellType]:
    """Convert shell character to ShellType enum."""
    char_lower = char.lower()
    shell_map = {
        's': ShellType.S,
        'p': ShellType.P,
        'd': ShellType.D,
        'f': ShellType.F,
        'g': ShellType.G,
        'h': ShellType.H,
        'i': ShellType.I,
    }
    return shell_map.get(char_lower)


def _safe_float(s: str) -> Optional[float]:
    """Safely parse a float string."""
    if not s:
        return None
    # Handle Fortran D notation
    s = s.replace('D', 'E').replace('d', 'e')
    # Check if it's a valid number
    if not re.match(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$', s):
        return None
    result = float(s)
    return result


def validate_basis_data(basis_data: BasisSetData) -> Tuple[bool, List[str]]:
    """
    Validate basis set data for common issues.
    
    Args:
        basis_data: BasisSetData to validate
        
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    if not basis_data.name:
        errors.append("Basis set has no name")
    
    if not basis_data.elements:
        errors.append("Basis set has no elements defined")
    
    for element, elem_basis in basis_data.elements.items():
        if not elem_basis.functions:
            errors.append(f"Element {element} has no basis functions")
            continue
        
        for i, func in enumerate(elem_basis.functions):
            if not func.primitives:
                errors.append(f"Element {element} function {i} has no primitives")
                continue
            
            for j, prim in enumerate(func.primitives):
                if prim.exponent <= 0:
                    errors.append(
                        f"Element {element} function {i} primitive {j} "
                        f"has non-positive exponent: {prim.exponent}"
                    )
    
    is_valid = len(errors) == 0
    return is_valid, errors


def compare_basis_sets(
    basis1: BasisSetData,
    basis2: BasisSetData,
) -> Dict[str, any]:
    """
    Compare two basis sets.
    
    Args:
        basis1: First basis set
        basis2: Second basis set
        
    Returns:
        Dictionary with comparison results
    """
    elements1 = set(basis1.elements.keys())
    elements2 = set(basis2.elements.keys())
    
    common_elements = elements1 & elements2
    only_in_first = elements1 - elements2
    only_in_second = elements2 - elements1
    
    element_comparisons = {}
    for elem in common_elements:
        eb1 = basis1.elements[elem]
        eb2 = basis2.elements[elem]
        element_comparisons[elem] = {
            "functions_in_first": eb1.n_functions,
            "functions_in_second": eb2.n_functions,
            "primitives_in_first": eb1.n_primitives,
            "primitives_in_second": eb2.n_primitives,
        }
    
    return {
        "name1": basis1.name,
        "name2": basis2.name,
        "common_elements": sorted(common_elements),
        "only_in_first": sorted(only_in_first),
        "only_in_second": sorted(only_in_second),
        "element_comparisons": element_comparisons,
    }
