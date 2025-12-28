"""
Geometry Utilities for Psi4 MCP Server.

This module provides utilities for molecular geometry operations:
- Coordinate transformations
- Geometry analysis (bonds, angles, dihedrals)
- Symmetry detection
- Structure alignment
- Geometry builders

Example Usage:
    from psi4_mcp.utils.geometry import (
        GeometryAnalyzer,
        calculate_distance,
        calculate_angle,
        align_structures,
        detect_point_group,
    )
    
    # Analyze geometry
    analyzer = GeometryAnalyzer(coordinates)
    bonds = analyzer.find_bonds()
"""

from psi4_mcp.utils.geometry.analysis import (
    GeometryAnalyzer,
    calculate_distance,
    calculate_angle,
    calculate_dihedral,
    find_bonds,
    find_angles,
    find_dihedrals,
    get_connectivity,
)

from psi4_mcp.utils.geometry.alignment import (
    align_structures,
    calculate_rmsd,
    kabsch_rotation,
    center_geometry,
    translate_geometry,
    rotate_geometry,
)

from psi4_mcp.utils.geometry.builders import (
    GeometryBuilder,
    build_molecule_from_smiles,
    build_from_zmatrix,
    add_hydrogens,
    generate_conformer,
)

from psi4_mcp.utils.geometry.symmetry import (
    PointGroup,
    detect_point_group,
    symmetrize_geometry,
    get_symmetry_operations,
    is_symmetric,
)

from psi4_mcp.utils.geometry.transformations import (
    cartesian_to_internal,
    internal_to_cartesian,
    rotate_around_axis,
    apply_transformation_matrix,
    get_rotation_matrix,
)

__all__ = [
    # Analysis
    "GeometryAnalyzer",
    "calculate_distance",
    "calculate_angle",
    "calculate_dihedral",
    "find_bonds",
    "find_angles",
    "find_dihedrals",
    "get_connectivity",
    
    # Alignment
    "align_structures",
    "calculate_rmsd",
    "kabsch_rotation",
    "center_geometry",
    "translate_geometry",
    "rotate_geometry",
    
    # Builders
    "GeometryBuilder",
    "build_molecule_from_smiles",
    "build_from_zmatrix",
    "add_hydrogens",
    "generate_conformer",
    
    # Symmetry
    "PointGroup",
    "detect_point_group",
    "symmetrize_geometry",
    "get_symmetry_operations",
    "is_symmetric",
    
    # Transformations
    "cartesian_to_internal",
    "internal_to_cartesian",
    "rotate_around_axis",
    "apply_transformation_matrix",
    "get_rotation_matrix",
]
