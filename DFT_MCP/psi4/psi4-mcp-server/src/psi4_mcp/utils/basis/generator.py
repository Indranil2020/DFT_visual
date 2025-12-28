"""
Basis Set Generator for Psi4 MCP Server.

Provides utilities for generating and manipulating basis sets,
including even-tempered and well-tempered basis generation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math


class ShellType(str, Enum):
    """Angular momentum shell types."""
    S = "s"
    P = "p"
    D = "d"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    
    @property
    def angular_momentum(self) -> int:
        """Get angular momentum quantum number."""
        return {"s": 0, "p": 1, "d": 2, "f": 3, "g": 4, "h": 5, "i": 6}[self.value]
    
    @property
    def num_functions(self) -> int:
        """Get number of Cartesian functions."""
        return (self.angular_momentum + 1) * (self.angular_momentum + 2) // 2
    
    @property
    def num_spherical(self) -> int:
        """Get number of spherical harmonics."""
        return 2 * self.angular_momentum + 1


@dataclass
class BasisFunction:
    """
    A single primitive Gaussian basis function.
    
    Attributes:
        exponent: Gaussian exponent (alpha)
        coefficient: Contraction coefficient (for contracted functions)
        shell_type: Angular momentum type
    """
    exponent: float
    coefficient: float = 1.0
    shell_type: ShellType = ShellType.S
    
    def evaluate(self, r_squared: float) -> float:
        """
        Evaluate the radial part of the Gaussian at r^2.
        
        Args:
            r_squared: Distance squared from center
            
        Returns:
            Value of exp(-alpha * r^2)
        """
        return math.exp(-self.exponent * r_squared)
    
    def __str__(self) -> str:
        return f"{self.shell_type.value}: {self.exponent:.8f} {self.coefficient:.8f}"


@dataclass
class ContractedFunction:
    """
    A contracted Gaussian basis function.
    
    Attributes:
        shell_type: Angular momentum type
        primitives: List of primitive Gaussian functions
        element: Element symbol this function is for
    """
    shell_type: ShellType
    primitives: List[BasisFunction] = field(default_factory=list)
    element: str = ""
    
    @property
    def num_primitives(self) -> int:
        """Get number of primitives in this contraction."""
        return len(self.primitives)
    
    @property
    def exponents(self) -> List[float]:
        """Get list of exponents."""
        return [p.exponent for p in self.primitives]
    
    @property
    def coefficients(self) -> List[float]:
        """Get list of coefficients."""
        return [p.coefficient for p in self.primitives]
    
    def add_primitive(self, exponent: float, coefficient: float = 1.0) -> None:
        """Add a primitive to this contracted function."""
        self.primitives.append(BasisFunction(
            exponent=exponent,
            coefficient=coefficient,
            shell_type=self.shell_type
        ))
    
    def normalize(self) -> None:
        """Normalize the contracted function."""
        if not self.primitives:
            return
        
        # Calculate overlap of contracted function with itself
        total_overlap = 0.0
        for i, pi in enumerate(self.primitives):
            for j, pj in enumerate(self.primitives):
                # S-type overlap formula
                alpha = pi.exponent + pj.exponent
                overlap = math.pow(math.pi / alpha, 1.5)
                total_overlap += pi.coefficient * pj.coefficient * overlap
        
        if total_overlap > 0:
            norm_factor = 1.0 / math.sqrt(total_overlap)
            for p in self.primitives:
                p.coefficient *= norm_factor
    
    def __str__(self) -> str:
        lines = [f"{self.shell_type.value.upper()} {self.num_primitives} 1.00"]
        for p in self.primitives:
            lines.append(f"  {p.exponent:18.10f}  {p.coefficient:18.10f}")
        return "\n".join(lines)


def generate_even_tempered_basis(
    n_functions: int,
    alpha_min: float,
    beta: float,
    shell_type: ShellType = ShellType.S,
    element: str = "",
) -> ContractedFunction:
    """
    Generate an even-tempered basis set.
    
    Even-tempered basis: alpha_i = alpha_min * beta^i
    
    Args:
        n_functions: Number of Gaussian primitives
        alpha_min: Smallest exponent
        beta: Ratio between consecutive exponents (> 1)
        shell_type: Angular momentum type
        element: Element symbol
        
    Returns:
        ContractedFunction with even-tempered exponents
    """
    if n_functions < 1:
        return ContractedFunction(shell_type=shell_type, element=element)
    
    if beta <= 1.0:
        beta = 2.0  # Default to reasonable value
    
    if alpha_min <= 0:
        alpha_min = 0.1  # Default to reasonable value
    
    contracted = ContractedFunction(shell_type=shell_type, element=element)
    
    for i in range(n_functions):
        exponent = alpha_min * math.pow(beta, i)
        # For uncontracted basis, each primitive has coefficient 1.0
        contracted.add_primitive(exponent, 1.0)
    
    return contracted


def generate_well_tempered_basis(
    n_functions: int,
    alpha_min: float,
    beta: float,
    gamma: float,
    shell_type: ShellType = ShellType.S,
    element: str = "",
) -> ContractedFunction:
    """
    Generate a well-tempered basis set.
    
    Well-tempered basis: alpha_i = alpha_min * beta^(i + gamma*i^2)
    
    This provides more flexibility than even-tempered bases by allowing
    non-constant ratios between exponents.
    
    Args:
        n_functions: Number of Gaussian primitives
        alpha_min: Smallest exponent
        beta: Base ratio parameter
        gamma: Quadratic parameter for ratio variation
        shell_type: Angular momentum type
        element: Element symbol
        
    Returns:
        ContractedFunction with well-tempered exponents
    """
    if n_functions < 1:
        return ContractedFunction(shell_type=shell_type, element=element)
    
    contracted = ContractedFunction(shell_type=shell_type, element=element)
    
    for i in range(n_functions):
        power = i + gamma * i * i
        exponent = alpha_min * math.pow(beta, power)
        contracted.add_primitive(exponent, 1.0)
    
    return contracted


def decontract_basis(contracted: ContractedFunction) -> List[ContractedFunction]:
    """
    Decontract a contracted basis function into primitives.
    
    Args:
        contracted: Contracted basis function
        
    Returns:
        List of single-primitive ContractedFunctions
    """
    result = []
    for primitive in contracted.primitives:
        new_contracted = ContractedFunction(
            shell_type=contracted.shell_type,
            element=contracted.element
        )
        new_contracted.add_primitive(primitive.exponent, 1.0)
        result.append(new_contracted)
    return result


def augment_basis(
    basis: List[ContractedFunction],
    shell_type: ShellType,
    exponent: float,
) -> List[ContractedFunction]:
    """
    Augment a basis set with a diffuse function.
    
    Args:
        basis: Original basis set
        shell_type: Shell type for the new function
        exponent: Exponent for the diffuse function
        
    Returns:
        Augmented basis set
    """
    augmented = list(basis)
    
    # Determine element from existing basis
    element = ""
    for func in basis:
        if func.element:
            element = func.element
            break
    
    new_func = ContractedFunction(shell_type=shell_type, element=element)
    new_func.add_primitive(exponent, 1.0)
    augmented.append(new_func)
    
    return augmented


def create_minimal_basis(element: str) -> List[ContractedFunction]:
    """
    Create a minimal (STO-3G like) basis for an element.
    
    Args:
        element: Element symbol
        
    Returns:
        List of contracted basis functions
    """
    # STO-3G exponents and coefficients for common elements
    # These are approximate values for demonstration
    sto3g_params: Dict[str, Dict[str, List[Tuple[float, float]]]] = {
        "H": {
            "s": [(3.42525091, 0.15432897), (0.62391373, 0.53532814), (0.16885540, 0.44463454)]
        },
        "He": {
            "s": [(6.36242139, 0.15432897), (1.15892300, 0.53532814), (0.31364979, 0.44463454)]
        },
        "C": {
            "s_core": [(71.6168370, 0.15432897), (13.0450960, 0.53532814), (3.5305122, 0.44463454)],
            "s_val": [(2.9412494, -0.09996723), (0.6834831, 0.39951283), (0.2222899, 0.70011547)],
            "p": [(2.9412494, 0.15591627), (0.6834831, 0.60768372), (0.2222899, 0.39195739)]
        },
        "N": {
            "s_core": [(99.1061690, 0.15432897), (18.0523120, 0.53532814), (4.8856602, 0.44463454)],
            "s_val": [(3.7804559, -0.09996723), (0.8784966, 0.39951283), (0.2857144, 0.70011547)],
            "p": [(3.7804559, 0.15591627), (0.8784966, 0.60768372), (0.2857144, 0.39195739)]
        },
        "O": {
            "s_core": [(130.7093200, 0.15432897), (23.8088610, 0.53532814), (6.4436083, 0.44463454)],
            "s_val": [(5.0331513, -0.09996723), (1.1695961, 0.39951283), (0.3803890, 0.70011547)],
            "p": [(5.0331513, 0.15591627), (1.1695961, 0.60768372), (0.3803890, 0.39195739)]
        },
        "F": {
            "s_core": [(166.6791300, 0.15432897), (30.3608120, 0.53532814), (8.2168207, 0.44463454)],
            "s_val": [(6.4648032, -0.09996723), (1.5022812, 0.39951283), (0.4885885, 0.70011547)],
            "p": [(6.4648032, 0.15591627), (1.5022812, 0.60768372), (0.4885885, 0.39195739)]
        },
    }
    
    element_upper = element.capitalize()
    
    if element_upper not in sto3g_params:
        # Create a generic minimal basis
        return _create_generic_minimal_basis(element_upper)
    
    params = sto3g_params[element_upper]
    basis = []
    
    for shell_name, primitives in params.items():
        shell_char = shell_name.split("_")[0]
        shell_type = ShellType(shell_char)
        
        func = ContractedFunction(shell_type=shell_type, element=element_upper)
        for exp, coef in primitives:
            func.add_primitive(exp, coef)
        basis.append(func)
    
    return basis


def _create_generic_minimal_basis(element: str) -> List[ContractedFunction]:
    """Create a generic minimal basis for unknown elements."""
    # Use a simple even-tempered basis as fallback
    s_func = generate_even_tempered_basis(
        n_functions=3,
        alpha_min=0.2,
        beta=3.0,
        shell_type=ShellType.S,
        element=element
    )
    
    return [s_func]


def scale_exponents(
    contracted: ContractedFunction,
    scale_factor: float,
) -> ContractedFunction:
    """
    Scale all exponents in a contracted function.
    
    Args:
        contracted: Original contracted function
        scale_factor: Factor to multiply exponents by
        
    Returns:
        New ContractedFunction with scaled exponents
    """
    new_func = ContractedFunction(
        shell_type=contracted.shell_type,
        element=contracted.element
    )
    
    for primitive in contracted.primitives:
        new_func.add_primitive(
            primitive.exponent * scale_factor,
            primitive.coefficient
        )
    
    return new_func


def merge_contracted_functions(
    func1: ContractedFunction,
    func2: ContractedFunction,
) -> Optional[ContractedFunction]:
    """
    Merge two contracted functions of the same shell type.
    
    Args:
        func1: First contracted function
        func2: Second contracted function
        
    Returns:
        Merged function or None if shell types differ
    """
    if func1.shell_type != func2.shell_type:
        return None
    
    merged = ContractedFunction(
        shell_type=func1.shell_type,
        element=func1.element or func2.element
    )
    
    for p in func1.primitives:
        merged.add_primitive(p.exponent, p.coefficient)
    
    for p in func2.primitives:
        merged.add_primitive(p.exponent, p.coefficient)
    
    # Sort by exponent (largest first)
    merged.primitives.sort(key=lambda x: x.exponent, reverse=True)
    
    return merged


def get_diffuse_exponent(
    contracted: ContractedFunction,
    ratio: float = 3.0,
) -> float:
    """
    Calculate a diffuse exponent based on the smallest existing exponent.
    
    Args:
        contracted: Contracted function to analyze
        ratio: Ratio for diffuse exponent (default 3.0 means 1/3 of smallest)
        
    Returns:
        Suggested diffuse exponent
    """
    if not contracted.primitives:
        return 0.1  # Default value
    
    min_exponent = min(p.exponent for p in contracted.primitives)
    return min_exponent / ratio


def calculate_basis_size(basis: List[ContractedFunction]) -> Dict[str, int]:
    """
    Calculate the size of a basis set.
    
    Args:
        basis: List of contracted functions
        
    Returns:
        Dictionary with counts of primitives and contracted functions
    """
    n_primitives = sum(func.num_primitives for func in basis)
    n_contracted = len(basis)
    n_cartesian = sum(
        func.num_primitives * func.shell_type.num_functions 
        for func in basis
    )
    n_spherical = sum(
        func.num_primitives * func.shell_type.num_spherical
        for func in basis
    )
    
    return {
        "n_primitives": n_primitives,
        "n_contracted": n_contracted,
        "n_cartesian_basis_functions": n_cartesian,
        "n_spherical_basis_functions": n_spherical,
    }
