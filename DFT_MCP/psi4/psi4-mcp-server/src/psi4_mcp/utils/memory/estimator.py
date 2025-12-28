"""
Memory Estimation Utilities for Psi4 MCP Server.

Provides memory requirement estimates for quantum chemistry calculations.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CalculationType(str, Enum):
    """Types of calculations for memory estimation."""
    SCF = "scf"
    DFT = "dft"
    MP2 = "mp2"
    CCSD = "ccsd"
    CCSD_T = "ccsd_t"
    TDDFT = "tddft"
    SAPT = "sapt"


@dataclass
class MemoryEstimate:
    """Memory estimate for a calculation."""
    total_mb: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    calculation_type: Optional[str] = None
    n_basis: int = 0
    n_electrons: int = 0
    confidence: str = "medium"
    notes: List[str] = field(default_factory=list)
    
    @property
    def total_gb(self) -> float:
        return self.total_mb / 1024


class MemoryEstimator:
    """Estimator for calculation memory requirements."""
    
    BYTES_PER_DOUBLE = 8
    
    def __init__(self, safety_factor: float = 1.5, use_density_fitting: bool = True):
        self.safety_factor = safety_factor
        self.use_density_fitting = use_density_fitting
    
    def estimate(self, calc_type: CalculationType, n_basis: int, n_electrons: int = 0) -> MemoryEstimate:
        """Estimate memory for a calculation."""
        if calc_type == CalculationType.SCF:
            return self._estimate_scf(n_basis, n_electrons)
        elif calc_type == CalculationType.DFT:
            return self._estimate_dft(n_basis, n_electrons)
        elif calc_type == CalculationType.MP2:
            return self._estimate_mp2(n_basis, n_electrons)
        elif calc_type == CalculationType.CCSD:
            return self._estimate_ccsd(n_basis, n_electrons)
        elif calc_type == CalculationType.CCSD_T:
            return self._estimate_ccsd_t(n_basis, n_electrons)
        elif calc_type == CalculationType.TDDFT:
            return self._estimate_tddft(n_basis, n_electrons)
        return self._estimate_scf(n_basis, n_electrons)
    
    def _estimate_scf(self, n_basis: int, n_electrons: int) -> MemoryEstimate:
        n = n_basis
        breakdown = {}
        matrices = n * n * self.BYTES_PER_DOUBLE * 4 / (1024 * 1024)
        breakdown["Matrices"] = matrices
        
        if self.use_density_fitting:
            integrals = n * n * 3 * n * self.BYTES_PER_DOUBLE / (1024 * 1024)
            breakdown["DF integrals"] = integrals
        else:
            integrals = (n**4 * self.BYTES_PER_DOUBLE / 8) / (1024 * 1024)
            breakdown["4-index integrals"] = integrals
        
        diis = n * n * self.BYTES_PER_DOUBLE * 12 / (1024 * 1024)
        breakdown["DIIS"] = diis
        
        total = sum(breakdown.values()) * self.safety_factor
        return MemoryEstimate(total_mb=total, breakdown=breakdown, calculation_type="SCF", 
                            n_basis=n_basis, n_electrons=n_electrons, confidence="high")
    
    def _estimate_dft(self, n_basis: int, n_electrons: int) -> MemoryEstimate:
        estimate = self._estimate_scf(n_basis, n_electrons)
        n_grid = 5000 * max(1, n_electrons // 10)
        grid_mem = n_grid * 4 * self.BYTES_PER_DOUBLE / (1024 * 1024)
        estimate.breakdown["DFT grid"] = grid_mem
        estimate.total_mb = sum(estimate.breakdown.values()) * self.safety_factor
        estimate.calculation_type = "DFT"
        return estimate
    
    def _estimate_mp2(self, n_basis: int, n_electrons: int) -> MemoryEstimate:
        n = n_basis
        n_occ = max(1, n_electrons // 2)
        n_vir = max(1, n - n_occ)
        breakdown = {}
        
        if self.use_density_fitting:
            breakdown["DF integrals"] = n_occ * n_vir * 3 * n * self.BYTES_PER_DOUBLE / (1024 * 1024)
        else:
            breakdown["MO integrals"] = (n_occ * n_vir)**2 * self.BYTES_PER_DOUBLE / (1024 * 1024)
        
        breakdown["Amplitudes"] = (n_occ * n_vir)**2 * self.BYTES_PER_DOUBLE / (1024 * 1024)
        total = sum(breakdown.values()) * self.safety_factor
        return MemoryEstimate(total_mb=total, breakdown=breakdown, calculation_type="MP2",
                            n_basis=n_basis, n_electrons=n_electrons, confidence="medium")
    
    def _estimate_ccsd(self, n_basis: int, n_electrons: int) -> MemoryEstimate:
        n_occ = max(1, n_electrons // 2)
        n_vir = max(1, n_basis - n_occ)
        breakdown = {}
        breakdown["T1 amplitudes"] = n_occ * n_vir * self.BYTES_PER_DOUBLE / (1024 * 1024)
        breakdown["T2 amplitudes"] = (n_occ**2 * n_vir**2) * self.BYTES_PER_DOUBLE / (1024 * 1024)
        breakdown["Intermediates"] = (n_occ**2 * n_vir**2) * 2 * self.BYTES_PER_DOUBLE / (1024 * 1024)
        total = sum(breakdown.values()) * self.safety_factor
        return MemoryEstimate(total_mb=total, breakdown=breakdown, calculation_type="CCSD",
                            n_basis=n_basis, n_electrons=n_electrons, confidence="medium")
    
    def _estimate_ccsd_t(self, n_basis: int, n_electrons: int) -> MemoryEstimate:
        estimate = self._estimate_ccsd(n_basis, n_electrons)
        n_occ = max(1, n_electrons // 2)
        n_vir = max(1, n_basis - n_occ)
        triples = (n_occ**3 * n_vir**3) * self.BYTES_PER_DOUBLE / (1024 * 1024) / 6
        estimate.breakdown["(T) intermediates"] = triples
        estimate.total_mb = sum(estimate.breakdown.values()) * self.safety_factor
        estimate.calculation_type = "CCSD(T)"
        return estimate
    
    def _estimate_tddft(self, n_basis: int, n_electrons: int) -> MemoryEstimate:
        estimate = self._estimate_dft(n_basis, n_electrons)
        n_occ = max(1, n_electrons // 2)
        n_vir = max(1, n_basis - n_occ)
        n_states = 10
        response = n_occ * n_vir * n_states * self.BYTES_PER_DOUBLE / (1024 * 1024) * 4
        estimate.breakdown["Response vectors"] = response
        estimate.total_mb = sum(estimate.breakdown.values()) * self.safety_factor
        estimate.calculation_type = "TDDFT"
        return estimate


def estimate_calculation_memory(calc_type: str, n_basis: int, n_electrons: int = 0) -> MemoryEstimate:
    """Convenience function to estimate memory."""
    estimator = MemoryEstimator()
    try:
        ct = CalculationType(calc_type.lower())
    except ValueError:
        ct = CalculationType.SCF
    return estimator.estimate(ct, n_basis, n_electrons)


def estimate_scf_memory(n_basis: int, use_df: bool = True) -> float:
    """Estimate SCF memory in MB."""
    estimator = MemoryEstimator(use_density_fitting=use_df)
    return estimator._estimate_scf(n_basis, n_basis).total_mb


def estimate_mp2_memory(n_basis: int, n_electrons: int, use_df: bool = True) -> float:
    """Estimate MP2 memory in MB."""
    estimator = MemoryEstimator(use_density_fitting=use_df)
    return estimator._estimate_mp2(n_basis, n_electrons).total_mb


def estimate_ccsd_memory(n_basis: int, n_electrons: int) -> float:
    """Estimate CCSD memory in MB."""
    estimator = MemoryEstimator()
    return estimator._estimate_ccsd(n_basis, n_electrons).total_mb
