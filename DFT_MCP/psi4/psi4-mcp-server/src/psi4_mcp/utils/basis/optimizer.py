"""
Basis Set Optimizer for Psi4 MCP Server.

Provides utilities for optimizing basis set parameters
(exponents and contraction coefficients).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple
import math

from psi4_mcp.utils.basis.generator import ContractedFunction, ShellType


class OptimizationTarget(str, Enum):
    """Target property for basis optimization."""
    ENERGY = "energy"
    DIPOLE = "dipole"
    POLARIZABILITY = "polarizability"
    RESPONSE = "response"
    CORRELATION = "correlation"


@dataclass
class OptimizationResult:
    """Result of a basis optimization."""
    converged: bool
    n_iterations: int
    final_value: float
    initial_value: float
    optimized_function: ContractedFunction
    message: str = ""


@dataclass
class BasisOptimizer:
    """
    Optimizer for basis set parameters.
    
    Provides methods to optimize exponents and contraction
    coefficients for specific target properties.
    """
    
    max_iterations: int = 100
    tolerance: float = 1e-6
    step_size: float = 0.01
    
    def optimize_exponents(
        self,
        initial_function: ContractedFunction,
        objective_func: Callable[[ContractedFunction], float],
        minimize: bool = True,
    ) -> OptimizationResult:
        """
        Optimize exponents of a contracted function.
        
        Args:
            initial_function: Starting contracted function
            objective_func: Function to evaluate (lower is better if minimize=True)
            minimize: Whether to minimize or maximize
            
        Returns:
            OptimizationResult with optimized function
        """
        current = _copy_contracted_function(initial_function)
        initial_value = objective_func(current)
        current_value = initial_value
        
        sign = 1.0 if minimize else -1.0
        
        for iteration in range(self.max_iterations):
            # Compute numerical gradient for each exponent
            gradients = []
            for i, prim in enumerate(current.primitives):
                # Forward difference
                delta = max(prim.exponent * self.step_size, 1e-8)
                
                # Test function with perturbed exponent
                test_func = _copy_contracted_function(current)
                test_func.primitives[i].exponent += delta
                value_plus = objective_func(test_func)
                
                gradient = sign * (value_plus - current_value) / delta
                gradients.append(gradient)
            
            # Update exponents using gradient descent
            max_gradient = max(abs(g) for g in gradients) if gradients else 0.0
            
            if max_gradient < self.tolerance:
                return OptimizationResult(
                    converged=True,
                    n_iterations=iteration + 1,
                    final_value=current_value,
                    initial_value=initial_value,
                    optimized_function=current,
                    message="Converged: gradient below tolerance"
                )
            
            # Line search with backtracking
            step = self.step_size
            for _ in range(10):  # Max backtracking iterations
                test_func = _copy_contracted_function(current)
                for i, grad in enumerate(gradients):
                    new_exp = test_func.primitives[i].exponent - step * grad
                    # Ensure exponent stays positive
                    test_func.primitives[i].exponent = max(new_exp, 1e-10)
                
                new_value = objective_func(test_func)
                
                if (minimize and new_value < current_value) or \
                   (not minimize and new_value > current_value):
                    current = test_func
                    current_value = new_value
                    break
                
                step *= 0.5
            else:
                # No improvement found
                return OptimizationResult(
                    converged=False,
                    n_iterations=iteration + 1,
                    final_value=current_value,
                    initial_value=initial_value,
                    optimized_function=current,
                    message="Failed: line search found no improvement"
                )
        
        return OptimizationResult(
            converged=False,
            n_iterations=self.max_iterations,
            final_value=current_value,
            initial_value=initial_value,
            optimized_function=current,
            message="Reached maximum iterations"
        )
    
    def optimize_coefficients(
        self,
        initial_function: ContractedFunction,
        objective_func: Callable[[ContractedFunction], float],
        minimize: bool = True,
        normalize: bool = True,
    ) -> OptimizationResult:
        """
        Optimize contraction coefficients of a contracted function.
        
        Args:
            initial_function: Starting contracted function
            objective_func: Function to evaluate
            minimize: Whether to minimize or maximize
            normalize: Whether to enforce normalization
            
        Returns:
            OptimizationResult with optimized function
        """
        current = _copy_contracted_function(initial_function)
        initial_value = objective_func(current)
        current_value = initial_value
        
        sign = 1.0 if minimize else -1.0
        
        for iteration in range(self.max_iterations):
            # Compute gradient for each coefficient
            gradients = []
            for i, prim in enumerate(current.primitives):
                delta = max(abs(prim.coefficient) * self.step_size, 1e-8)
                
                test_func = _copy_contracted_function(current)
                test_func.primitives[i].coefficient += delta
                if normalize:
                    test_func.normalize()
                
                value_plus = objective_func(test_func)
                gradient = sign * (value_plus - current_value) / delta
                gradients.append(gradient)
            
            max_gradient = max(abs(g) for g in gradients) if gradients else 0.0
            
            if max_gradient < self.tolerance:
                return OptimizationResult(
                    converged=True,
                    n_iterations=iteration + 1,
                    final_value=current_value,
                    initial_value=initial_value,
                    optimized_function=current,
                    message="Converged: gradient below tolerance"
                )
            
            # Update coefficients
            step = self.step_size
            for _ in range(10):
                test_func = _copy_contracted_function(current)
                for i, grad in enumerate(gradients):
                    test_func.primitives[i].coefficient -= step * grad
                
                if normalize:
                    test_func.normalize()
                
                new_value = objective_func(test_func)
                
                if (minimize and new_value < current_value) or \
                   (not minimize and new_value > current_value):
                    current = test_func
                    current_value = new_value
                    break
                
                step *= 0.5
            else:
                return OptimizationResult(
                    converged=False,
                    n_iterations=iteration + 1,
                    final_value=current_value,
                    initial_value=initial_value,
                    optimized_function=current,
                    message="Failed: line search found no improvement"
                )
        
        return OptimizationResult(
            converged=False,
            n_iterations=self.max_iterations,
            final_value=current_value,
            initial_value=initial_value,
            optimized_function=current,
            message="Reached maximum iterations"
        )


def optimize_exponents(
    initial_function: ContractedFunction,
    objective_func: Callable[[ContractedFunction], float],
    minimize: bool = True,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> OptimizationResult:
    """
    Convenience function to optimize exponents.
    
    Args:
        initial_function: Starting contracted function
        objective_func: Objective function to optimize
        minimize: Whether to minimize (True) or maximize (False)
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
        
    Returns:
        OptimizationResult
    """
    optimizer = BasisOptimizer(
        max_iterations=max_iterations,
        tolerance=tolerance,
    )
    return optimizer.optimize_exponents(initial_function, objective_func, minimize)


def optimize_contraction_coefficients(
    initial_function: ContractedFunction,
    objective_func: Callable[[ContractedFunction], float],
    minimize: bool = True,
    normalize: bool = True,
    max_iterations: int = 100,
    tolerance: float = 1e-6,
) -> OptimizationResult:
    """
    Convenience function to optimize contraction coefficients.
    
    Args:
        initial_function: Starting contracted function
        objective_func: Objective function to optimize
        minimize: Whether to minimize (True) or maximize (False)
        normalize: Whether to enforce normalization
        max_iterations: Maximum iterations
        tolerance: Convergence tolerance
        
    Returns:
        OptimizationResult
    """
    optimizer = BasisOptimizer(
        max_iterations=max_iterations,
        tolerance=tolerance,
    )
    return optimizer.optimize_coefficients(
        initial_function, objective_func, minimize, normalize
    )


def optimize_basis_for_property(
    initial_function: ContractedFunction,
    target: OptimizationTarget,
    reference_value: Optional[float] = None,
) -> OptimizationResult:
    """
    Optimize basis for a specific property using heuristics.
    
    This provides guidance-based optimization when a full
    objective function is not available.
    
    Args:
        initial_function: Starting contracted function
        target: Target property to optimize for
        reference_value: Optional reference value to match
        
    Returns:
        OptimizationResult with suggested modifications
    """
    current = _copy_contracted_function(initial_function)
    
    # Apply heuristic modifications based on target
    if target == OptimizationTarget.ENERGY:
        # For energy, tighter functions are generally needed
        _tighten_exponents(current, factor=1.1)
    
    elif target == OptimizationTarget.DIPOLE:
        # Dipole needs diffuse functions
        _add_diffuse_character(current, factor=0.5)
    
    elif target == OptimizationTarget.POLARIZABILITY:
        # Polarizability needs very diffuse functions
        _add_diffuse_character(current, factor=0.3)
    
    elif target == OptimizationTarget.RESPONSE:
        # Response properties need diffuse functions
        _add_diffuse_character(current, factor=0.4)
    
    elif target == OptimizationTarget.CORRELATION:
        # Correlation needs both tight and diffuse
        # Leave as is - balanced approach
        pass
    
    return OptimizationResult(
        converged=True,
        n_iterations=1,
        final_value=0.0,  # Heuristic, no actual optimization
        initial_value=0.0,
        optimized_function=current,
        message=f"Applied heuristics for {target.value} optimization"
    )


def _copy_contracted_function(func: ContractedFunction) -> ContractedFunction:
    """Create a deep copy of a contracted function."""
    from psi4_mcp.utils.basis.generator import BasisFunction
    
    new_func = ContractedFunction(
        shell_type=func.shell_type,
        element=func.element
    )
    
    for prim in func.primitives:
        new_func.primitives.append(BasisFunction(
            exponent=prim.exponent,
            coefficient=prim.coefficient,
            shell_type=prim.shell_type
        ))
    
    return new_func


def _tighten_exponents(func: ContractedFunction, factor: float = 1.1) -> None:
    """Scale exponents larger (tighter functions)."""
    for prim in func.primitives:
        prim.exponent *= factor


def _add_diffuse_character(func: ContractedFunction, factor: float = 0.5) -> None:
    """Add diffuse character by reducing smallest exponents."""
    if not func.primitives:
        return
    
    # Find and modify smallest exponent
    min_idx = 0
    min_exp = func.primitives[0].exponent
    for i, prim in enumerate(func.primitives):
        if prim.exponent < min_exp:
            min_exp = prim.exponent
            min_idx = i
    
    func.primitives[min_idx].exponent *= factor


def calculate_overlap_integral(
    func1: ContractedFunction,
    func2: ContractedFunction,
) -> float:
    """
    Calculate overlap integral between two contracted functions.
    
    Only valid for S-type functions. Used for normalization
    and optimization diagnostics.
    
    Args:
        func1: First contracted function
        func2: Second contracted function
        
    Returns:
        Overlap integral value
    """
    if func1.shell_type != ShellType.S or func2.shell_type != ShellType.S:
        # For non-S shells, return approximate value
        return 0.0
    
    total_overlap = 0.0
    
    for p1 in func1.primitives:
        for p2 in func2.primitives:
            alpha = p1.exponent + p2.exponent
            # S-type overlap: (pi/alpha)^(3/2)
            overlap = math.pow(math.pi / alpha, 1.5)
            total_overlap += p1.coefficient * p2.coefficient * overlap
    
    return total_overlap


def estimate_completeness(
    basis: List[ContractedFunction],
    shell_type: ShellType,
) -> float:
    """
    Estimate basis completeness for a shell type.
    
    Returns a value between 0 and 1 indicating how complete
    the basis is for the specified angular momentum.
    
    Args:
        basis: List of contracted functions
        shell_type: Shell type to analyze
        
    Returns:
        Estimated completeness (0 to 1)
    """
    # Filter functions by shell type
    shell_funcs = [f for f in basis if f.shell_type == shell_type]
    
    if not shell_funcs:
        return 0.0
    
    # Count primitives
    n_primitives = sum(f.num_primitives for f in shell_funcs)
    
    # Analyze exponent range
    all_exponents = []
    for f in shell_funcs:
        all_exponents.extend([p.exponent for p in f.primitives])
    
    if not all_exponents:
        return 0.0
    
    min_exp = min(all_exponents)
    max_exp = max(all_exponents)
    
    # Estimate completeness based on range and density
    # A complete basis should span from ~0.01 to ~10000 for valence
    range_factor = math.log10(max_exp / min_exp) / 6.0  # 6 orders of magnitude
    range_factor = min(1.0, max(0.0, range_factor))
    
    # Density factor based on number of functions
    density_factor = min(1.0, n_primitives / 10.0)  # ~10 functions is good
    
    return (range_factor + density_factor) / 2.0
