"""
Coordinate Transformation Utilities for Psi4 MCP Server.

Provides tools for coordinate system transformations.
"""

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class InternalCoordinate:
    """An internal coordinate."""
    type: str  # "bond", "angle", "dihedral"
    indices: Tuple[int, ...]
    value: float
    unit: str  # "angstrom" for bonds, "degrees" for angles


def cartesian_to_internal(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    connectivity: Optional[Dict[int, List[int]]] = None,
) -> List[InternalCoordinate]:
    """
    Convert Cartesian to internal coordinates.
    
    Args:
        elements: Element symbols
        coordinates: Cartesian coordinates
        connectivity: Optional connectivity (auto-detected if None)
        
    Returns:
        List of internal coordinates
    """
    from psi4_mcp.utils.geometry.analysis import GeometryAnalyzer
    
    analyzer = GeometryAnalyzer(elements, coordinates)
    
    if connectivity is None:
        conn_dict = analyzer.get_connectivity()
        connectivity = {k: list(v) for k, v in conn_dict.items()}
    
    internals: List[InternalCoordinate] = []
    
    # Bond lengths
    bonds = analyzer.find_bonds()
    for bond in bonds:
        internals.append(InternalCoordinate(
            type="bond",
            indices=(bond.atom1_idx, bond.atom2_idx),
            value=bond.distance,
            unit="angstrom",
        ))
    
    # Bond angles
    angles = analyzer.find_angles()
    for angle in angles:
        internals.append(InternalCoordinate(
            type="angle",
            indices=(angle.atom1_idx, angle.atom2_idx, angle.atom3_idx),
            value=angle.angle_degrees,
            unit="degrees",
        ))
    
    # Dihedral angles
    dihedrals = analyzer.find_dihedrals()
    for dihedral in dihedrals:
        internals.append(InternalCoordinate(
            type="dihedral",
            indices=(dihedral.atom1_idx, dihedral.atom2_idx,
                    dihedral.atom3_idx, dihedral.atom4_idx),
            value=dihedral.angle_degrees,
            unit="degrees",
        ))
    
    return internals


def internal_to_cartesian(
    internals: List[InternalCoordinate],
    elements: List[str],
    initial_coords: Optional[List[Tuple[float, float, float]]] = None,
) -> List[Tuple[float, float, float]]:
    """
    Convert internal coordinates to Cartesian.
    
    Uses Z-matrix style reconstruction.
    
    Args:
        internals: Internal coordinates
        elements: Element symbols
        initial_coords: Starting coordinates (used for orientation)
        
    Returns:
        Cartesian coordinates
    """
    n_atoms = len(elements)
    
    if n_atoms == 0:
        return []
    
    # Sort bonds by atom index to build up molecule
    bonds = [ic for ic in internals if ic.type == "bond"]
    angles = [ic for ic in internals if ic.type == "angle"]
    dihedrals = [ic for ic in internals if ic.type == "dihedral"]
    
    # Build coordinates progressively
    coords: List[Optional[Tuple[float, float, float]]] = [None] * n_atoms
    
    # First atom at origin
    coords[0] = (0.0, 0.0, 0.0)
    
    if n_atoms == 1:
        return [(0.0, 0.0, 0.0)]
    
    # Find bond from atom 0
    bond_01 = None
    for b in bonds:
        if 0 in b.indices and 1 in b.indices:
            bond_01 = b
            break
    
    if bond_01 is None and bonds:
        bond_01 = bonds[0]
    
    dist_01 = bond_01.value if bond_01 else 1.5
    coords[1] = (dist_01, 0.0, 0.0)
    
    if n_atoms == 2:
        return [coords[0], coords[1]]  # type: ignore
    
    # Third atom in xy-plane
    # Find relevant angle
    angle_012 = None
    for a in angles:
        if set(a.indices[:3]) == {0, 1, 2}:
            angle_012 = a
            break
    
    angle_val = angle_012.value if angle_012 else 109.5
    
    # Find bond to atom 2
    dist_12 = None
    for b in bonds:
        if 1 in b.indices and 2 in b.indices:
            dist_12 = b.value
            break
    
    if dist_12 is None:
        dist_12 = 1.5
    
    angle_rad = math.radians(angle_val)
    coords[2] = (
        coords[1][0] - dist_12 * math.cos(angle_rad),
        dist_12 * math.sin(angle_rad),
        0.0,
    )
    
    # Remaining atoms using Z-matrix style
    for i in range(3, n_atoms):
        # Find connecting information
        ref1, ref2, ref3 = None, None, None
        dist, angle, dihedral_val = 1.5, 109.5, 0.0
        
        # Find bond to placed atom
        for b in bonds:
            if i in b.indices:
                other = b.indices[0] if b.indices[1] == i else b.indices[1]
                if coords[other] is not None:
                    ref1 = other
                    dist = b.value
                    break
        
        if ref1 is None:
            ref1 = i - 1
        
        # Find angle reference
        for a in angles:
            if i in a.indices and ref1 in a.indices:
                for idx in a.indices:
                    if idx != i and idx != ref1 and coords[idx] is not None:
                        ref2 = idx
                        angle = a.value
                        break
        
        if ref2 is None:
            for j in range(i):
                if j != ref1 and coords[j] is not None:
                    ref2 = j
                    break
        
        if ref2 is None:
            ref2 = 0 if ref1 != 0 else 1
        
        # Find dihedral reference
        for d in dihedrals:
            if i in d.indices and ref1 in d.indices and ref2 in d.indices:
                for idx in d.indices:
                    if idx not in (i, ref1, ref2) and coords[idx] is not None:
                        ref3 = idx
                        dihedral_val = d.value
                        break
        
        if ref3 is None:
            for j in range(i):
                if j not in (ref1, ref2) and coords[j] is not None:
                    ref3 = j
                    break
        
        if ref3 is None:
            ref3 = 0 if ref1 != 0 and ref2 != 0 else (1 if ref1 != 1 and ref2 != 1 else 2)
        
        # Calculate position
        coords[i] = _place_atom_zmatrix(
            coords[ref1], coords[ref2], coords[ref3],  # type: ignore
            dist, angle, dihedral_val
        )
    
    return [c if c is not None else (0.0, 0.0, 0.0) for c in coords]


def _place_atom_zmatrix(
    coord1: Tuple[float, float, float],
    coord2: Tuple[float, float, float],
    coord3: Tuple[float, float, float],
    distance: float,
    angle: float,
    dihedral: float,
) -> Tuple[float, float, float]:
    """Place atom using Z-matrix parameters."""
    # Vector from coord2 to coord1
    v1 = (coord1[0] - coord2[0], coord1[1] - coord2[1], coord1[2] - coord2[2])
    v1_len = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
    if v1_len < 1e-10:
        v1 = (1.0, 0.0, 0.0)
        v1_len = 1.0
    v1 = (v1[0]/v1_len, v1[1]/v1_len, v1[2]/v1_len)
    
    # Vector from coord3 to coord2
    v2 = (coord2[0] - coord3[0], coord2[1] - coord3[1], coord2[2] - coord3[2])
    v2_len = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
    if v2_len < 1e-10:
        v2 = (0.0, 1.0, 0.0)
        v2_len = 1.0
    v2 = (v2[0]/v2_len, v2[1]/v2_len, v2[2]/v2_len)
    
    # Normal to plane
    n = (
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0],
    )
    n_len = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2)
    if n_len < 1e-10:
        n = (0.0, 0.0, 1.0)
    else:
        n = (n[0]/n_len, n[1]/n_len, n[2]/n_len)
    
    # Perpendicular in plane
    m = (
        n[1]*v1[2] - n[2]*v1[1],
        n[2]*v1[0] - n[0]*v1[2],
        n[0]*v1[1] - n[1]*v1[0],
    )
    
    # Convert angles
    angle_rad = math.radians(180.0 - angle)
    dihedral_rad = math.radians(dihedral)
    
    # Calculate displacement
    dx = distance * math.cos(angle_rad)
    dy = distance * math.sin(angle_rad) * math.cos(dihedral_rad)
    dz = distance * math.sin(angle_rad) * math.sin(dihedral_rad)
    
    # Transform to global coordinates
    x = coord1[0] + dx * v1[0] + dy * m[0] + dz * n[0]
    y = coord1[1] + dx * v1[1] + dy * m[1] + dz * n[1]
    z = coord1[2] + dx * v1[2] + dy * m[2] + dz * n[2]
    
    return (x, y, z)


def rotate_around_axis(
    coordinates: List[Tuple[float, float, float]],
    axis: Tuple[float, float, float],
    point: Tuple[float, float, float],
    angle_degrees: float,
) -> List[Tuple[float, float, float]]:
    """
    Rotate coordinates around an axis through a point.
    
    Args:
        coordinates: Coordinates to rotate
        axis: Rotation axis direction
        point: Point on axis
        angle_degrees: Rotation angle in degrees
        
    Returns:
        Rotated coordinates
    """
    angle = math.radians(angle_degrees)
    
    # Normalize axis
    ax_len = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    if ax_len < 1e-10:
        return list(coordinates)
    
    ux, uy, uz = axis[0]/ax_len, axis[1]/ax_len, axis[2]/ax_len
    
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    rotated = []
    for coord in coordinates:
        # Translate to origin
        x = coord[0] - point[0]
        y = coord[1] - point[1]
        z = coord[2] - point[2]
        
        # Rodrigues' rotation formula
        dot = ux*x + uy*y + uz*z
        
        rx = x*cos_a + (uy*z - uz*y)*sin_a + ux*dot*(1 - cos_a)
        ry = y*cos_a + (uz*x - ux*z)*sin_a + uy*dot*(1 - cos_a)
        rz = z*cos_a + (ux*y - uy*x)*sin_a + uz*dot*(1 - cos_a)
        
        # Translate back
        rotated.append((rx + point[0], ry + point[1], rz + point[2]))
    
    return rotated


def get_rotation_matrix(
    axis: Tuple[float, float, float],
    angle_degrees: float,
) -> List[List[float]]:
    """
    Get rotation matrix for rotation around axis.
    
    Args:
        axis: Rotation axis
        angle_degrees: Rotation angle in degrees
        
    Returns:
        3x3 rotation matrix
    """
    angle = math.radians(angle_degrees)
    
    # Normalize axis
    ax_len = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    if ax_len < 1e-10:
        return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    
    ux, uy, uz = axis[0]/ax_len, axis[1]/ax_len, axis[2]/ax_len
    
    c = math.cos(angle)
    s = math.sin(angle)
    t = 1 - c
    
    return [
        [t*ux*ux + c,    t*ux*uy - s*uz, t*ux*uz + s*uy],
        [t*ux*uy + s*uz, t*uy*uy + c,    t*uy*uz - s*ux],
        [t*ux*uz - s*uy, t*uy*uz + s*ux, t*uz*uz + c   ],
    ]


def apply_transformation_matrix(
    coordinates: List[Tuple[float, float, float]],
    matrix: List[List[float]],
    translation: Optional[Tuple[float, float, float]] = None,
) -> List[Tuple[float, float, float]]:
    """
    Apply transformation matrix to coordinates.
    
    Args:
        coordinates: Coordinates to transform
        matrix: 3x3 transformation matrix
        translation: Optional translation vector
        
    Returns:
        Transformed coordinates
    """
    transformed = []
    
    for x, y, z in coordinates:
        nx = matrix[0][0]*x + matrix[0][1]*y + matrix[0][2]*z
        ny = matrix[1][0]*x + matrix[1][1]*y + matrix[1][2]*z
        nz = matrix[2][0]*x + matrix[2][1]*y + matrix[2][2]*z
        
        if translation is not None:
            nx += translation[0]
            ny += translation[1]
            nz += translation[2]
        
        transformed.append((nx, ny, nz))
    
    return transformed


def scale_coordinates(
    coordinates: List[Tuple[float, float, float]],
    scale_factor: float,
    center: Optional[Tuple[float, float, float]] = None,
) -> List[Tuple[float, float, float]]:
    """
    Scale coordinates by a factor.
    
    Args:
        coordinates: Coordinates to scale
        scale_factor: Scaling factor
        center: Center point for scaling (default: origin)
        
    Returns:
        Scaled coordinates
    """
    if center is None:
        center = (0.0, 0.0, 0.0)
    
    scaled = []
    for x, y, z in coordinates:
        nx = center[0] + scale_factor * (x - center[0])
        ny = center[1] + scale_factor * (y - center[1])
        nz = center[2] + scale_factor * (z - center[2])
        scaled.append((nx, ny, nz))
    
    return scaled


def reflect_through_plane(
    coordinates: List[Tuple[float, float, float]],
    plane_point: Tuple[float, float, float],
    plane_normal: Tuple[float, float, float],
) -> List[Tuple[float, float, float]]:
    """
    Reflect coordinates through a plane.
    
    Args:
        coordinates: Coordinates to reflect
        plane_point: Point on plane
        plane_normal: Normal vector to plane
        
    Returns:
        Reflected coordinates
    """
    # Normalize
    n_len = math.sqrt(plane_normal[0]**2 + plane_normal[1]**2 + plane_normal[2]**2)
    if n_len < 1e-10:
        return list(coordinates)
    
    nx, ny, nz = plane_normal[0]/n_len, plane_normal[1]/n_len, plane_normal[2]/n_len
    
    reflected = []
    for x, y, z in coordinates:
        # Vector from plane point to coordinate
        vx = x - plane_point[0]
        vy = y - plane_point[1]
        vz = z - plane_point[2]
        
        # Distance to plane
        d = vx*nx + vy*ny + vz*nz
        
        # Reflect
        rx = x - 2*d*nx
        ry = y - 2*d*ny
        rz = z - 2*d*nz
        
        reflected.append((rx, ry, rz))
    
    return reflected


def invert_through_point(
    coordinates: List[Tuple[float, float, float]],
    center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> List[Tuple[float, float, float]]:
    """
    Invert coordinates through a point.
    
    Args:
        coordinates: Coordinates to invert
        center: Center of inversion
        
    Returns:
        Inverted coordinates
    """
    return [
        (2*center[0] - x, 2*center[1] - y, 2*center[2] - z)
        for x, y, z in coordinates
    ]
