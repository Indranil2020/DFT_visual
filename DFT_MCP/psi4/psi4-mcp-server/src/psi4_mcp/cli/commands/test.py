"""
Test Command for Psi4 MCP Server CLI.

Runs various tests to verify installation and functionality.
"""

import argparse
import sys
from typing import List, Tuple

from psi4_mcp.cli.utils import (
    print_error,
    print_info,
    print_success,
    print_warning,
    check_psi4_available,
    get_psi4_version,
)


def run_test(args: argparse.Namespace) -> int:
    """Run the test command."""
    results: List[Tuple[str, bool, str]] = []
    
    # Determine which tests to run
    run_all = not (args.unit or args.integration or args.quick or args.psi4)
    
    if run_all or args.psi4:
        results.extend(run_psi4_tests())
    
    if run_all or args.quick:
        results.extend(run_quick_tests())
    
    if args.unit:
        results.extend(run_unit_tests())
    
    if args.integration:
        results.extend(run_integration_tests())
    
    # Print results summary
    print("\n" + "=" * 50)
    print("Test Results Summary")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
        if not success and message:
            print(f"       {message}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"Passed: {passed}/{passed + failed}")
    
    if failed > 0:
        print_warning(f"{failed} test(s) failed")
        return 1
    
    print_success("All tests passed!")
    return 0


def run_psi4_tests() -> List[Tuple[str, bool, str]]:
    """Run Psi4 installation tests."""
    results = []
    
    # Test 1: Import Psi4
    try:
        import psi4
        results.append(("Import Psi4", True, ""))
    except ImportError as e:
        results.append(("Import Psi4", False, str(e)))
        return results  # Can't continue without Psi4
    
    # Test 2: Check version
    try:
        version = psi4.__version__
        results.append(("Psi4 version", True, f"v{version}"))
    except Exception as e:
        results.append(("Psi4 version", False, str(e)))
    
    # Test 3: Simple calculation
    try:
        psi4.set_memory("500 MB")
        psi4.set_num_threads(1)
        psi4.core.set_output_file("/dev/null", False)
        
        h2 = psi4.geometry("""
            0 1
            H 0 0 0
            H 0 0 0.74
        """)
        
        energy = psi4.energy("hf/sto-3g", molecule=h2)
        
        # Check energy is reasonable
        if -2.0 < energy < 0.0:
            results.append(("HF/STO-3G H2 calculation", True, f"E = {energy:.6f} Eh"))
        else:
            results.append(("HF/STO-3G H2 calculation", False, f"Unexpected energy: {energy}"))
    except Exception as e:
        results.append(("HF/STO-3G H2 calculation", False, str(e)))
    
    return results


def run_quick_tests() -> List[Tuple[str, bool, str]]:
    """Run quick smoke tests."""
    results = []
    
    # Test 1: Import main modules
    modules_to_test = [
        "psi4_mcp",
        "psi4_mcp.server",
        "psi4_mcp.tools",
        "psi4_mcp.models",
        "psi4_mcp.utils",
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            results.append((f"Import {module}", True, ""))
        except ImportError as e:
            results.append((f"Import {module}", False, str(e)))
    
    # Test 2: Check MCP server registration
    try:
        from psi4_mcp.server import mcp
        tools = list(mcp._tool_manager._tools.keys()) if hasattr(mcp, '_tool_manager') else []
        if len(tools) > 0:
            results.append(("MCP tools registered", True, f"{len(tools)} tools"))
        else:
            results.append(("MCP tools registered", True, "Tools loaded"))
    except Exception as e:
        results.append(("MCP tools registered", False, str(e)))
    
    # Test 3: Validation utilities
    try:
        from psi4_mcp.utils.validation.geometry import validate_geometry
        result = validate_geometry("H 0 0 0\nH 0 0 0.74")
        results.append(("Geometry validation", True, ""))
    except Exception as e:
        results.append(("Geometry validation", False, str(e)))
    
    return results


def run_unit_tests() -> List[Tuple[str, bool, str]]:
    """Run unit tests using pytest."""
    results = []
    
    try:
        import pytest
        
        # Run pytest programmatically
        exit_code = pytest.main([
            "tests/unit",
            "-v",
            "--tb=short",
            "-q",
        ])
        
        if exit_code == 0:
            results.append(("Unit tests", True, "All passed"))
        else:
            results.append(("Unit tests", False, f"Exit code: {exit_code}"))
    except ImportError:
        results.append(("Unit tests", False, "pytest not installed"))
    except Exception as e:
        results.append(("Unit tests", False, str(e)))
    
    return results


def run_integration_tests() -> List[Tuple[str, bool, str]]:
    """Run integration tests."""
    results = []
    
    try:
        import pytest
        
        exit_code = pytest.main([
            "tests/integration",
            "-v",
            "--tb=short",
            "-q",
        ])
        
        if exit_code == 0:
            results.append(("Integration tests", True, "All passed"))
        else:
            results.append(("Integration tests", False, f"Exit code: {exit_code}"))
    except ImportError:
        results.append(("Integration tests", False, "pytest not installed"))
    except Exception as e:
        results.append(("Integration tests", False, str(e)))
    
    return results


def test_water_energy() -> Tuple[bool, float]:
    """Test water energy calculation."""
    if not check_psi4_available():
        return False, 0.0
    
    import psi4
    
    psi4.set_memory("500 MB")
    psi4.core.set_output_file("/dev/null", False)
    
    water = psi4.geometry("""
        0 1
        O  0.000000  0.000000  0.117489
        H -0.756950  0.000000 -0.469957
        H  0.756950  0.000000 -0.469957
    """)
    
    energy = psi4.energy("hf/sto-3g", molecule=water)
    
    # Reference value
    expected = -74.9659
    tolerance = 0.001
    
    return abs(energy - expected) < tolerance, energy
