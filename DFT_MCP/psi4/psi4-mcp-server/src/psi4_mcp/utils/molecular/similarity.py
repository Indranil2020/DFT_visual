"""
Molecular Similarity for Psi4 MCP Server.

Calculates similarity between molecules.
"""

from typing import List, Tuple
from psi4_mcp.utils.molecular.fingerprints import MolecularFingerprint, calculate_fingerprint


def tanimoto_similarity(fp1: MolecularFingerprint, fp2: MolecularFingerprint) -> float:
    """Calculate Tanimoto similarity between two fingerprints."""
    intersection = len(fp1.bits & fp2.bits)
    union = len(fp1.bits | fp2.bits)
    return intersection / union if union > 0 else 0.0


def dice_similarity(fp1: MolecularFingerprint, fp2: MolecularFingerprint) -> float:
    """Calculate Dice similarity between two fingerprints."""
    intersection = len(fp1.bits & fp2.bits)
    total = len(fp1.bits) + len(fp2.bits)
    return 2 * intersection / total if total > 0 else 0.0


def cosine_similarity(fp1: MolecularFingerprint, fp2: MolecularFingerprint) -> float:
    """Calculate cosine similarity between two fingerprints."""
    intersection = len(fp1.bits & fp2.bits)
    denom = (len(fp1.bits) * len(fp2.bits)) ** 0.5
    return intersection / denom if denom > 0 else 0.0


def calculate_similarity(
    elements1: List[str],
    coords1: List[Tuple[float, float, float]],
    elements2: List[str],
    coords2: List[Tuple[float, float, float]],
    method: str = "tanimoto",
) -> float:
    """Calculate similarity between two molecules."""
    fp1 = calculate_fingerprint(elements1, coords1)
    fp2 = calculate_fingerprint(elements2, coords2)
    
    methods = {
        "tanimoto": tanimoto_similarity,
        "dice": dice_similarity,
        "cosine": cosine_similarity,
    }
    
    sim_func = methods.get(method, tanimoto_similarity)
    return sim_func(fp1, fp2)


def find_similar_molecules(
    query_elements: List[str],
    query_coords: List[Tuple[float, float, float]],
    database: List[Tuple[str, List[str], List[Tuple[float, float, float]]]],
    threshold: float = 0.7,
    top_k: int = 10,
) -> List[Tuple[str, float]]:
    """Find similar molecules in database."""
    query_fp = calculate_fingerprint(query_elements, query_coords)
    
    similarities = []
    for name, elements, coords in database:
        fp = calculate_fingerprint(elements, coords)
        sim = tanimoto_similarity(query_fp, fp)
        if sim >= threshold:
            similarities.append((name, sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]
