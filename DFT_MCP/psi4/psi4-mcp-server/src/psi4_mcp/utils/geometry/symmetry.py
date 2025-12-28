"""
Symmetry Utilities for Psi4 MCP Server.

Provides tools for molecular symmetry detection and handling.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class PointGroup(str, Enum):
    """Point groups for molecular symmetry."""
    C1 = "c1"       # No symmetry
    CI = "ci"       # Inversion only
    CS = "cs"       # Reflection only
    C2 = "c2"       # 2-fold rotation
    C3 = "c3"       # 3-fold rotation
    C4 = "c4"       # 4-fold rotation
    C5 = "c5"       # 5-fold rotation
    C6 = "c6"       # 6-fold rotation
    C2V = "c2v"     # C2 + 2 mirror planes
    C3V = "c3v"     # C3 + 3 mirror planes
    C4V = "c4v"     # C4 + 4 mirror planes
    C2H = "c2h"     # C2 + horizontal mirror
    C3H = "c3h"     # C3 + horizontal mirror
    D2 = "d2"       # 3 C2 axes
    D3 = "d3"       # C3 + 3 C2 axes
    D4 = "d4"       # C4 + 4 C2 axes
    D2H = "d2h"     # D2 + center + mirror planes
    D3H = "d3h"     # D3 + horizontal mirror
    D4H = "d4h"     # D4 + horizontal mirror
    D6H = "d6h"     # D6 + horizontal mirror
    TD = "td"       # Tetrahedral
    TH = "th"       # Th symmetry
    OH = "oh"       # Octahedral
    IH = "ih"       # Icosahedral
    CINFV = "c_inf_v"  # Linear (heteronuclear)
    DINFH = "d_inf_h"  # Linear (homonuclear)


@dataclass
class SymmetryOperation:
    """A symmetry operation."""
    name: str
    type: str  # "rotation", "reflection", "inversion", "improper"
    axis: Optional[Tuple[float, float, float]] = None
    plane_normal: Optional[Tuple[float, float, float]] = None
    order: int = 1  # For rotations


@dataclass
class SymmetryAnalysis:
    """Result of symmetry analysis."""
    point_group: PointGroup
    operations: List[SymmetryOperation]
    principal_axis: Optional[Tuple[float, float, float]] = None
    is_linear: bool = False
    is_planar: bool = False
    tolerance: float = 0.1


def detect_point_group(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    tolerance: float = 0.1,
) -> SymmetryAnalysis:
    """
    Detect point group of a molecule.
    
    Args:
        elements: Element symbols
        coordinates: Atomic coordinates
        tolerance: Distance tolerance for symmetry detection
        
    Returns:
        SymmetryAnalysis with detected symmetry
    """
    n_atoms = len(elements)
    
    if n_atoms == 0:
        return SymmetryAnalysis(
            point_group=PointGroup.C1,
            operations=[],
            tolerance=tolerance,
        )
    
    # Center molecule
    cx = sum(c[0] for c in coordinates) / n_atoms
    cy = sum(c[1] for c in coordinates) / n_atoms
    cz = sum(c[2] for c in coordinates) / n_atoms
    centered = [(c[0]-cx, c[1]-cy, c[2]-cz) for c in coordinates]
    
    operations: List[SymmetryOperation] = []
    
    # Check if linear
    is_linear = _check_linear(centered, tolerance)
    if is_linear:
        # Check for inversion center (homonuclear diatomic)
        has_inversion = _check_inversion(elements, centered, tolerance)
        if has_inversion:
            return SymmetryAnalysis(
                point_group=PointGroup.DINFH,
                operations=[SymmetryOperation("C_inf", "rotation", (0, 0, 1))],
                principal_axis=(0.0, 0.0, 1.0),
                is_linear=True,
                tolerance=tolerance,
            )
        else:
            return SymmetryAnalysis(
                point_group=PointGroup.CINFV,
                operations=[SymmetryOperation("C_inf", "rotation", (0, 0, 1))],
                principal_axis=(0.0, 0.0, 1.0),
                is_linear=True,
                tolerance=tolerance,
            )
    
    # Check if planar
    is_planar = _check_planar(centered, tolerance)
    
    # Check for inversion center
    has_inversion = _check_inversion(elements, centered, tolerance)
    if has_inversion:
        operations.append(SymmetryOperation("i", "inversion"))
    
    # Check for rotation axes
    c2_axes = _find_c2_axes(elements, centered, tolerance)
    c3_axes = _find_cn_axes(elements, centered, 3, tolerance)
    c4_axes = _find_cn_axes(elements, centered, 4, tolerance)
    
    # Check for mirror planes
    sigma_h = _check_horizontal_plane(elements, centered, tolerance)
    sigma_v = _find_vertical_planes(elements, centered, tolerance)
    
    # Determine point group based on found operations
    point_group = _determine_point_group(
        has_inversion,
        c2_axes,
        c3_axes,
        c4_axes,
        sigma_h,
        sigma_v,
        is_planar,
    )
    
    # Build operations list
    for axis in c2_axes:
        operations.append(SymmetryOperation("C2", "rotation", axis, order=2))
    for axis in c3_axes:
        operations.append(SymmetryOperation("C3", "rotation", axis, order=3))
    for axis in c4_axes:
        operations.append(SymmetryOperation("C4", "rotation", axis, order=4))
    if sigma_h:
        operations.append(SymmetryOperation("sigma_h", "reflection", plane_normal=(0, 0, 1)))
    for plane in sigma_v:
        operations.append(SymmetryOperation("sigma_v", "reflection", plane_normal=plane))
    
    # Determine principal axis
    principal_axis = None
    if c4_axes:
        principal_axis = c4_axes[0]
    elif c3_axes:
        principal_axis = c3_axes[0]
    elif c2_axes:
        principal_axis = c2_axes[0]
    
    return SymmetryAnalysis(
        point_group=point_group,
        operations=operations,
        principal_axis=principal_axis,
        is_linear=is_linear,
        is_planar=is_planar,
        tolerance=tolerance,
    )


def _check_linear(
    coords: List[Tuple[float, float, float]],
    tolerance: float,
) -> bool:
    """Check if molecule is linear."""
    if len(coords) <= 2:
        return True
    
    # Find direction of first two non-coincident atoms
    v = None
    for i in range(1, len(coords)):
        dx = coords[i][0] - coords[0][0]
        dy = coords[i][1] - coords[0][1]
        dz = coords[i][2] - coords[0][2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist > tolerance:
            v = (dx/dist, dy/dist, dz/dist)
            break
    
    if v is None:
        return True
    
    # Check all other atoms lie on this line
    for i in range(2, len(coords)):
        dx = coords[i][0] - coords[0][0]
        dy = coords[i][1] - coords[0][1]
        dz = coords[i][2] - coords[0][2]
        
        # Project onto line
        proj = dx*v[0] + dy*v[1] + dz*v[2]
        
        # Distance from line
        perp_x = dx - proj * v[0]
        perp_y = dy - proj * v[1]
        perp_z = dz - proj * v[2]
        perp_dist = math.sqrt(perp_x**2 + perp_y**2 + perp_z**2)
        
        if perp_dist > tolerance:
            return False
    
    return True


def _check_planar(
    coords: List[Tuple[float, float, float]],
    tolerance: float,
) -> bool:
    """Check if molecule is planar."""
    if len(coords) <= 3:
        return True
    
    # Find plane defined by first three non-collinear atoms
    v1 = None
    normal = None
    
    for i in range(1, len(coords)):
        dx = coords[i][0] - coords[0][0]
        dy = coords[i][1] - coords[0][1]
        dz = coords[i][2] - coords[0][2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist > tolerance:
            if v1 is None:
                v1 = (dx/dist, dy/dist, dz/dist)
            else:
                # Check not parallel
                v2_temp = (dx/dist, dy/dist, dz/dist)
                cross = (
                    v1[1]*v2_temp[2] - v1[2]*v2_temp[1],
                    v1[2]*v2_temp[0] - v1[0]*v2_temp[2],
                    v1[0]*v2_temp[1] - v1[1]*v2_temp[0],
                )
                cross_mag = math.sqrt(cross[0]**2 + cross[1]**2 + cross[2]**2)
                if cross_mag > tolerance:
                    normal = (cross[0]/cross_mag, cross[1]/cross_mag, cross[2]/cross_mag)
                    break
    
    if normal is None:
        return True  # Collinear points
    
    # Check all atoms lie in this plane
    for i in range(3, len(coords)):
        dx = coords[i][0] - coords[0][0]
        dy = coords[i][1] - coords[0][1]
        dz = coords[i][2] - coords[0][2]
        
        dist_from_plane = abs(dx*normal[0] + dy*normal[1] + dz*normal[2])
        if dist_from_plane > tolerance:
            return False
    
    return True


def _check_inversion(
    elements: List[str],
    coords: List[Tuple[float, float, float]],
    tolerance: float,
) -> bool:
    """Check for inversion center at origin."""
    n = len(elements)
    
    for i in range(n):
        # Find atom at inverted position
        inv_x, inv_y, inv_z = -coords[i][0], -coords[i][1], -coords[i][2]
        
        found = False
        for j in range(n):
            if elements[j] != elements[i]:
                continue
            
            dx = coords[j][0] - inv_x
            dy = coords[j][1] - inv_y
            dz = coords[j][2] - inv_z
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < tolerance:
                found = True
                break
        
        if not found:
            return False
    
    return True


def _find_c2_axes(
    elements: List[str],
    coords: List[Tuple[float, float, float]],
    tolerance: float,
) -> List[Tuple[float, float, float]]:
    """Find C2 rotation axes."""
    axes = []
    
    # Check standard axes
    for axis in [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]:
        if _check_cn_axis(elements, coords, axis, 2, tolerance):
            axes.append(axis)
    
    return axes


def _find_cn_axes(
    elements: List[str],
    coords: List[Tuple[float, float, float]],
    n: int,
    tolerance: float,
) -> List[Tuple[float, float, float]]:
    """Find Cn rotation axes."""
    axes = []
    
    # Check z-axis
    if _check_cn_axis(elements, coords, (0.0, 0.0, 1.0), n, tolerance):
        axes.append((0.0, 0.0, 1.0))
    
    return axes


def _check_cn_axis(
    elements: List[str],
    coords: List[Tuple[float, float, float]],
    axis: Tuple[float, float, float],
    n: int,
    tolerance: float,
) -> bool:
    """Check if axis is a Cn rotation axis."""
    angle = 2 * math.pi / n
    
    # Rotate all atoms and check if structure is unchanged
    rotated = _rotate_around_axis_simple(coords, axis, angle)
    
    return _structures_equivalent(elements, coords, elements, rotated, tolerance)


def _rotate_around_axis_simple(
    coords: List[Tuple[float, float, float]],
    axis: Tuple[float, float, float],
    angle: float,
) -> List[Tuple[float, float, float]]:
    """Rotate coordinates around an axis."""
    # Normalize axis
    ax_len = math.sqrt(axis[0]**2 + axis[1]**2 + axis[2]**2)
    if ax_len < 1e-10:
        return list(coords)
    
    ux, uy, uz = axis[0]/ax_len, axis[1]/ax_len, axis[2]/ax_len
    
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    rotated = []
    for x, y, z in coords:
        # Rodrigues' rotation formula
        dot = ux*x + uy*y + uz*z
        
        rx = x*cos_a + (uy*z - uz*y)*sin_a + ux*dot*(1 - cos_a)
        ry = y*cos_a + (uz*x - ux*z)*sin_a + uy*dot*(1 - cos_a)
        rz = z*cos_a + (ux*y - uy*x)*sin_a + uz*dot*(1 - cos_a)
        
        rotated.append((rx, ry, rz))
    
    return rotated


def _structures_equivalent(
    elem1: List[str],
    coords1: List[Tuple[float, float, float]],
    elem2: List[str],
    coords2: List[Tuple[float, float, float]],
    tolerance: float,
) -> bool:
    """Check if two structures are equivalent."""
    n = len(elem1)
    if n != len(elem2):
        return False
    
    used = [False] * n
    
    for i in range(n):
        found = False
        for j in range(n):
            if used[j] or elem1[i] != elem2[j]:
                continue
            
            dx = coords1[i][0] - coords2[j][0]
            dy = coords1[i][1] - coords2[j][1]
            dz = coords1[i][2] - coords2[j][2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)
            
            if dist < tolerance:
                found = True
                used[j] = True
                break
        
        if not found:
            return False
    
    return True


def _check_horizontal_plane(
    elements: List[str],
    coords: List[Tuple[float, float, float]],
    tolerance: float,
) -> bool:
    """Check for horizontal mirror plane (xy plane)."""
    # Reflect through xy plane and check equivalence
    reflected = [(x, y, -z) for x, y, z in coords]
    return _structures_equivalent(elements, coords, elements, reflected, tolerance)


def _find_vertical_planes(
    elements: List[str],
    coords: List[Tuple[float, float, float]],
    tolerance: float,
) -> List[Tuple[float, float, float]]:
    """Find vertical mirror planes."""
    planes = []
    
    # Check xz and yz planes
    for normal in [(0.0, 1.0, 0.0), (1.0, 0.0, 0.0)]:
        reflected = _reflect_through_plane(coords, normal)
        if _structures_equivalent(elements, coords, elements, reflected, tolerance):
            planes.append(normal)
    
    return planes


def _reflect_through_plane(
    coords: List[Tuple[float, float, float]],
    normal: Tuple[float, float, float],
) -> List[Tuple[float, float, float]]:
    """Reflect coordinates through a plane."""
    # Normalize
    n_len = math.sqrt(normal[0]**2 + normal[1]**2 + normal[2]**2)
    if n_len < 1e-10:
        return list(coords)
    
    nx, ny, nz = normal[0]/n_len, normal[1]/n_len, normal[2]/n_len
    
    reflected = []
    for x, y, z in coords:
        # Distance to plane
        d = x*nx + y*ny + z*nz
        
        # Reflect
        rx = x - 2*d*nx
        ry = y - 2*d*ny
        rz = z - 2*d*nz
        
        reflected.append((rx, ry, rz))
    
    return reflected


def _determine_point_group(
    has_inversion: bool,
    c2_axes: List[Tuple[float, float, float]],
    c3_axes: List[Tuple[float, float, float]],
    c4_axes: List[Tuple[float, float, float]],
    sigma_h: bool,
    sigma_v: List[Tuple[float, float, float]],
    is_planar: bool,
) -> PointGroup:
    """Determine point group from symmetry elements."""
    n_c2 = len(c2_axes)
    n_c3 = len(c3_axes)
    n_c4 = len(c4_axes)
    n_sigma_v = len(sigma_v)
    
    # High symmetry groups
    if n_c3 >= 4 and n_c4 >= 3:
        if has_inversion:
            return PointGroup.OH
        return PointGroup.TD
    
    # Dnh groups
    if n_c4 > 0 and n_c2 >= 4 and sigma_h:
        return PointGroup.D4H
    if n_c3 > 0 and n_c2 >= 3 and sigma_h:
        return PointGroup.D3H
    if n_c2 >= 3 and sigma_h and has_inversion:
        return PointGroup.D2H
    
    # Dn groups
    if n_c4 > 0 and n_c2 >= 4:
        return PointGroup.D4
    if n_c3 > 0 and n_c2 >= 3:
        return PointGroup.D3
    if n_c2 >= 3:
        return PointGroup.D2
    
    # Cnv groups
    if n_c4 > 0 and n_sigma_v >= 4:
        return PointGroup.C4V
    if n_c3 > 0 and n_sigma_v >= 3:
        return PointGroup.C3V
    if n_c2 > 0 and n_sigma_v >= 2:
        return PointGroup.C2V
    
    # Cnh groups
    if n_c3 > 0 and sigma_h:
        return PointGroup.C3H
    if n_c2 > 0 and sigma_h:
        return PointGroup.C2H
    
    # Cn groups
    if n_c4 > 0:
        return PointGroup.C4
    if n_c3 > 0:
        return PointGroup.C3
    if n_c2 > 0:
        return PointGroup.C2
    
    # Ci and Cs
    if has_inversion:
        return PointGroup.CI
    if sigma_h or n_sigma_v > 0:
        return PointGroup.CS
    
    return PointGroup.C1


def symmetrize_geometry(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    point_group: PointGroup,
    tolerance: float = 0.1,
) -> List[Tuple[float, float, float]]:
    """
    Symmetrize geometry to given point group.
    
    Averages atomic positions to enforce symmetry.
    
    Args:
        elements: Element symbols
        coordinates: Atomic coordinates
        point_group: Target point group
        tolerance: Tolerance for atom matching
        
    Returns:
        Symmetrized coordinates
    """
    # Get symmetry operations for the point group
    operations = get_symmetry_operations(point_group)
    
    # Apply each operation and average equivalent positions
    n = len(coordinates)
    symmetrized = list(coordinates)
    
    for i in range(n):
        sum_x, sum_y, sum_z = 0.0, 0.0, 0.0
        count = 0
        
        for op in operations:
            # Apply operation to get equivalent position
            if op.type == "identity":
                equiv = coordinates[i]
            elif op.type == "rotation" and op.axis is not None:
                equiv = _rotate_around_axis_simple(
                    [coordinates[i]], 
                    op.axis, 
                    2*math.pi/op.order
                )[0]
            elif op.type == "reflection" and op.plane_normal is not None:
                equiv = _reflect_through_plane([coordinates[i]], op.plane_normal)[0]
            elif op.type == "inversion":
                equiv = (-coordinates[i][0], -coordinates[i][1], -coordinates[i][2])
            else:
                equiv = coordinates[i]
            
            # Find matching atom
            for j in range(n):
                if elements[j] != elements[i]:
                    continue
                dx = coordinates[j][0] - equiv[0]
                dy = coordinates[j][1] - equiv[1]
                dz = coordinates[j][2] - equiv[2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                if dist < tolerance:
                    sum_x += coordinates[j][0]
                    sum_y += coordinates[j][1]
                    sum_z += coordinates[j][2]
                    count += 1
                    break
        
        if count > 0:
            symmetrized[i] = (sum_x/count, sum_y/count, sum_z/count)
    
    return symmetrized


def get_symmetry_operations(point_group: PointGroup) -> List[SymmetryOperation]:
    """
    Get symmetry operations for a point group.
    
    Args:
        point_group: Point group
        
    Returns:
        List of symmetry operations
    """
    operations = [SymmetryOperation("E", "identity")]
    
    if point_group == PointGroup.C1:
        pass
    
    elif point_group == PointGroup.CI:
        operations.append(SymmetryOperation("i", "inversion"))
    
    elif point_group == PointGroup.CS:
        operations.append(SymmetryOperation("sigma", "reflection", plane_normal=(0, 0, 1)))
    
    elif point_group == PointGroup.C2:
        operations.append(SymmetryOperation("C2", "rotation", axis=(0, 0, 1), order=2))
    
    elif point_group == PointGroup.C2V:
        operations.append(SymmetryOperation("C2", "rotation", axis=(0, 0, 1), order=2))
        operations.append(SymmetryOperation("sigma_v", "reflection", plane_normal=(1, 0, 0)))
        operations.append(SymmetryOperation("sigma_v'", "reflection", plane_normal=(0, 1, 0)))
    
    elif point_group == PointGroup.C2H:
        operations.append(SymmetryOperation("C2", "rotation", axis=(0, 0, 1), order=2))
        operations.append(SymmetryOperation("i", "inversion"))
        operations.append(SymmetryOperation("sigma_h", "reflection", plane_normal=(0, 0, 1)))
    
    elif point_group == PointGroup.D2H:
        operations.append(SymmetryOperation("C2z", "rotation", axis=(0, 0, 1), order=2))
        operations.append(SymmetryOperation("C2y", "rotation", axis=(0, 1, 0), order=2))
        operations.append(SymmetryOperation("C2x", "rotation", axis=(1, 0, 0), order=2))
        operations.append(SymmetryOperation("i", "inversion"))
        operations.append(SymmetryOperation("sigma_xy", "reflection", plane_normal=(0, 0, 1)))
        operations.append(SymmetryOperation("sigma_xz", "reflection", plane_normal=(0, 1, 0)))
        operations.append(SymmetryOperation("sigma_yz", "reflection", plane_normal=(1, 0, 0)))
    
    # Add more point groups as needed
    
    return operations


def is_symmetric(
    elements: List[str],
    coordinates: List[Tuple[float, float, float]],
    point_group: PointGroup,
    tolerance: float = 0.1,
) -> bool:
    """
    Check if geometry has given point group symmetry.
    
    Args:
        elements: Element symbols
        coordinates: Atomic coordinates
        point_group: Point group to check
        tolerance: Tolerance for symmetry check
        
    Returns:
        True if geometry has the symmetry
    """
    analysis = detect_point_group(elements, coordinates, tolerance)
    
    # Check if detected point group is compatible
    # (equal or higher symmetry)
    return analysis.point_group == point_group
