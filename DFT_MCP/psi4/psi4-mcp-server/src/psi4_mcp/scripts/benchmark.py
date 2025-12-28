"""
Benchmarking Script for Psi4 MCP Server.

Runs performance and accuracy benchmarks for the server.
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class BenchmarkResult:
    """Result from a single benchmark."""
    name: str
    success: bool
    elapsed_time: float
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    name: str
    results: List[BenchmarkResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def add_result(self, result: BenchmarkResult) -> None:
        """Add a benchmark result."""
        self.results.append(result)
    
    def complete(self) -> None:
        """Mark suite as complete."""
        self.completed_at = datetime.utcnow()
    
    @property
    def passed(self) -> int:
        """Number of passed benchmarks."""
        return sum(1 for r in self.results if r.success)
    
    @property
    def failed(self) -> int:
        """Number of failed benchmarks."""
        return sum(1 for r in self.results if not r.success)
    
    @property
    def total_time(self) -> float:
        """Total elapsed time."""
        return sum(r.elapsed_time for r in self.results)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "passed": self.passed,
            "failed": self.failed,
            "total_time": self.total_time,
            "results": [
                {
                    "name": r.name,
                    "success": r.success,
                    "elapsed_time": r.elapsed_time,
                    "error": r.error,
                    "metadata": r.metadata,
                }
                for r in self.results
            ],
        }


class BenchmarkRunner:
    """Runs benchmarks for Psi4 MCP Server."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize benchmark runner."""
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "benchmark_results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def run_energy_benchmarks(self) -> BenchmarkSuite:
        """Run energy calculation benchmarks."""
        suite = BenchmarkSuite(name="Energy Benchmarks")
        
        # Define test cases
        test_cases = [
            {
                "name": "H2 HF/STO-3G",
                "geometry": "H 0 0 0\nH 0 0 0.74",
                "method": "hf",
                "basis": "sto-3g",
                "reference": -1.117,
            },
            {
                "name": "H2O HF/STO-3G",
                "geometry": "O 0 0 0.117\nH 0 0.757 -0.470\nH 0 -0.757 -0.470",
                "method": "hf",
                "basis": "sto-3g",
                "reference": -74.966,
            },
            {
                "name": "H2O B3LYP/6-31G*",
                "geometry": "O 0 0 0.117\nH 0 0.757 -0.470\nH 0 -0.757 -0.470",
                "method": "b3lyp",
                "basis": "6-31g*",
                "reference": -76.408,
            },
        ]
        
        for test in test_cases:
            result = self._run_energy_test(test)
            suite.add_result(result)
        
        suite.complete()
        return suite
    
    def _run_energy_test(self, test: Dict[str, Any]) -> BenchmarkResult:
        """Run a single energy benchmark."""
        start_time = time.time()
        
        try:
            # Check if Psi4 is available
            import psi4
            
            psi4.set_memory("500 MB")
            psi4.core.set_output_file("/dev/null", False)
            
            mol_string = f"""
            0 1
            {test['geometry']}
            """
            
            mol = psi4.geometry(mol_string)
            energy = psi4.energy(f"{test['method']}/{test['basis']}")
            
            elapsed = time.time() - start_time
            
            # Check accuracy
            reference = test.get("reference")
            error = None
            if reference is not None:
                diff = abs(energy - reference)
                if diff > 0.01:
                    error = f"Energy differs from reference: {energy:.6f} vs {reference:.6f}"
            
            return BenchmarkResult(
                name=test["name"],
                success=error is None,
                elapsed_time=elapsed,
                result=energy,
                error=error,
                metadata={
                    "method": test["method"],
                    "basis": test["basis"],
                    "reference": reference,
                },
            )
        
        except ImportError:
            return BenchmarkResult(
                name=test["name"],
                success=False,
                elapsed_time=time.time() - start_time,
                error="Psi4 not available",
            )
        
        except Exception as e:
            return BenchmarkResult(
                name=test["name"],
                success=False,
                elapsed_time=time.time() - start_time,
                error=str(e),
            )
    
    def run_performance_benchmarks(self) -> BenchmarkSuite:
        """Run performance benchmarks."""
        suite = BenchmarkSuite(name="Performance Benchmarks")
        
        # Time various operations
        benchmarks = [
            ("Import psi4_mcp", self._benchmark_import),
            ("Geometry validation", self._benchmark_validation),
            ("Unit conversion", self._benchmark_conversion),
        ]
        
        for name, func in benchmarks:
            result = self._run_timed_benchmark(name, func)
            suite.add_result(result)
        
        suite.complete()
        return suite
    
    def _run_timed_benchmark(self, name: str, func: callable) -> BenchmarkResult:
        """Run a timed benchmark."""
        start_time = time.time()
        
        try:
            result = func()
            elapsed = time.time() - start_time
            
            return BenchmarkResult(
                name=name,
                success=True,
                elapsed_time=elapsed,
                result=result,
            )
        
        except Exception as e:
            return BenchmarkResult(
                name=name,
                success=False,
                elapsed_time=time.time() - start_time,
                error=str(e),
            )
    
    def _benchmark_import(self) -> Dict[str, float]:
        """Benchmark import time."""
        import importlib
        
        times = {}
        
        modules = [
            "psi4_mcp",
            "psi4_mcp.tools",
            "psi4_mcp.utils",
            "psi4_mcp.models",
        ]
        
        for mod in modules:
            start = time.time()
            importlib.import_module(mod)
            times[mod] = time.time() - start
        
        return times
    
    def _benchmark_validation(self) -> Dict[str, float]:
        """Benchmark validation performance."""
        from psi4_mcp.utils.validation.geometry import validate_geometry
        
        geometry = "O 0 0 0.117\nH 0 0.757 -0.470\nH 0 -0.757 -0.470"
        
        # Run multiple times
        n_iterations = 100
        start = time.time()
        
        for _ in range(n_iterations):
            validate_geometry(geometry)
        
        elapsed = time.time() - start
        
        return {
            "iterations": n_iterations,
            "total_time": elapsed,
            "per_iteration": elapsed / n_iterations,
        }
    
    def _benchmark_conversion(self) -> Dict[str, float]:
        """Benchmark unit conversion performance."""
        from psi4_mcp.utils.helpers.units import convert_energy
        
        n_iterations = 1000
        start = time.time()
        
        for i in range(n_iterations):
            convert_energy(float(i), "hartree", "ev")
        
        elapsed = time.time() - start
        
        return {
            "iterations": n_iterations,
            "total_time": elapsed,
            "per_iteration": elapsed / n_iterations,
        }
    
    def save_results(self, suite: BenchmarkSuite) -> Path:
        """Save benchmark results to file."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{suite.name.lower().replace(' ', '_')}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(suite.to_dict(), f, indent=2)
        
        return filepath
    
    def run_all(self) -> List[BenchmarkSuite]:
        """Run all benchmarks."""
        suites = []
        
        print("Running energy benchmarks...")
        suites.append(self.run_energy_benchmarks())
        
        print("Running performance benchmarks...")
        suites.append(self.run_performance_benchmarks())
        
        # Save results
        for suite in suites:
            filepath = self.save_results(suite)
            print(f"Saved {suite.name} results to {filepath}")
        
        return suites


def run_benchmark(
    benchmark_type: str = "all",
    output_dir: Optional[str] = None,
) -> List[BenchmarkSuite]:
    """
    Run benchmarks.
    
    Args:
        benchmark_type: Type of benchmark (all, energy, performance)
        output_dir: Directory for results
        
    Returns:
        List of benchmark suites
    """
    runner = BenchmarkRunner(output_dir)
    
    if benchmark_type == "all":
        return runner.run_all()
    elif benchmark_type == "energy":
        return [runner.run_energy_benchmarks()]
    elif benchmark_type == "performance":
        return [runner.run_performance_benchmarks()]
    
    return []


def print_summary(suites: List[BenchmarkSuite]) -> None:
    """Print benchmark summary."""
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_time = 0.0
    
    for suite in suites:
        print(f"\n{suite.name}:")
        print(f"  Passed: {suite.passed}")
        print(f"  Failed: {suite.failed}")
        print(f"  Time: {suite.total_time:.3f}s")
        
        total_passed += suite.passed
        total_failed += suite.failed
        total_time += suite.total_time
        
        if suite.failed > 0:
            print("  Failed tests:")
            for r in suite.results:
                if not r.success:
                    print(f"    - {r.name}: {r.error}")
    
    print("\n" + "-" * 60)
    print(f"Total: {total_passed} passed, {total_failed} failed")
    print(f"Total time: {total_time:.3f}s")


if __name__ == "__main__":
    suites = run_benchmark()
    print_summary(suites)
