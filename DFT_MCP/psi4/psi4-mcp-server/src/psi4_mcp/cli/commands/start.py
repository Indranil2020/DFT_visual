"""
Start Command for Psi4 MCP Server CLI.

Starts the MCP server with specified configuration.
"""

import argparse
import os
import sys
from typing import Optional

from psi4_mcp.cli.utils import (
    print_error,
    print_info,
    print_success,
    check_psi4_available,
    get_psi4_version,
    setup_psi4_environment,
)


def run_start(args: argparse.Namespace) -> int:
    """Run the start command."""
    print_info("Starting Psi4 MCP Server...")
    
    # Check Psi4 availability
    if not check_psi4_available():
        print_error("Psi4 is not installed. Please install Psi4 first.")
        print_info("Install with: conda install -c psi4 psi4")
        return 1
    
    psi4_version = get_psi4_version()
    print_info(f"Psi4 version: {psi4_version}")
    
    # Set up scratch directory
    scratch_dir = args.scratch
    if scratch_dir is None:
        scratch_dir = os.environ.get("PSI_SCRATCH", "/tmp/psi4_scratch")
    
    if not os.path.exists(scratch_dir):
        os.makedirs(scratch_dir, exist_ok=True)
        print_info(f"Created scratch directory: {scratch_dir}")
    
    os.environ["PSI_SCRATCH"] = scratch_dir
    
    # Set up Psi4 environment
    if not setup_psi4_environment(
        memory=args.memory,
        threads=args.threads,
        scratch=scratch_dir,
    ):
        return 1
    
    print_info(f"Memory: {args.memory}")
    print_info(f"Threads: {args.threads}")
    print_info(f"Scratch: {scratch_dir}")
    print_info(f"Transport: {args.transport}")
    
    # Start the server
    if args.transport == "stdio":
        return start_stdio_server()
    elif args.transport == "http":
        return start_http_server(args.host, args.port)
    
    return 0


def start_stdio_server() -> int:
    """Start server with stdio transport."""
    print_success("Server starting with stdio transport...")
    print_info("Ready to accept MCP connections")
    
    # Import and run the server
    from psi4_mcp.server import mcp
    
    # Run the server (this blocks)
    mcp.run()
    
    return 0


def start_http_server(host: str, port: int) -> int:
    """Start server with HTTP transport."""
    print_success(f"Server starting at http://{host}:{port}")
    
    # Import and run the server with HTTP
    from psi4_mcp.server import mcp
    
    # Note: HTTP transport requires additional setup
    # This is a simplified version
    print_info("HTTP transport requires SSE support")
    print_info("Starting server...")
    
    # For HTTP, we would use uvicorn or similar
    # mcp.run_http(host=host, port=port)
    
    # Fallback to stdio for now
    print_info("Falling back to stdio transport")
    mcp.run()
    
    return 0


def configure_logging_for_server() -> None:
    """Configure logging for server operation."""
    import logging
    
    # All logging must go to stderr for stdio transport
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    
    # Suppress noisy loggers
    logging.getLogger("psi4").setLevel(logging.WARNING)


def check_dependencies() -> bool:
    """Check all required dependencies."""
    required = ["psi4", "mcp", "pydantic", "numpy"]
    missing = []
    
    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print_error(f"Missing dependencies: {', '.join(missing)}")
        return False
    
    return True
