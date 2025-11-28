"""
Input validation functions for DFT Flight Simulator.

All validators return None on failure (no exceptions raised).
This follows the project's no-try/except policy.
"""

from typing import Union, Optional
from utils.constants import (
    ELEMENTS,
    ATOMIC_NUMBERS,
    FUNCTIONAL_INFO,
    PSEUDO_ACCURACY,
)


def validate_element(element: Union[int, str]) -> Optional[int]:
    """
    Validate element input and return atomic number.
    
    Args:
        element: Either atomic number (int) or element symbol (str)
        
    Returns:
        Atomic number if valid, None otherwise
        
    Examples:
        >>> validate_element(6)
        6
        >>> validate_element('C')
        6
        >>> validate_element('Carbon')
        None
        >>> validate_element(999)
        None
    """
    if element is None:
        return None
    
    # If integer, check if it's a valid atomic number
    if isinstance(element, int):
        if element in ELEMENTS:
            return element
        return None
    
    # If string, try to convert to atomic number
    if isinstance(element, str):
        # Remove whitespace and convert to uppercase
        symbol = element.strip().upper()
        
        # Check if it's a valid symbol
        if symbol in ATOMIC_NUMBERS:
            return ATOMIC_NUMBERS[symbol]
        
        # Try lowercase (e.g., 'He' not 'HE')
        symbol_proper = element.strip().capitalize()
        if symbol_proper in ATOMIC_NUMBERS:
            return ATOMIC_NUMBERS[symbol_proper]
    
    return None


def validate_basis_set(basis_name: str) -> Optional[str]:
    """
    Validate basis set name.
    
    Args:
        basis_name: Name of basis set
        
    Returns:
        Normalized basis set name if valid, None otherwise
        
    Note:
        This is a simple check. Full validation requires checking
        against basis-set-exchange library.
    """
    if basis_name is None:
        return None
    
    if not isinstance(basis_name, str):
        return None
    
    # Remove whitespace
    name = basis_name.strip()
    
    if len(name) == 0:
        return None
    
    # Basis set names should not be empty or just whitespace
    return name


def validate_functional(functional: str) -> Optional[str]:
    """
    Validate XC functional name.
    
    Args:
        functional: Name of XC functional
        
    Returns:
        Normalized functional name if valid, None otherwise
        
    Examples:
        >>> validate_functional('PBE')
        'PBE'
        >>> validate_functional('pbe')
        'PBE'
        >>> validate_functional('INVALID')
        None
    """
    if functional is None:
        return None
    
    if not isinstance(functional, str):
        return None
    
    # Normalize: uppercase and strip whitespace
    func = functional.strip().upper()
    
    if len(func) == 0:
        return None
    
    # Check if it's in our known functionals
    if func in FUNCTIONAL_INFO:
        return func
    
    # Check case-insensitive match
    for known_func in FUNCTIONAL_INFO.keys():
        if func == known_func.upper():
            return known_func
    
    return None


def validate_pseudo_accuracy(accuracy: str) -> Optional[str]:
    """
    Validate pseudopotential accuracy level.
    
    Args:
        accuracy: Accuracy level ('standard' or 'stringent')
        
    Returns:
        Normalized accuracy level if valid, None otherwise
        
    Examples:
        >>> validate_pseudo_accuracy('standard')
        'standard'
        >>> validate_pseudo_accuracy('STRINGENT')
        'stringent'
        >>> validate_pseudo_accuracy('medium')
        None
    """
    if accuracy is None:
        return None
    
    if not isinstance(accuracy, str):
        return None
    
    # Normalize: lowercase and strip
    acc = accuracy.strip().lower()
    
    if acc in PSEUDO_ACCURACY:
        return acc
    
    return None


def validate_url_response(status_code: int) -> bool:
    """
    Check if HTTP response status code indicates success.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if successful (2xx), False otherwise
        
    Examples:
        >>> validate_url_response(200)
        True
        >>> validate_url_response(404)
        False
    """
    if status_code is None:
        return False
    
    if not isinstance(status_code, int):
        return False
    
    # 2xx status codes are successful
    return 200 <= status_code < 300


def validate_grid_points(points: int, min_points: int = 10, max_points: int = 200) -> Optional[int]:
    """
    Validate number of grid points for visualization.
    
    Args:
        points: Number of grid points
        min_points: Minimum allowed points
        max_points: Maximum allowed points
        
    Returns:
        Number of points if valid, None otherwise
        
    Examples:
        >>> validate_grid_points(50)
        50
        >>> validate_grid_points(5)
        None
        >>> validate_grid_points(300)
        None
    """
    if points is None:
        return None
    
    if not isinstance(points, int):
        return None
    
    if min_points <= points <= max_points:
        return points
    
    return None


def validate_orbital_type(orbital_type: str) -> Optional[str]:
    """
    Validate orbital type string.
    
    Args:
        orbital_type: Orbital type ('s', 'p', 'p_x', 'd', 'f', etc.)
        
    Returns:
        Normalized orbital type if valid, None otherwise
        
    Examples:
        >>> validate_orbital_type('s')
        's'
        >>> validate_orbital_type('p_x')
        'p_x'
        >>> validate_orbital_type('invalid')
        None
    """
    if orbital_type is None:
        return None
    
    if not isinstance(orbital_type, str):
        return None
    
    # Normalize: lowercase and strip
    orb = orbital_type.strip().lower()
    
    # Valid orbital types
    valid_types = ['s', 'p', 'p_x', 'p_y', 'p_z', 'd', 'f']
    
    if orb in valid_types:
        return orb
    
    return None


def validate_positive_number(value: Union[int, float]) -> Optional[Union[int, float]]:
    """
    Validate that a number is positive.
    
    Args:
        value: Number to validate
        
    Returns:
        The value if positive, None otherwise
        
    Examples:
        >>> validate_positive_number(5.0)
        5.0
        >>> validate_positive_number(-1)
        None
        >>> validate_positive_number(0)
        None
    """
    if value is None:
        return None
    
    if not isinstance(value, (int, float)):
        return None
    
    if value > 0:
        return value
    
    return None


def validate_file_content(content: str, min_length: int = 10) -> Optional[str]:
    """
    Validate file content (e.g., UPF file content).
    
    Args:
        content: File content string
        min_length: Minimum content length
        
    Returns:
        Content if valid, None otherwise
    """
    if content is None:
        return None
    
    if not isinstance(content, str):
        return None
    
    if len(content) < min_length:
        return None
    
    return content


def validate_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float]) -> Optional[Union[int, float]]:
    """
    Validate that a value is within a specified range.
    
    Args:
        value: Value to check
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        
    Returns:
        The value if in range, None otherwise
        
    Examples:
        >>> validate_range(5, 0, 10)
        5
        >>> validate_range(15, 0, 10)
        None
    """
    if value is None:
        return None
    
    if not isinstance(value, (int, float)):
        return None
    
    if min_val <= value <= max_val:
        return value
    
    return None


# ==================== EXPORT ====================

__all__ = [
    'validate_element',
    'validate_basis_set',
    'validate_functional',
    'validate_pseudo_accuracy',
    'validate_url_response',
    'validate_grid_points',
    'validate_orbital_type',
    'validate_positive_number',
    'validate_file_content',
    'validate_range',
]
