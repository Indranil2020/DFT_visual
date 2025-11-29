"""
Psi4 MCP Server Version Information.

This module contains version information for the psi4-mcp-server package.
The version follows Semantic Versioning (SemVer) conventions:
- MAJOR: Incompatible API changes
- MINOR: New functionality in a backwards compatible manner
- PATCH: Backwards compatible bug fixes
"""

# Version components
MAJOR: int = 1
MINOR: int = 0
PATCH: int = 0

# Pre-release identifier (empty string for stable releases)
# Examples: "alpha", "beta", "rc1"
PRE_RELEASE: str = ""

# Build metadata (empty string if not applicable)
# Example: "build.123"
BUILD_METADATA: str = ""

# Construct version string
__version__: str = f"{MAJOR}.{MINOR}.{PATCH}"

if PRE_RELEASE:
    __version__ = f"{__version__}-{PRE_RELEASE}"

if BUILD_METADATA:
    __version__ = f"{__version__}+{BUILD_METADATA}"

# Version tuple for programmatic comparison
VERSION_TUPLE: tuple[int, int, int] = (MAJOR, MINOR, PATCH)

# Package metadata
__title__: str = "psi4-mcp-server"
__description__: str = (
    "Model Context Protocol (MCP) server for Psi4 quantum chemistry calculations"
)
__author__: str = "Psi4 MCP Team"
__author_email__: str = "psi4mcp@example.com"
__license__: str = "LGPL-3.0"
__copyright__: str = "Copyright 2025 Psi4 MCP Team"
__url__: str = "https://github.com/psi4/psi4-mcp-server"
__docs_url__: str = "https://psi4-mcp-server.readthedocs.io"

# Minimum required Python version
PYTHON_REQUIRES: str = ">=3.10"

# Minimum required Psi4 version
PSI4_MIN_VERSION: str = "1.8"


def get_version() -> str:
    """
    Return the full version string.
    
    Returns:
        Full version string including pre-release and build metadata if present.
    """
    return __version__


def get_version_tuple() -> tuple[int, int, int]:
    """
    Return the version as a tuple of integers.
    
    Returns:
        Tuple of (major, minor, patch) version numbers.
    """
    return VERSION_TUPLE


def is_pre_release() -> bool:
    """
    Check if this is a pre-release version.
    
    Returns:
        True if this is a pre-release (alpha, beta, rc), False otherwise.
    """
    return bool(PRE_RELEASE)


def get_package_info() -> dict[str, str]:
    """
    Return complete package metadata as a dictionary.
    
    Returns:
        Dictionary containing all package metadata.
    """
    return {
        "name": __title__,
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "author_email": __author_email__,
        "license": __license__,
        "copyright": __copyright__,
        "url": __url__,
        "docs_url": __docs_url__,
        "python_requires": PYTHON_REQUIRES,
        "psi4_min_version": PSI4_MIN_VERSION,
    }
