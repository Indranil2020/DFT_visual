"""
Constraint Validation for Psi4 MCP Server.

Validates optimization constraints.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class ConstraintValidationResult:
    """Result of constraint validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ConstraintValidator:
    """Validates optimization constraints."""
    
    VALID_CONSTRAINT_TYPES = {"freeze", "distance", "angle", "dihedral"}
    
    def validate(self, constraints: List[Dict[str, Any]], n_atoms: int) -> ConstraintValidationResult:
        """Validate list of constraints."""
        errors = []
        warnings = []
        
        for i, constraint in enumerate(constraints):
            if "type" not in constraint:
                errors.append(f"Constraint {i+1}: missing 'type' field")
                continue
            
            ctype = constraint["type"].lower()
            if ctype not in self.VALID_CONSTRAINT_TYPES:
                errors.append(f"Constraint {i+1}: unknown type '{ctype}'")
                continue
            
            # Validate based on type
            if ctype == "freeze":
                result = self._validate_freeze(constraint, n_atoms, i+1)
            elif ctype == "distance":
                result = self._validate_distance(constraint, n_atoms, i+1)
            elif ctype == "angle":
                result = self._validate_angle(constraint, n_atoms, i+1)
            elif ctype == "dihedral":
                result = self._validate_dihedral(constraint, n_atoms, i+1)
            else:
                result = ConstraintValidationResult(valid=True)
            
            errors.extend(result.errors)
            warnings.extend(result.warnings)
        
        return ConstraintValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_freeze(self, constraint: Dict[str, Any], n_atoms: int, idx: int) -> ConstraintValidationResult:
        """Validate freeze constraint."""
        errors = []
        
        if "atoms" not in constraint:
            errors.append(f"Constraint {idx}: freeze requires 'atoms' field")
            return ConstraintValidationResult(valid=False, errors=errors)
        
        atoms = constraint["atoms"]
        if not isinstance(atoms, list):
            atoms = [atoms]
        
        for atom in atoms:
            if not isinstance(atom, int):
                errors.append(f"Constraint {idx}: atom index must be integer")
            elif atom < 1 or atom > n_atoms:
                errors.append(f"Constraint {idx}: atom {atom} out of range [1, {n_atoms}]")
        
        return ConstraintValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _validate_distance(self, constraint: Dict[str, Any], n_atoms: int, idx: int) -> ConstraintValidationResult:
        """Validate distance constraint."""
        errors = []
        
        required = ["atom1", "atom2", "value"]
        for field in required:
            if field not in constraint:
                errors.append(f"Constraint {idx}: distance requires '{field}' field")
        
        if errors:
            return ConstraintValidationResult(valid=False, errors=errors)
        
        for field in ["atom1", "atom2"]:
            atom = constraint[field]
            if not isinstance(atom, int) or atom < 1 or atom > n_atoms:
                errors.append(f"Constraint {idx}: {field}={atom} out of range [1, {n_atoms}]")
        
        if constraint["atom1"] == constraint["atom2"]:
            errors.append(f"Constraint {idx}: atom1 and atom2 must be different")
        
        value = constraint["value"]
        if not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"Constraint {idx}: distance value must be positive")
        
        return ConstraintValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _validate_angle(self, constraint: Dict[str, Any], n_atoms: int, idx: int) -> ConstraintValidationResult:
        """Validate angle constraint."""
        errors = []
        
        required = ["atom1", "atom2", "atom3", "value"]
        for field in required:
            if field not in constraint:
                errors.append(f"Constraint {idx}: angle requires '{field}' field")
        
        if errors:
            return ConstraintValidationResult(valid=False, errors=errors)
        
        atoms = [constraint["atom1"], constraint["atom2"], constraint["atom3"]]
        if len(set(atoms)) != 3:
            errors.append(f"Constraint {idx}: angle requires 3 different atoms")
        
        for i, atom in enumerate(atoms, 1):
            if not isinstance(atom, int) or atom < 1 or atom > n_atoms:
                errors.append(f"Constraint {idx}: atom{i}={atom} out of range")
        
        value = constraint["value"]
        if not isinstance(value, (int, float)) or not (0 < value < 180):
            errors.append(f"Constraint {idx}: angle must be between 0 and 180 degrees")
        
        return ConstraintValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _validate_dihedral(self, constraint: Dict[str, Any], n_atoms: int, idx: int) -> ConstraintValidationResult:
        """Validate dihedral constraint."""
        errors = []
        
        required = ["atom1", "atom2", "atom3", "atom4", "value"]
        for field in required:
            if field not in constraint:
                errors.append(f"Constraint {idx}: dihedral requires '{field}' field")
        
        if errors:
            return ConstraintValidationResult(valid=False, errors=errors)
        
        atoms = [constraint[f"atom{i}"] for i in range(1, 5)]
        if len(set(atoms)) != 4:
            errors.append(f"Constraint {idx}: dihedral requires 4 different atoms")
        
        for i, atom in enumerate(atoms, 1):
            if not isinstance(atom, int) or atom < 1 or atom > n_atoms:
                errors.append(f"Constraint {idx}: atom{i}={atom} out of range")
        
        value = constraint["value"]
        if not isinstance(value, (int, float)) or not (-180 <= value <= 180):
            errors.append(f"Constraint {idx}: dihedral must be between -180 and 180 degrees")
        
        return ConstraintValidationResult(valid=len(errors) == 0, errors=errors)


def validate_constraints(constraints: List[Dict[str, Any]], n_atoms: int) -> Tuple[bool, List[str]]:
    """Validate constraints list."""
    validator = ConstraintValidator()
    result = validator.validate(constraints, n_atoms)
    return result.valid, result.errors


def validate_frozen_atoms(atoms: List[int], n_atoms: int) -> Tuple[bool, List[str]]:
    """Validate frozen atom list."""
    errors = []
    for atom in atoms:
        if not isinstance(atom, int):
            errors.append(f"Atom index must be integer, got {type(atom).__name__}")
        elif atom < 1 or atom > n_atoms:
            errors.append(f"Atom {atom} out of range [1, {n_atoms}]")
    return len(errors) == 0, errors


def validate_distance_constraints(
    constraints: List[Tuple[int, int, float]],
    n_atoms: int,
) -> Tuple[bool, List[str]]:
    """Validate distance constraints."""
    errors = []
    for i, (a1, a2, dist) in enumerate(constraints):
        if a1 < 1 or a1 > n_atoms:
            errors.append(f"Constraint {i+1}: atom1={a1} out of range")
        if a2 < 1 or a2 > n_atoms:
            errors.append(f"Constraint {i+1}: atom2={a2} out of range")
        if a1 == a2:
            errors.append(f"Constraint {i+1}: atoms must be different")
        if dist <= 0:
            errors.append(f"Constraint {i+1}: distance must be positive")
    return len(errors) == 0, errors
