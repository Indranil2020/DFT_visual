"""
DFT Functional Scan Tool.

Computes energies across multiple DFT functionals for comparison
and functional selection.
"""

from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional
import logging

from pydantic import Field

from psi4_mcp.tools.core.base_tool import (
    BaseTool, ToolInput, ToolOutput, ToolCategory, register_tool,
)
from psi4_mcp.models.errors import Result, ValidationError


logger = logging.getLogger(__name__)
HARTREE_TO_KCAL = 627.5094740631


FUNCTIONAL_CATEGORIES = {
    "lda": ["svwn", "svwn5"],
    "gga": ["blyp", "pbe", "bp86"],
    "meta_gga": ["tpss", "m06-l"],
    "hybrid": ["b3lyp", "pbe0", "b3pw91"],
    "range_separated": ["cam-b3lyp", "wb97x", "lc-wpbe"],
    "meta_hybrid": ["m06", "m06-2x"],
    "double_hybrid": ["b2plyp"],
}


@dataclass
class FunctionalResult:
    """Single functional calculation result."""
    functional: str
    category: str
    energy: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {"functional": self.functional, "category": self.category, 
                "energy_hartree": self.energy}


@dataclass
class FunctionalScanResult:
    """Functional scan results."""
    results: List[FunctionalResult]
    basis: str
    reference_functional: Optional[str]
    reference_energy: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        sorted_results = sorted(self.results, key=lambda x: x.energy)
        return {
            "results": [r.to_dict() for r in sorted_results],
            "basis": self.basis,
            "reference_functional": self.reference_functional,
            "reference_energy_hartree": self.reference_energy,
            "lowest_energy": sorted_results[0].to_dict() if sorted_results else None,
        }


class FunctionalScanInput(ToolInput):
    """Input for functional scan."""
    geometry: str = Field(..., description="Molecular geometry")
    basis: str = Field(default="cc-pvdz")
    charge: int = Field(default=0)
    multiplicity: int = Field(default=1)
    
    functionals: Optional[List[str]] = Field(default=None, description="Specific functionals to test")
    categories: Optional[List[str]] = Field(default=None, description="Functional categories to scan")
    
    reference_functional: Optional[str] = Field(default=None, description="Reference for comparison")
    
    memory: int = Field(default=4000)
    n_threads: int = Field(default=1)


def validate_functional_scan_input(input_data: FunctionalScanInput) -> Optional[ValidationError]:
    if not input_data.geometry or not input_data.geometry.strip():
        return ValidationError(field="geometry", message="Geometry cannot be empty")
    return None


def get_functional_category(functional: str) -> str:
    """Get category for a functional."""
    func_lower = functional.lower()
    for category, funcs in FUNCTIONAL_CATEGORIES.items():
        if func_lower in funcs:
            return category
    return "unknown"


def run_functional_scan(input_data: FunctionalScanInput) -> FunctionalScanResult:
    """Execute functional scan."""
    import psi4
    
    psi4.core.clean()
    psi4.set_memory(f"{input_data.memory} MB")
    psi4.set_num_threads(input_data.n_threads)
    psi4.core.set_output_file("psi4_func_scan.out", False)
    
    mol_string = f"{input_data.charge} {input_data.multiplicity}\n{input_data.geometry}"
    mol = psi4.geometry(mol_string)
    mol.update_geometry()
    
    # Build list of functionals to test
    functionals_to_test = []
    
    if input_data.functionals:
        functionals_to_test = input_data.functionals
    elif input_data.categories:
        for cat in input_data.categories:
            if cat in FUNCTIONAL_CATEGORIES:
                functionals_to_test.extend(FUNCTIONAL_CATEGORIES[cat])
    else:
        # Default: one from each category
        functionals_to_test = ["svwn", "pbe", "b3lyp", "wb97x", "m06-2x"]
    
    psi4.set_options({
        "basis": input_data.basis,
        "reference": "rhf" if input_data.multiplicity == 1 else "uhf",
    })
    
    results = []
    reference_energy = None
    
    for functional in functionals_to_test:
        logger.info(f"Testing {functional}/{input_data.basis}")
        
        energy = psi4.energy(f"{functional}/{input_data.basis}", molecule=mol)
        
        category = get_functional_category(functional)
        results.append(FunctionalResult(
            functional=functional.upper(),
            category=category,
            energy=energy,
        ))
        
        if input_data.reference_functional and functional.lower() == input_data.reference_functional.lower():
            reference_energy = energy
        
        psi4.core.clean_options()
        psi4.set_options({"basis": input_data.basis})
    
    psi4.core.clean()
    
    return FunctionalScanResult(
        results=results,
        basis=input_data.basis,
        reference_functional=input_data.reference_functional,
        reference_energy=reference_energy,
    )


@register_tool
class FunctionalScanTool(BaseTool[FunctionalScanInput, ToolOutput]):
    """Tool for DFT functional comparison."""
    name: ClassVar[str] = "scan_functionals"
    description: ClassVar[str] = "Compare DFT functionals for a given system."
    category: ClassVar[ToolCategory] = ToolCategory.DFT
    version: ClassVar[str] = "1.0.0"
    
    def _validate_input(self, input_data: FunctionalScanInput) -> Optional[ValidationError]:
        return validate_functional_scan_input(input_data)
    
    def _execute(self, input_data: FunctionalScanInput) -> Result[ToolOutput]:
        result = run_functional_scan(input_data)
        
        lines = [f"Functional Scan ({input_data.basis})", "="*50]
        sorted_results = sorted(result.results, key=lambda x: x.energy)
        
        for r in sorted_results:
            lines.append(f"{r.functional:12s} ({r.category:15s}): {r.energy:.10f} Eh")
        
        message = "\n".join(lines)
        return Result.success(ToolOutput(success=True, message=message, data=result.to_dict()))


def scan_functionals(geometry: str, basis: str = "cc-pvdz", **kwargs: Any) -> ToolOutput:
    """Scan DFT functionals."""
    return FunctionalScanTool().run({"geometry": geometry, "basis": basis, **kwargs})
