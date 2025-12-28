"""
Convert Command for Psi4 MCP Server CLI.

Converts between different molecular file formats.
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
    write_file,
    get_file_extension,
    detect_format_from_extension,
)


def run_convert(args: argparse.Namespace) -> int:
    """Run the convert command."""
    input_file = args.input_file
    output_file = args.output_file
    
    if not file_exists(input_file):
        print_error(f"Input file not found: {input_file}")
        return 1
    
    # Detect formats
    from_format = args.from_format or detect_format_from_extension(input_file)
    to_format = args.to_format or detect_format_from_extension(output_file)
    
    if not from_format:
        print_error(f"Cannot detect input format for: {input_file}")
        return 1
    
    if not to_format:
        print_error(f"Cannot detect output format for: {output_file}")
        return 1
    
    print_info(f"Converting: {input_file} -> {output_file}")
    print_info(f"Format: {from_format} -> {to_format}")
    
    # Read input
    content = read_file(input_file)
    
    # Parse input
    molecule_data = parse_input(content, from_format)
    if molecule_data is None:
        print_error("Failed to parse input file")
        return 1
    
    # Convert to output format
    output_content = format_output(molecule_data, to_format)
    if output_content is None:
        print_error("Failed to convert to output format")
        return 1
    
    # Write output
    write_file(output_file, output_content)
    
    print_success(f"Converted successfully: {output_file}")
    return 0


def parse_input(content: str, format: str) -> Optional[Dict[str, Any]]:
    """Parse input file content."""
    if format == "xyz":
        return parse_xyz(content)
    elif format == "pdb":
        return parse_pdb(content)
    elif format == "mol2":
        return parse_mol2(content)
    elif format == "psi4":
        return parse_psi4(content)
    elif format == "json":
        return parse_json(content)
    
    return None


def format_output(data: Dict[str, Any], format: str) -> Optional[str]:
    """Format molecule data for output."""
    if format == "xyz":
        return format_xyz(data)
    elif format == "psi4":
        return format_psi4(data)
    elif format == "json":
        return format_json(data)
    
    return None


def parse_xyz(content: str) -> Optional[Dict[str, Any]]:
    """Parse XYZ format."""
    lines = content.strip().split("\n")
    
    if len(lines) < 2:
        return None
    
    try:
        n_atoms = int(lines[0].strip())
    except ValueError:
        return None
    
    comment = lines[1].strip() if len(lines) > 1 else ""
    
    elements = []
    coordinates = []
    
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) < 4:
            continue
        
        elements.append(parts[0])
        try:
            coords = [float(parts[1]), float(parts[2]), float(parts[3])]
            coordinates.append(coords)
        except ValueError:
            continue
    
    return {
        "elements": elements,
        "coordinates": coordinates,
        "comment": comment,
        "charge": 0,
        "multiplicity": 1,
    }


def parse_pdb(content: str) -> Optional[Dict[str, Any]]:
    """Parse PDB format."""
    elements = []
    coordinates = []
    
    for line in content.split("\n"):
        if line.startswith("ATOM") or line.startswith("HETATM"):
            if len(line) < 54:
                continue
            
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
            except ValueError:
                continue
            
            # Get element from columns 77-78 or from atom name
            if len(line) >= 78:
                element = line[76:78].strip()
            else:
                element = line[12:16].strip()[0]
            
            elements.append(element)
            coordinates.append([x, y, z])
    
    if not elements:
        return None
    
    return {
        "elements": elements,
        "coordinates": coordinates,
        "comment": "Converted from PDB",
        "charge": 0,
        "multiplicity": 1,
    }


def parse_mol2(content: str) -> Optional[Dict[str, Any]]:
    """Parse MOL2 format."""
    elements = []
    coordinates = []
    
    in_atom_section = False
    
    for line in content.split("\n"):
        if "@<TRIPOS>ATOM" in line:
            in_atom_section = True
            continue
        elif line.startswith("@<TRIPOS>"):
            in_atom_section = False
            continue
        
        if in_atom_section:
            parts = line.split()
            if len(parts) >= 6:
                try:
                    x = float(parts[2])
                    y = float(parts[3])
                    z = float(parts[4])
                    element = parts[5].split(".")[0]  # Remove atom type suffix
                    
                    elements.append(element)
                    coordinates.append([x, y, z])
                except (ValueError, IndexError):
                    continue
    
    if not elements:
        return None
    
    return {
        "elements": elements,
        "coordinates": coordinates,
        "comment": "Converted from MOL2",
        "charge": 0,
        "multiplicity": 1,
    }


def parse_psi4(content: str) -> Optional[Dict[str, Any]]:
    """Parse Psi4 input format."""
    # Find molecule block
    import re
    
    mol_match = re.search(r'molecule\s*\{?\s*\n(.*?)\n\s*\}', content, re.DOTALL | re.IGNORECASE)
    
    if not mol_match:
        # Try simple format
        lines = content.strip().split("\n")
        geometry_lines = []
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    float(parts[1])
                    float(parts[2])
                    float(parts[3])
                    geometry_lines.append(line)
                except (ValueError, IndexError):
                    continue
        
        if not geometry_lines:
            return None
        
        content = "\n".join(geometry_lines)
    else:
        content = mol_match.group(1)
    
    # Parse charge/multiplicity
    charge = 0
    multiplicity = 1
    
    lines = content.strip().split("\n")
    first_line = lines[0].split()
    
    if len(first_line) == 2:
        try:
            charge = int(first_line[0])
            multiplicity = int(first_line[1])
            lines = lines[1:]
        except ValueError:
            pass
    
    # Parse coordinates
    elements = []
    coordinates = []
    
    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            try:
                element = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                
                elements.append(element)
                coordinates.append([x, y, z])
            except (ValueError, IndexError):
                continue
    
    if not elements:
        return None
    
    return {
        "elements": elements,
        "coordinates": coordinates,
        "comment": "Converted from Psi4",
        "charge": charge,
        "multiplicity": multiplicity,
    }


def parse_json(content: str) -> Optional[Dict[str, Any]]:
    """Parse JSON format."""
    try:
        data = json.loads(content)
        
        # Handle different JSON formats
        if "elements" in data and "coordinates" in data:
            return data
        elif "molecule" in data:
            mol = data["molecule"]
            if "geometry" in mol:
                # Parse geometry string
                return parse_psi4(mol["geometry"])
        
        return None
    except json.JSONDecodeError:
        return None


def format_xyz(data: Dict[str, Any]) -> str:
    """Format as XYZ."""
    elements = data["elements"]
    coordinates = data["coordinates"]
    comment = data.get("comment", "")
    
    lines = [str(len(elements)), comment]
    
    for elem, (x, y, z) in zip(elements, coordinates):
        lines.append(f"{elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
    
    return "\n".join(lines)


def format_psi4(data: Dict[str, Any]) -> str:
    """Format as Psi4 input."""
    elements = data["elements"]
    coordinates = data["coordinates"]
    charge = data.get("charge", 0)
    multiplicity = data.get("multiplicity", 1)
    
    lines = [
        "molecule {",
        f"  {charge} {multiplicity}",
    ]
    
    for elem, (x, y, z) in zip(elements, coordinates):
        lines.append(f"  {elem:2s} {x:15.10f} {y:15.10f} {z:15.10f}")
    
    lines.append("}")
    
    return "\n".join(lines)


def format_json(data: Dict[str, Any]) -> str:
    """Format as JSON."""
    return json.dumps(data, indent=2)
