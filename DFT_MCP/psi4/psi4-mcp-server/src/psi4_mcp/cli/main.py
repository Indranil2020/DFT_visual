"""
Main CLI entry point for Psi4 MCP Server.

Provides the command-line interface using argparse.
"""

import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="psi4-mcp",
        description="Psi4 MCP Server - Quantum Chemistry via Model Context Protocol",
        epilog="For more information, visit: https://github.com/psi4/psi4-mcp-server",
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="Increase verbosity (can be repeated)",
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Available commands",
    )
    
    # Start command
    start_parser = subparsers.add_parser(
        "start",
        help="Start the MCP server",
    )
    start_parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    start_parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP transport (default: localhost)",
    )
    start_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)",
    )
    start_parser.add_argument(
        "--memory",
        default="2 GB",
        help="Memory limit for Psi4 (default: 2 GB)",
    )
    start_parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of threads (default: 1)",
    )
    start_parser.add_argument(
        "--scratch",
        help="Scratch directory for Psi4",
    )
    
    # Test command
    test_parser = subparsers.add_parser(
        "test",
        help="Run tests",
    )
    test_parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests",
    )
    test_parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests",
    )
    test_parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick smoke tests",
    )
    test_parser.add_argument(
        "--psi4",
        action="store_true",
        help="Test Psi4 installation",
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate inputs",
    )
    validate_parser.add_argument(
        "input_file",
        help="Input file to validate",
    )
    validate_parser.add_argument(
        "--type",
        choices=["geometry", "input", "basis"],
        default="input",
        help="Type of validation (default: input)",
    )
    
    # Convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert file formats",
    )
    convert_parser.add_argument(
        "input_file",
        help="Input file",
    )
    convert_parser.add_argument(
        "output_file",
        help="Output file",
    )
    convert_parser.add_argument(
        "--from",
        dest="from_format",
        choices=["xyz", "pdb", "mol2", "psi4"],
        help="Input format (auto-detected if not specified)",
    )
    convert_parser.add_argument(
        "--to",
        dest="to_format",
        choices=["xyz", "psi4", "json"],
        help="Output format (auto-detected if not specified)",
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Show information about methods, basis sets, etc.",
    )
    info_parser.add_argument(
        "topic",
        choices=["methods", "basis", "functionals", "all"],
        help="Topic to show information about",
    )
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    if parsed_args.version:
        from psi4_mcp import __version__
        print(f"psi4-mcp version {__version__}")
        return 0
    
    if parsed_args.command is None:
        parser.print_help()
        return 0
    
    # Set up logging based on verbosity
    import logging
    log_level = logging.WARNING
    if parsed_args.verbose == 1:
        log_level = logging.INFO
    elif parsed_args.verbose >= 2:
        log_level = logging.DEBUG
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    
    # Dispatch to command handlers
    if parsed_args.command == "start":
        from psi4_mcp.cli.commands.start import run_start
        return run_start(parsed_args)
    
    elif parsed_args.command == "test":
        from psi4_mcp.cli.commands.test import run_test
        return run_test(parsed_args)
    
    elif parsed_args.command == "validate":
        from psi4_mcp.cli.commands.validate import run_validate
        return run_validate(parsed_args)
    
    elif parsed_args.command == "convert":
        from psi4_mcp.cli.commands.convert import run_convert
        return run_convert(parsed_args)
    
    elif parsed_args.command == "info":
        return run_info(parsed_args)
    
    return 0


def run_info(args: argparse.Namespace) -> int:
    """Run the info command."""
    topic = args.topic
    
    if topic == "methods" or topic == "all":
        print("=== Available Methods ===")
        print("Hartree-Fock: hf, rhf, uhf, rohf")
        print("DFT: b3lyp, pbe, pbe0, wb97x-d, m06-2x, cam-b3lyp")
        print("Post-HF: mp2, mp3, ccsd, ccsd(t)")
        print("CI: cisd, fci")
        print("SAPT: sapt0, sapt2, sapt2+")
        print()
    
    if topic == "basis" or topic == "all":
        print("=== Available Basis Sets ===")
        print("Minimal: sto-3g")
        print("Double-zeta: 6-31g*, cc-pvdz, def2-svp")
        print("Triple-zeta: 6-311g**, cc-pvtz, def2-tzvp")
        print("Quadruple-zeta: cc-pvqz, def2-qzvp")
        print("Augmented: aug-cc-pvdz, aug-cc-pvtz")
        print()
    
    if topic == "functionals" or topic == "all":
        print("=== DFT Functionals ===")
        print("LDA: svwn")
        print("GGA: blyp, pbe, bp86")
        print("Meta-GGA: tpss, m06-l")
        print("Hybrid: b3lyp, pbe0, b97")
        print("Range-separated: cam-b3lyp, wb97x, lc-wpbe")
        print("Double-hybrid: b2plyp")
        print()
    
    return 0


def cli() -> None:
    """CLI entry point for setuptools."""
    sys.exit(main())


if __name__ == "__main__":
    cli()
