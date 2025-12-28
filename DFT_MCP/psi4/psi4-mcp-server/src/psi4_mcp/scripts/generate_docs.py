"""
Documentation Generation Script for Psi4 MCP Server.

Generates API documentation and user guides.
"""

import inspect
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type


class DocGenerator:
    """Generates documentation for the Psi4 MCP Server."""
    
    def __init__(self, output_dir: str = "docs"):
        """Initialize documentation generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_all(self) -> None:
        """Generate all documentation."""
        print("Generating documentation...")
        
        self.generate_api_reference()
        self.generate_tool_reference()
        self.generate_cli_reference()
        self.generate_index()
        
        print(f"Documentation generated in {self.output_dir}")
    
    def generate_api_reference(self) -> None:
        """Generate API reference documentation."""
        api_dir = self.output_dir / "api"
        api_dir.mkdir(exist_ok=True)
        
        # Document main modules
        modules = [
            ("psi4_mcp", "Main Package"),
            ("psi4_mcp.server", "MCP Server"),
            ("psi4_mcp.tools", "Calculation Tools"),
            ("psi4_mcp.models", "Data Models"),
            ("psi4_mcp.utils", "Utilities"),
        ]
        
        for module_name, title in modules:
            self._document_module(module_name, title, api_dir)
    
    def _document_module(
        self,
        module_name: str,
        title: str,
        output_dir: Path,
    ) -> None:
        """Document a single module."""
        try:
            module = __import__(module_name, fromlist=[""])
        except ImportError:
            return
        
        lines = [f"# {title}", "", f"Module: `{module_name}`", ""]
        
        # Module docstring
        if module.__doc__:
            lines.append(module.__doc__.strip())
            lines.append("")
        
        # List classes
        classes = []
        functions = []
        
        for name in dir(module):
            if name.startswith("_"):
                continue
            
            obj = getattr(module, name)
            
            if inspect.isclass(obj):
                classes.append((name, obj))
            elif inspect.isfunction(obj):
                functions.append((name, obj))
        
        if classes:
            lines.append("## Classes")
            lines.append("")
            for name, cls in classes:
                lines.append(f"### `{name}`")
                if cls.__doc__:
                    lines.append(cls.__doc__.strip())
                lines.append("")
        
        if functions:
            lines.append("## Functions")
            lines.append("")
            for name, func in functions:
                lines.append(f"### `{name}()`")
                if func.__doc__:
                    lines.append(func.__doc__.strip())
                lines.append("")
        
        # Write file
        filename = module_name.replace(".", "_") + ".md"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            f.write("\n".join(lines))
    
    def generate_tool_reference(self) -> None:
        """Generate tool reference documentation."""
        tools_dir = self.output_dir / "tools"
        tools_dir.mkdir(exist_ok=True)
        
        # Generate index
        lines = [
            "# Tool Reference",
            "",
            "Complete reference for all MCP tools provided by the Psi4 MCP Server.",
            "",
            "## Categories",
            "",
        ]
        
        categories = [
            ("Core", ["energy", "optimization", "gradient", "hessian"]),
            ("Frequencies", ["frequencies", "thermochemistry"]),
            ("Properties", ["properties", "dipole", "charges"]),
            ("Excited States", ["tddft", "cis", "eom_ccsd"]),
            ("Advanced", ["sapt", "ccsd", "casscf"]),
        ]
        
        for category, tools in categories:
            lines.append(f"### {category}")
            lines.append("")
            for tool in tools:
                lines.append(f"- [{tool}](tools/{tool}.md)")
            lines.append("")
        
        # Write index
        with open(tools_dir / "index.md", "w") as f:
            f.write("\n".join(lines))
        
        # Generate individual tool docs
        self._generate_tool_docs(tools_dir)
    
    def _generate_tool_docs(self, output_dir: Path) -> None:
        """Generate documentation for individual tools."""
        # Template for tool documentation
        tool_template = """# {name}

{description}

## Usage

```python
result = await {function_name}({{
    "molecule": {{
        "geometry": "...",
        "charge": 0,
        "multiplicity": 1
    }},
    "method": "{default_method}",
    "basis": "{default_basis}"
}})
```

## Parameters

{parameters}

## Returns

{returns}

## Examples

{examples}
"""
        
        # Define tools
        tools = [
            {
                "name": "Energy Calculation",
                "function_name": "calculate_energy",
                "description": "Calculate the electronic energy of a molecular system.",
                "default_method": "b3lyp",
                "default_basis": "cc-pvdz",
                "parameters": "- `molecule`: Molecular geometry and charge/multiplicity\n- `method`: Computational method\n- `basis`: Basis set",
                "returns": "Energy in Hartree and calculation metadata",
                "examples": "See examples/01_basic_energy.py",
            },
            {
                "name": "Geometry Optimization",
                "function_name": "optimize_geometry",
                "description": "Optimize molecular geometry to find energy minimum.",
                "default_method": "b3lyp",
                "default_basis": "6-31g*",
                "parameters": "- `molecule`: Initial geometry\n- `method`: Computational method\n- `basis`: Basis set\n- `max_iterations`: Maximum optimization steps",
                "returns": "Optimized geometry and final energy",
                "examples": "See examples/02_geometry_optimization.py",
            },
        ]
        
        for tool in tools:
            content = tool_template.format(**tool)
            filename = tool["function_name"] + ".md"
            
            with open(output_dir / filename, "w") as f:
                f.write(content)
    
    def generate_cli_reference(self) -> None:
        """Generate CLI reference documentation."""
        cli_doc = """# CLI Reference

The Psi4 MCP Server provides a command-line interface for common operations.

## Installation

```bash
pip install psi4-mcp-server
```

## Commands

### Start Server

```bash
psi4-mcp start [OPTIONS]
```

Options:
- `--transport`: Transport protocol (stdio, http)
- `--host`: Host for HTTP transport
- `--port`: Port for HTTP transport
- `--memory`: Memory limit for Psi4
- `--threads`: Number of threads

### Run Tests

```bash
psi4-mcp test [OPTIONS]
```

Options:
- `--unit`: Run unit tests
- `--integration`: Run integration tests
- `--quick`: Run quick smoke tests
- `--psi4`: Test Psi4 installation

### Validate Input

```bash
psi4-mcp validate INPUT_FILE [OPTIONS]
```

Options:
- `--type`: Validation type (geometry, input, basis)

### Convert Formats

```bash
psi4-mcp convert INPUT_FILE OUTPUT_FILE [OPTIONS]
```

Options:
- `--from`: Input format
- `--to`: Output format

### Show Information

```bash
psi4-mcp info TOPIC
```

Topics: methods, basis, functionals, all
"""
        
        with open(self.output_dir / "cli.md", "w") as f:
            f.write(cli_doc)
    
    def generate_index(self) -> None:
        """Generate main index page."""
        index = """# Psi4 MCP Server Documentation

Welcome to the Psi4 MCP Server documentation.

## Quick Start

1. Install the package:
   ```bash
   pip install psi4-mcp-server
   ```

2. Start the server:
   ```bash
   psi4-mcp start
   ```

3. Connect your MCP client and start running calculations!

## Contents

- [API Reference](api/)
- [Tool Reference](tools/)
- [CLI Reference](cli.md)
- [Examples](examples/)
- [Tutorials](tutorials/)

## About

The Psi4 MCP Server provides a Model Context Protocol interface to the
Psi4 quantum chemistry package, enabling AI assistants to perform
quantum chemistry calculations.

## License

LGPL-3.0 (same as Psi4)
"""
        
        with open(self.output_dir / "index.md", "w") as f:
            f.write(index)


def generate_docs(output_dir: str = "docs") -> None:
    """
    Generate documentation.
    
    Args:
        output_dir: Output directory for documentation
    """
    generator = DocGenerator(output_dir)
    generator.generate_all()


if __name__ == "__main__":
    generate_docs()
