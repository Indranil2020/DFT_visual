"""
XC Functionals module for DFT Flight Simulator.

Calculates enhancement factors and XC potentials for different functionals.
All functions return None on failure (no exceptions).
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

from utils.validators import validate_element, validate_functional
from utils.constants import ELEMENTS, FUNCTIONAL_INFO


# Load functional database
FUNCTIONAL_DB_FILE = Path("data/libxc_functionals.json")


def load_functional_database() -> Optional[dict]:
    """
    Load XC functional database.
    
    Returns:
        Database dictionary or None if not found
    """
    if not FUNCTIONAL_DB_FILE.exists():
        return None
    
    with open(FUNCTIONAL_DB_FILE, 'r') as f:
        db = json.load(f)
    
    return db if db else None


def get_available_functionals() -> List[str]:
    """
    Get list of all available XC functionals.
    
    Returns:
        List of functional names
    """
    db = load_functional_database()
    if db is None:
        return []
    
    return list(db.get('functionals', {}).keys())


def get_functional_info(functional: str) -> Optional[dict]:
    """
    Get detailed information about a functional.
    
    Args:
        functional: Functional name
        
    Returns:
        Info dictionary or None if not found
    """
    validated = validate_functional(functional)
    if validated is None:
        return None
    
    db = load_functional_database()
    if db is None:
        return None
    
    functionals = db.get('functionals', {})
    return functionals.get(validated)


def calculate_lda_enhancement(s: np.ndarray) -> np.ndarray:
    """
    Calculate LDA enhancement factor.
    
    For LDA, F_x(s) = 1.0 (constant, no gradient dependence)
    
    Args:
        s: Reduced gradient array
        
    Returns:
        Enhancement factor array (all ones)
    """
    return np.ones_like(s)


def calculate_pbe_enhancement(s: np.ndarray) -> np.ndarray:
    """
    Calculate PBE enhancement factor.
    
    F_x^PBE(s) = 1 + κ - κ/(1 + μs²/κ)
    
    Parameters:
        κ (kappa) = 0.804
        μ (mu) = 0.21951
    
    Args:
        s: Reduced gradient array
        
    Returns:
        Enhancement factor array
    """
    kappa = 0.804
    mu = 0.21951
    
    F_x = 1.0 + kappa - kappa / (1.0 + mu * s**2 / kappa)
    return F_x


def calculate_b88_enhancement(s: np.ndarray) -> np.ndarray:
    """
    Calculate Becke88 enhancement factor.
    
    F_x^B88(s) = 1 + (β/κ) * x²/(1 + 6βx * sinh⁻¹(x))
    where x = s and β = 0.0042
    
    Args:
        s: Reduced gradient array
        
    Returns:
        Enhancement factor array
    """
    beta = 0.0042
    kappa = 0.804  # Standard value
    
    x = s
    # Avoid division by zero
    x_safe = np.where(np.abs(x) < 1e-10, 1e-10, x)
    
    # sinh^-1(x) = ln(x + sqrt(x^2 + 1))
    asinh_x = np.arcsinh(x_safe)
    
    denominator = 1.0 + 6.0 * beta * x_safe * asinh_x
    denominator_safe = np.where(np.abs(denominator) < 1e-10, 1e-10, denominator)
    
    F_x = 1.0 + (beta / kappa) * x**2 / denominator_safe
    return F_x


def calculate_rpbe_enhancement(s: np.ndarray) -> np.ndarray:
    """
    Calculate RPBE (revised PBE) enhancement factor.
    
    F_x^RPBE(s) = 1 + κ(1 - exp(-μs²/κ))
    
    Args:
        s: Reduced gradient array
        
    Returns:
        Enhancement factor array
    """
    kappa = 0.804
    mu = 0.21951
    
    F_x = 1.0 + kappa * (1.0 - np.exp(-mu * s**2 / kappa))
    return F_x


def calculate_pw91_enhancement(s: np.ndarray) -> np.ndarray:
    """
    Calculate PW91 enhancement factor (simplified).
    
    Similar to PBE but with different parameters.
    
    Args:
        s: Reduced gradient array
        
    Returns:
        Enhancement factor array
    """
    # PW91 is complex, using simplified form similar to PBE
    a = 0.19645
    b = 7.7956
    c = 0.2743
    d = 0.1508
    
    s2 = s**2
    s4 = s2**2
    
    F_x = 1.0 + a * s2 + b * s4 + c * s4 * s2 + d * s4 * s4
    
    # Limit growth for numerical stability
    F_x = np.minimum(F_x, 3.0)
    return F_x


def get_enhancement_comparison(
    functionals: List[str],
    s_range: Tuple[float, float] = (0.0, 4.0),
    n_points: int = 200
) -> Optional[dict]:
    """
    Calculate enhancement factors for multiple functionals.
    
    Args:
        functionals: List of functional names
        s_range: (min, max) for reduced gradient
        n_points: Number of points
        
    Returns:
        Dictionary with {functional: {'s': array, 'F': array}} or None
    """
    if not functionals:
        return None
    
    # Create reduced gradient array
    s = np.linspace(s_range[0], s_range[1], n_points)
    
    result = {}
    
    for func_name in functionals:
        func_upper = func_name.upper()
        
        # Calculate enhancement factor based on functional type
        if 'LDA' in func_upper or func_upper == 'SVWN':
            F = calculate_lda_enhancement(s)
        elif func_upper == 'PBE':
            F = calculate_pbe_enhancement(s)
        elif func_upper == 'B88' or 'B88' in func_upper:
            F = calculate_b88_enhancement(s)
        elif func_upper == 'RPBE':
            F = calculate_rpbe_enhancement(s)
        elif func_upper == 'PW91':
            F = calculate_pw91_enhancement(s)
        elif func_upper == 'BLYP':
            # BLYP uses B88 exchange
            F = calculate_b88_enhancement(s)
        elif func_upper == 'PBESOL':
            # PBEsol is similar to PBE with different parameters
            F = calculate_pbe_enhancement(s) * 0.95  # Approximate
        else:
            # Default to PBE-like
            F = calculate_pbe_enhancement(s)
        
        result[func_name] = {
            's': s,
            'F': F
        }
    
    return result if result else None


def calculate_fermi_wavevector(rho: np.ndarray) -> np.ndarray:
    """
    Calculate Fermi wavevector k_F = (3π²ρ)^(1/3).
    
    Args:
        rho: Electron density
        
    Returns:
        Fermi wavevector array
    """
    rho_safe = np.where(rho > 1e-10, rho, 1e-10)
    k_F = (3.0 * np.pi**2 * rho_safe)**(1.0/3.0)
    return k_F


def calculate_reduced_gradient(rho: np.ndarray, grad_rho: np.ndarray) -> np.ndarray:
    """
    Calculate reduced gradient s = |∇ρ|/(2k_F ρ).
    
    Args:
        rho: Electron density
        grad_rho: Gradient of density
        
    Returns:
        Reduced gradient array
    """
    rho_safe = np.where(rho > 1e-10, rho, 1e-10)
    k_F = calculate_fermi_wavevector(rho_safe)
    
    s = np.abs(grad_rho) / (2.0 * k_F * rho_safe)
    return s


def calculate_lda_exchange_energy_density(rho: np.ndarray) -> np.ndarray:
    """
    Calculate LDA exchange energy density.
    
    ε_x^LDA = -C_x * ρ^(4/3)
    where C_x = (3/4)(3/π)^(1/3)
    
    Args:
        rho: Electron density
        
    Returns:
        Exchange energy density
    """
    C_x = (3.0/4.0) * (3.0/np.pi)**(1.0/3.0)
    rho_safe = np.where(rho > 1e-10, rho, 1e-10)
    
    epsilon_x = -C_x * rho_safe**(4.0/3.0)
    return epsilon_x


def get_functional_family(functional: str) -> Optional[str]:
    """
    Determine functional family (LDA, GGA, Hybrid, meta-GGA).
    
    Args:
        functional: Functional name
        
    Returns:
        Family string or None
    """
    info = get_functional_info(functional)
    if info is None:
        return None
    
    return info.get('type')


def compare_functionals_simple(
    func1: str,
    func2: str,
    s_range: Tuple[float, float] = (0.0, 4.0),
    n_points: int = 200
) -> Optional[dict]:
    """
    Simple comparison of two functionals (enhancement factors only).
    
    Args:
        func1: First functional name
        func2: Second functional name
        s_range: Range for reduced gradient
        n_points: Number of points
        
    Returns:
        Comparison dictionary or None
    """
    data = get_enhancement_comparison([func1, func2], s_range, n_points)
    if data is None:
        return None
    
    if func1 not in data or func2 not in data:
        return None
    
    s = data[func1]['s']
    F1 = data[func1]['F']
    F2 = data[func2]['F']
    
    return {
        's': s,
        'F1': F1,
        'F2': F2,
        'diff': F1 - F2,
        'func1': func1,
        'func2': func2,
        'max_diff': np.max(np.abs(F1 - F2)),
        'max_diff_location': s[np.argmax(np.abs(F1 - F2))]
    }


def get_functional_recommendations(use_case: str) -> List[str]:
    """
    Get recommended functionals for a specific use case.
    
    Args:
        use_case: One of 'molecules', 'solids', 'fast', 'accurate', 'general'
        
    Returns:
        List of recommended functional names
    """
    recommendations = {
        'molecules': ['B3LYP', 'PBE0', 'wB97X', 'M06-2X'],
        'solids': ['PBE', 'PBEsol', 'HSE06', 'SCAN'],
        'fast': ['LDA', 'PBE', 'BLYP'],
        'accurate': ['wB97X', 'M06-2X', 'SCAN', 'PBE0'],
        'general': ['PBE', 'B3LYP', 'PBE0', 'TPSS'],
        'thermochemistry': ['B3LYP', 'M06-2X', 'wB97X'],
        'band_gaps': ['HSE06', 'PBE0', 'B3LYP'],
        'weak_interactions': ['wB97X', 'M06-2X', 'BLYP']
    }
    
    return recommendations.get(use_case.lower(), ['PBE', 'B3LYP'])


def get_jacobs_ladder_info() -> dict:
    """
    Get information about Jacob's Ladder of DFT functionals.
    
    Returns:
        Dictionary with ladder information
    """
    return {
        'rungs': {
            1: {
                'name': 'LDA',
                'description': 'Local Density Approximation',
                'depends_on': 'ρ(r) only',
                'examples': ['LDA', 'SVWN'],
                'accuracy': 'Low',
                'cost': 'Very Fast'
            },
            2: {
                'name': 'GGA',
                'description': 'Generalized Gradient Approximation',
                'depends_on': 'ρ(r) and ∇ρ(r)',
                'examples': ['PBE', 'BLYP', 'PW91'],
                'accuracy': 'Medium',
                'cost': 'Fast'
            },
            3: {
                'name': 'meta-GGA',
                'description': 'Meta-GGA',
                'depends_on': 'ρ(r), ∇ρ(r), and τ(r)',
                'examples': ['TPSS', 'SCAN', 'M06-L'],
                'accuracy': 'High',
                'cost': 'Medium'
            },
            4: {
                'name': 'Hybrid',
                'description': 'Hybrid functionals',
                'depends_on': 'DFT + exact exchange',
                'examples': ['B3LYP', 'PBE0', 'HSE06'],
                'accuracy': 'Very High',
                'cost': 'Slow'
            },
            5: {
                'name': 'Double-Hybrid',
                'description': 'Double-hybrid functionals',
                'depends_on': 'DFT + exact exchange + MP2',
                'examples': ['B2PLYP'],
                'accuracy': 'Highest',
                'cost': 'Very Slow'
            }
        },
        'climbing_ladder': 'Higher rungs = more accurate but more expensive'
    }


# ==================== EXPORT ====================

__all__ = [
    'load_functional_database',
    'get_available_functionals',
    'get_functional_info',
    'calculate_lda_enhancement',
    'calculate_pbe_enhancement',
    'calculate_b88_enhancement',
    'calculate_rpbe_enhancement',
    'get_enhancement_comparison',
    'calculate_reduced_gradient',
    'compare_functionals_simple',
    'get_functional_recommendations',
    'get_jacobs_ladder_info',
]
