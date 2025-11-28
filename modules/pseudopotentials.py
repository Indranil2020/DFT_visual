"""
Pseudopotential module for DFT Flight Simulator.

Fetches, parses, and analyzes pseudopotentials from PseudoDojo.
All functions return None on failure (no exceptions).
"""

import numpy as np
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

from utils.validators import (
    validate_element,
    validate_pseudo_accuracy,
    validate_url_response,
    validate_file_content
)
from utils.constants import ELEMENTS, ATOMIC_NUMBERS


# PseudoDojo GitHub raw URL base
PSEUDODOJO_BASE_URL = "https://raw.githubusercontent.com/pseudo-dojo/pseudo-dojo/master/pseudo_dojo/pseudos"

# Cache directory
CACHE_DIR = Path("data/pseudo_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_available_pseudos() -> dict:
    """
    Get dictionary of available pseudopotentials.
    
    Returns:
        Dictionary: {element_symbol: {accuracies: [...], functionals: [...]}}
        
    Note:
        PseudoDojo provides:
        - Accuracies: 'standard' (soft), 'stringent' (hard)
        - Functionals: 'PBE', 'LDA', 'PW'
        - Elements: H-Rn (most elements)
    """
    # Comprehensive list of available pseudos from PseudoDojo
    available = {}
    
    # Elements with pseudopotentials in PseudoDojo (H to Rn, excluding lanthanides)
    pseudo_elements = list(range(1, 87))  # H to Rn
    # Remove lanthanides (57-71) as they're less common
    pseudo_elements = [z for z in pseudo_elements if z not in range(58, 72)]
    
    for z in pseudo_elements:
        symbol = ELEMENTS.get(z)
        if symbol:
            available[symbol] = {
                'Z': z,
                'accuracies': ['standard', 'stringent'],
                'functionals': ['PBE', 'LDA', 'PW'],
                'types': ['NC']  # Norm-conserving
            }
    
    return available


def construct_pseudo_url(element: str, accuracy: str, functional: str) -> Optional[str]:
    """
    Construct URL for pseudopotential file from PseudoDojo.
    
    Args:
        element: Element symbol (e.g., 'C', 'Si')
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        
    Returns:
        URL string or None if invalid inputs
        
    Example URL format:
        https://raw.githubusercontent.com/pseudo-dojo/pseudo-dojo/master/
        pseudo_dojo/pseudos/ONCVPSP-PBE-PDv0.4/standard/C.upf
    """
    # Validate inputs
    z = validate_element(element)
    if z is None:
        return None
    
    symbol = ELEMENTS.get(z)
    if symbol is None:
        return None
    
    acc = validate_pseudo_accuracy(accuracy)
    if acc is None:
        return None
    
    if functional not in ['PBE', 'LDA', 'PW']:
        return None
    
    # Construct URL
    # Format: ONCVPSP-{FUNCTIONAL}-PDv0.4/{accuracy}/{element}.upf
    pseudo_set = f"ONCVPSP-{functional}-PDv0.4"
    url = f"{PSEUDODOJO_BASE_URL}/{pseudo_set}/{acc}/{symbol}.upf"
    
    return url


def check_pseudo_exists(element: str, accuracy: str, functional: str) -> bool:
    """
    Check if pseudopotential exists without downloading.
    
    Args:
        element: Element symbol
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        
    Returns:
        True if exists, False otherwise
    """
    url = construct_pseudo_url(element, accuracy, functional)
    if url is None:
        return False
    
    response = requests.head(url, timeout=10)
    return validate_url_response(response.status_code)


def get_cache_path(element: str, accuracy: str, functional: str) -> Path:
    """
    Get cache file path for pseudopotential.
    
    Args:
        element: Element symbol
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        
    Returns:
        Path object for cache file
    """
    filename = f"{element}_{functional}_{accuracy}.upf"
    return CACHE_DIR / filename


def load_cached_pseudo(element: str, accuracy: str, functional: str) -> Optional[str]:
    """
    Load pseudopotential from cache if available.
    
    Args:
        element: Element symbol
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        
    Returns:
        UPF file content as string, or None if not cached
    """
    cache_path = get_cache_path(element, accuracy, functional)
    
    if not cache_path.exists():
        return None
    
    content = cache_path.read_text()
    return validate_file_content(content)


def cache_pseudo_file(element: str, accuracy: str, functional: str, content: str) -> bool:
    """
    Save pseudopotential content to cache.
    
    Args:
        element: Element symbol
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        content: UPF file content
        
    Returns:
        True if saved successfully, False otherwise
    """
    validated_content = validate_file_content(content)
    if validated_content is None:
        return False
    
    cache_path = get_cache_path(element, accuracy, functional)
    
    cache_path.write_text(validated_content)
    return cache_path.exists()


def fetch_pseudo_file(element: str, accuracy: str, functional: str, use_cache: bool = True) -> Optional[str]:
    """
    Fetch pseudopotential file from PseudoDojo or cache.
    
    Args:
        element: Element symbol
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        use_cache: If True, check cache first
        
    Returns:
        UPF file content as string, or None if failed
    """
    # Check cache first
    if use_cache:
        cached = load_cached_pseudo(element, accuracy, functional)
        if cached is not None:
            return cached
    
    # Construct URL
    url = construct_pseudo_url(element, accuracy, functional)
    if url is None:
        return None
    
    # Fetch from web
    response = requests.get(url, timeout=30)
    
    if not validate_url_response(response.status_code):
        return None
    
    content = response.text
    validated = validate_file_content(content)
    
    if validated is None:
        return None
    
    # Cache for future use
    cache_pseudo_file(element, accuracy, functional, validated)
    
    return validated


def parse_upf_header(upf_content: str) -> Optional[dict]:
    """
    Parse header information from UPF file.
    
    Args:
        upf_content: UPF XML content
        
    Returns:
        Dictionary with header info, or None if parsing failed
    """
    content = validate_file_content(upf_content)
    if content is None:
        return None
    
    root = ET.fromstring(content)
    if root is None:
        return None
    
    header = {}
    
    # Extract PP_INFO
    pp_info = root.find('.//PP_INFO')
    if pp_info is not None:
        header['info'] = pp_info.text.strip() if pp_info.text else ''
    
    # Extract PP_HEADER
    pp_header = root.find('.//PP_HEADER')
    if pp_header is not None:
        header['element'] = pp_header.get('element', '')
        header['pseudo_type'] = pp_header.get('pseudo_type', '')
        header['functional'] = pp_header.get('functional', '')
        header['z_valence'] = float(pp_header.get('z_valence', 0))
        header['l_max'] = int(pp_header.get('l_max', 0))
        header['mesh_size'] = int(pp_header.get('mesh_size', 0))
    
    return header if header else None


def parse_upf_mesh(upf_content: str) -> Optional[np.ndarray]:
    """
    Parse radial mesh from UPF file.
    
    Args:
        upf_content: UPF XML content
        
    Returns:
        Numpy array of radial grid points, or None if parsing failed
    """
    content = validate_file_content(upf_content)
    if content is None:
        return None
    
    root = ET.fromstring(content)
    if root is None:
        return None
    
    # Find PP_R (radial mesh)
    pp_r = root.find('.//PP_R')
    if pp_r is None or pp_r.text is None:
        return None
    
    # Parse values
    r_values = np.fromstring(pp_r.text, sep=' ')
    
    if len(r_values) == 0:
        return None
    
    return r_values


def parse_upf_local_potential(upf_content: str) -> Optional[np.ndarray]:
    """
    Parse local pseudopotential from UPF file.
    
    Args:
        upf_content: UPF XML content
        
    Returns:
        Numpy array of V_local values, or None if parsing failed
    """
    content = validate_file_content(upf_content)
    if content is None:
        return None
    
    root = ET.fromstring(content)
    if root is None:
        return None
    
    # Find PP_LOCAL
    pp_local = root.find('.//PP_LOCAL')
    if pp_local is None or pp_local.text is None:
        return None
    
    # Parse values
    v_local = np.fromstring(pp_local.text, sep=' ')
    
    if len(v_local) == 0:
        return None
    
    return v_local


def parse_upf_file(upf_content: str) -> Optional[dict]:
    """
    Parse complete UPF file.
    
    Args:
        upf_content: UPF XML content
        
    Returns:
        Dictionary with all parsed data, or None if parsing failed
    """
    header = parse_upf_header(upf_content)
    if header is None:
        return None
    
    r = parse_upf_mesh(upf_content)
    if r is None:
        return None
    
    v_local = parse_upf_local_potential(upf_content)
    if v_local is None:
        return None
    
    return {
        'header': header,
        'r': r,
        'v_local': v_local
    }


def calculate_coulomb_potential(r: np.ndarray, Z: int) -> np.ndarray:
    """
    Calculate Coulomb potential V(r) = -Z/r.
    
    Args:
        r: Radial grid (Bohr)
        Z: Atomic number
        
    Returns:
        Coulomb potential values
    """
    # Avoid division by zero
    r_safe = np.where(r > 1e-10, r, 1e-10)
    return -Z / r_safe


def calculate_pseudo_difference(v_pseudo: np.ndarray, v_coulomb: np.ndarray) -> np.ndarray:
    """
    Calculate difference between pseudopotential and Coulomb potential.
    
    Args:
        v_pseudo: Pseudopotential values
        v_coulomb: Coulomb potential values
        
    Returns:
        Difference array
    """
    return v_pseudo - v_coulomb


def find_core_radius(r: np.ndarray, v_diff: np.ndarray, threshold: float = 0.1) -> float:
    """
    Find core radius where pseudopotential significantly deviates from Coulomb.
    
    Args:
        r: Radial grid
        v_diff: Difference between pseudo and Coulomb
        threshold: Threshold for "significant" deviation
        
    Returns:
        Core radius in Bohr
    """
    # Find where |v_diff| > threshold * max(|v_diff|)
    max_diff = np.max(np.abs(v_diff))
    significant = np.abs(v_diff) > threshold * max_diff
    
    if not np.any(significant):
        return r[-1]  # No significant deviation
    
    # Find first point with significant deviation
    idx = np.where(significant)[0][0]
    return r[idx]


def get_pseudo_data(element: str, accuracy: str, functional: str) -> Optional[dict]:
    """
    Get complete pseudopotential data (fetch + parse).
    
    Args:
        element: Element symbol
        accuracy: 'standard' or 'stringent'
        functional: 'PBE', 'LDA', or 'PW'
        
    Returns:
        Dictionary with all data, or None if failed
    """
    # Fetch UPF file
    upf_content = fetch_pseudo_file(element, accuracy, functional)
    if upf_content is None:
        return None
    
    # Parse UPF file
    parsed = parse_upf_file(upf_content)
    if parsed is None:
        return None
    
    # Get atomic number
    z = validate_element(element)
    if z is None:
        return None
    
    # Calculate Coulomb potential
    v_coulomb = calculate_coulomb_potential(parsed['r'], z)
    
    # Calculate difference
    v_diff = calculate_pseudo_difference(parsed['v_local'], v_coulomb)
    
    # Find core radius
    r_core = find_core_radius(parsed['r'], v_diff)
    
    # Combine all data
    result = {
        'element': element,
        'Z': z,
        'accuracy': accuracy,
        'functional': functional,
        'header': parsed['header'],
        'r': parsed['r'],
        'v_local': parsed['v_local'],
        'v_coulomb': v_coulomb,
        'v_diff': v_diff,
        'r_core': r_core
    }
    
    return result


def compare_pseudos(element: str, acc1: str, acc2: str, functional: str) -> Optional[dict]:
    """
    Compare two pseudopotentials (different accuracies).
    
    Args:
        element: Element symbol
        acc1: First accuracy level
        acc2: Second accuracy level
        functional: XC functional
        
    Returns:
        Comparison dictionary, or None if failed
    """
    # Get both pseudopotentials
    pseudo1 = get_pseudo_data(element, acc1, functional)
    if pseudo1 is None:
        return None
    
    pseudo2 = get_pseudo_data(element, acc2, functional)
    if pseudo2 is None:
        return None
    
    # Interpolate to common grid if needed
    r_common = pseudo1['r']  # Use first grid as reference
    
    return {
        'element': element,
        'functional': functional,
        'accuracy1': acc1,
        'accuracy2': acc2,
        'r': r_common,
        'v1': pseudo1['v_local'],
        'v2': pseudo2['v_local'],
        'diff': pseudo1['v_local'] - pseudo2['v_local'],
        'r_core1': pseudo1['r_core'],
        'r_core2': pseudo2['r_core']
    }


# ==================== EXPORT ====================

__all__ = [
    'get_available_pseudos',
    'construct_pseudo_url',
    'check_pseudo_exists',
    'fetch_pseudo_file',
    'parse_upf_file',
    'calculate_coulomb_potential',
    'get_pseudo_data',
    'compare_pseudos',
]
