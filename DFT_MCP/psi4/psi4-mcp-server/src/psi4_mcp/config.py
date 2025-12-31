"""
Psi4 MCP Server Configuration.

Manages server settings, defaults, and environment configuration.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class ServerConfig:
    """Server configuration settings."""
    
    # Memory and compute
    default_memory: int = 4000  # MB
    default_threads: int = 4
    max_memory: int = 64000  # MB
    max_threads: int = 64
    
    # Scratch and output
    scratch_dir: str = field(default_factory=lambda: os.environ.get('PSI_SCRATCH', '/tmp/psi4_scratch'))
    output_dir: str = field(default_factory=lambda: os.environ.get('PSI4_OUTPUT', '/tmp/psi4_output'))
    
    # Calculation defaults
    default_basis: str = "cc-pvdz"
    default_method: str = "hf"
    default_scf_type: str = "df"  # density fitting
    
    # Convergence
    e_convergence: float = 1e-8
    d_convergence: float = 1e-8
    geom_maxiter: int = 100
    scf_maxiter: int = 100
    
    # Timeouts (seconds)
    calculation_timeout: int = 3600  # 1 hour
    
    # Server settings
    log_level: str = "INFO"
    debug: bool = False
    
    def __post_init__(self):
        """Ensure directories exist."""
        Path(self.scratch_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def to_psi4_options(self) -> Dict[str, Any]:
        """Convert to Psi4 options dict."""
        return {
            'basis': self.default_basis,
            'scf_type': self.default_scf_type,
            'e_convergence': self.e_convergence,
            'd_convergence': self.d_convergence,
            'geom_maxiter': self.geom_maxiter,
            'maxiter': self.scf_maxiter,
        }


@dataclass
class CalculationLimits:
    """Resource limits for calculations."""
    
    max_atoms: int = 500
    max_basis_functions: int = 10000
    max_electrons: int = 1000
    max_excited_states: int = 50
    
    # Method-specific limits
    max_atoms_ccsd_t: int = 30
    max_atoms_fci: int = 10
    max_atoms_casscf: int = 50


# Singleton config instance
_config: Optional[ServerConfig] = None


def get_config() -> ServerConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = ServerConfig()
    return _config


def set_config(config: ServerConfig) -> None:
    """Set global config instance."""
    global _config
    _config = config


# Environment variable overrides
def load_from_env() -> ServerConfig:
    """Load configuration from environment variables."""
    return ServerConfig(
        default_memory=int(os.environ.get('PSI4_MEMORY', 4000)),
        default_threads=int(os.environ.get('PSI4_THREADS', 4)),
        scratch_dir=os.environ.get('PSI_SCRATCH', '/tmp/psi4_scratch'),
        output_dir=os.environ.get('PSI4_OUTPUT', '/tmp/psi4_output'),
        default_basis=os.environ.get('PSI4_BASIS', 'cc-pvdz'),
        log_level=os.environ.get('PSI4_LOG_LEVEL', 'INFO'),
        debug=os.environ.get('PSI4_DEBUG', '').lower() in ('true', '1', 'yes'),
    )
