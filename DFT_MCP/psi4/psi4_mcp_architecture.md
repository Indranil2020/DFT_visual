# Psi4 MCP Server - Architecture Diagram & Data Flow

**Visual Guide to System Architecture**  
**Version:** 1.0  
**Date:** 2025-11-27

---

## **System Architecture Overview**

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI/LLM Client                                │
│                  (Claude, GPT-4, Local LLM, etc.)                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │ MCP Protocol (JSON-RPC over stdio)
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                     MCP SERVER (FastMCP)                             │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Server Layer (server.py)                    │ │
│  │  • Request routing                                             │ │
│  │  • Session management                                          │ │
│  │  • Logging (stderr only!)                                      │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐ │
│  │                 Validation Layer (utils/validation.py)         │ │
│  │  • Input validation (Pydantic)                                 │ │
│  │  • Geometry validation                                         │ │
│  │  • Basis set validation                                        │ │
│  │  • Method validation                                           │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                       │
│  ┌───────────────────────────┴───────────────────────────────────┐ │
│  │                    Tool Layer (tools/)                         │ │
│  │                                                                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │ │
│  │  │  Energy  │  │   Opt    │  │   Freq   │  │   Prop   │     │ │
│  │  │ (P0)     │  │  (P0)    │  │  (P0)    │  │  (P1)    │     │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │ │
│  │       │             │             │             │             │ │
│  │  ┌────▼─────┐  ┌───▼──────┐  ┌──▼───────┐  ┌──▼───────┐   │ │
│  │  │  TDDFT   │  │   SAPT   │  │    CC    │  │  Other   │   │ │
│  │  │  (P1)    │  │   (P2)   │  │   (P2)   │  │   ...    │   │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │ │
│  │       └──────────────┴──────────────┴──────────────┘         │ │
│  │                              │                                 │ │
│  └──────────────────────────────┼─────────────────────────────────┘ │
│                              │                                       │
│  ┌───────────────────────────▼───────────────────────────────────┐ │
│  │                 Error Handler (utils/error_handler.py)         │ │
│  │  • Error detection & categorization                            │ │
│  │  • Auto-recovery strategies                                    │ │
│  │  • Suggestion generation                                       │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                       │
│  ┌───────────────────────────▼───────────────────────────────────┐ │
│  │               Psi4 Wrapper & Executor                          │ │
│  │  • Configuration management                                    │ │
│  │  • Memory management                                           │ │
│  │  • Process management                                          │ │
│  └───────────────────────────┬───────────────────────────────────┘ │
│                              │                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                               │ Python API calls
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                         Psi4 Core Engine                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │     SCF     │  │  Post-SCF   │  │     DFT     │  │    TDDFT    ││
│  │  (HF, KS)   │  │(MP2, CC, CI)│  │ (Functionals)│  │ (Excited)   ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │   Geometry  │  │  Frequency  │  │ Properties  │  │    SAPT     ││
│  │ Optimization│  │  Analysis   │  │  Analysis   │  │  Analysis   ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│
└───────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Scratch Files   │
                    │   (PSI_SCRATCH)  │
                    └──────────────────┘
```

---

## **Data Flow Diagrams**

### **1. Energy Calculation Flow**

```
User Request (via LLM)
    │
    ├─► "Calculate the energy of water at B3LYP/cc-pVDZ"
    │
    ▼
MCP Client
    │
    ├─► Converts to tool call: calculate_energy(...)
    │
    ▼
MCP Server (Tool Handler)
    │
    ├─► Validates input with Pydantic
    │   ├─► Geometry format valid? ✓
    │   ├─► Method exists? ✓
    │   ├─► Basis set available? ✓
    │   └─► Memory sufficient? ✓
    │
    ├─► [Progress: 0%] "Starting calculation..."
    │
    ▼
Psi4 Wrapper
    │
    ├─► Configure Psi4:
    │   ├─► set_memory('2 GB')
    │   ├─► set_num_threads(4)
    │   └─► Set scratch directory
    │
    ├─► Build molecule object
    │   └─► psi4.geometry(mol_string)
    │
    ├─► [Progress: 20%] "Running SCF..."
    │
    ▼
Psi4 Core Engine
    │
    ├─► DFT calculation (B3LYP)
    │   ├─► Basis set setup
    │   ├─► Initial guess (SAD)
    │   ├─► SCF iterations
    │   │   ├─► Iteration 1... [Progress: 30%]
    │   │   ├─► Iteration 2... [Progress: 40%]
    │   │   └─► Converged! ✓
    │   └─► Final energy: -76.404 hartree
    │
    ▼
Output Parser
    │
    ├─► Extract results:
    │   ├─► Energy
    │   ├─► SCF iterations
    │   ├─► Convergence status
    │   └─► Dipole moment
    │
    ├─► [Progress: 90%] "Formatting results..."
    │
    ▼
MCP Server Response
    │
    ├─► Format as EnergyCalculationOutput
    │   {
    │     "energy": -76.404,
    │     "units": "hartree",
    │     "method": "b3lyp",
    │     "basis": "cc-pvdz",
    │     "converged": true,
    │     "scf_iterations": 12
    │   }
    │
    ├─► [Progress: 100%] "Complete!"
    │
    ▼
MCP Client
    │
    └─► Returns to LLM
        │
        ▼
    LLM Response to User
        │
        └─► "The B3LYP/cc-pVDZ energy of water is -76.404 hartree."
```

### **2. Optimization Flow with Error Recovery**

```
User Request
    │
    └─► "Optimize the geometry of methanol"
        │
        ▼
    MCP Server (optimize_geometry)
        │
        ├─► Validate input ✓
        │
        ├─► [Progress: 0%] "Starting optimization..."
        │
        ├─► Configure Psi4
        │
        ├─► Initial geometry → Psi4
        │
        ▼
    Psi4 Optimization Loop
        │
        ├─► Step 1:
        │   ├─► Calculate energy & gradient
        │   ├─► Update geometry
        │   ├─► Check convergence
        │   ├─► [Progress: 10%] "Step 1/50"
        │   └─► Not converged, continue
        │
        ├─► Step 2:
        │   ├─► Calculate energy & gradient
        │   ├─► Update geometry
        │   ├─► Check convergence
        │   ├─► [Progress: 20%] "Step 2/50"
        │   └─► Not converged, continue
        │
        ├─► ... (more steps)
        │
        ├─► Step 15:
        │   ├─► Calculate energy & gradient
        │   ├─► ERROR! SCF not converging ✗
        │   │
        │   ▼
        │   Error Handler Activated
        │       │
        │       ├─► Detect error type: CONVERGENCE_FAILURE
        │       │
        │       ├─► Suggest fixes:
        │       │   1. Try SOSCF
        │       │   2. Try damping
        │       │   3. Try level shift
        │       │
        │       ├─► [Auto-recovery] Try Strategy 1: SOSCF
        │       │   │
        │       │   ├─► Modify options: {'soscf': True}
        │       │   │
        │       │   ├─► Retry calculation
        │       │   │
        │       │   └─► SUCCESS! ✓
        │       │
        │       └─► Continue optimization from Step 15
        │
        ├─► Step 16-30: Continue normally
        │   └─► [Progress: 60%] "Step 30/50"
        │
        ├─► Step 35:
        │   ├─► Check convergence
        │   └─► CONVERGED! ✓
        │
        └─► [Progress: 100%] "Optimization complete!"
            │
            ▼
        Extract Results
            │
            ├─► Final energy
            ├─► Final geometry
            ├─► Convergence info
            └─► Trajectory
                │
                ▼
            Return to User
```

### **3. TDDFT Flow**

```
User Request
    │
    └─► "Calculate the UV-Vis spectrum of benzene"
        │
        ▼
    MCP Server (calculate_excited_states)
        │
        ├─► Validate: Method must be DFT ✓
        │
        ├─► [Progress: 0%] "Setting up TDDFT..."
        │
        ▼
    Ground State DFT
        │
        ├─► Run B3LYP/aug-cc-pVDZ
        │   └─► Ground state energy: -232.234 hartree
        │
        ├─► [Progress: 40%] "Ground state complete"
        │
        ▼
    TDDFT Calculation
        │
        ├─► Configure TDDFT:
        │   ├─► n_states = 10
        │   ├─► TDA = False
        │   └─► triplets = False
        │
        ├─► [Progress: 50%] "Computing excited states..."
        │
        ├─► Solve TDDFT equations
        │   ├─► State 1: 5.89 eV (210 nm), f=0.012
        │   ├─► State 2: 6.12 eV (203 nm), f=0.654
        │   ├─► State 3: 6.45 eV (192 nm), f=0.000
        │   └─► ... (7 more states)
        │
        ├─► [Progress: 80%] "Generating spectrum..."
        │
        ▼
    Spectrum Generation
        │
        ├─► Apply Gaussian broadening
        │
        ├─► Generate wavelength vs intensity
        │   └─► 1000 data points (200-800 nm)
        │
        ├─► [Progress: 100%] "Complete!"
        │
        ▼
    Return Results
        │
        ├─► excited_states: [...]
        ├─► uv_vis_spectrum: {...}
        └─► Return to user
            │
            ▼
        LLM analyzes and explains spectrum
```

---

## **Component Interaction Matrix**

```
                      │ Server │ Tools │ Psi4 │ Error │ Parser │ Valid │
──────────────────────┼────────┼───────┼──────┼───────┼────────┼───────┤
Server                │   —    │  ●●●  │  —   │  ●●   │   ●    │  ●●●  │
Tools                 │   ●    │   —   │ ●●●  │  ●●   │  ●●●   │   ●   │
Psi4 Wrapper          │   —    │  ●●   │ ●●●  │   ●   │   —    │   —   │
Error Handler         │   ●    │  ●●●  │   ●  │   —   │   ●    │   ●   │
Output Parser         │   —    │  ●●●  │  ●●  │   ●   │   —    │   —   │
Validation            │  ●●    │  ●●●  │   ●  │   ●   │   —    │   —   │
──────────────────────┴────────┴───────┴──────┴───────┴────────┴───────┘

Legend:
  ●●● = Heavy interaction (constant communication)
  ●●  = Moderate interaction (frequent calls)
  ●   = Light interaction (occasional calls)
  —   = No direct interaction
```

---

## **File Dependency Graph**

```
server.py (entry point)
    │
    ├──► models.py (data structures)
    │
    ├──► tools/
    │    ├──► energy.py
    │    │    ├──► utils/validation.py
    │    │    ├──► utils/output_parser.py
    │    │    └──► utils/error_handler.py
    │    │
    │    ├──► optimization.py
    │    │    ├──► utils/validation.py
    │    │    ├──► utils/output_parser.py
    │    │    ├──► utils/error_handler.py
    │    │    └──► utils/convergence_helper.py
    │    │
    │    ├──► frequencies.py
    │    │    └──► ... (similar dependencies)
    │    │
    │    └──► ... (other tools)
    │
    ├──► resources/
    │    ├──► basis_sets.py
    │    └──► methods.py
    │
    ├──► prompts/
    │    └──► templates.py
    │
    └──► utils/
         ├──► validation.py
         ├──► output_parser.py
         ├──► error_handler.py
         └──► convergence_helper.py
```

---

## **Error Handling Flow**

```
Psi4 Execution
    │
    ├─► Try: Execute calculation
    │   │
    │   ├─► SUCCESS ✓
    │   │   └─► Return results
    │   │
    │   └─► FAILURE ✗
    │       │
    │       ▼
    │   Error Handler
    │       │
    │       ├─► 1. Detect Error Type
    │       │   ├─► Convergence? → CONVERGENCE_ERROR
    │       │   ├─► Memory? → MEMORY_ERROR
    │       │   ├─► Basis? → BASIS_ERROR
    │       │   └─► Other? → UNKNOWN_ERROR
    │       │
    │       ├─► 2. Generate Suggestions
    │       │   │
    │       │   ├─► CONVERGENCE_ERROR:
    │       │   │   ├─► Try SOSCF
    │       │   │   ├─► Try damping
    │       │   │   ├─► Try level shift
    │       │   │   └─► Try SAD guess
    │       │   │
    │       │   ├─► MEMORY_ERROR:
    │       │   │   ├─► Reduce memory
    │       │   │   ├─► Use DF methods
    │       │   │   └─► Reduce basis
    │       │   │
    │       │   └─► ... (other errors)
    │       │
    │       ├─► 3. Attempt Auto-Recovery
    │       │   │
    │       │   ├─► Strategy 1: Try modification
    │       │   │   ├─► SUCCESS? → Return results ✓
    │       │   │   └─► FAILURE? → Try next
    │       │   │
    │       │   ├─► Strategy 2: Try modification
    │       │   │   ├─► SUCCESS? → Return results ✓
    │       │   │   └─► FAILURE? → Try next
    │       │   │
    │       │   └─► All failed?
    │       │       │
    │       │       ▼
    │       │   Report to User
    │       │       │
    │       │       ├─► Error type
    │       │       ├─► Detailed message
    │       │       ├─► Suggestions
    │       │       └─► Recovery attempts made
    │       │
    │       └─► Log for debugging
```

---

## **Memory Management Strategy**

```
┌─────────────────────────────────────────────────────┐
│              Memory Allocation                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│  User Configurable Memory (e.g., 2 GB)             │
│  ┌────────────────────────────────────────────┐   │
│  │                                             │   │
│  │  Psi4 Working Memory                       │   │
│  │  ├─► Basis function integrals (40%)        │   │
│  │  ├─► Density matrices (20%)                │   │
│  │  ├─► Fock matrices (20%)                   │   │
│  │  ├─► Temporary arrays (15%)                │   │
│  │  └─► Buffer (5%)                           │   │
│  │                                             │   │
│  └────────────────────────────────────────────┘   │
│                                                      │
│  Python Overhead (~200 MB)                          │
│  ┌────────────────────────────────────────────┐   │
│  │  MCP server, Pydantic models, etc.         │   │
│  └────────────────────────────────────────────┘   │
│                                                      │
│  System Reserved (~500 MB)                          │
│  ┌────────────────────────────────────────────┐   │
│  │  OS, filesystem cache, etc.                │   │
│  └────────────────────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘

Total System RAM should be:
  User Memory + Python Overhead + System Reserved
  = 2 GB + 0.2 GB + 0.5 GB
  = ~2.7 GB minimum

Recommended: 2× user memory for safety
  = 2 GB × 2 = 4 GB total system RAM
```

---

## **Testing Pyramid**

```
                    ┌─────────────┐
                    │  E2E Tests  │  (5% - Full workflows)
                    │    ~10      │
                    └─────────────┘
                          △
                     ┌───────────────┐
                     │Integration    │  (15% - Multi-component)
                     │   Tests       │
                     │    ~30        │
                     └───────────────┘
                          △
                ┌─────────────────────┐
                │   Unit Tests        │  (80% - Individual functions)
                │      ~150+          │
                └─────────────────────┘

Focus:
  Unit: Test each function in isolation
  Integration: Test tool → Psi4 → parser chains
  E2E: Test full user workflow through MCP
```

---

## **Deployment Options**

```
┌────────────────────────────────────────────────────────┐
│                  Deployment Model                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Option 1: Local Stdio (Recommended for development)  │
│  ┌──────────────────────────────────────────────┐    │
│  │  Claude Desktop ←→ MCP Server ←→ Psi4        │    │
│  │  (Same machine,   (stdio)      (subprocess)   │    │
│  │   IPC via pipes)                              │    │
│  └──────────────────────────────────────────────┘    │
│                                                         │
│  Option 2: HTTP Server (For remote/multi-user)        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Client ←→ MCP Server ←→ Psi4                │    │
│  │  (Network) (HTTP+SSE)   (subprocess)          │    │
│  └──────────────────────────────────────────────┘    │
│                                                         │
│  Option 3: Docker Container (For isolation)           │
│  ┌──────────────────────────────────────────────┐    │
│  │  Host → Docker Container                      │    │
│  │         ├─► MCP Server                        │    │
│  │         └─► Psi4 + dependencies               │    │
│  └──────────────────────────────────────────────┘    │
│                                                         │
└────────────────────────────────────────────────────────┘

Recommendation:
  Development: Option 1 (stdio, local)
  Production: Option 3 (Docker, with Option 2 for access)
```

---

## **Key Architectural Principles**

### **1. Separation of Concerns**
```
User Interface (LLM) ≠ Business Logic (Tools) ≠ Computation (Psi4)
                          ↓
              Each layer can evolve independently
```

### **2. Fail Fast, Fail Safe**
```
Validate Early → Detect Errors → Auto-Recover → Report Clearly
     ↓               ↓               ↓               ↓
  Pydantic      Pattern Match    Strategies    User-Friendly
```

### **3. Progressive Enhancement**
```
Phase 0: Foundation
    ↓
Phase 1: Basic tools
    ↓
Phase 2: Advanced tools
    ↓
Phase 3: Optimization
    ↓
Production Ready
```

### **4. Observability**
```
Progress Reporting → Logging → Error Tracking → Performance Metrics
        ↓               ↓            ↓                ↓
   User sees       Debug         Improve         Optimize
   progress       issues        reliability     performance
```

---

**This architecture ensures:**
- ✅ Modularity (easy to extend)
- ✅ Reliability (error handling at every layer)
- ✅ Performance (efficient resource use)
- ✅ Maintainability (clear separation of concerns)
- ✅ Testability (each component testable in isolation)

**Reference this diagram during implementation to maintain architectural consistency.**
