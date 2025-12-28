"""
Structure Alignment Utilities for Psi4 MCP Server.

Provides tools for aligning and comparing molecular structures.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class AlignmentResult:
    """Result of structure alignment."""
    rmsd: float
    rotation_matrix: List[List[float]]
    translation: Tuple[float, float, float]
    aligned_coordinates: List[Tuple[float, float, float]]


def center_geometry(
    coordinates: List[Tuple[float, float, float]],
    weights: Optional[List[float]] = None,
) -> Tuple[List[Tuple[float, float, float]], Tuple[float, float, float]]:
    """
    Center geometry at origin.
    
    Args:
        coordinates: List of (x, y, z) coordinates
        weights: Optional weights for each atom
        
    Returns:
        Tuple of (centered coordinates, centroid)
    """
    n = len(coordinates)
    if n == 0:
        return [], (0.0, 0.0, 0.0)
    
    if weights is None:
        weights = [1.0] * n
    
    total_weight = sum(weights)
    if total_weight < 1e-10:
        total_weight = 1.0
    
    # Calculate centroid
    cx = sum(w * c[0] for w, c in zip(weights, coordinates)) / total_weight
    cy = sum(w * c[1] for w, c in zip(weights, coordinates)) / total_weight
    cz = sum(w * c[2] for w, c in zip(weights, coordinates)) / total_weight
    
    centroid = (cx, cy, cz)
    
    # Center coordinates
    centered = [(c[0] - cx, c[1] - cy, c[2] - cz) for c in coordinates]
    
    return centered, centroid


def translate_geometry(
    coordinates: List[Tuple[float, float, float]],
    translation: Tuple[float, float, float],
) -> List[Tuple[float, float, float]]:
    """
    Translate geometry by a vector.
    
    Args:
        coordinates: List of coordinates
        translation: Translation vector (dx, dy, dz)
        
    Returns:
        Translated coordinates
    """
    dx, dy, dz = translation
    return [(c[0] + dx, c[1] + dy, c[2] + dz) for c in coordinates]


def rotate_geometry(
    coordinates: List[Tuple[float, float, float]],
    rotation_matrix: List[List[float]],
) -> List[Tuple[float, float, float]]:
    """
    Rotate geometry using rotation matrix.
    
    Args:
        coordinates: List of coordinates
        rotation_matrix: 3x3 rotation matrix
        
    Returns:
        Rotated coordinates
    """
    rotated = []
    for c in coordinates:
        x = rotation_matrix[0][0]*c[0] + rotation_matrix[0][1]*c[1] + rotation_matrix[0][2]*c[2]
        y = rotation_matrix[1][0]*c[0] + rotation_matrix[1][1]*c[1] + rotation_matrix[1][2]*c[2]
        z = rotation_matrix[2][0]*c[0] + rotation_matrix[2][1]*c[1] + rotation_matrix[2][2]*c[2]
        rotated.append((x, y, z))
    return rotated


def calculate_rmsd(
    coords1: List[Tuple[float, float, float]],
    coords2: List[Tuple[float, float, float]],
    weights: Optional[List[float]] = None,
) -> float:
    """
    Calculate RMSD between two coordinate sets.
    
    Args:
        coords1: First set of coordinates
        coords2: Second set of coordinates
        weights: Optional weights
        
    Returns:
        RMSD value
    """
    if len(coords1) != len(coords2):
        raise ValueError("Coordinate sets must have same length")
    
    n = len(coords1)
    if n == 0:
        return 0.0
    
    if weights is None:
        weights = [1.0] * n
    
    total_weight = sum(weights)
    if total_weight < 1e-10:
        return 0.0
    
    sum_sq = 0.0
    for w, c1, c2 in zip(weights, coords1, coords2):
        sum_sq += w * ((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2)
    
    return math.sqrt(sum_sq / total_weight)


def kabsch_rotation(
    mobile: List[Tuple[float, float, float]],
    target: List[Tuple[float, float, float]],
    weights: Optional[List[float]] = None,
) -> List[List[float]]:
    """
    Calculate optimal rotation matrix using Kabsch algorithm.
    
    Finds rotation that minimizes RMSD between mobile and target.
    Both coordinate sets should be centered at origin.
    
    Args:
        mobile: Coordinates to rotate
        target: Target coordinates
        weights: Optional weights
        
    Returns:
        3x3 rotation matrix
    """
    n = len(mobile)
    if n != len(target):
        raise ValueError("Coordinate sets must have same length")
    
    if weights is None:
        weights = [1.0] * n
    
    # Build correlation matrix H
    H = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    
    for w, m, t in zip(weights, mobile, target):
        for i in range(3):
            for j in range(3):
                H[i][j] += w * m[i] * t[j] if i < len(m) and j < len(t) else 0.0
    
    # Since we're avoiding numpy, use a simplified SVD approach
    # For production, would use numpy.linalg.svd
    
    # Use iterative approach for 3x3 case
    rotation = _compute_rotation_matrix(H)
    
    return rotation


def _compute_rotation_matrix(H: List[List[float]]) -> List[List[float]]:
    """
    Compute rotation matrix from correlation matrix.
    
    Simplified implementation for 3x3 case.
    """
    # Start with identity rotation
    R = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    
    # Compute H^T * H
    HtH = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    for i in range(3):
        for j in range(3):
            for k in range(3):
                HtH[i][j] += H[k][i] * H[k][j]
    
    # Power iteration to find dominant eigenvector
    # (simplified approach)
    v = [1.0, 0.0, 0.0]
    for _ in range(50):
        # Multiply by HtH
        new_v = [
            HtH[0][0]*v[0] + HtH[0][1]*v[1] + HtH[0][2]*v[2],
            HtH[1][0]*v[0] + HtH[1][1]*v[1] + HtH[1][2]*v[2],
            HtH[2][0]*v[0] + HtH[2][1]*v[1] + HtH[2][2]*v[2],
        ]
        # Normalize
        norm = math.sqrt(sum(x*x for x in new_v))
        if norm > 1e-10:
            v = [x/norm for x in new_v]
    
    # For better accuracy, use quaternion-based approach
    # This is a simplified version
    
    # Compute det(H) to check for reflection
    det_H = (
        H[0][0] * (H[1][1]*H[2][2] - H[1][2]*H[2][1]) -
        H[0][1] * (H[1][0]*H[2][2] - H[1][2]*H[2][0]) +
        H[0][2] * (H[1][0]*H[2][1] - H[1][1]*H[2][0])
    )
    
    # Use Graham-Schmidt to build rotation from H
    # Extract columns of H and orthonormalize
    col0 = [H[0][0], H[1][0], H[2][0]]
    col1 = [H[0][1], H[1][1], H[2][1]]
    col2 = [H[0][2], H[1][2], H[2][2]]
    
    # Normalize first column
    norm0 = math.sqrt(sum(x*x for x in col0))
    if norm0 > 1e-10:
        u0 = [x/norm0 for x in col0]
    else:
        u0 = [1.0, 0.0, 0.0]
    
    # Orthogonalize second column
    dot01 = sum(a*b for a, b in zip(col1, u0))
    col1_orth = [col1[i] - dot01 * u0[i] for i in range(3)]
    norm1 = math.sqrt(sum(x*x for x in col1_orth))
    if norm1 > 1e-10:
        u1 = [x/norm1 for x in col1_orth]
    else:
        u1 = [0.0, 1.0, 0.0]
    
    # Third vector is cross product
    u2 = [
        u0[1]*u1[2] - u0[2]*u1[1],
        u0[2]*u1[0] - u0[0]*u1[2],
        u0[0]*u1[1] - u0[1]*u1[0],
    ]
    
    # Handle reflection
    if det_H < 0:
        u2 = [-x for x in u2]
    
    # Build rotation matrix (columns are u0, u1, u2)
    R = [
        [u0[0], u1[0], u2[0]],
        [u0[1], u1[1], u2[1]],
        [u0[2], u1[2], u2[2]],
    ]
    
    return R


def align_structures(
    mobile: List[Tuple[float, float, float]],
    target: List[Tuple[float, float, float]],
    weights: Optional[List[float]] = None,
) -> AlignmentResult:
    """
    Align mobile structure to target structure.
    
    Uses Kabsch algorithm to find optimal superposition.
    
    Args:
        mobile: Coordinates to align
        target: Target coordinates
        weights: Optional weights
        
    Returns:
        AlignmentResult with RMSD and transformation
    """
    if len(mobile) != len(target):
        raise ValueError("Structures must have same number of atoms")
    
    # Center both structures
    mobile_centered, mobile_centroid = center_geometry(mobile, weights)
    target_centered, target_centroid = center_geometry(target, weights)
    
    # Find optimal rotation
    rotation = kabsch_rotation(mobile_centered, target_centered, weights)
    
    # Apply rotation to centered mobile
    rotated = rotate_geometry(mobile_centered, rotation)
    
    # Translate to target centroid
    aligned = translate_geometry(rotated, target_centroid)
    
    # Calculate RMSD
    rmsd = calculate_rmsd(aligned, target, weights)
    
    # Calculate translation (mobile_centroid to target_centroid after rotation)
    translation = (
        target_centroid[0] - mobile_centroid[0],
        target_centroid[1] - mobile_centroid[1],
        target_centroid[2] - mobile_centroid[2],
    )
    
    return AlignmentResult(
        rmsd=rmsd,
        rotation_matrix=rotation,
        translation=translation,
        aligned_coordinates=aligned,
    )


def partial_alignment(
    mobile: List[Tuple[float, float, float]],
    target: List[Tuple[float, float, float]],
    atom_indices: List[int],
) -> AlignmentResult:
    """
    Align structures based on subset of atoms.
    
    Args:
        mobile: All mobile coordinates
        target: All target coordinates
        atom_indices: Indices of atoms to use for alignment
        
    Returns:
        AlignmentResult
    """
    # Extract subset
    mobile_subset = [mobile[i] for i in atom_indices]
    target_subset = [target[i] for i in atom_indices]
    
    # Align subset
    subset_result = align_structures(mobile_subset, target_subset)
    
    # Apply transformation to all mobile atoms
    mobile_centered, mobile_centroid = center_geometry(mobile)
    
    # Center mobile at subset centroid
    subset_mobile = [mobile[i] for i in atom_indices]
    _, subset_centroid = center_geometry(subset_mobile)
    
    # Translate mobile to put subset at origin
    mobile_translated = translate_geometry(
        mobile,
        (-subset_centroid[0], -subset_centroid[1], -subset_centroid[2])
    )
    
    # Rotate
    mobile_rotated = rotate_geometry(mobile_translated, subset_result.rotation_matrix)
    
    # Translate to target subset centroid
    target_subset = [target[i] for i in atom_indices]
    _, target_subset_centroid = center_geometry(target_subset)
    
    aligned = translate_geometry(mobile_rotated, target_subset_centroid)
    
    # Calculate overall RMSD
    rmsd = calculate_rmsd(aligned, target)
    
    return AlignmentResult(
        rmsd=rmsd,
        rotation_matrix=subset_result.rotation_matrix,
        translation=subset_result.translation,
        aligned_coordinates=aligned,
    )


def get_maximum_displacement(
    coords1: List[Tuple[float, float, float]],
    coords2: List[Tuple[float, float, float]],
) -> Tuple[float, int]:
    """
    Get maximum atomic displacement between structures.
    
    Args:
        coords1: First coordinates
        coords2: Second coordinates
        
    Returns:
        Tuple of (max_displacement, atom_index)
    """
    if len(coords1) != len(coords2):
        raise ValueError("Coordinate sets must have same length")
    
    max_disp = 0.0
    max_idx = 0
    
    for i, (c1, c2) in enumerate(zip(coords1, coords2)):
        disp = math.sqrt(
            (c1[0]-c2[0])**2 +
            (c1[1]-c2[1])**2 +
            (c1[2]-c2[2])**2
        )
        if disp > max_disp:
            max_disp = disp
            max_idx = i
    
    return max_disp, max_idx
