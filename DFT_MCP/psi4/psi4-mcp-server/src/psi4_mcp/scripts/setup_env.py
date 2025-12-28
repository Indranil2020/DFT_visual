"""
Environment Setup Script for Psi4 MCP Server.

Sets up the computational environment for running Psi4 calculations.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_executable": sys.executable,
    }


def get_cpu_count() -> int:
    """Get number of CPU cores."""
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


def get_memory_info() -> Dict[str, float]:
    """Get memory information in GB."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        return {
            "total": mem.total / (1024**3),
            "available": mem.available / (1024**3),
            "used": mem.used / (1024**3),
            "percent": mem.percent,
        }
    except ImportError:
        return {"total": 0, "available": 0, "used": 0, "percent": 0}


def find_scratch_directory() -> Path:
    """Find or create a suitable scratch directory."""
    # Check environment variable first
    psi_scratch = os.environ.get("PSI_SCRATCH")
    if psi_scratch:
        scratch = Path(psi_scratch)
        if scratch.exists() or scratch.parent.exists():
            scratch.mkdir(parents=True, exist_ok=True)
            return scratch
    
    # Try common locations
    candidates = [
        Path("/tmp/psi4_scratch"),
        Path("/scratch/psi4"),
        Path.home() / ".psi4_scratch",
    ]
    
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            # Test write access
            test_file = candidate / ".test"
            test_file.write_text("test")
            test_file.unlink()
            return candidate
        except (OSError, PermissionError):
            continue
    
    # Fall back to temp directory
    import tempfile
    return Path(tempfile.mkdtemp(prefix="psi4_"))


def setup_environment(
    memory: str = "auto",
    threads: int = 0,
    scratch: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Set up the Psi4 environment.
    
    Args:
        memory: Memory to allocate (auto, or specific like "4 GB")
        threads: Number of threads (0 = auto)
        scratch: Scratch directory path
        
    Returns:
        Dictionary with environment configuration
    """
    config = {}
    
    # System info
    sys_info = get_system_info()
    config["system"] = sys_info
    
    # CPU configuration
    n_cpus = get_cpu_count()
    if threads <= 0:
        # Use half of available cores by default
        threads = max(1, n_cpus // 2)
    config["threads"] = threads
    
    # Memory configuration
    mem_info = get_memory_info()
    if memory == "auto":
        # Use 50% of available memory, max 8 GB
        available_gb = mem_info.get("available", 4)
        auto_memory = min(available_gb * 0.5, 8)
        memory = f"{auto_memory:.1f} GB"
    config["memory"] = memory
    
    # Scratch directory
    if scratch:
        scratch_dir = Path(scratch)
        scratch_dir.mkdir(parents=True, exist_ok=True)
    else:
        scratch_dir = find_scratch_directory()
    config["scratch"] = str(scratch_dir)
    
    # Set environment variables
    os.environ["PSI_SCRATCH"] = str(scratch_dir)
    os.environ["OMP_NUM_THREADS"] = str(threads)
    os.environ["MKL_NUM_THREADS"] = str(threads)
    
    # Check Psi4
    psi4_available = check_psi4()
    config["psi4_available"] = psi4_available
    
    if psi4_available:
        config["psi4_version"] = get_psi4_version()
        
        # Configure Psi4
        configure_psi4(memory, threads)
    
    return config


def check_psi4() -> bool:
    """Check if Psi4 is available."""
    try:
        import psi4
        return True
    except ImportError:
        return False


def get_psi4_version() -> Optional[str]:
    """Get Psi4 version."""
    try:
        import psi4
        return psi4.__version__
    except ImportError:
        return None


def configure_psi4(memory: str, threads: int) -> None:
    """Configure Psi4 settings."""
    try:
        import psi4
        
        psi4.set_memory(memory)
        psi4.set_num_threads(threads)
        
        # Suppress output by default
        psi4.core.set_output_file("/dev/null", False)
    except ImportError:
        pass


def create_config_file(config: Dict[str, Any], path: Optional[str] = None) -> Path:
    """
    Create a configuration file.
    
    Args:
        config: Configuration dictionary
        path: Output path (default: ~/.psi4_mcp/config.json)
        
    Returns:
        Path to created file
    """
    import json
    
    if path is None:
        config_dir = Path.home() / ".psi4_mcp"
        config_dir.mkdir(parents=True, exist_ok=True)
        path = config_dir / "config.json"
    else:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    
    return path


def load_config_file(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load configuration from file.
    
    Args:
        path: Config file path (default: ~/.psi4_mcp/config.json)
        
    Returns:
        Configuration dictionary or None
    """
    import json
    
    if path is None:
        path = Path.home() / ".psi4_mcp" / "config.json"
    else:
        path = Path(path)
    
    if not path.exists():
        return None
    
    with open(path) as f:
        return json.load(f)


def print_environment_info() -> None:
    """Print environment information."""
    print("\n" + "=" * 60)
    print("ENVIRONMENT INFORMATION")
    print("=" * 60)
    
    # System
    sys_info = get_system_info()
    print(f"\nSystem: {sys_info['platform']} {sys_info['platform_release']}")
    print(f"Architecture: {sys_info['architecture']}")
    print(f"Python: {sys.version}")
    
    # CPU
    n_cpus = get_cpu_count()
    print(f"\nCPU Cores: {n_cpus}")
    
    # Memory
    mem_info = get_memory_info()
    if mem_info["total"] > 0:
        print(f"Total Memory: {mem_info['total']:.1f} GB")
        print(f"Available Memory: {mem_info['available']:.1f} GB")
    
    # Psi4
    print(f"\nPsi4 Available: {check_psi4()}")
    if check_psi4():
        print(f"Psi4 Version: {get_psi4_version()}")
    
    # Scratch
    scratch = find_scratch_directory()
    print(f"\nScratch Directory: {scratch}")
    
    # Check scratch space
    try:
        usage = shutil.disk_usage(scratch)
        free_gb = usage.free / (1024**3)
        print(f"Scratch Free Space: {free_gb:.1f} GB")
    except Exception:
        pass


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Set up environment for Psi4 MCP Server"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show environment information",
    )
    parser.add_argument(
        "--memory",
        default="auto",
        help="Memory to allocate (default: auto)",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=0,
        help="Number of threads (default: auto)",
    )
    parser.add_argument(
        "--scratch",
        help="Scratch directory path",
    )
    parser.add_argument(
        "--save-config",
        action="store_true",
        help="Save configuration to file",
    )
    
    args = parser.parse_args()
    
    if args.info:
        print_environment_info()
        return 0
    
    print("Setting up environment...")
    
    config = setup_environment(
        memory=args.memory,
        threads=args.threads,
        scratch=args.scratch,
    )
    
    print(f"\nConfiguration:")
    print(f"  Memory: {config['memory']}")
    print(f"  Threads: {config['threads']}")
    print(f"  Scratch: {config['scratch']}")
    print(f"  Psi4 Available: {config['psi4_available']}")
    
    if config['psi4_available']:
        print(f"  Psi4 Version: {config.get('psi4_version', 'unknown')}")
    
    if args.save_config:
        config_path = create_config_file(config)
        print(f"\nConfiguration saved to: {config_path}")
    
    print("\n✓ Environment setup complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
