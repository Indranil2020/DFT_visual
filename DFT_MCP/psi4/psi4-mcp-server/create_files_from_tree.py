#!/usr/bin/env python3
"""
Psi4 MCP Server - Create Files from Tree
Parses psi4_mcp_complete_tree.txt and creates all files
Version: 1.0
Date: 2025-11-27
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("psi4-mcp-server")
TREE_FILE = Path("psi4_mcp_complete_tree.txt")

# Templates
PY_TEMPLATE = '''"""
Psi4 MCP Server - {filename}

TODO: Implement according to psi4_mcp_comprehensive_plan.md
"""

pass
'''

MD_TEMPLATE = '''# {filename}

TODO: Add content
'''

YAML_TEMPLATE = '''# Psi4 MCP Server Configuration
# TODO: Add settings
'''

def get_template(filename):
    """Get appropriate template based on file extension."""
    if filename.endswith('.py'):
        return PY_TEMPLATE
    elif filename.endswith('.md'):
        return MD_TEMPLATE
    elif filename.endswith(('.yml', '.yaml')):
        return YAML_TEMPLATE
    else:
        return "# Placeholder\n"

def parse_tree_file():
    """Parse the tree file and extract all file paths."""
    if not TREE_FILE.exists():
        print(f"Error: {TREE_FILE} not found!")
        return []
    
    files = []
    with open(TREE_FILE, 'r') as f:
        for line in f:
            # Skip empty lines and directory markers
            line = line.rstrip()
            if not line or '├──' not in line and '└──' not in line:
                continue
            
            # Extract filename (after tree characters)
            match = re.search(r'[├└]── (.+)$', line)
            if match:
                filename = match.group(1).strip()
                # Skip if it's a directory (no extension or ends with /)
                if '.' in filename and not filename.endswith('/'):
                    files.append(filename)
    
    return files

def build_full_paths():
    """Build full file paths from tree structure."""
    if not TREE_FILE.exists():
        return []
    
    paths = []
    current_path = []
    
    with open(TREE_FILE, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        # Skip header lines
        if line.startswith('psi4-mcp-server') or line.strip() == '':
            continue
        
        # Count indentation level
        stripped = line.lstrip()
        if not stripped:
            continue
        
        indent = len(line) - len(stripped)
        level = indent // 4  # Assuming 4 spaces per level
        
        # Extract name
        match = re.search(r'[├└│]── (.+)$', stripped)
        if not match:
            continue
        
        name = match.group(1).strip()
        
        # Adjust current path based on level
        current_path = current_path[:level]
        current_path.append(name)
        
        # If it's a file (has extension), add to paths
        if '.' in name and not name.endswith('/'):
            full_path = '/'.join(current_path)
            paths.append(full_path)
    
    return paths

def create_file(filepath: Path):
    """Create a file with appropriate template."""
    if filepath.exists():
        return False
    
    # Create parent directories
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Get template and create file
    template = get_template(filepath.name)
    content = template.format(filename=filepath.name)
    filepath.write_text(content)
    
    return True

def main():
    print("=" * 60)
    print("Creating All Files from Tree Structure")
    print("=" * 60)
    print()
    
    if not PROJECT_ROOT.exists():
        print(f"Error: {PROJECT_ROOT} not found!")
        print("Run ./setup_structure.sh first")
        return 1
    
    os.chdir(PROJECT_ROOT)
    print(f"Working in: {Path.cwd()}")
    print()
    
    # Parse tree file from parent directory
    os.chdir("..")
    file_paths = build_full_paths()
    os.chdir(PROJECT_ROOT)
    
    if not file_paths:
        print("No files found in tree file!")
        return 1
    
    print(f"Found {len(file_paths)} files to create")
    print()
    
    created = 0
    skipped = 0
    
    for file_path in file_paths:
        filepath = Path(file_path)
        if create_file(filepath):
            created += 1
            if created % 50 == 0:
                print(f"  Created {created} files...")
        else:
            skipped += 1
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Files created: {created}")
    print(f"Files skipped (already exist): {skipped}")
    print(f"Total files: {created + skipped}")
    print()
    
    # Final statistics
    total_files = sum(1 for _ in Path('.').rglob('*') if _.is_file())
    total_py = sum(1 for _ in Path('.').rglob('*.py'))
    
    print(f"Total files in project: {total_files}")
    print(f"Python files: {total_py}")
    print()
    print("✓ Done!")
    
    return 0

if __name__ == "__main__":
    exit(main())

