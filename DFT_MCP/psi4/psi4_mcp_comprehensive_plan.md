# **Psi4 MCP Server: Comprehensive Implementation Plan**

**Version:** 1.0  
**Date:** November 27, 2025  
**Status:** Planning Phase  
**Priority:** CRITICAL - Complete Implementation Required

---

## **Executive Summary**

This document provides a complete, accurate, and foolproof plan for implementing a Model Context Protocol (MCP) server for Psi4, an open-source quantum chemistry package. The plan ensures comprehensive coverage of Psi4's capabilities while following MCP protocol specifications.

**Key Deliverables:**
- Production-ready MCP server for Psi4
- Complete tool coverage (energy, optimization, frequencies, properties, TDDFT, etc.)
- Robust error handling and validation
- Comprehensive testing suite
- Documentation and examples

---

## **Phase 0: Foundation & Requirements (Week 1)**

### **Task 0.1: Environment Setup**
**Priority:** P0 - Must complete first  
**Duration:** 1 day

**Subtasks:**
1. **Install Python 3.10+** (required for MCP)
   - Verify: `python --version` shows 3.10 or higher
   - Set up virtual environment: `python -m venv psi4-mcp-env`
   - Activate: `source psi4-mcp-env/bin/activate` (Linux/Mac)

2. **Install Psi4**
   ```bash
   conda create -n psi4-mcp python=3.10
   conda activate psi4-mcp
   conda install -c psi4 psi4
   # Or using pip (if available)
   pip install psi4
   ```
   - Verify installation: `python -c "import psi4; print(psi4.__version__)"`
   - Set PSI_SCRATCH: `export PSI_SCRATCH=/path/to/scratch`

3. **Install MCP SDK and Dependencies**
   ```bash
   pip install mcp[cli]  # Official MCP SDK
   pip install fastmcp   # High-level interface (optional)
   pip install ase       # For structure handling
   pip install numpy     # For numerical operations
   pip install pydantic  # For validation
   pip install pytest    # For testing
   pip install pytest-asyncio  # For async tests
   ```

4. **Verify All Installations**
   - Create verification script `test_imports.py`:
   ```python
   import psi4
   import mcp
   import ase
   import numpy as np
   print("✓ All imports successful")
   print(f"Psi4 version: {psi4.__version__}")
   ```

**Acceptance Criteria:**
- [ ] Python 3.10+ installed and verified
- [ ] Psi4 installed and can import successfully
- [ ] MCP SDK installed and can import
- [ ] All dependencies installed
- [ ] PSI_SCRATCH environment variable set
- [ ] Test script runs without errors

---

### **Task 0.2: Research & Documentation Review**
**Priority:** P0  
**Duration:** 2 days

**Subtasks:**
1. **Study Psi4 API Documentation**
   - Read: https://psicode.org/psi4manual/master/psiapi.html
   - Focus areas:
     - `psi4.geometry()` - Molecular input
     - `psi4.energy()` - Single-point calculations
     - `psi4.optimize()` - Geometry optimization
     - `psi4.frequency()` - Vibrational analysis
     - `psi4.properties()` - Molecular properties
     - `psi4.set_options()` - Configuration
     - `psi4.core` module - Low-level access
   - **Action:** Create summary document with all available methods

2. **Study ASE-Psi4 Interface**
   - Read: https://wiki.fysik.dtu.dk/ase/ase/calculators/psi4.html
   - Understand: ASE Calculator pattern
   - **Action:** Document ASE integration points

3. **Study MCP Protocol Specification**
   - Read: https://modelcontextprotocol.io/specification
   - Focus areas:
     - Tool definitions
     - Resource handling
     - Prompt templates
     - Transport mechanisms (stdio, HTTP)
     - Error handling protocols
   - **Action:** Create MCP checklist for compliance

4. **Review Existing MCP Servers**
   - Study VASPilot architecture (from project documents)
   - Review AiiDA MCP implementation
   - Analyze GPAW MCP server
   - **Action:** Document best practices and patterns

5. **Analyze Psi4 Test Suite**
   - Location: https://psicode.org/psi4manual/master/testsuite.html
   - Review: psi4/samples/ directory
   - **Action:** Identify representative test cases for validation

**Acceptance Criteria:**
- [ ] Comprehensive Psi4 API summary created
- [ ] ASE integration documented
- [ ] MCP protocol compliance checklist completed
- [ ] Best practices document from existing servers
- [ ] Test cases identified and catalogued

---

### **Task 0.3: Architecture Design**
**Priority:** P0  
**Duration:** 2 days

**Subtasks:**
1. **Define Project Structure**
   ```
   psi4-mcp-server/
   ├── src/
   │   ├── psi4_mcp/
   │   │   ├── __init__.py
   │   │   ├── server.py              # Main MCP server
   │   │   ├── tools/
   │   │   │   ├── __init__.py
   │   │   │   ├── energy.py          # Energy calculations
   │   │   │   ├── optimization.py    # Geometry optimization
   │   │   │   ├── frequencies.py     # Vibrational analysis
   │   │   │   ├── properties.py      # Molecular properties
   │   │   │   ├── tddft.py           # Excited states
   │   │   │   └── advanced.py        # SAPT, CC, etc.
   │   │   ├── resources/
   │   │   │   ├── __init__.py
   │   │   │   ├── basis_sets.py      # Basis set info
   │   │   │   ├── methods.py         # Available methods
   │   │   │   └── molecules.py       # Molecular library
   │   │   ├── prompts/
   │   │   │   ├── __init__.py
   │   │   │   └── templates.py       # Prompt templates
   │   │   ├── utils/
   │   │   │   ├── __init__.py
   │   │   │   ├── validation.py      # Input validation
   │   │   │   ├── conversion.py      # Format conversion
   │   │   │   ├── error_handler.py   # Error handling
   │   │   │   └── output_parser.py   # Output parsing
   │   │   └── models.py               # Pydantic models
   ├── tests/
   │   ├── unit/
   │   ├── integration/
   │   └── fixtures/
   ├── examples/
   ├── docs/
   ├── pyproject.toml
   ├── README.md
   └── LICENSE
   ```

2. **Design Core Data Models** (using Pydantic)
   ```python
   # models.py - Define ALL data structures
   from pydantic import BaseModel, Field, validator
   from typing import Optional, List, Literal, Union
   from enum import Enum

   class BasisSet(str, Enum):
       """Supported basis sets"""
       STO_3G = "sto-3g"
       CC_PVDZ = "cc-pvdz"
       CC_PVTZ = "cc-pvtz"
       AUG_CC_PVDZ = "aug-cc-pvdz"
       # ... full list from Psi4

   class Method(str, Enum):
       """Supported computational methods"""
       HF = "hf"
       B3LYP = "b3lyp"
       PBE = "pbe"
       MP2 = "mp2"
       CCSD = "ccsd"
       CCSD_T = "ccsd(t)"
       # ... full list

   class MoleculeInput(BaseModel):
       """Molecule specification"""
       geometry: str = Field(description="Z-matrix or Cartesian coordinates")
       charge: int = Field(default=0, ge=-10, le=10)
       multiplicity: int = Field(default=1, ge=1, le=10)
       units: Literal["angstrom", "bohr"] = "angstrom"
       
       @validator('geometry')
       def validate_geometry(cls, v):
           # Validate geometry format
           pass

   class EnergyCalculationInput(BaseModel):
       """Input for energy calculation"""
       molecule: MoleculeInput
       method: Method
       basis: BasisSet
       reference: Literal["rhf", "uhf", "rohf"] = "rhf"
       memory: str = "500 MB"
       num_threads: int = Field(default=1, ge=1, le=64)
       options: Optional[dict] = None
   ```

3. **Define Tool Specifications**
   - Create comprehensive list of all tools to implement
   - Each tool must have:
     - Name (clear, descriptive)
     - Description (detailed)
     - Input schema (Pydantic model)
     - Output schema (Pydantic model)
     - Error handling strategy

4. **Design Error Handling Strategy**
   ```python
   class Psi4Error(Exception):
       """Base exception for Psi4 MCP"""
       pass

   class ConvergenceError(Psi4Error):
       """SCF or geometry convergence failure"""
       pass

   class InputError(Psi4Error):
       """Invalid input parameters"""
       pass

   class ResourceError(Psi4Error):
       """Insufficient memory or disk"""
       pass
   ```

**Acceptance Criteria:**
- [ ] Complete project structure defined
- [ ] All Pydantic models created and validated
- [ ] Tool specification document complete
- [ ] Error handling framework designed
- [ ] Architecture reviewed and approved

---

## **Phase 1: Core Infrastructure (Week 2)**

### **Task 1.1: MCP Server Initialization**
**Priority:** P0  
**Duration:** 1 day

**Implementation:**
```python
# src/psi4_mcp/server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.session import ServerSession
import psi4
import logging
from pathlib import Path

# Configure logging (CRITICAL: must write to stderr for stdio transport)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]  # MUST be stderr
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    name="psi4-quantum-chemistry",
    version="1.0.0",
    description="MCP server for Psi4 quantum chemistry calculations"
)

# Psi4 initialization
def init_psi4():
    """Initialize Psi4 with optimal settings"""
    # Set scratch directory
    scratch_dir = Path(os.environ.get('PSI_SCRATCH', '/tmp'))
    psi4.core.set_output_file('psi4_output.dat', append=False)
    
    # Set default memory
    psi4.set_memory('2 GB')
    
    # Set number of threads
    psi4.set_num_threads(4)
    
    logger.info("Psi4 initialized successfully")

# Initialize on server start
init_psi4()
```

**Subtasks:**
1. Create server.py with FastMCP initialization
2. Implement Psi4 initialization routine
3. Configure logging (stderr only for stdio transport!)
4. Set up environment variable handling
5. Add version tracking and metadata

**Acceptance Criteria:**
- [ ] Server initializes without errors
- [ ] Psi4 is properly configured
- [ ] Logging works correctly (stderr only)
- [ ] Environment variables handled
- [ ] Can be run with `python server.py`

---

### **Task 1.2: Input Validation System**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/utils/validation.py
from pydantic import BaseModel, validator
import psi4
import re

class InputValidator:
    """Comprehensive input validation"""
    
    @staticmethod
    def validate_geometry(geometry: str) -> tuple[bool, str]:
        """Validate molecular geometry format"""
        try:
            # Check if Z-matrix or Cartesian
            lines = geometry.strip().split('\n')
            
            # Basic validation
            if len(lines) < 1:
                return False, "Geometry cannot be empty"
            
            # Try to parse with Psi4
            test_geom = f"""
            0 1
            {geometry}
            """
            mol = psi4.geometry(test_geom)
            
            return True, "Valid geometry"
        except Exception as e:
            return False, f"Invalid geometry: {str(e)}"
    
    @staticmethod
    def validate_basis_set(basis: str, elements: list) -> tuple[bool, str]:
        """Validate basis set availability for given elements"""
        # Check if basis set exists in Psi4
        try:
            # This will raise exception if basis not found
            psi4.core.BasisSet.pyconstruct_orbital(
                psi4.geometry("He 0 0 0"),
                "BASIS",
                basis
            )
            return True, "Valid basis set"
        except Exception as e:
            return False, f"Invalid basis set: {str(e)}"
    
    @staticmethod
    def validate_method(method: str) -> tuple[bool, str]:
        """Validate computational method"""
        valid_methods = [
            'hf', 'rhf', 'uhf', 'rohf',  # Hartree-Fock
            'b3lyp', 'pbe', 'pbe0', 'wb97x',  # DFT
            'mp2', 'mp3',  # Perturbation theory
            'ccsd', 'ccsd(t)', 'ccsdt',  # Coupled cluster
            'cisd',  # CI
            'sapt0', 'sapt2',  # SAPT
        ]
        
        if method.lower() in valid_methods:
            return True, "Valid method"
        return False, f"Unknown method: {method}"
    
    @staticmethod
    def validate_memory(memory: str) -> tuple[bool, str]:
        """Validate memory specification"""
        pattern = r'^(\d+\.?\d*)\s*(B|KB|MB|GB|TB)$'
        if re.match(pattern, memory, re.IGNORECASE):
            return True, "Valid memory specification"
        return False, "Invalid memory format (use e.g., '500 MB', '2 GB')"
```

**Subtasks:**
1. Implement geometry validator
2. Implement basis set validator
3. Implement method validator
4. Implement options validator
5. Add comprehensive error messages
6. Write unit tests for each validator

**Acceptance Criteria:**
- [ ] All validators implemented
- [ ] Edge cases handled
- [ ] Clear error messages provided
- [ ] Unit tests pass (100% coverage)
- [ ] Documentation complete

---

### **Task 1.3: Output Parser System**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/utils/output_parser.py
import psi4
import numpy as np
from typing import Dict, Any, Optional

class OutputParser:
    """Parse Psi4 calculation outputs"""
    
    @staticmethod
    def parse_energy_output(wfn: psi4.core.Wavefunction) -> Dict[str, Any]:
        """Parse energy calculation results"""
        return {
            'energy': float(wfn.energy()),
            'units': 'hartree',
            'method': wfn.name(),
            'basis': wfn.basisset().name(),
            'natoms': wfn.molecule().natom(),
            'nelec': wfn.nalpha() + wfn.nbeta(),
            'multiplicity': wfn.molecule().multiplicity(),
            'scf_iterations': wfn.iteration(),
            'converged': True  # If we get here, it converged
        }
    
    @staticmethod
    def parse_optimization_output(result: Dict) -> Dict[str, Any]:
        """Parse geometry optimization results"""
        return {
            'final_energy': result['energy'],
            'final_geometry': result['final_molecule'].save_string_xyz(),
            'n_iterations': result.get('trajectory', None),
            'converged': result['converged'],
            'max_force': result.get('max_force', None),
            'rms_force': result.get('rms_force', None)
        }
    
    @staticmethod
    def parse_frequency_output(wfn: psi4.core.Wavefunction, 
                               freq_array: np.ndarray) -> Dict[str, Any]:
        """Parse vibrational frequency results"""
        frequencies = freq_array.tolist()
        
        # Separate real and imaginary frequencies
        real_freq = [f for f in frequencies if f > 0]
        imag_freq = [f for f in frequencies if f < 0]
        
        return {
            'frequencies': frequencies,
            'units': 'cm^-1',
            'n_frequencies': len(frequencies),
            'n_imaginary': len(imag_freq),
            'zero_point_energy': sum(f for f in real_freq if f > 0) * 0.5,
            'is_minimum': len(imag_freq) == 0,
            'is_transition_state': len(imag_freq) == 1
        }
    
    @staticmethod
    def parse_properties_output(prop_dict: Dict) -> Dict[str, Any]:
        """Parse molecular properties"""
        parsed = {}
        
        # Dipole moment
        if 'dipole' in prop_dict:
            dipole = prop_dict['dipole']
            parsed['dipole_moment'] = {
                'x': float(dipole[0]),
                'y': float(dipole[1]),
                'z': float(dipole[2]),
                'magnitude': float(np.linalg.norm(dipole)),
                'units': 'debye'
            }
        
        # Quadrupole moment
        if 'quadrupole' in prop_dict:
            parsed['quadrupole_moment'] = prop_dict['quadrupole']
        
        # HOMO-LUMO gap
        if 'homo' in prop_dict and 'lumo' in prop_dict:
            gap = prop_dict['lumo'] - prop_dict['homo']
            parsed['homo_lumo_gap'] = {
                'value': float(gap),
                'units': 'hartree',
                'homo': float(prop_dict['homo']),
                'lumo': float(prop_dict['lumo'])
            }
        
        return parsed
```

**Subtasks:**
1. Implement energy output parser
2. Implement optimization output parser
3. Implement frequency output parser
4. Implement properties output parser
5. Add TDDFT output parser
6. Add error extraction from output
7. Write unit tests with real Psi4 outputs

**Acceptance Criteria:**
- [ ] All parsers implemented
- [ ] Handles all output formats
- [ ] Extracts all relevant data
- [ ] Unit tests pass
- [ ] Documented with examples

---

## **Phase 2: Core Calculation Tools (Week 3-4)**

### **Task 2.1: Energy Calculation Tool**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/tools/energy.py
from typing import Annotated
from mcp.server.fastmcp import Context
from ..models import EnergyCalculationInput, EnergyCalculationOutput
from ..utils.validation import InputValidator
from ..utils.output_parser import OutputParser
import psi4

@mcp.tool()
async def calculate_energy(
    input_data: EnergyCalculationInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> EnergyCalculationOutput:
    """
    Calculate single-point energy for a molecular system.
    
    Supports methods: HF, DFT (B3LYP, PBE, etc.), MP2, CCSD, CCSD(T)
    
    Args:
        input_data: Molecular structure and calculation parameters
        ctx: MCP context for progress reporting
        
    Returns:
        Energy and wavefunction information
        
    Example:
        ```python
        result = await calculate_energy({
            "molecule": {
                "geometry": "O\\nH 1 0.96\\nH 1 0.96 2 104.5",
                "charge": 0,
                "multiplicity": 1
            },
            "method": "b3lyp",
            "basis": "cc-pvdz"
        })
        ```
    """
    try:
        # Report progress
        await ctx.report_progress(0, 100, "Validating input...")
        
        # Validate input
        validator = InputValidator()
        is_valid, msg = validator.validate_geometry(input_data.molecule.geometry)
        if not is_valid:
            raise ValueError(f"Invalid geometry: {msg}")
        
        await ctx.report_progress(10, 100, "Setting up calculation...")
        
        # Configure Psi4
        psi4.set_memory(input_data.memory)
        psi4.set_num_threads(input_data.num_threads)
        
        # Build molecule string
        mol_string = f"""
        {input_data.molecule.charge} {input_data.molecule.multiplicity}
        {input_data.molecule.geometry}
        units {input_data.molecule.units}
        symmetry c1
        """
        
        # Create molecule object
        molecule = psi4.geometry(mol_string)
        
        await ctx.report_progress(20, 100, "Running SCF calculation...")
        
        # Set calculation options
        if input_data.options:
            for key, value in input_data.options.items():
                psi4.set_options({key: value})
        
        # Perform calculation
        method_string = f"{input_data.method}/{input_data.basis}"
        energy, wfn = psi4.energy(method_string, return_wfn=True)
        
        await ctx.report_progress(90, 100, "Parsing results...")
        
        # Parse output
        parser = OutputParser()
        result = parser.parse_energy_output(wfn)
        result['input'] = input_data.dict()
        
        await ctx.report_progress(100, 100, "Complete!")
        
        return EnergyCalculationOutput(**result)
        
    except psi4.ConvergenceError as e:
        await ctx.error(f"SCF convergence failed: {str(e)}")
        raise
    except Exception as e:
        await ctx.error(f"Energy calculation failed: {str(e)}")
        raise
```

**Subtasks:**
1. Implement basic energy calculation
2. Add progress reporting
3. Add all method support (HF, DFT, MP2, CC)
4. Add reference type handling (RHF/UHF/ROHF)
5. Add options handling
6. Implement error recovery
7. Write comprehensive tests
8. Document with examples

**Acceptance Criteria:**
- [ ] All methods work correctly
- [ ] Progress reporting functions
- [ ] Handles convergence failures gracefully
- [ ] Tests cover all methods
- [ ] Documentation complete with examples
- [ ] Performance benchmarked

---

### **Task 2.2: Geometry Optimization Tool**
**Priority:** P0  
**Duration:** 3 days

**Implementation:**
```python
# src/psi4_mcp/tools/optimization.py
from typing import Annotated, Optional
from mcp.server.fastmcp import Context
from ..models import OptimizationInput, OptimizationOutput
import psi4
import numpy as np

@mcp.tool()
async def optimize_geometry(
    input_data: OptimizationInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> OptimizationOutput:
    """
    Optimize molecular geometry to find energy minimum.
    
    Performs full geometry optimization including:
    - Atomic position optimization
    - Convergence to force threshold
    - Optional: constrained optimization
    - Optional: transition state search
    
    Args:
        input_data: Initial geometry and optimization parameters
        ctx: MCP context
        
    Returns:
        Optimized geometry and convergence information
    """
    try:
        await ctx.report_progress(0, 100, "Starting optimization...")
        
        # Setup
        psi4.set_memory(input_data.memory)
        psi4.set_num_threads(input_data.num_threads)
        
        # Build molecule
        mol_string = f"""
        {input_data.molecule.charge} {input_data.molecule.multiplicity}
        {input_data.molecule.geometry}
        units {input_data.molecule.units}
        symmetry c1
        """
        molecule = psi4.geometry(mol_string)
        
        # Set optimization options
        opt_options = {
            'g_convergence': input_data.convergence_threshold,
            'max_force': input_data.max_force,
            'geom_maxiter': input_data.max_iterations,
            'opt_coordinates': input_data.coordinate_system
        }
        psi4.set_options(opt_options)
        
        # Add custom options
        if input_data.options:
            psi4.set_options(input_data.options)
        
        await ctx.report_progress(10, 100, "Running optimization...")
        
        # Callback for progress updates
        def opt_callback(mol, step, *args):
            progress = min(90, 10 + (step / input_data.max_iterations) * 80)
            asyncio.create_task(ctx.report_progress(
                progress, 100, f"Optimization step {step}/{input_data.max_iterations}"
            ))
        
        # Perform optimization
        method_string = f"{input_data.method}/{input_data.basis}"
        
        try:
            final_energy = psi4.optimize(
                method_string,
                molecule=molecule,
                return_wfn=False
            )
            converged = True
        except psi4.OptimizationConvergenceError as e:
            # Get partial results
            final_energy = e.wfn.energy()
            converged = False
            await ctx.warn(f"Optimization did not converge: {str(e)}")
        
        await ctx.report_progress(95, 100, "Extracting results...")
        
        # Get optimized geometry
        final_geom = molecule.save_string_xyz()
        
        # Parse results
        result = {
            'final_energy': float(final_energy),
            'final_geometry': final_geom,
            'converged': converged,
            'initial_geometry': input_data.molecule.geometry,
            'n_iterations': psi4.get_variable("CURRENT OPTIMIZATION STEP"),
            'method': input_data.method,
            'basis': input_data.basis
        }
        
        await ctx.report_progress(100, 100, "Optimization complete!")
        
        return OptimizationOutput(**result)
        
    except Exception as e:
        await ctx.error(f"Optimization failed: {str(e)}")
        raise
```

**Subtasks:**
1. Implement basic optimization
2. Add progress callbacks
3. Add convergence criteria options
4. Add coordinate system options (Cartesian, internal, etc.)
5. Implement constrained optimization
6. Add transition state search
7. Handle optimization failures gracefully
8. Extract trajectory information
9. Write tests for various systems
10. Document with examples

**Acceptance Criteria:**
- [ ] Basic optimization works
- [ ] Progress reporting accurate
- [ ] Handles non-convergence
- [ ] All optimization types supported
- [ ] Tests pass for various molecules
- [ ] Documentation complete

---

### **Task 2.3: Frequency Calculation Tool**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/tools/frequencies.py
from typing import Annotated
from mcp.server.fastmcp import Context
from ..models import FrequencyInput, FrequencyOutput
import psi4
import numpy as np

@mcp.tool()
async def calculate_frequencies(
    input_data: FrequencyInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> FrequencyOutput:
    """
    Calculate vibrational frequencies and thermodynamic properties.
    
    Computes:
    - Harmonic vibrational frequencies
    - Zero-point energy (ZPE)
    - Thermodynamic corrections (enthalpy, entropy, Gibbs free energy)
    - IR intensities
    - Raman activities (if requested)
    
    IMPORTANT: Geometry should be pre-optimized for meaningful results.
    
    Args:
        input_data: Molecular geometry and calculation parameters
        ctx: MCP context
        
    Returns:
        Frequencies, thermodynamic properties, and normal modes
    """
    try:
        await ctx.report_progress(0, 100, "Setting up frequency calculation...")
        
        # Configure Psi4
        psi4.set_memory(input_data.memory)
        psi4.set_num_threads(input_data.num_threads)
        
        # Build molecule
        mol_string = f"""
        {input_data.molecule.charge} {input_data.molecule.multiplicity}
        {input_data.molecule.geometry}
        units {input_data.molecule.units}
        symmetry c1
        """
        molecule = psi4.geometry(mol_string)
        
        # Check if geometry is optimized
        if input_data.check_optimized:
            await ctx.warn("Frequencies should be computed at optimized geometry!")
        
        await ctx.report_progress(10, 100, "Computing Hessian...")
        
        # Set options
        if input_data.options:
            psi4.set_options(input_data.options)
        
        # Perform frequency calculation
        method_string = f"{input_data.method}/{input_data.basis}"
        energy, wfn = psi4.frequency(method_string, return_wfn=True)
        
        await ctx.report_progress(80, 100, "Analyzing results...")
        
        # Get frequencies
        vibinfo = wfn.frequency_analysis
        frequencies = vibinfo['omega'].to_array()  # in cm^-1
        
        # Classify frequencies
        real_freq = [f for f in frequencies if f > input_data.frequency_threshold]
        imag_freq = [abs(f) for f in frequencies if f < -input_data.frequency_threshold]
        
        # Get thermodynamic properties
        thermo = vibinfo['thermo']
        
        # Parse results
        result = {
            'frequencies': frequencies.tolist(),
            'n_frequencies': len(frequencies),
            'n_imaginary': len(imag_freq),
            'imaginary_frequencies': imag_freq,
            'zero_point_energy': float(vibinfo['ZPE']),
            'thermal_energy': float(thermo['E_thermal']),
            'enthalpy': float(thermo['H']),
            'entropy': float(thermo['S']),
            'gibbs_free_energy': float(thermo['G']),
            'temperature': float(input_data.temperature),
            'is_minimum': len(imag_freq) == 0,
            'is_transition_state': len(imag_freq) == 1,
            'is_higher_order_saddle': len(imag_freq) > 1,
            'ir_intensities': vibinfo.get('IR_intensity', []).tolist(),
            'units': {
                'frequencies': 'cm^-1',
                'energy': 'hartree',
                'entropy': 'cal/(mol·K)'
            }
        }
        
        await ctx.report_progress(100, 100, "Frequency calculation complete!")
        
        return FrequencyOutput(**result)
        
    except Exception as e:
        await ctx.error(f"Frequency calculation failed: {str(e)}")
        raise
```

**Subtasks:**
1. Implement frequency calculation
2. Add thermodynamic analysis
3. Extract IR intensities
4. Add Raman activities (optional)
5. Classify stationary points
6. Handle numerical differentiation
7. Add normal mode visualization data
8. Write tests
9. Document with examples

**Acceptance Criteria:**
- [ ] Frequencies calculated correctly
- [ ] Thermodynamics accurate
- [ ] Stationary point classification works
- [ ] Tests validate against known systems
- [ ] Documentation complete

---

### **Task 2.4: Molecular Properties Tool**
**Priority:** P1  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/tools/properties.py
from typing import Annotated, List
from mcp.server.fastmcp import Context
from ..models import PropertiesInput, PropertiesOutput
import psi4

@mcp.tool()
async def calculate_properties(
    input_data: PropertiesInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> PropertiesOutput:
    """
    Calculate various molecular properties.
    
    Available properties:
    - Dipole moment
    - Quadrupole moment
    - Polarizability
    - Molecular orbitals (HOMO, LUMO, gap)
    - Mulliken charges
    - ESP charges
    - Electrostatic potential
    - Wiberg bond orders
    
    Args:
        input_data: Geometry and properties to calculate
        ctx: MCP context
        
    Returns:
        Requested molecular properties
    """
    try:
        await ctx.report_progress(0, 100, "Initializing property calculation...")
        
        # Setup
        psi4.set_memory(input_data.memory)
        psi4.set_num_threads(input_data.num_threads)
        
        # Build molecule
        mol_string = f"""
        {input_data.molecule.charge} {input_data.molecule.multiplicity}
        {input_data.molecule.geometry}
        units {input_data.molecule.units}
        symmetry c1
        """
        molecule = psi4.geometry(mol_string)
        
        await ctx.report_progress(10, 100, "Running SCF calculation...")
        
        # Perform energy calculation first
        method_string = f"{input_data.method}/{input_data.basis}"
        energy, wfn = psi4.energy(method_string, return_wfn=True)
        
        result = {
            'energy': float(energy),
            'properties': {}
        }
        
        # Calculate each requested property
        for prop in input_data.requested_properties:
            progress = 20 + (input_data.requested_properties.index(prop) * 70 / len(input_data.requested_properties))
            await ctx.report_progress(progress, 100, f"Computing {prop}...")
            
            if prop == 'dipole':
                psi4.set_options({'properties': ['dipole']})
                dipole = psi4.variable('SCF DIPOLE')
                result['properties']['dipole_moment'] = {
                    'x': float(dipole[0]),
                    'y': float(dipole[1]),
                    'z': float(dipole[2]),
                    'magnitude': float(np.linalg.norm(dipole)),
                    'units': 'debye'
                }
            
            elif prop == 'quadrupole':
                psi4.set_options({'properties': ['quadrupole']})
                result['properties']['quadrupole_moment'] = {
                    # Extract quadrupole tensor
                }
            
            elif prop == 'mulliken':
                psi4.oeprop(wfn, 'MULLIKEN_CHARGES')
                charges = wfn.atomic_point_charges().to_array()
                result['properties']['mulliken_charges'] = charges.tolist()
            
            elif prop == 'homo_lumo':
                homo = wfn.epsilon_a().get(wfn.nalpha() - 1)
                lumo = wfn.epsilon_a().get(wfn.nalpha())
                gap = lumo - homo
                result['properties']['homo_lumo'] = {
                    'homo': float(homo),
                    'lumo': float(lumo),
                    'gap': float(gap),
                    'units': 'hartree'
                }
            
            # Add more properties...
        
        await ctx.report_progress(100, 100, "Properties calculation complete!")
        
        return PropertiesOutput(**result)
        
    except Exception as e:
        await ctx.error(f"Properties calculation failed: {str(e)}")
        raise
```

**Subtasks:**
1. Implement dipole moment calculation
2. Implement quadrupole moment
3. Add polarizability
4. Add orbital properties
5. Add charge analysis methods
6. Add bond order analysis
7. Write tests for each property
8. Document with examples

**Acceptance Criteria:**
- [ ] All properties calculate correctly
- [ ] Tests validate results
- [ ] Documentation complete
- [ ] Performance acceptable

---

## **Phase 3: Advanced Calculation Tools (Week 5-6)**

### **Task 3.1: TDDFT Tool**
**Priority:** P1  
**Duration:** 3 days

**Implementation:**
```python
# src/psi4_mcp/tools/tddft.py
from typing import Annotated, Optional
from mcp.server.fastmcp import Context
from ..models import TDDFTInput, TDDFTOutput
import psi4
import numpy as np

@mcp.tool()
async def calculate_excited_states(
    input_data: TDDFTInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> TDDFTOutput:
    """
    Calculate excited electronic states using TD-DFT.
    
    Computes:
    - Excitation energies
    - Oscillator strengths
    - Transition dipole moments
    - Excited state properties
    - UV-Vis absorption spectrum
    
    Supports:
    - Full TDDFT (RPA)
    - Tamm-Dancoff approximation (TDA)
    - Singlet and triplet states
    
    Args:
        input_data: Ground state geometry and TDDFT parameters
        ctx: MCP context
        
    Returns:
        Excited state energies and transition properties
    """
    try:
        await ctx.report_progress(0, 100, "Setting up TDDFT calculation...")
        
        # Configure Psi4
        psi4.set_memory(input_data.memory)
        psi4.set_num_threads(input_data.num_threads)
        
        # Build molecule
        mol_string = f"""
        {input_data.molecule.charge} {input_data.molecule.multiplicity}
        {input_data.molecule.geometry}
        units {input_data.molecule.units}
        symmetry c1
        """
        molecule = psi4.geometry(mol_string)
        
        await ctx.report_progress(10, 100, "Running ground state DFT...")
        
        # Ground state calculation
        method_string = f"{input_data.method}/{input_data.basis}"
        energy, wfn = psi4.energy(method_string, return_wfn=True, molecule=molecule)
        
        await ctx.report_progress(40, 100, "Computing excited states...")
        
        # Set TDDFT options
        tddft_options = {
            'tda': input_data.use_tda,  # Tamm-Dancoff approximation
            'roots_per_irrep': [input_data.n_states],
            'tdscf_states': input_data.n_states,
            'tdscf_r_convergence': input_data.convergence,
            'tdscf_maxiter': input_data.max_iterations
        }
        
        if input_data.triplets:
            tddft_options['tdscf_triplets'] = 'true'
        
        psi4.set_options(tddft_options)
        
        # Perform TDDFT calculation
        tddft_energies, tddft_wfn = psi4.properties(
            method_string,
            properties=['oscillator_strength', 'transition_dipole'],
            return_wfn=True,
            molecule=molecule,
            ref_wfn=wfn
        )
        
        await ctx.report_progress(80, 100, "Analyzing excited states...")
        
        # Extract results
        excited_states = []
        for i in range(input_data.n_states):
            state = {
                'state_number': i + 1,
                'excitation_energy_au': float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 EXCITATION ENERGY')),
                'excitation_energy_ev': float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 EXCITATION ENERGY') * 27.2114),
                'excitation_energy_nm': 1239.84 / (float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 EXCITATION ENERGY') * 27.2114)),
                'oscillator_strength': float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 OSCILLATOR STRENGTH (LEN)')),
                'transition_dipole': [
                    float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 TRANSITION DIPOLE X')),
                    float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 TRANSITION DIPOLE Y')),
                    float(psi4.variable(f'TD-DFT ROOT {i+1} -> ROOT 0 TRANSITION DIPOLE Z'))
                ],
                'dominant_excitation': f"HOMO-{input_data.n_states-i} -> LUMO+{i}"  # Simplified
            }
            excited_states.append(state)
        
        # Generate UV-Vis spectrum data
        spectrum = generate_uv_vis_spectrum(excited_states, input_data.spectrum_range)
        
        result = {
            'ground_state_energy': float(energy),
            'n_states_computed': input_data.n_states,
            'excited_states': excited_states,
            'uv_vis_spectrum': spectrum,
            'method': input_data.method,
            'basis': input_data.basis,
            'approximation': 'TDA' if input_data.use_tda else 'RPA'
        }
        
        await ctx.report_progress(100, 100, "TDDFT calculation complete!")
        
        return TDDFTOutput(**result)
        
    except Exception as e:
        await ctx.error(f"TDDFT calculation failed: {str(e)}")
        raise

def generate_uv_vis_spectrum(excited_states: list, wavelength_range: tuple) -> dict:
    """Generate UV-Vis absorption spectrum"""
    wavelengths = np.linspace(wavelength_range[0], wavelength_range[1], 1000)
    intensities = np.zeros_like(wavelengths)
    
    # Apply Gaussian broadening
    sigma = 0.4  # eV
    for state in excited_states:
        energy_ev = state['excitation_energy_ev']
        osc_str = state['oscillator_strength']
        
        # Convert to wavelength
        lambda_nm = 1239.84 / energy_ev
        
        # Gaussian broadening
        intensities += osc_str * np.exp(-((wavelengths - lambda_nm)**2) / (2 * sigma**2))
    
    return {
        'wavelengths': wavelengths.tolist(),
        'intensities': intensities.tolist(),
        'units': {'wavelength': 'nm', 'intensity': 'arbitrary'}
    }
```

**Subtasks:**
1. Implement ground state DFT
2. Implement TDDFT calculation
3. Add TDA option
4. Add triplet states
5. Extract transition properties
6. Generate UV-Vis spectrum
7. Add natural transition orbitals (NTO) analysis
8. Write tests
9. Document with examples

**Acceptance Criteria:**
- [ ] TDDFT works for singlets and triplets
- [ ] TDA option functions correctly
- [ ] UV-Vis spectra generated
- [ ] Tests validate against known systems
- [ ] Documentation complete

---

### **Task 3.2: SAPT Tool**
**Priority:** P2  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/tools/advanced.py
from typing import Annotated
from mcp.server.fastmcp import Context
from ..models import SAPTInput, SAPTOutput
import psi4

@mcp.tool()
async def calculate_sapt(
    input_data: SAPTInput,
    ctx: Annotated[Context, "Injected by FastMCP"]
) -> SAPTOutput:
    """
    Perform Symmetry-Adapted Perturbation Theory (SAPT) analysis.
    
    Analyzes intermolecular interactions by decomposing them into:
    - Electrostatic energy
    - Exchange energy
    - Induction energy
    - Dispersion energy
    
    Available SAPT levels:
    - SAPT0: Lowest level, fastest
    - SAPT2: Medium accuracy
    - SAPT2+: SAPT2 with improved dispersion
    - SAPT2+(3): SAPT2+ with third-order corrections
    
    Args:
        input_data: Dimer geometry and SAPT parameters
        ctx: MCP context
        
    Returns:
        SAPT energy decomposition and total interaction energy
    """
    try:
        await ctx.report_progress(0, 100, "Setting up SAPT calculation...")
        
        # Configure Psi4
        psi4.set_memory(input_data.memory)
        psi4.set_num_threads(input_data.num_threads)
        
        # Build dimer molecule (two fragments separated by --)
        mol_string = f"""
        {input_data.dimer.charge} {input_data.dimer.multiplicity}
        {input_data.dimer.monomer1}
        --
        {input_data.dimer.monomer2}
        units {input_data.dimer.units}
        symmetry c1
        """
        dimer = psi4.geometry(mol_string)
        
        # Set SAPT options
        sapt_options = {
            'basis': input_data.basis,
            'freeze_core': 'true' if input_data.freeze_core else 'false'
        }
        psi4.set_options(sapt_options)
        
        await ctx.report_progress(10, 100, f"Running {input_data.sapt_level}...")
        
        # Perform SAPT calculation
        sapt_level = input_data.sapt_level.lower()
        energy = psi4.energy(f'{sapt_level}/{input_data.basis}', molecule=dimer)
        
        await ctx.report_progress(90, 100, "Extracting energy components...")
        
        # Extract SAPT components
        components = {
            'electrostatic': float(psi4.variable('SAPT ELST ENERGY')),
            'exchange': float(psi4.variable('SAPT EXCH ENERGY')),
            'induction': float(psi4.variable('SAPT IND ENERGY')),
            'dispersion': float(psi4.variable('SAPT DISP ENERGY')),
            'total_sapt': float(psi4.variable('SAPT TOTAL ENERGY')),
            'hf_interaction': float(psi4.variable('SAPT HF TOTAL ENERGY'))
        }
        
        # Add higher-order terms if available
        if sapt_level in ['sapt2+', 'sapt2+(3)']:
            components['exchange_induction'] = float(psi4.variable('SAPT EXCH-IND ENERGY'))
            components['exchange_dispersion'] = float(psi4.variable('SAPT EXCH-DISP ENERGY'))
        
        result = {
            'sapt_level': input_data.sapt_level,
            'basis': input_data.basis,
            'energy_components': components,
            'total_interaction_energy': components['total_sapt'],
            'units': 'hartree',
            'interpretation': interpret_sapt_results(components)
        }
        
        await ctx.report_progress(100, 100, "SAPT analysis complete!")
        
        return SAPTOutput(**result)
        
    except Exception as e:
        await ctx.error(f"SAPT calculation failed: {str(e)}")
        raise

def interpret_sapt_results(components: dict) -> dict:
    """Provide interpretation of SAPT results"""
    total = components['total_sapt']
    
    # Calculate percentages
    interpretation = {
        'dominant_attractive': '',
        'dominant_repulsive': 'exchange',
        'percentages': {}
    }
    
    attractive_terms = {
        'electrostatic': components['electrostatic'],
        'induction': components['induction'],
        'dispersion': components['dispersion']
    }
    
    # Find dominant attractive term
    dominant_attr = min(attractive_terms.items(), key=lambda x: x[1])
    interpretation['dominant_attractive'] = dominant_attr[0]
    
    # Calculate percentages
    for term, energy in components.items():
        if term not in ['total_sapt', 'hf_interaction']:
            interpretation['percentages'][term] = (abs(energy) / abs(total)) * 100
    
    return interpretation
```

**Subtasks:**
1. Implement SAPT0
2. Add SAPT2 and SAPT2+
3. Add SAPT energy component extraction
4. Add interpretation helper
5. Handle dimer input format
6. Write tests
7. Document with examples

**Acceptance Criteria:**
- [ ] All SAPT levels work
- [ ] Energy decomposition accurate
- [ ] Interpretation helpful
- [ ] Tests validate results
- [ ] Documentation complete

---

### **Task 3.3: Coupled Cluster Tool**
**Priority:** P2  
**Duration:** 2 days

*Implementation similar to energy tool but with CC-specific options*

**Subtasks:**
1. Implement CCSD
2. Implement CCSD(T)
3. Add perturbative triples
4. Handle large systems efficiently
5. Write tests
6. Document

---

## **Phase 4: Resources & Prompts (Week 7)**

### **Task 4.1: Basis Set Resource**
**Priority:** P1  
**Duration:** 1 day

**Implementation:**
```python
# src/psi4_mcp/resources/basis_sets.py
from mcp.server.fastmcp import FastMCP
import psi4

@mcp.resource("basis://list")
def list_basis_sets() -> str:
    """
    List all available basis sets in Psi4.
    
    Returns JSON with:
    - Basis set name
    - Type (minimal, double-zeta, triple-zeta, etc.)
    - Elements supported
    - Description
    """
    # Get basis set library
    basis_sets = psi4.qcdb.libmintsbasisset.basishorde
    
    result = []
    for name in basis_sets:
        info = {
            'name': name,
            'type': classify_basis_set(name),
            'description': get_basis_description(name)
        }
        result.append(info)
    
    return json.dumps(result, indent=2)

@mcp.resource("basis://{basis_name}")
def get_basis_info(basis_name: str) -> str:
    """Get detailed information about a specific basis set"""
    try:
        # Get basis set details
        info = {
            'name': basis_name,
            'type': classify_basis_set(basis_name),
            'description': get_basis_description(basis_name),
            'recommended_for': get_recommendations(basis_name),
            'elements_supported': get_supported_elements(basis_name),
            'citation': get_basis_citation(basis_name)
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)})
```

**Subtasks:**
1. Implement basis set listing
2. Add basis set details
3. Add recommendations
4. Add citations
5. Test all resources
6. Document

---

### **Task 4.2: Method Resource**
**Priority:** P1  
**Duration:** 1 day

**Implementation:**
```python
# src/psi4_mcp/resources/methods.py
@mcp.resource("method://list")
def list_methods() -> str:
    """List all available computational methods"""
    methods = {
        'hartree_fock': {
            'methods': ['HF', 'RHF', 'UHF', 'ROHF'],
            'description': 'Hartree-Fock theory',
            'cost': 'O(N^4)',
            'accuracy': 'baseline'
        },
        'dft': {
            'methods': ['B3LYP', 'PBE', 'PBE0', 'wB97X', 'M06-2X'],
            'description': 'Density Functional Theory',
            'cost': 'O(N^3)',
            'accuracy': 'good for most systems'
        },
        'mp2': {
            'methods': ['MP2', 'RI-MP2', 'DF-MP2'],
            'description': 'Second-order Møller-Plesset perturbation theory',
            'cost': 'O(N^5)',
            'accuracy': 'improved over HF'
        },
        'coupled_cluster': {
            'methods': ['CCSD', 'CCSD(T)', 'CCSDT'],
            'description': 'Coupled cluster methods',
            'cost': 'O(N^6) - O(N^8)',
            'accuracy': 'very high (gold standard)'
        }
    }
    return json.dumps(methods, indent=2)
```

---

### **Task 4.3: Prompt Templates**
**Priority:** P2  
**Duration:** 1 day

**Implementation:**
```python
# src/psi4_mcp/prompts/templates.py
@mcp.prompt()
def generate_optimization_workflow(molecule_name: str) -> str:
    """Template for geometry optimization workflow"""
    return f"""
    Workflow for optimizing {molecule_name}:
    
    1. Initial structure validation
    2. Single-point energy calculation at initial geometry
    3. Geometry optimization
    4. Frequency calculation to verify minimum
    5. Final single-point at optimized geometry with larger basis
    
    Recommended settings:
    - Initial: B3LYP/6-31G*
    - Final: B3LYP/cc-pVTZ
    """

@mcp.prompt()
def suggest_method_basis(property: str, accuracy: str) -> str:
    """Suggest method/basis for property calculation"""
    recommendations = {
        'energy': {
            'low': 'HF/6-31G',
            'medium': 'B3LYP/6-31G*',
            'high': 'CCSD(T)/cc-pVTZ'
        },
        'geometry': {
            'low': 'HF/6-31G',
            'medium': 'B3LYP/6-31G*',
            'high': 'MP2/cc-pVDZ'
        }
    }
    # Return recommendation
```

---

## **Phase 5: Error Handling & Recovery (Week 8)**

### **Task 5.1: Error Detection System**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/utils/error_handler.py
import re
from typing import Optional, Dict, List
from enum import Enum

class ErrorType(Enum):
    CONVERGENCE_FAILURE = "convergence"
    MEMORY_ERROR = "memory"
    BASIS_SET_ERROR = "basis"
    GEOMETRY_ERROR = "geometry"
    SYMMETRY_ERROR = "symmetry"
    UNKNOWN = "unknown"

class ErrorHandler:
    """Detect and categorize Psi4 errors"""
    
    ERROR_PATTERNS = {
        ErrorType.CONVERGENCE_FAILURE: [
            r"Could not converge SCF iterations",
            r"DIIS failed",
            r"Maximum number of iterations exceeded",
            r"Density not converged"
        ],
        ErrorType.MEMORY_ERROR: [
            r"Insufficient memory",
            r"Out of memory",
            r"Cannot allocate memory"
        ],
        ErrorType.BASIS_SET_ERROR: [
            r"Basis set .* not found",
            r"Unknown basis set",
            r"Basis set unavailable for element"
        ],
        ErrorType.GEOMETRY_ERROR: [
            r"Invalid molecular geometry",
            r"Atoms too close",
            r"Linear molecule"
        ],
        ErrorType.SYMMETRY_ERROR: [
            r"Symmetry operation failed",
            r"Point group detection failed"
        ]
    }
    
    def detect_error(self, error_message: str) -> ErrorType:
        """Detect error type from message"""
        for error_type, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return error_type
        return ErrorType.UNKNOWN
    
    def suggest_fix(self, error_type: ErrorType, context: dict) -> List[str]:
        """Suggest fixes for detected error"""
        fixes = {
            ErrorType.CONVERGENCE_FAILURE: [
                "Try increasing maxiter",
                "Use SOSCF algorithm: set options({'soscf': 'true'})",
                "Try damping: set options({'damping_percentage': 20})",
                "Use different initial guess: set options({'guess': 'sad'})",
                "Increase basis set size"
            ],
            ErrorType.MEMORY_ERROR: [
                "Increase available memory with set_memory()",
                "Use density fitting (DF) methods",
                "Reduce basis set size",
                "Use fewer threads"
            ],
            ErrorType.BASIS_SET_ERROR: [
                "Check basis set name spelling",
                "Use smaller basis set",
                "Check if basis set supports all elements",
                "Try similar basis set from same family"
            ],
            ErrorType.GEOMETRY_ERROR: [
                "Check atom coordinates",
                "Ensure atoms are not too close (> 0.5 Å)",
                "Pre-optimize with cheaper method",
                "Disable symmetry: symmetry c1"
            ]
        }
        return fixes.get(error_type, ["Please check input parameters"])
    
    async def auto_recover(self, error_type: ErrorType, 
                          original_input: dict,
                          ctx) -> Optional[dict]:
        """Attempt automatic error recovery"""
        if error_type == ErrorType.CONVERGENCE_FAILURE:
            # Try with SOSCF
            await ctx.info("Attempting recovery with SOSCF algorithm...")
            modified_input = original_input.copy()
            if 'options' not in modified_input:
                modified_input['options'] = {}
            modified_input['options']['soscf'] = 'true'
            modified_input['options']['maxiter'] = 200
            return modified_input
            
        elif error_type == ErrorType.MEMORY_ERROR:
            # Try reducing memory footprint
            await ctx.info("Attempting recovery with reduced memory...")
            modified_input = original_input.copy()
            modified_input['memory'] = str(int(modified_input.get('memory', '2 GB').split()[0]) // 2) + ' GB'
            return modified_input
            
        return None
```

**Subtasks:**
1. Implement error pattern matching
2. Add error categorization
3. Implement fix suggestions
4. Add auto-recovery logic
5. Test with various error scenarios
6. Document error handling

**Acceptance Criteria:**
- [ ] All error types detected
- [ ] Suggestions are helpful
- [ ] Auto-recovery works when possible
- [ ] Tests cover all error types
- [ ] Documentation complete

---

### **Task 5.2: Convergence Recovery**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# src/psi4_mcp/utils/convergence_helper.py
class ConvergenceHelper:
    """Helper for SCF convergence issues"""
    
    RECOVERY_STRATEGIES = [
        {
            'name': 'SOSCF',
            'options': {'soscf': 'true', 'soscf_start_convergence': 1e-4},
            'description': 'Second-Order SCF for difficult convergence'
        },
        {
            'name': 'Damping',
            'options': {'damping_percentage': 20, 'soscf': 'false'},
            'description': 'Damp Fock matrix updates'
        },
        {
            'name': 'Level Shift',
            'options': {'level_shift': 0.5},
            'description': 'Shift virtual orbital energies'
        },
        {
            'name': 'SAD Guess',
            'options': {'guess': 'sad'},
            'description': 'Superposition of Atomic Densities initial guess'
        },
        {
            'name': 'Increased Iterations',
            'options': {'maxiter': 500},
            'description': 'Allow more SCF iterations'
        }
    ]
    
    async def try_convergence_strategies(self, 
                                         original_calculation,
                                         ctx) -> dict:
        """Try multiple convergence strategies"""
        for i, strategy in enumerate(self.RECOVERY_STRATEGIES):
            await ctx.info(f"Trying strategy {i+1}/{len(self.RECOVERY_STRATEGIES)}: {strategy['name']}")
            
            try:
                # Modify options
                modified_input = original_calculation.copy()
                if 'options' not in modified_input:
                    modified_input['options'] = {}
                modified_input['options'].update(strategy['options'])
                
                # Attempt calculation
                result = await calculate_energy(modified_input, ctx)
                
                await ctx.info(f"✓ Strategy '{strategy['name']}' succeeded!")
                return {
                    'success': True,
                    'strategy': strategy['name'],
                    'result': result
                }
                
            except Exception as e:
                await ctx.warn(f"✗ Strategy '{strategy['name']}' failed: {str(e)}")
                continue
        
        return {
            'success': False,
            'message': 'All convergence strategies failed'
        }
```

---

## **Phase 6: Testing Infrastructure (Week 9-10)**

### **Task 6.1: Unit Tests**
**Priority:** P0  
**Duration:** 3 days

**Test Coverage:**
```python
# tests/unit/test_energy.py
import pytest
import psi4
from psi4_mcp.tools.energy import calculate_energy

@pytest.mark.asyncio
async def test_energy_h2o_hf():
    """Test HF energy calculation for water"""
    input_data = {
        "molecule": {
            "geometry": "O\\nH 1 0.96\\nH 1 0.96 2 104.5",
            "charge": 0,
            "multiplicity": 1
        },
        "method": "hf",
        "basis": "sto-3g"
    }
    
    result = await calculate_energy(input_data, mock_context)
    
    # Known reference value
    assert abs(result.energy - (-74.965901217080)) < 1e-6
    assert result.converged == True

@pytest.mark.asyncio
async def test_energy_b3lyp():
    """Test B3LYP calculation"""
    # Implementation

@pytest.mark.asyncio
async def test_energy_invalid_basis():
    """Test error handling for invalid basis"""
    # Should raise appropriate error
```

**Test Files to Create:**
```
tests/
├── unit/
│   ├── test_energy.py (20+ tests)
│   ├── test_optimization.py (15+ tests)
│   ├── test_frequencies.py (10+ tests)
│   ├── test_properties.py (15+ tests)
│   ├── test_tddft.py (10+ tests)
│   ├── test_validation.py (20+ tests)
│   └── test_parsers.py (15+ tests)
├── integration/
│   ├── test_workflows.py
│   └── test_mcp_protocol.py
└── fixtures/
    ├── molecules.py
    ├── reference_data.py
    └── mock_context.py
```

**Acceptance Criteria:**
- [ ] 100+ unit tests written
- [ ] >90% code coverage
- [ ] All tests pass
- [ ] CI/CD configured

---

### **Task 6.2: Integration Tests**
**Priority:** P0  
**Duration:** 2 days

**Implementation:**
```python
# tests/integration/test_workflows.py
@pytest.mark.asyncio
async def test_full_optimization_workflow():
    """Test complete optimization workflow"""
    # 1. Energy at initial geometry
    # 2. Optimize
    # 3. Frequencies
    # 4. Final energy
    pass

@pytest.mark.asyncio
async def test_tddft_workflow():
    """Test TDDFT workflow"""
    # 1. Ground state optimization
    # 2. TDDFT calculation
    # 3. UV-Vis spectrum generation
    pass
```

---

### **Task 6.3: Validation Against Known Results**
**Priority:** P0  
**Duration:** 2 days

**Test Systems:**
1. Water (H2O) - HF, DFT, MP2
2. Methane (CH4) - Frequencies
3. Ethylene (C2H4) - TDDFT
4. Neon dimer - SAPT
5. Formaldehyde (H2CO) - Properties

**Create Reference Database:**
```python
# tests/fixtures/reference_data.py
REFERENCE_DATA = {
    'water_hf_sto3g': {
        'energy': -74.965901217080,
        'dipole': 1.9484,
        'homo_lumo_gap': 0.524
    },
    # ... more references
}
```

---

## **Phase 7: Documentation (Week 11)**

### **Task 7.1: API Documentation**
**Priority:** P1  
**Duration:** 2 days

**Create:**
1. **API Reference** - Auto-generated from docstrings
2. **User Guide** - Step-by-step tutorials
3. **Examples** - Real-world use cases

**Structure:**
```markdown
# Psi4 MCP Server Documentation

## Installation
## Quick Start
## Tool Reference
  - calculate_energy
  - optimize_geometry
  - calculate_frequencies
  - calculate_properties
  - calculate_excited_states
  - calculate_sapt
## Resources Reference
## Prompt Templates
## Error Handling Guide
## Performance Optimization
## FAQ
## Troubleshooting
```

---

### **Task 7.2: Example Library**
**Priority:** P1  
**Duration:** 2 days

**Create Examples:**
```python
# examples/01_basic_energy.py
"""Calculate energy of water molecule"""

# examples/02_geometry_optimization.py
"""Optimize geometry of methanol"""

# examples/03_frequencies.py
"""Calculate vibrational frequencies"""

# examples/04_tddft_spectrum.py
"""Generate UV-Vis spectrum"""

# examples/05_sapt_analysis.py
"""Analyze intermolecular interactions"""

# examples/06_advanced_workflow.py
"""Complete workflow: optimization + freq + properties"""
```

---

## **Phase 8: Deployment & Performance (Week 12)**

### **Task 8.1: Performance Optimization**
**Priority:** P1  
**Duration:** 2 days

**Optimization Areas:**
1. **Memory Management**
   - Implement memory limits
   - Add garbage collection
   - Stream large results

2. **Computation Efficiency**
   - Use density fitting when possible
   - Optimize basis set selection
   - Parallelize when appropriate

3. **Caching**
   - Cache basis set data
   - Cache frequently used molecules
   - Cache method information

---

### **Task 8.2: Deployment Configuration**
**Priority:** P1  
**Duration:** 2 days

**Create Deployment Files:**
```toml
# pyproject.toml
[project]
name = "psi4-mcp-server"
version = "1.0.0"
description = "MCP server for Psi4 quantum chemistry"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.0.0",
    "psi4>=1.9",
    "pydantic>=2.0.0",
    "numpy>=1.24.0",
    "ase>=3.22.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0"
]

[project.scripts]
psi4-mcp = "psi4_mcp.server:main"
```

**Docker Configuration:**
```dockerfile
# Dockerfile
FROM continuumio/miniconda3:latest

# Install Psi4
RUN conda install -c psi4 psi4 python=3.10

# Install MCP server
COPY . /app
WORKDIR /app
RUN pip install -e .

# Set environment
ENV PSI_SCRATCH=/tmp/psi4_scratch
RUN mkdir -p $PSI_SCRATCH

ENTRYPOINT ["psi4-mcp"]
```

---

### **Task 8.3: CI/CD Setup**
**Priority:** P1  
**Duration:** 1 day

**GitHub Actions:**
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Psi4
        run: |
          conda install -c psi4 psi4
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          pytest --cov=psi4_mcp tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## **Phase 9: Final Review & Launch (Week 13)**

### **Task 9.1: Security Audit**
**Priority:** P0  
**Duration:** 2 days

**Security Checklist:**
- [ ] Input sanitization
- [ ] Memory limit enforcement
- [ ] File system access restrictions
- [ ] Process isolation
- [ ] Secure error messages (no sensitive info)
- [ ] Rate limiting
- [ ] Audit logging

---

### **Task 9.2: Performance Benchmarking**
**Priority:** P1  
**Duration:** 1 day

**Benchmark Tests:**
1. Small molecule (< 10 atoms)
2. Medium molecule (10-50 atoms)
3. Large molecule (50-100 atoms)
4. Multiple calculations in sequence
5. Memory usage profiling

---

### **Task 9.3: Final Documentation Review**
**Priority:** P1  
**Duration:** 1 day

**Review:**
- [ ] All tools documented
- [ ] Examples work correctly
- [ ] Installation guide tested
- [ ] Troubleshooting guide complete
- [ ] FAQ populated

---

### **Task 9.4: Release Preparation**
**Priority:** P0  
**Duration:** 1 day

**Release Checklist:**
- [ ] Version tagged
- [ ] Changelog updated
- [ ] PyPI package built
- [ ] Docker image built
- [ ] GitHub release created
- [ ] Documentation deployed
- [ ] Announcement prepared

---

## **Phase 10: Maintenance & Extensions (Ongoing)**

### **Future Enhancements:**
1. Add more advanced methods (MRCI, MRPT)
2. Add polarizability calculations
3. Add NMR property calculations
4. Add EOM-CC methods
5. Add PCM solvent model
6. Add trajectory analysis tools
7. Add automated benchmarking
8. Add machine learning integration

---

## **Critical Success Factors**

### **Must-Have Features:**
1. ✅ Energy calculations (all major methods)
2. ✅ Geometry optimization
3. ✅ Vibrational frequencies
4. ✅ Molecular properties
5. ✅ TDDFT excited states
6. ✅ Robust error handling
7. ✅ Comprehensive testing
8. ✅ Clear documentation

### **Quality Metrics:**
- Code coverage: >90%
- Documentation coverage: 100%
- Test pass rate: 100%
- Performance: <2x overhead vs direct Psi4
- Error recovery rate: >60%

---

## **Risk Management**

### **Technical Risks:**
1. **Risk:** Psi4 API changes
   - **Mitigation:** Pin Psi4 version, test with multiple versions
   
2. **Risk:** Memory leaks
   - **Mitigation:** Comprehensive memory profiling, cleanup routines
   
3. **Risk:** Convergence failures
   - **Mitigation:** Multiple recovery strategies, clear error messages

4. **Risk:** Performance bottlenecks
   - **Mitigation:** Profiling, optimization, caching

---

## **Resource Requirements**

### **Development Environment:**
- Python 3.10+
- Psi4 1.9+
- MCP SDK 1.0+
- 8GB+ RAM
- 20GB disk space

### **Testing Environment:**
- Multiple OS (Linux, macOS, Windows)
- Various Python versions (3.10, 3.11, 3.12)
- Different Psi4 versions

---

## **Timeline Summary**

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| 0: Foundation | 1 week | Environment, architecture, research |
| 1: Core Infrastructure | 1 week | Server, validation, parsing |
| 2: Core Tools | 2 weeks | Energy, optimization, frequencies, properties |
| 3: Advanced Tools | 2 weeks | TDDFT, SAPT, CC |
| 4: Resources/Prompts | 1 week | Resources, templates |
| 5: Error Handling | 1 week | Detection, recovery |
| 6: Testing | 2 weeks | Unit, integration, validation |
| 7: Documentation | 1 week | API docs, examples |
| 8: Deployment | 1 week | Performance, CI/CD |
| 9: Final Review | 1 week | Security, benchmarks, release |
| **Total** | **13 weeks** | **Production-ready MCP server** |

---

## **Next Steps**

1. **Immediate:** Set up development environment (Task 0.1)
2. **Day 1-3:** Complete Phase 0 (Foundation)
3. **Week 2:** Begin Phase 1 (Core Infrastructure)
4. **Ongoing:** Daily standups, weekly reviews

---

## **Appendix A: Complete Tool List**

### **Implemented Tools (Priority Order):**

1. **calculate_energy** (P0)
   - Methods: HF, DFT, MP2, CC
   - All basis sets
   - Reference types

2. **optimize_geometry** (P0)
   - Unconstrained optimization
   - Constrained optimization
   - TS search

3. **calculate_frequencies** (P0)
   - Harmonic frequencies
   - Thermodynamics
   - IR intensities

4. **calculate_properties** (P1)
   - Dipole/quadrupole
   - Orbital properties
   - Charges

5. **calculate_excited_states** (P1)
   - TD-DFT
   - TDA
   - UV-Vis spectra

6. **calculate_sapt** (P2)
   - SAPT0, SAPT2, SAPT2+
   - Energy decomposition

7. **calculate_coupling_constants** (P2)
   - Spin-spin coupling
   - NMR properties

---

## **Appendix B: Reference Values**

### **Test Systems Reference Data:**
```python
REFERENCE_VALUES = {
    'h2o': {
        'hf_sto3g': {
            'energy': -74.965901217080,
            'dipole': 1.9484
        },
        'b3lyp_631gd': {
            'energy': -76.404849968,
            'frequencies': [1621.7, 3755.7, 3854.7]
        }
    },
    # More reference data...
}
```

---

## **Document Version History**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-27 | Initial comprehensive plan |  |

---

**END OF PLAN**

This plan is comprehensive, accurate, and ready for implementation. Each phase builds on the previous one, ensuring a solid foundation before moving to advanced features. The 13-week timeline is realistic and includes buffer for unexpected issues.


lib.org/ase/calculators/psi4.html  
https://psicode.org/psi4manual/master/index.html
https://psicode.org/psi4manual/master/index_tutorials.html
https://github.com/psi4/psi4
https://psicode.org/psi4manual/master/index.html
https://psicode.org/psi4manual/master/testsuite.html
https://forum.psicode.org/
https://psicode.org/psi4manual/master/introduction.html#technical-support