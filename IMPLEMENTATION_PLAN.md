# DFT Flight Simulator - Complete Implementation Plan

## 🎯 **PROJECT VISION**
Build a comprehensive, modular DFT learning platform where students visually understand:
1. **Basis Sets** (Where electrons live)
2. **Pseudopotentials** (How we simplify the nucleus)
3. **XC Functionals** (How different approximations affect energy)

---

## 📋 **PHASE 1: ARCHITECTURAL RESTRUCTURING**

### **Goal:** Transform monolithic app into modular, maintainable architecture

### **New Directory Structure:**
```
DFT_TOOLS/
├── app.py                          # Main entry - Navigation & Landing
├── requirements.txt                # Dependencies
│
├── data/                           # Data storage
│   ├── basis_cache.json           # Existing
│   └── pseudo_cache/              # NEW: Cached pseudopotentials
│
├── modules/                        # Core logic (NO UI)
│   ├── __init__.py
│   ├── basis_sets.py              # Refactored from existing
│   ├── pseudopotentials.py        # NEW: Pseudo fetching & parsing
│   └── xc_functionals.py          # NEW: XC calculations
│
├── pages/                          # Streamlit pages (UI only)
│   ├── 1_📦_Basis_Sets.py         # Refactored existing
│   ├── 2_⚛️_Pseudopotentials.py   # NEW
│   └── 3_🔧_XC_Functionals.py     # NEW
│
└── utils/                          # Shared utilities
    ├── __init__.py
    ├── plotting.py                # Common plot styles
    ├── constants.py               # Physical constants, elements
    └── validators.py              # Input validation (no try/except)
```

### **Tasks:**
- [ ] Create directory structure
- [ ] Move existing code to modular structure
- [ ] Create `__init__.py` files
- [ ] Update imports

---

## 📋 **PHASE 2: MODULE A - PSEUDOPOTENTIALS ("The Core")**

### **Educational Goal:**
Show students why we replace the nucleus (-Z/r singularity) with a smooth pseudopotential

### **Backend: `modules/pseudopotentials.py`**

#### **Functions to Implement:**

1. **`fetch_pseudo_metadata() -> dict`**
   - Fetch available pseudopotentials from PseudoDojo
   - Return: {element: {types: ['standard', 'stringent'], functionals: ['PBE', 'LDA']}}
   - No try/except: Check response.status_code, return None if failed

2. **`fetch_pseudo_data(element: str, accuracy: str, functional: str) -> dict | None`**
   - Download UPF file from PseudoDojo GitHub
   - Parse XML to extract: r_grid, v_local, v_coulomb
   - Return: {'r': array, 'v_local': array, 'v_coulomb': array} or None

3. **`parse_upf_file(upf_content: str) -> dict | None`**
   - Parse UPF XML format
   - Extract mesh, local potential, atomic info
   - Return structured dict or None

4. **`calculate_coulomb_potential(r: np.ndarray, Z: int) -> np.ndarray`**
   - Pure function: V(r) = -Z/r
   - No exceptions needed

5. **`get_pseudo_comparison(element: str, accuracy1: str, accuracy2: str) -> dict | None`**
   - Compare two pseudopotentials
   - Return difference data

#### **Data Source:**
- **PseudoDojo**: https://github.com/pseudo-dojo/pseudo-dojo/tree/master/pseudo_dojo/pseudos
- **Format**: UPF (Unified Pseudopotential Format)
- **Cache**: Store downloaded files locally to avoid re-fetching

### **Frontend: `pages/2_⚛️_Pseudopotentials.py`**

#### **UI Components:**

1. **Element Selector**
   - Reuse periodic table from basis sets
   - Highlight elements with available pseudos

2. **Configuration Panel**
   - Accuracy: Standard (soft) vs Stringent (hard)
   - Functional: PBE, LDA, PW91
   - Show compatibility warning if mismatch with XC tab

3. **Main Visualization**
   - Plot 1: Coulomb (-Z/r) vs Pseudopotential
   - Plot 2: Difference (shows smoothing region)
   - Annotations: "Core region", "Valence region"

4. **Educational Info Box**
   - Explain why pseudopotentials exist
   - Show cutoff radius
   - Display transferability info

#### **Tasks:**
- [ ] Implement `fetch_pseudo_metadata()`
- [ ] Implement `fetch_pseudo_data()`
- [ ] Implement `parse_upf_file()`
- [ ] Implement `calculate_coulomb_potential()`
- [ ] Create caching system
- [ ] Build UI page
- [ ] Add educational annotations
- [ ] Implement compatibility checker

---

## 📋 **PHASE 3: MODULE B - XC FUNCTIONALS ("The Engine")**

### **Educational Goal:**
Demystify LDA, GGA, Hybrid functionals by showing:
1. Mathematical form (enhancement factor)
2. Real-space effect on atoms

### **Backend: `modules/xc_functionals.py`**

#### **Functions to Implement:**

**Part 1: Mathematical Visualization (No atoms needed)**

1. **`calculate_lda_enhancement(s: np.ndarray) -> np.ndarray`**
   - F_x^LDA(s) = 1.0 (flat line)
   - Pure function

2. **`calculate_pbe_enhancement(s: np.ndarray) -> np.ndarray`**
   - F_x^PBE(s) = 1 + κ - κ/(1 + μs²/κ)
   - κ = 0.804, μ = 0.21951

3. **`calculate_b88_enhancement(s: np.ndarray) -> np.ndarray`**
   - Becke88 formula
   - β = 0.0042

4. **`get_enhancement_comparison(functionals: list[str], s_range: tuple) -> dict`**
   - Compare multiple functionals
   - Return: {functional: {'s': array, 'F': array}}

**Part 2: Real Atom Calculations (PySCF)**

5. **`calculate_atom_density(element: str, basis: str) -> dict | None`**
   - Use PySCF to get atomic density
   - Method: dft.init_guess_by_atom (instant, no SCF)
   - Return: {'r': array, 'rho': array} or None

6. **`calculate_xc_potential(element: str, functional: str, basis: str) -> dict | None`**
   - Calculate V_xc for given functional
   - Use PySCF's eval_xc
   - Return: {'r': array, 'v_xc': array} or None

7. **`get_xc_difference(element: str, func1: str, func2: str, basis: str) -> dict | None`**
   - Calculate ΔV_xc = V_xc(func1) - V_xc(func2)
   - Show where functionals differ most
   - Return: {'r': array, 'delta_v': array} or None

8. **`get_functional_info(functional: str) -> dict`**
   - Return metadata: type (LDA/GGA/Hybrid), description, reference
   - Pure lookup, no exceptions

#### **Dependencies:**
- PySCF (for atom calculations)
- NumPy, SciPy (for math)

### **Frontend: `pages/3_🔧_XC_Functionals.py`**

#### **UI Structure:**

**Sub-Tab 1: Jacob's Ladder (Mathematical)**
- Plot enhancement factor F_x(s) vs reduced gradient s
- Checkboxes: LDA, PBE, B88, BLYP, PW91
- Interactive: Hover shows formula
- Educational: Explain what s means (gradient/density)

**Sub-Tab 2: Real Space Impact**
- Element selector
- Functional comparison: Dropdown 1 vs Dropdown 2
- Plot: ΔV_xc(r) showing difference
- Annotation: Highlight shell regions where difference is largest

**Educational Panel:**
- Explain rungs of Jacob's ladder
- Show when to use each functional
- Link to pseudopotential compatibility

#### **Tasks:**
- [ ] Implement enhancement factor functions (LDA, PBE, B88)
- [ ] Implement PySCF atom density calculation
- [ ] Implement XC potential calculation
- [ ] Implement difference calculator
- [ ] Create Sub-Tab 1: Mathematical view
- [ ] Create Sub-Tab 2: Real atom view
- [ ] Add educational content
- [ ] Add functional database/lookup

---

## 📋 **PHASE 4: REFACTOR EXISTING BASIS SET MODULE**

### **Goal:** Make existing code modular and consistent

### **Backend: `modules/basis_sets.py`**

#### **Extract and refactor:**

1. **`get_available_basis_sets() -> list[str]`**
   - Return list of all basis sets
   - Use cached metadata

2. **`get_basis_metadata(basis_name: str) -> dict | None`**
   - Return basis set info
   - Check if exists, return None if not

3. **`get_basis_for_element(basis_name: str, element: int) -> dict | None`**
   - Fetch basis set data for specific element
   - Return None if not available (no exceptions)

4. **`calculate_orbital_wavefunction(basis_data: dict, orbital_type: str, grid_points: int) -> dict | None`**
   - Calculate 3D orbital
   - Return {'X': array, 'Y': array, 'Z': array, 'psi': array}

5. **`analyze_basis_set(basis_data: dict) -> dict`**
   - Return analysis: zeta level, shell count, etc.

### **Frontend: `pages/1_📦_Basis_Sets.py`**

- Move all UI code here
- Keep only UI logic
- Call functions from `modules/basis_sets.py`

#### **Tasks:**
- [ ] Extract logic from existing app
- [ ] Create `modules/basis_sets.py`
- [ ] Create `pages/1_📦_Basis_Sets.py`
- [ ] Update imports
- [ ] Test refactored code

---

## 📋 **PHASE 5: SHARED UTILITIES**

### **`utils/constants.py`**

```python
# Physical constants
BOHR_TO_ANGSTROM = 0.529177
HARTREE_TO_EV = 27.2114

# Element data
ELEMENTS = {1: 'H', 2: 'He', ...}
ELEMENT_NAMES = {1: 'Hydrogen', ...}
ATOMIC_NUMBERS = {'H': 1, 'He': 2, ...}

# Functional categories
FUNCTIONAL_TYPES = {
    'LDA': ['SVWN', 'VWN', 'PZ'],
    'GGA': ['PBE', 'PW91', 'BLYP', 'B88'],
    'Hybrid': ['B3LYP', 'PBE0', 'HSE06']
}
```

### **`utils/plotting.py`**

```python
def get_plot_theme() -> dict:
    """Return consistent Plotly theme"""
    
def create_comparison_plot(data1, data2, labels) -> go.Figure:
    """Standard comparison plot"""
    
def add_educational_annotation(fig, text, position) -> go.Figure:
    """Add teaching annotations"""
```

### **`utils/validators.py`**

```python
def validate_element(element: int | str) -> int | None:
    """Validate element input, return Z or None"""
    
def validate_basis_set(basis_name: str) -> str | None:
    """Check if basis set exists"""
    
def validate_functional(functional: str) -> str | None:
    """Check if functional is supported"""
```

#### **Tasks:**
- [ ] Create `utils/constants.py`
- [ ] Create `utils/plotting.py`
- [ ] Create `utils/validators.py`
- [ ] Document all utility functions

---

## 📋 **PHASE 6: MAIN APP & NAVIGATION**

### **`app.py` - Landing Page**

#### **Features:**
1. **Hero Section**
   - Title: "DFT Flight Simulator"
   - Subtitle: "Learn Density Functional Theory Visually"
   - Quick start guide

2. **Navigation Cards**
   - Card 1: Basis Sets (The Input)
   - Card 2: Pseudopotentials (The Core)
   - Card 3: XC Functionals (The Engine)

3. **Learning Path**
   - Suggested order for students
   - Prerequisites for each module

4. **Resources**
   - Links to papers, videos
   - Glossary of terms

#### **Tasks:**
- [ ] Create landing page
- [ ] Add navigation
- [ ] Create learning path guide
- [ ] Add resources section

---

## 📋 **PHASE 7: INTEGRATION & CROSS-MODULE FEATURES**

### **Consistency Checker**

When student selects:
- Element: Carbon
- Basis: 6-31G*
- Pseudo: PBE (stringent)
- Functional: LDA

**Warning:** "⚠️ Pseudopotential uses PBE but functional is LDA. Inconsistent!"

### **Unified Workflow**

Student can:
1. Start in Basis Sets → Pick element
2. Navigate to Pseudopotentials → Auto-select same element
3. Navigate to XC Functionals → Auto-select compatible functional

### **Tasks:**
- [ ] Implement session state sharing
- [ ] Create consistency checker
- [ ] Add cross-module navigation
- [ ] Implement auto-selection

---

## 📋 **PHASE 8: TESTING & DOCUMENTATION**

### **Testing Strategy:**
- Unit tests for all calculation functions
- Integration tests for data fetching
- UI tests for each page
- Performance tests for 3D rendering

### **Documentation:**
- Docstrings for every function
- README with installation instructions
- Tutorial for students
- Developer guide for contributors

### **Tasks:**
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create user documentation
- [ ] Create developer documentation

---

## 🎯 **IMPLEMENTATION ORDER (Priority)**

### **Sprint 1: Foundation (Week 1)**
1. Create directory structure
2. Refactor existing basis set code
3. Create utility modules
4. Set up testing framework

### **Sprint 2: Pseudopotentials (Week 2)**
5. Implement pseudopotential backend
6. Create caching system
7. Build pseudopotential UI
8. Add educational content

### **Sprint 3: XC Functionals (Week 3)**
9. Implement enhancement factor calculations
10. Integrate PySCF for atom calculations
11. Build XC functionals UI (both sub-tabs)
12. Add educational content

### **Sprint 4: Integration (Week 4)**
13. Create main landing page
14. Implement cross-module features
15. Add consistency checker
16. Polish UI/UX

### **Sprint 5: Testing & Launch (Week 5)**
17. Comprehensive testing
18. Documentation
19. Performance optimization
20. Deploy & release

---

## 📊 **SUCCESS METRICS**

- ✅ Zero errors in production
- ✅ 100% modular code (each function reusable)
- ✅ No try/except blocks (use validators)
- ✅ <2s load time for any visualization
- ✅ Works for all elements H-Ar (at minimum)
- ✅ Educational content for every concept
- ✅ Consistent UI/UX across all modules

---

## 🔧 **TECHNICAL STACK**

### **Core:**
- Python 3.10+
- Streamlit (multi-page app)
- NumPy, SciPy

### **DFT Calculations:**
- PySCF (atom calculations, XC potentials)
- basis-set-exchange (basis sets)

### **Data Fetching:**
- requests (HTTP)
- xml.etree.ElementTree (UPF parsing)

### **Visualization:**
- Plotly (interactive plots)
- Matplotlib (fallback)

### **Testing:**
- pytest
- pytest-cov (coverage)

---

## 📝 **NOTES**

### **No try/except Policy:**
All functions return `None` on failure. Calling code checks:
```python
result = fetch_data(...)
if result is None:
    st.error("Failed to fetch data")
    return
```

### **Caching Strategy:**
- Use `@st.cache_data` for expensive computations
- Store downloaded pseudopotentials locally
- Cache PySCF calculations

### **Educational Focus:**
Every visualization must answer: "What does this teach the student?"

---

## 🚀 **READY TO START?**

This plan is extensive, modular, and production-ready. Each phase builds on the previous one, ensuring zero errors and maximum reusability.

**Next Step:** Create detailed task list for Sprint 1 and begin implementation.
