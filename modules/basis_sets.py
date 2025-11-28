"""
Basis set module for DFT Flight Simulator.

Handles fetching, parsing, and analyzing basis sets from basis-set-exchange.
All functions return None on failure (no exceptions).
"""

import numpy as np
import basis_set_exchange as bse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union

from utils.validators import validate_element, validate_basis_set
from utils.constants import ELEMENTS, ANGULAR_MOMENTUM


# Cache directory
CACHE_DIR = Path("data")
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BASIS_CACHE_FILE = CACHE_DIR / "basis_cache.json"


def load_basis_cache() -> Optional[dict]:
    """
    Load basis set cache from file.
    
    Returns:
        Cache dictionary or None if not found
    """
    if not BASIS_CACHE_FILE.exists():
        return None
    
    with open(BASIS_CACHE_FILE, 'r') as f:
        cache = json.load(f)
    
    return cache if cache else None


def get_available_basis_sets() -> List[str]:
    """
    Get list of all available basis sets from basis-set-exchange.
    
    Returns:
        List of basis set names
    """
    basis_names = bse.get_all_basis_names()
    return sorted(basis_names) if basis_names else []


def get_basis_metadata(basis_name: str) -> Optional[dict]:
    """
    Get metadata for a basis set.
    
    Args:
        basis_name: Name of basis set
        
    Returns:
        Metadata dictionary or None if not found
    """
    validated_name = validate_basis_set(basis_name)
    if validated_name is None:
        return None
    
    basis_info = bse.get_basis(validated_name)
    return basis_info if basis_info else None


def get_available_elements_for_basis(basis_name: str) -> List[int]:
    """
    Get list of element atomic numbers that are available for a given basis set.
    
    Args:
        basis_name: Name of basis set
        
    Returns:
        List of atomic numbers (Z) that have this basis set available
    """
    validated_name = validate_basis_set(basis_name)
    if validated_name is None:
        return []
    
    try:
        # Get the basis set metadata which includes element list
        metadata = bse.get_metadata()
        if validated_name in metadata:
            basis_meta = metadata[validated_name]
            if 'elements' in basis_meta:
                # Convert element strings to atomic numbers
                available_z = []
                for elem_str in basis_meta['elements']:
                    # elem_str is like '1' for H, '6' for C, etc.
                    try:
                        available_z.append(int(elem_str))
                    except (ValueError, TypeError):
                        continue
                return sorted(available_z)
    except Exception:
        pass
    
    # Fallback: try to get basis for each element (slower but more reliable)
    available = []
    for z in range(1, 87):  # H to Fr
        try:
            data = bse.get_basis(validated_name, elements=[str(z)])
            if data and 'elements' in data and str(z) in data['elements']:
                available.append(z)
        except Exception:
            continue
    
    return available


def get_basis_for_element(basis_name: str, element: Union[int, str]) -> Optional[dict]:
    """
    Get basis set data for a specific element.
    
    Args:
        basis_name: Name of basis set
        element: Atomic number or symbol
        
    Returns:
        Basis set data dictionary or None if not available
    """
    # Validate inputs
    validated_name = validate_basis_set(basis_name)
    if validated_name is None:
        return None
    
    z = validate_element(element)
    if z is None:
        return None
    
    # Check if element is available in this basis set
    basis_info = bse.get_basis(validated_name)
    if basis_info is None:
        return None
    
    if str(z) not in basis_info['elements']:
        return None
    
    # Fetch basis set data
    basis_data = bse.get_basis(validated_name, elements=str(z))
    return basis_data if basis_data else None


def count_shells_by_type(basis_data: dict) -> dict:
    """
    Count number of shells by angular momentum type.
    
    Args:
        basis_data: Basis set data dictionary
        
    Returns:
        Dictionary of {shell_type: count}
    """
    if basis_data is None:
        return {}
    
    elem_data = list(basis_data['elements'].values())[0]
    shells = elem_data['electron_shells']
    
    counts = {'s': 0, 'p': 0, 'd': 0, 'f': 0, 'g': 0}
    
    for shell in shells:
        am = shell['angular_momentum'][0]
        shell_type = ANGULAR_MOMENTUM.get(am, 'unknown')
        if shell_type in counts:
            counts[shell_type] += 1
    
    return counts


def get_exponent_range(shell: dict) -> Tuple[float, float]:
    """
    Get min and max exponents for a shell.
    
    Args:
        shell: Shell dictionary
        
    Returns:
        (min_exponent, max_exponent)
    """
    if shell is None or 'exponents' not in shell:
        return (0.0, 0.0)
    
    exponents = [float(exp) for exp in shell['exponents']]
    if not exponents:
        return (0.0, 0.0)
    
    return (min(exponents), max(exponents))


def determine_zeta_level(basis_name: str, shell_counts: dict) -> str:
    """
    Determine zeta level (SZ, DZ, TZ, QZ, etc.) from basis set name and shell counts.
    
    Args:
        basis_name: Name of basis set
        shell_counts: Dictionary of shell counts
        
    Returns:
        Zeta level string
    """
    name_upper = basis_name.upper()
    
    # Check basis set name for explicit zeta indicators
    if 'STO-3G' in name_upper:
        return 'Minimal (STO-3G)'
    if '3-21G' in name_upper:
        return 'Split-Valence (3-21G)'
    if '6-31G' in name_upper:
        return 'Double-Zeta (6-31G)'
    if '6-311G' in name_upper:
        return 'Triple-Zeta (6-311G)'
    
    # Dunning basis sets
    if 'CC-PVDZ' in name_upper or 'DZ' in name_upper:
        return 'Double-Zeta (cc-pVDZ)'
    if 'CC-PVTZ' in name_upper or 'TZ' in name_upper:
        return 'Triple-Zeta (cc-pVTZ)'
    if 'CC-PVQZ' in name_upper or 'QZ' in name_upper:
        return 'Quadruple-Zeta (cc-pVQZ)'
    if 'CC-PV5Z' in name_upper or '5Z' in name_upper:
        return 'Quintuple-Zeta (cc-pV5Z)'
    
    # Ahlrichs basis sets
    if 'DEF2-SVP' in name_upper:
        return 'Split-Valence Polarized (def2-SVP)'
    if 'DEF2-TZVP' in name_upper:
        return 'Triple-Zeta Valence Polarized (def2-TZVP)'
    if 'DEF2-QZVP' in name_upper:
        return 'Quadruple-Zeta Valence Polarized (def2-QZVP)'
    
    # Fallback: analyze shell counts
    total_valence = shell_counts.get('s', 0) + shell_counts.get('p', 0)
    if total_valence <= 2:
        return 'Minimal/Single-Zeta'
    elif total_valence <= 4:
        return 'Double-Zeta'
    elif total_valence <= 6:
        return 'Triple-Zeta'
    else:
        return 'Quadruple-Zeta or higher'


def analyze_basis_set(basis_data: dict, basis_name: str) -> dict:
    """
    Comprehensive analysis of basis set characteristics.
    
    Args:
        basis_data: Basis set data dictionary
        basis_name: Name of basis set
        
    Returns:
        Analysis dictionary with zeta level, explanation, etc.
    """
    if basis_data is None:
        return {
            'zeta': 'Unknown',
            'explanation': 'Unable to analyze basis set',
            'shell_counts': {},
            'has_polarization': False,
            'has_diffuse': False
        }
    
    elem_data = list(basis_data['elements'].values())[0]
    shells = elem_data['electron_shells']
    
    # Count shells
    shell_counts = count_shells_by_type(basis_data)
    
    # Determine zeta level
    zeta = determine_zeta_level(basis_name, shell_counts)
    
    # Check for polarization functions
    has_polarization = shell_counts.get('d', 0) > 0 or shell_counts.get('f', 0) > 0
    
    # Check for diffuse functions (aug- prefix or diffuse in name)
    has_diffuse = 'aug' in basis_name.lower() or 'diffuse' in basis_name.lower()
    
    # Generate explanation
    explanation = f"This is a **{zeta}** basis set"
    
    if has_polarization:
        explanation += " with **polarization functions** (d, f orbitals)"
    
    if has_diffuse:
        explanation += " and **diffuse functions** for better description of anions and excited states"
    
    explanation += f".\n\n**Shell composition:** {shell_counts['s']} s-type, {shell_counts['p']} p-type"
    
    if shell_counts['d'] > 0:
        explanation += f", {shell_counts['d']} d-type"
    if shell_counts['f'] > 0:
        explanation += f", {shell_counts['f']} f-type"
    
    explanation += " shells."
    
    # Add use case recommendation
    if 'minimal' in zeta.lower() or 'STO-3G' in basis_name:
        explanation += "\n\n**Use case:** Quick qualitative calculations, teaching purposes."
    elif 'double' in zeta.lower():
        explanation += "\n\n**Use case:** Good balance of accuracy and speed for routine calculations."
    elif 'triple' in zeta.lower():
        explanation += "\n\n**Use case:** High accuracy for research-quality results."
    elif 'quadruple' in zeta.lower() or 'quintuple' in zeta.lower():
        explanation += "\n\n**Use case:** Benchmark calculations, very high accuracy needed."
    
    return {
        'zeta': zeta,
        'explanation': explanation,
        'shell_counts': shell_counts,
        'has_polarization': has_polarization,
        'has_diffuse': has_diffuse,
        'total_shells': len(shells)
    }


def calculate_radial_wavefunction(basis_data: dict, orbital_type: str, r_points: int = 200) -> Optional[dict]:
    """
    Calculate radial wavefunction for visualization.
    
    Args:
        basis_data: Basis set data
        orbital_type: Type of orbital ('s', 'p', 'd', 'f')
        r_points: Number of radial points
        
    Returns:
        Dictionary with r and psi arrays, or None if failed
    """
    if basis_data is None:
        return None
    
    elem_data = list(basis_data['elements'].values())[0]
    shells = elem_data['electron_shells']
    
    # Find first shell of requested type
    target_am = None
    if orbital_type == 's':
        target_am = 0
    elif orbital_type in ['p', 'p_x', 'p_y', 'p_z']:
        target_am = 1
    elif orbital_type == 'd':
        target_am = 2
    elif orbital_type == 'f':
        target_am = 3
    
    if target_am is None:
        return None
    
    # Find shell
    target_shell = None
    for shell in shells:
        if shell['angular_momentum'][0] == target_am:
            target_shell = shell
            break
    
    if target_shell is None:
        return None
    
    # Get exponents and coefficients
    exponents = [float(exp) for exp in target_shell['exponents']]
    coefficients = [float(coef) for coef in target_shell['coefficients'][0]]
    
    # Create radial grid
    r = np.linspace(0.01, 10.0, r_points)
    
    # Calculate radial part: sum of Gaussian primitives
    psi = np.zeros_like(r)
    for alpha, coef in zip(exponents, coefficients):
        # Gaussian: exp(-alpha * r^2)
        psi += coef * np.exp(-alpha * r**2)
    
    # Normalize
    psi = psi / np.max(np.abs(psi))
    
    return {
        'r': r,
        'psi': psi,
        'orbital_type': orbital_type,
        'angular_momentum': target_am
    }


def calculate_orbital_wavefunction(basis_data: dict, orbital_type: str, grid_points: int = 45) -> Optional[dict]:
    """
    Calculate 3D orbital wavefunction for visualization.
    
    Args:
        basis_data: Basis set data
        orbital_type: Type of orbital ('s', 'p_x', 'p_y', 'p_z', 'd', 'f')
        grid_points: Number of grid points per dimension
        
    Returns:
        Dictionary with X, Y, Z, psi arrays, or None if failed
    """
    if basis_data is None:
        return None
    
    elem_data = list(basis_data['elements'].values())[0]
    shells = elem_data['electron_shells']
    
    # Determine angular momentum
    if orbital_type == 's':
        am = 0
    elif 'p' in orbital_type:
        am = 1
    elif orbital_type == 'd':
        am = 2
    elif orbital_type == 'f':
        am = 3
    else:
        return None
    
    # Find shell
    target_shell = None
    for shell in shells:
        if shell['angular_momentum'][0] == am:
            target_shell = shell
            break
    
    if target_shell is None:
        return None
    
    # Get exponents and coefficients
    exponents = [float(exp) for exp in target_shell['exponents']]
    coefficients = [float(coef) for coef in target_shell['coefficients'][0]]
    
    # Set grid range based on orbital type
    if 'p' in orbital_type:
        grid_range = 4.0
    elif 'd' in orbital_type:
        grid_range = 3.5
    elif 'f' in orbital_type:
        grid_range = 4.0
    else:
        grid_range = 3.0
    
    # Create 3D grid
    x = np.linspace(-grid_range, grid_range, grid_points)
    y = np.linspace(-grid_range, grid_range, grid_points)
    z = np.linspace(-grid_range, grid_range, grid_points)
    X, Y, Z = np.meshgrid(x, y, z)
    
    # Calculate distance from origin
    r = np.sqrt(X**2 + Y**2 + Z**2)
    r = np.where(r < 0.01, 0.01, r)  # Avoid division by zero
    
    # Calculate radial part (Gaussian sum)
    radial = np.zeros_like(r)
    for alpha, coef in zip(exponents, coefficients):
        radial += coef * np.exp(-alpha * r**2)
    
    # Apply angular part
    if orbital_type == 's':
        psi = radial
    elif orbital_type == 'p_x':
        psi = radial * X / r
    elif orbital_type == 'p_y':
        psi = radial * Y / r
    elif orbital_type == 'p_z':
        psi = radial * Z / r
    elif orbital_type == 'd':
        # d_z2 orbital
        psi = radial * (3 * Z**2 - r**2) / r**2
    elif orbital_type == 'f':
        # f_z3 orbital
        psi = radial * Z * (5 * Z**2 - 3 * r**2) / r**3
    else:
        psi = radial
    
    return {
        'X': X,
        'Y': Y,
        'Z': Z,
        'psi': psi,
        'orbital_type': orbital_type
    }


def get_orbital_metadata(basis_data: dict, orbital_type: str) -> Optional[dict]:
    """
    Get metadata about a specific orbital.
    
    Args:
        basis_data: Basis set data
        orbital_type: Type of orbital
        
    Returns:
        Metadata dictionary or None
    """
    if basis_data is None:
        return None
    
    # Determine angular momentum
    if orbital_type == 's':
        am = 0
        description = "Spherical s-orbital"
    elif 'p' in orbital_type:
        am = 1
        if orbital_type == 'p_x':
            description = "p-orbital along x-axis (dumbbell shape)"
        elif orbital_type == 'p_y':
            description = "p-orbital along y-axis (dumbbell shape)"
        elif orbital_type == 'p_z':
            description = "p-orbital along z-axis (dumbbell shape)"
        else:
            description = "p-orbital"
    elif orbital_type == 'd':
        am = 2
        description = "d-orbital (cloverleaf shape)"
    elif orbital_type == 'f':
        am = 3
        description = "f-orbital (complex shape)"
    else:
        return None
    
    return {
        'angular_momentum': am,
        'symbol': ANGULAR_MOMENTUM.get(am, 'unknown'),
        'description': description,
        'orbital_type': orbital_type
    }


# ==================== EXPORT ====================

__all__ = [
    'load_basis_cache',
    'get_available_basis_sets',
    'get_basis_metadata',
    'get_basis_for_element',
    'count_shells_by_type',
    'analyze_basis_set',
    'calculate_radial_wavefunction',
    'calculate_orbital_wavefunction',
    'get_orbital_metadata',
]
