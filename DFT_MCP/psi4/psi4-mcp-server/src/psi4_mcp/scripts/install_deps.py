"""
Dependency Installation Script for Psi4 MCP Server.

Helps install and verify all required dependencies.
"""

import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Dependency:
    """Information about a dependency."""
    name: str
    package: str
    version: Optional[str] = None
    optional: bool = False
    conda_channel: Optional[str] = None
    description: str = ""


# Required dependencies
REQUIRED_DEPS = [
    Dependency(
        name="psi4",
        package="psi4",
        conda_channel="psi4",
        description="Quantum chemistry engine",
    ),
    Dependency(
        name="mcp",
        package="mcp[cli]",
        description="Model Context Protocol SDK",
    ),
    Dependency(
        name="pydantic",
        package="pydantic",
        version=">=2.0.0",
        description="Data validation",
    ),
    Dependency(
        name="numpy",
        package="numpy",
        description="Numerical computing",
    ),
]

# Optional dependencies
OPTIONAL_DEPS = [
    Dependency(
        name="ase",
        package="ase",
        optional=True,
        description="Atomic Simulation Environment",
    ),
    Dependency(
        name="rdkit",
        package="rdkit",
        optional=True,
        conda_channel="conda-forge",
        description="Cheminformatics toolkit",
    ),
    Dependency(
        name="openbabel",
        package="openbabel",
        optional=True,
        conda_channel="conda-forge",
        description="Chemical format conversion",
    ),
    Dependency(
        name="cclib",
        package="cclib",
        optional=True,
        description="Output file parsing",
    ),
    Dependency(
        name="qcportal",
        package="qcportal",
        optional=True,
        conda_channel="conda-forge",
        description="MolSSI QCArchive integration",
    ),
]

# Development dependencies
DEV_DEPS = [
    Dependency(
        name="pytest",
        package="pytest",
        version=">=7.0.0",
        optional=True,
        description="Testing framework",
    ),
    Dependency(
        name="pytest-asyncio",
        package="pytest-asyncio",
        optional=True,
        description="Async test support",
    ),
    Dependency(
        name="pytest-cov",
        package="pytest-cov",
        optional=True,
        description="Coverage reporting",
    ),
    Dependency(
        name="black",
        package="black",
        optional=True,
        description="Code formatter",
    ),
    Dependency(
        name="ruff",
        package="ruff",
        optional=True,
        description="Fast linter",
    ),
]


def check_dependency(dep: Dependency) -> Tuple[bool, Optional[str]]:
    """
    Check if a dependency is installed.
    
    Returns:
        Tuple of (is_installed, version)
    """
    try:
        module = __import__(dep.name.replace("-", "_"))
        version = getattr(module, "__version__", "unknown")
        return True, version
    except ImportError:
        return False, None


def install_pip(package: str, version: Optional[str] = None) -> bool:
    """Install a package using pip."""
    pkg = package
    if version:
        pkg = f"{package}{version}"
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", pkg
        ])
        return True
    except subprocess.CalledProcessError:
        return False


def install_conda(package: str, channel: Optional[str] = None) -> bool:
    """Install a package using conda."""
    cmd = ["conda", "install", "-y"]
    if channel:
        cmd.extend(["-c", channel])
    cmd.append(package)
    
    try:
        subprocess.check_call(cmd)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_all_dependencies() -> Dict[str, Dict[str, Any]]:
    """
    Check all dependencies.
    
    Returns:
        Dictionary with status of each dependency
    """
    status = {
        "required": {},
        "optional": {},
        "development": {},
    }
    
    for dep in REQUIRED_DEPS:
        installed, version = check_dependency(dep)
        status["required"][dep.name] = {
            "installed": installed,
            "version": version,
            "description": dep.description,
        }
    
    for dep in OPTIONAL_DEPS:
        installed, version = check_dependency(dep)
        status["optional"][dep.name] = {
            "installed": installed,
            "version": version,
            "description": dep.description,
        }
    
    for dep in DEV_DEPS:
        installed, version = check_dependency(dep)
        status["development"][dep.name] = {
            "installed": installed,
            "version": version,
            "description": dep.description,
        }
    
    return status


def install_required() -> List[str]:
    """
    Install all required dependencies.
    
    Returns:
        List of failed installations
    """
    failed = []
    
    for dep in REQUIRED_DEPS:
        installed, _ = check_dependency(dep)
        if installed:
            print(f"✓ {dep.name} already installed")
            continue
        
        print(f"Installing {dep.name}...")
        
        # Try conda for psi4
        if dep.conda_channel:
            if install_conda(dep.package, dep.conda_channel):
                print(f"✓ {dep.name} installed via conda")
                continue
        
        # Try pip
        if install_pip(dep.package, dep.version):
            print(f"✓ {dep.name} installed via pip")
            continue
        
        print(f"✗ Failed to install {dep.name}")
        failed.append(dep.name)
    
    return failed


def install_optional(names: Optional[List[str]] = None) -> List[str]:
    """
    Install optional dependencies.
    
    Args:
        names: Specific packages to install (None = all)
        
    Returns:
        List of failed installations
    """
    failed = []
    
    deps_to_install = OPTIONAL_DEPS
    if names:
        deps_to_install = [d for d in OPTIONAL_DEPS if d.name in names]
    
    for dep in deps_to_install:
        installed, _ = check_dependency(dep)
        if installed:
            print(f"✓ {dep.name} already installed")
            continue
        
        print(f"Installing {dep.name}...")
        
        # Try conda first if available
        if dep.conda_channel:
            if install_conda(dep.package, dep.conda_channel):
                print(f"✓ {dep.name} installed via conda")
                continue
        
        # Try pip
        if install_pip(dep.package, dep.version):
            print(f"✓ {dep.name} installed via pip")
            continue
        
        print(f"✗ Failed to install {dep.name}")
        failed.append(dep.name)
    
    return failed


def install_development() -> List[str]:
    """
    Install development dependencies.
    
    Returns:
        List of failed installations
    """
    failed = []
    
    for dep in DEV_DEPS:
        installed, _ = check_dependency(dep)
        if installed:
            print(f"✓ {dep.name} already installed")
            continue
        
        print(f"Installing {dep.name}...")
        
        if install_pip(dep.package, dep.version):
            print(f"✓ {dep.name} installed")
            continue
        
        print(f"✗ Failed to install {dep.name}")
        failed.append(dep.name)
    
    return failed


def print_status() -> None:
    """Print dependency status."""
    status = check_all_dependencies()
    
    print("\n" + "=" * 60)
    print("DEPENDENCY STATUS")
    print("=" * 60)
    
    for category, deps in status.items():
        print(f"\n{category.upper()}:")
        
        for name, info in deps.items():
            icon = "✓" if info["installed"] else "✗"
            version = info["version"] or "not installed"
            print(f"  {icon} {name}: {version}")
            print(f"      {info['description']}")


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Install dependencies for Psi4 MCP Server"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check dependency status only",
    )
    parser.add_argument(
        "--required",
        action="store_true",
        help="Install required dependencies",
    )
    parser.add_argument(
        "--optional",
        action="store_true",
        help="Install optional dependencies",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Install development dependencies",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Install all dependencies",
    )
    
    args = parser.parse_args()
    
    if args.check or not any([args.required, args.optional, args.dev, args.all]):
        print_status()
        return 0
    
    failed = []
    
    if args.required or args.all:
        failed.extend(install_required())
    
    if args.optional or args.all:
        failed.extend(install_optional())
    
    if args.dev or args.all:
        failed.extend(install_development())
    
    if failed:
        print(f"\nFailed to install: {', '.join(failed)}")
        return 1
    
    print("\nAll requested dependencies installed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
