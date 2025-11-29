"""
Mathematical Utility Functions for Quantum Chemistry.

This module provides mathematical utility functions commonly used in
quantum chemistry calculations, including linear algebra operations,
numerical methods, and statistical functions.

Functions are designed to be efficient and numerically stable.
No external numerical libraries are assumed as dependencies here;
complex operations may use numpy when available.
"""

import math
from typing import Sequence, TypeVar, Callable

# Type variable for numeric types
Numeric = TypeVar("Numeric", int, float)


# =============================================================================
# BASIC MATHEMATICAL FUNCTIONS
# =============================================================================

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to be within a specified range.
    
    Args:
        value: The value to clamp.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        
    Returns:
        The clamped value.
    """
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.
    
    Args:
        a: Start value.
        b: End value.
        t: Interpolation parameter (0 to 1).
        
    Returns:
        Interpolated value.
    """
    return a + (b - a) * t


def sign(x: float) -> int:
    """
    Return the sign of a number.
    
    Args:
        x: Input number.
        
    Returns:
        1 if positive, -1 if negative, 0 if zero.
    """
    if x > 0:
        return 1
    elif x < 0:
        return -1
    return 0


def is_close(a: float, b: float, rel_tol: float = 1e-9, abs_tol: float = 0.0) -> bool:
    """
    Check if two floating point numbers are approximately equal.
    
    Args:
        a: First number.
        b: Second number.
        rel_tol: Relative tolerance.
        abs_tol: Absolute tolerance.
        
    Returns:
        True if the numbers are close, False otherwise.
    """
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default if denominator is zero.
    
    Args:
        numerator: The numerator.
        denominator: The denominator.
        default: Value to return if denominator is zero.
        
    Returns:
        The quotient or the default value.
    """
    if abs(denominator) < 1e-300:
        return default
    return numerator / denominator


def safe_sqrt(x: float) -> float:
    """
    Safely compute square root, returning 0 for negative numbers.
    
    Args:
        x: Input value.
        
    Returns:
        Square root of x if x >= 0, else 0.
    """
    if x < 0:
        return 0.0
    return math.sqrt(x)


def safe_log(x: float, default: float = float('-inf')) -> float:
    """
    Safely compute natural logarithm, returning default for non-positive values.
    
    Args:
        x: Input value.
        default: Value to return if x <= 0.
        
    Returns:
        Natural logarithm of x or default.
    """
    if x <= 0:
        return default
    return math.log(x)


def factorial(n: int) -> int:
    """
    Compute factorial of a non-negative integer.
    
    Args:
        n: Non-negative integer.
        
    Returns:
        n! (factorial of n), or 1 if n < 0.
    """
    if n < 0:
        return 1
    if n <= 1:
        return 1
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def double_factorial(n: int) -> int:
    """
    Compute double factorial n!! = n * (n-2) * (n-4) * ...
    
    Args:
        n: Integer value.
        
    Returns:
        Double factorial of n.
    """
    if n <= 0:
        return 1
    result = 1
    while n > 0:
        result *= n
        n -= 2
    return result


def binomial(n: int, k: int) -> int:
    """
    Compute binomial coefficient C(n, k) = n! / (k! * (n-k)!).
    
    Args:
        n: Total number of items.
        k: Number of items to choose.
        
    Returns:
        Binomial coefficient.
    """
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    
    # Use the smaller of k and n-k for efficiency
    k = min(k, n - k)
    
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


# =============================================================================
# VECTOR OPERATIONS
# =============================================================================

def dot_product(v1: Sequence[float], v2: Sequence[float]) -> float:
    """
    Compute the dot product of two vectors.
    
    Args:
        v1: First vector.
        v2: Second vector.
        
    Returns:
        Dot product (scalar).
    """
    if len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))


def vector_norm(v: Sequence[float]) -> float:
    """
    Compute the Euclidean norm (magnitude) of a vector.
    
    Args:
        v: Input vector.
        
    Returns:
        Euclidean norm of the vector.
    """
    return math.sqrt(sum(x * x for x in v))


def vector_normalize(v: Sequence[float]) -> list[float]:
    """
    Normalize a vector to unit length.
    
    Args:
        v: Input vector.
        
    Returns:
        Normalized vector, or zero vector if input has zero norm.
    """
    norm = vector_norm(v)
    if norm < 1e-300:
        return [0.0] * len(v)
    return [x / norm for x in v]


def vector_add(v1: Sequence[float], v2: Sequence[float]) -> list[float]:
    """
    Add two vectors element-wise.
    
    Args:
        v1: First vector.
        v2: Second vector.
        
    Returns:
        Sum vector.
    """
    return [a + b for a, b in zip(v1, v2)]


def vector_subtract(v1: Sequence[float], v2: Sequence[float]) -> list[float]:
    """
    Subtract two vectors element-wise (v1 - v2).
    
    Args:
        v1: First vector.
        v2: Second vector.
        
    Returns:
        Difference vector.
    """
    return [a - b for a, b in zip(v1, v2)]


def vector_scale(v: Sequence[float], scalar: float) -> list[float]:
    """
    Scale a vector by a scalar.
    
    Args:
        v: Input vector.
        scalar: Scaling factor.
        
    Returns:
        Scaled vector.
    """
    return [x * scalar for x in v]


def cross_product(v1: Sequence[float], v2: Sequence[float]) -> list[float]:
    """
    Compute the cross product of two 3D vectors.
    
    Args:
        v1: First 3D vector.
        v2: Second 3D vector.
        
    Returns:
        Cross product vector.
    """
    if len(v1) != 3 or len(v2) != 3:
        return [0.0, 0.0, 0.0]
    
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]


def distance(p1: Sequence[float], p2: Sequence[float]) -> float:
    """
    Compute Euclidean distance between two points.
    
    Args:
        p1: First point.
        p2: Second point.
        
    Returns:
        Euclidean distance.
    """
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def angle_between_vectors(v1: Sequence[float], v2: Sequence[float]) -> float:
    """
    Compute the angle between two vectors in radians.
    
    Args:
        v1: First vector.
        v2: Second vector.
        
    Returns:
        Angle in radians (0 to π).
    """
    norm1 = vector_norm(v1)
    norm2 = vector_norm(v2)
    
    if norm1 < 1e-300 or norm2 < 1e-300:
        return 0.0
    
    cos_angle = dot_product(v1, v2) / (norm1 * norm2)
    # Clamp to [-1, 1] to handle numerical errors
    cos_angle = clamp(cos_angle, -1.0, 1.0)
    
    return math.acos(cos_angle)


# =============================================================================
# MATRIX OPERATIONS (Simple implementations)
# =============================================================================

def matrix_multiply_vector(
    matrix: Sequence[Sequence[float]], 
    vector: Sequence[float]
) -> list[float]:
    """
    Multiply a matrix by a vector.
    
    Args:
        matrix: 2D matrix (list of rows).
        vector: 1D vector.
        
    Returns:
        Result vector.
    """
    return [dot_product(row, vector) for row in matrix]


def matrix_transpose(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    """
    Transpose a matrix.
    
    Args:
        matrix: 2D matrix (list of rows).
        
    Returns:
        Transposed matrix.
    """
    if not matrix:
        return []
    return [[matrix[i][j] for i in range(len(matrix))] for j in range(len(matrix[0]))]


def matrix_trace(matrix: Sequence[Sequence[float]]) -> float:
    """
    Compute the trace of a square matrix.
    
    Args:
        matrix: Square matrix.
        
    Returns:
        Sum of diagonal elements.
    """
    return sum(matrix[i][i] for i in range(min(len(matrix), len(matrix[0]) if matrix else 0)))


def identity_matrix(n: int) -> list[list[float]]:
    """
    Create an n×n identity matrix.
    
    Args:
        n: Size of the matrix.
        
    Returns:
        Identity matrix.
    """
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def determinant_3x3(m: Sequence[Sequence[float]]) -> float:
    """
    Compute determinant of a 3x3 matrix.
    
    Args:
        m: 3x3 matrix.
        
    Returns:
        Determinant value.
    """
    if len(m) != 3 or any(len(row) != 3 for row in m):
        return 0.0
    
    return (
        m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) -
        m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) +
        m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
    )


# =============================================================================
# STATISTICAL FUNCTIONS
# =============================================================================

def mean(values: Sequence[float]) -> float:
    """
    Compute the arithmetic mean of a sequence.
    
    Args:
        values: Sequence of numbers.
        
    Returns:
        Mean value, or 0.0 if empty.
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: Sequence[float], ddof: int = 0) -> float:
    """
    Compute the variance of a sequence.
    
    Args:
        values: Sequence of numbers.
        ddof: Delta degrees of freedom (0 for population, 1 for sample).
        
    Returns:
        Variance, or 0.0 if insufficient data.
    """
    n = len(values)
    if n <= ddof:
        return 0.0
    
    avg = mean(values)
    return sum((x - avg) ** 2 for x in values) / (n - ddof)


def std_dev(values: Sequence[float], ddof: int = 0) -> float:
    """
    Compute the standard deviation of a sequence.
    
    Args:
        values: Sequence of numbers.
        ddof: Delta degrees of freedom (0 for population, 1 for sample).
        
    Returns:
        Standard deviation.
    """
    return math.sqrt(variance(values, ddof))


def rms(values: Sequence[float]) -> float:
    """
    Compute the root mean square of a sequence.
    
    Args:
        values: Sequence of numbers.
        
    Returns:
        RMS value, or 0.0 if empty.
    """
    if not values:
        return 0.0
    return math.sqrt(sum(x * x for x in values) / len(values))


def max_abs(values: Sequence[float]) -> float:
    """
    Find the maximum absolute value in a sequence.
    
    Args:
        values: Sequence of numbers.
        
    Returns:
        Maximum absolute value, or 0.0 if empty.
    """
    if not values:
        return 0.0
    return max(abs(x) for x in values)


def median(values: Sequence[float]) -> float:
    """
    Compute the median of a sequence.
    
    Args:
        values: Sequence of numbers.
        
    Returns:
        Median value, or 0.0 if empty.
    """
    if not values:
        return 0.0
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    
    if n % 2 == 0:
        return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
    return sorted_vals[mid]


# =============================================================================
# SPECIAL FUNCTIONS
# =============================================================================

def erf(x: float) -> float:
    """
    Compute the error function using Horner's method approximation.
    
    This is a good approximation with maximum error < 1.5e-7.
    
    Args:
        x: Input value.
        
    Returns:
        Error function value.
    """
    # Save the sign
    sign_x = 1 if x >= 0 else -1
    x = abs(x)
    
    # Coefficients for approximation
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911
    
    # Approximation
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    
    return sign_x * y


def erfc(x: float) -> float:
    """
    Compute the complementary error function.
    
    Args:
        x: Input value.
        
    Returns:
        Complementary error function value (1 - erf(x)).
    """
    return 1.0 - erf(x)


def gamma_function(z: float) -> float:
    """
    Compute the gamma function using Lanczos approximation.
    
    Args:
        z: Input value (must be > 0 for positive branch).
        
    Returns:
        Gamma function value.
    """
    if z < 0.5:
        # Reflection formula
        return math.pi / (math.sin(math.pi * z) * gamma_function(1 - z))
    
    z -= 1
    
    # Lanczos coefficients
    g = 7
    c = [
        0.99999999999980993,
        676.5203681218851,
        -1259.1392167224028,
        771.32342877765313,
        -176.61502916214059,
        12.507343278686905,
        -0.13857109526572012,
        9.9843695780195716e-6,
        1.5056327351493116e-7
    ]
    
    x = c[0]
    for i in range(1, g + 2):
        x += c[i] / (z + i)
    
    t = z + g + 0.5
    return math.sqrt(2 * math.pi) * (t ** (z + 0.5)) * math.exp(-t) * x


def boys_function(n: int, x: float) -> float:
    """
    Compute the Boys function F_n(x), used in molecular integrals.
    
    F_n(x) = ∫₀¹ t^(2n) exp(-x*t²) dt
    
    Args:
        n: Order of the Boys function (non-negative integer).
        x: Argument (non-negative).
        
    Returns:
        Value of F_n(x).
    """
    if x < 1e-10:
        # Small x approximation
        return 1.0 / (2 * n + 1)
    
    if x > 30.0:
        # Large x asymptotic form
        return double_factorial(2 * n - 1) / (2 ** (n + 1)) * math.sqrt(math.pi / (x ** (2 * n + 1)))
    
    # General case: use incomplete gamma function relation
    # F_n(x) = (1/2) * x^(-(n+1/2)) * γ(n+1/2, x)
    # Using series expansion for moderate x
    
    term = 1.0 / (2 * n + 1)
    result = term
    exp_x = math.exp(-x)
    
    for k in range(1, 100):
        term *= x / (n + k + 0.5)
        result += term
        if abs(term) < 1e-15 * abs(result):
            break
    
    return result * exp_x


# =============================================================================
# NUMERICAL METHODS
# =============================================================================

def newton_raphson(
    f: Callable[[float], float],
    df: Callable[[float], float],
    x0: float,
    tol: float = 1e-10,
    max_iter: int = 100
) -> tuple[float, bool]:
    """
    Find a root using Newton-Raphson method.
    
    Args:
        f: Function to find root of.
        df: Derivative of the function.
        x0: Initial guess.
        tol: Convergence tolerance.
        max_iter: Maximum iterations.
        
    Returns:
        Tuple of (root, converged).
    """
    x = x0
    for _ in range(max_iter):
        fx = f(x)
        dfx = df(x)
        
        if abs(dfx) < 1e-300:
            return x, False
        
        x_new = x - fx / dfx
        
        if abs(x_new - x) < tol:
            return x_new, True
        
        x = x_new
    
    return x, False


def bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1e-10,
    max_iter: int = 100
) -> tuple[float, bool]:
    """
    Find a root using bisection method.
    
    Args:
        f: Function to find root of.
        a: Left bound of interval.
        b: Right bound of interval.
        tol: Convergence tolerance.
        max_iter: Maximum iterations.
        
    Returns:
        Tuple of (root, converged).
    """
    fa = f(a)
    fb = f(b)
    
    # Check if signs are different
    if fa * fb > 0:
        return (a + b) / 2, False
    
    for _ in range(max_iter):
        c = (a + b) / 2
        fc = f(c)
        
        if abs(fc) < tol or (b - a) / 2 < tol:
            return c, True
        
        if fc * fa < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    
    return (a + b) / 2, False


def numerical_derivative(
    f: Callable[[float], float],
    x: float,
    h: float = 1e-8
) -> float:
    """
    Compute numerical derivative using central difference.
    
    Args:
        f: Function to differentiate.
        x: Point at which to evaluate derivative.
        h: Step size.
        
    Returns:
        Approximate derivative.
    """
    return (f(x + h) - f(x - h)) / (2 * h)


def trapezoidal_integration(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 100
) -> float:
    """
    Numerical integration using trapezoidal rule.
    
    Args:
        f: Function to integrate.
        a: Lower bound.
        b: Upper bound.
        n: Number of intervals.
        
    Returns:
        Approximate integral value.
    """
    h = (b - a) / n
    result = 0.5 * (f(a) + f(b))
    
    for i in range(1, n):
        result += f(a + i * h)
    
    return result * h
