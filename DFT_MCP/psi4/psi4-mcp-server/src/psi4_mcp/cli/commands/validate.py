"""
Validate Command for Psi4 MCP Server CLI.

Validates input files and configurations.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from psi4_mcp.cli.utils import (
    print_error,
    print_info,
    print_success,
    print_warning,
    file_exists,
    read_file,
    get_file_extension,
)


def run_validate(args: argparse.Namespace) -> int:
    """Run the validate command."""
    input_file = args.input_file
    validation_type = args.type
    
    if not file_exists(input_file):
        print_error(f"File not found: {input_file}")
        return 1
    
    print_info(f"Validating: {input_file}")
    print_info(f"Type: {validation_type}")
    
    # Read file content
    content = read_file(input_file)
    
    # Run appropriate validation
    if validation_type == "geometry":
        return validate_geometry_file(content, input_file)
    elif validation_type == "input":
        return validate_input_file(content, input_file)
    elif validation_type == "basis":
        return validate_basis_file(content, input_file)
    
    return 0


def validate_geometry_file(content: str, filename: str) -> int:
    """Validate a geometry file."""
    from psi4_mcp.utils.validation.geometry import (
        GeometryValidator,
        validate_geometry,
    )
    
    print_info("Running geometry validation...")
    
    # Detect format
    ext = get_file_extension(filename).lower()
    
    if ext == "xyz":
        return validate_xyz_geometry(content)
    elif ext == "pdb":
        return validate_pdb_geometry(content)
    else:
        # Try to parse as raw geometry
        return validate_raw_geometry(content)


def validate_xyz_geometry(content: str) -> int:
    """Validate XYZ format geometry."""
    lines = content.strip().split("\n")
    errors = []
    warnings = []
    
    if len(lines) < 2:
        print_error("XYZ file too short (need at least 2 lines)")
        return 1
    
    # Check atom count line
    try:
        n_atoms = int(lines[0].strip())
    except ValueError:
        print_error(f"Invalid atom count on line 1: '{lines[0]}'")
        return 1
    
    # Line 2 is comment (skip)
    
    # Check coordinate lines
    actual_atoms = 0
    for i, line in enumerate(lines[2:], start=3):
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) < 4:
            errors.append(f"Line {i}: Expected 4 fields (element x y z), got {len(parts)}")
            continue
        
        element = parts[0]
        
        # Check coordinates
        for j, coord_str in enumerate(parts[1:4]):
            try:
                float(coord_str)
            except ValueError:
                errors.append(f"Line {i}: Invalid coordinate '{coord_str}'")
        
        actual_atoms += 1
    
    # Check atom count matches
    if actual_atoms != n_atoms:
        warnings.append(f"Atom count mismatch: header says {n_atoms}, found {actual_atoms}")
    
    # Run distance validation
    geometry = "\n".join(lines[2:])
    from psi4_mcp.utils.validation.geometry import GeometryValidator
    validator = GeometryValidator()
    result = validator.validate(geometry, 0, 1)
    
    if not result.valid:
        errors.extend(result.errors)
    warnings.extend(result.warnings)
    
    # Print results
    if errors:
        print_error("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    if warnings:
        print_warning("Validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print_success(f"XYZ geometry valid: {actual_atoms} atoms")
    return 0


def validate_pdb_geometry(content: str) -> int:
    """Validate PDB format geometry."""
    lines = content.strip().split("\n")
    errors = []
    warnings = []
    
    atom_count = 0
    
    for i, line in enumerate(lines, start=1):
        if line.startswith("ATOM") or line.startswith("HETATM"):
            # PDB format is column-based
            if len(line) < 54:
                errors.append(f"Line {i}: Too short for PDB ATOM record")
                continue
            
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                errors.append(f"Line {i}: Invalid coordinates")
                continue
            
            atom_count += 1
    
    if atom_count == 0:
        errors.append("No ATOM or HETATM records found")
    
    if errors:
        print_error("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print_success(f"PDB geometry valid: {atom_count} atoms")
    return 0


def validate_raw_geometry(content: str) -> int:
    """Validate raw geometry string."""
    from psi4_mcp.utils.validation.geometry import GeometryValidator
    
    validator = GeometryValidator()
    result = validator.validate(content, 0, 1)
    
    if not result.valid:
        print_error("Validation errors found:")
        for error in result.errors:
            print(f"  - {error}")
        return 1
    
    if result.warnings:
        print_warning("Validation warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")
    
    print_success("Geometry valid")
    return 0


def validate_input_file(content: str, filename: str) -> int:
    """Validate a calculation input file."""
    print_info("Validating calculation input...")
    
    ext = get_file_extension(filename).lower()
    
    if ext == "json":
        return validate_json_input(content)
    else:
        return validate_psi4_input(content)


def validate_json_input(content: str) -> int:
    """Validate JSON input file."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
        return 1
    
    errors = []
    warnings = []
    
    # Check required fields
    required = ["molecule", "method", "basis"]
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate molecule
    if "molecule" in data:
        mol = data["molecule"]
        if "geometry" not in mol:
            errors.append("molecule.geometry is required")
    
    # Validate method
    if "method" in data:
        from psi4_mcp.utils.validation.methods import validate_method
        result = validate_method(data["method"])
        if not result.valid:
            errors.extend(result.errors)
    
    # Validate basis
    if "basis" in data:
        from psi4_mcp.utils.validation.basis_sets import validate_basis_set
        result = validate_basis_set(data["basis"])
        if not result.valid:
            errors.extend(result.errors)
    
    if errors:
        print_error("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print_success("JSON input valid")
    return 0


def validate_psi4_input(content: str) -> int:
    """Validate Psi4 input file format."""
    errors = []
    warnings = []
    
    # Check for basic structure
    has_molecule = "molecule" in content.lower()
    has_energy = "energy(" in content.lower() or "optimize(" in content.lower()
    
    if not has_molecule:
        warnings.append("No molecule block found")
    
    if not has_energy:
        warnings.append("No energy or optimize call found")
    
    # Check for common issues
    if "set {" in content and "}" not in content:
        errors.append("Unclosed set block")
    
    if content.count("(") != content.count(")"):
        errors.append("Mismatched parentheses")
    
    if errors:
        print_error("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    if warnings:
        print_warning("Validation warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print_success("Psi4 input appears valid (full validation requires Psi4)")
    return 0


def validate_basis_file(content: str, filename: str) -> int:
    """Validate a basis set file."""
    print_info("Validating basis set file...")
    
    errors = []
    
    # Basic format checks
    lines = content.strip().split("\n")
    
    if len(lines) < 2:
        errors.append("Basis file too short")
    
    # Check for common basis file markers
    has_header = any("BASIS" in line.upper() or "****" in line for line in lines[:10])
    
    if not has_header:
        errors.append("No basis set header found")
    
    if errors:
        print_error("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
        return 1
    
    print_success("Basis file format appears valid")
    return 0
