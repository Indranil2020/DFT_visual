# DFT Flight Simulator - Detailed Task List

## ✅ **SPRINT 1: FOUNDATION** (Days 1-7)

### **Day 1: Directory Structure & Setup**

- [ ] **Task 1.1:** Create new directory structure
  ```bash
  mkdir -p modules pages utils data/pseudo_cache
  touch modules/__init__.py utils/__init__.py
  ```

- [ ] **Task 1.2:** Update `requirements.txt`
  ```
  streamlit>=1.28.0
  numpy>=1.24.0
  scipy>=1.10.0
  plotly>=5.17.0
  basis-set-exchange>=0.9.0
  pyscf>=2.3.0
  requests>=2.31.0
  pytest>=7.4.0
  pytest-cov>=4.1.0
  ```

- [ ] **Task 1.3:** Create `.gitignore` updates
  ```
  data/pseudo_cache/
  __pycache__/
  *.pyc
  .pytest_cache/
  ```

### **Day 2: Utility Modules**

- [ ] **Task 2.1:** Create `utils/constants.py`
  - Physical constants (BOHR_TO_ANGSTROM, HARTREE_TO_EV)
  - Element dictionaries (ELEMENTS, ELEMENT_NAMES, ATOMIC_NUMBERS)
  - Functional categories (FUNCTIONAL_TYPES)
  - Periodic table layout (PERIODIC_TABLE)

- [ ] **Task 2.2:** Create `utils/validators.py`
  - `validate_element(element) -> int | None`
  - `validate_basis_set(basis_name) -> str | None`
  - `validate_functional(functional) -> str | None`
  - `validate_url_response(response) -> bool`

- [ ] **Task 2.3:** Create `utils/plotting.py`
  - `get_plot_theme() -> dict`
  - `create_comparison_plot(data1, data2, labels) -> go.Figure`
  - `add_educational_annotation(fig, text, position) -> go.Figure`
  - `create_3d_orbital_plot(X, Y, Z, psi) -> go.Figure`

### **Day 3-4: Refactor Basis Sets Module**

- [ ] **Task 3.1:** Create `modules/basis_sets.py` - Part 1 (Data)
  - `load_basis_cache() -> dict`
  - `get_available_basis_sets() -> list[str]`
  - `get_basis_metadata(basis_name) -> dict | None`
  - `get_basis_for_element(basis_name, element) -> dict | None`

- [ ] **Task 3.2:** Create `modules/basis_sets.py` - Part 2 (Analysis)
  - `analyze_basis_set(basis_data) -> dict`
  - `count_shells_by_type(basis_data) -> dict`
  - `get_exponent_range(shell) -> tuple[float, float]`
  - `determine_zeta_level(basis_name, shell_count) -> str`

- [ ] **Task 3.3:** Create `modules/basis_sets.py` - Part 3 (Visualization)
  - `calculate_orbital_wavefunction(basis_data, orbital_type, grid_points) -> dict | None`
  - `calculate_radial_wavefunction(basis_data, orbital_type, r_points) -> dict | None`
  - `get_orbital_metadata(basis_data, orbital_type) -> dict | None`

- [ ] **Task 3.4:** Create `pages/1_📦_Basis_Sets.py`
  - Extract all UI code from current `basis_visualizer_app.py`
  - Import functions from `modules/basis_sets.py`
  - Keep only Streamlit UI logic
  - Maintain all existing features

### **Day 5: Testing Framework**

- [ ] **Task 5.1:** Create `tests/` directory structure
  ```bash
  mkdir -p tests/unit tests/integration
  touch tests/__init__.py tests/conftest.py
  ```

- [ ] **Task 5.2:** Create `tests/unit/test_validators.py`
  - Test `validate_element()` with valid/invalid inputs
  - Test `validate_basis_set()` with existing/non-existing sets
  - Test `validate_functional()` with supported/unsupported functionals

- [ ] **Task 5.3:** Create `tests/unit/test_basis_sets.py`
  - Test `get_basis_for_element()` returns correct data
  - Test `analyze_basis_set()` returns correct analysis
  - Test `calculate_orbital_wavefunction()` with known inputs

- [ ] **Task 5.4:** Set up pytest configuration
  - Create `pytest.ini`
  - Configure coverage reporting
  - Set up test fixtures in `conftest.py`

### **Day 6-7: Main App Structure**

- [ ] **Task 6.1:** Create `app.py` - Landing Page
  - Hero section with title and description
  - Navigation cards for 3 modules
  - Learning path guide
  - Quick start instructions

- [ ] **Task 6.2:** Configure Streamlit multi-page
  - Create `.streamlit/config.toml`
  - Set page layout, theme
  - Configure sidebar navigation

- [ ] **Task 6.3:** Test refactored basis sets page
  - Verify all features work
  - Check 3D visualization
  - Test comparison mode
  - Verify caching works

---

## ✅ **SPRINT 2: PSEUDOPOTENTIALS MODULE** (Days 8-14)

### **Day 8: Pseudopotential Backend - Data Fetching**

- [ ] **Task 8.1:** Create `modules/pseudopotentials.py` - Part 1 (Metadata)
  - `get_available_pseudos() -> dict`
    - Return: {element: {accuracies: [...], functionals: [...]}}
  - `get_pseudo_url(element, accuracy, functional) -> str | None`
    - Construct PseudoDojo GitHub raw URL
  - `check_pseudo_exists(element, accuracy, functional) -> bool`
    - HEAD request to check availability

- [ ] **Task 8.2:** Create `modules/pseudopotentials.py` - Part 2 (Fetching)
  - `fetch_pseudo_file(element, accuracy, functional) -> str | None`
    - Download UPF file content
    - Check response status (no try/except)
    - Return content or None
  - `cache_pseudo_file(element, accuracy, functional, content) -> bool`
    - Save to `data/pseudo_cache/`
    - Return success status
  - `load_cached_pseudo(element, accuracy, functional) -> str | None`
    - Load from cache if exists
    - Return content or None

### **Day 9: Pseudopotential Backend - UPF Parsing**

- [ ] **Task 9.1:** Create `modules/pseudopotentials.py` - Part 3 (Parsing)
  - `parse_upf_header(upf_content) -> dict | None`
    - Extract: element, Z, functional, cutoff
  - `parse_upf_mesh(upf_content) -> np.ndarray | None`
    - Extract radial mesh (r grid)
  - `parse_upf_local_potential(upf_content) -> np.ndarray | None`
    - Extract V_local(r)
  - `parse_upf_file(upf_content) -> dict | None`
    - Combine all parsing
    - Return: {'header': {...}, 'r': array, 'v_local': array}

### **Day 10: Pseudopotential Backend - Calculations**

- [ ] **Task 10.1:** Create `modules/pseudopotentials.py` - Part 4 (Physics)
  - `calculate_coulomb_potential(r, Z) -> np.ndarray`
    - V_coulomb(r) = -Z/r
    - Pure function, no exceptions
  - `calculate_pseudo_difference(v_pseudo, v_coulomb) -> np.ndarray`
    - Return v_pseudo - v_coulomb
  - `find_core_radius(r, v_diff, threshold) -> float`
    - Find where pseudopotential deviates significantly
  - `get_pseudo_comparison(element, acc1, acc2, functional) -> dict | None`
    - Compare two accuracies
    - Return: {'r': array, 'v1': array, 'v2': array, 'diff': array}

### **Day 11-12: Pseudopotential Frontend**

- [ ] **Task 11.1:** Create `pages/2_⚛️_Pseudopotentials.py` - Structure
  - Page title and description
  - Educational introduction
  - Layout: Sidebar controls + Main visualization

- [ ] **Task 11.2:** Sidebar Controls
  - Element selector (reuse periodic table component)
  - Accuracy selector: Standard vs Stringent
  - Functional selector: PBE, LDA, PW91
  - "Fetch Pseudopotential" button

- [ ] **Task 11.3:** Main Visualization - Plot 1
  - Coulomb potential (dashed gray line)
  - Pseudopotential (solid red line)
  - Annotations: "Core region", "Valence region"
  - Vertical line at core radius

- [ ] **Task 11.4:** Main Visualization - Plot 2
  - Difference plot (V_pseudo - V_coulomb)
  - Highlight smoothing region
  - Show where pseudo "fixes" the singularity

- [ ] **Task 11.5:** Educational Info Boxes
  - "What is a pseudopotential?"
  - "Why do we need them?"
  - "What is the core radius?"
  - "Standard vs Stringent accuracy"

### **Day 13: Pseudopotential Features**

- [ ] **Task 13.1:** Comparison Mode
  - Allow comparing Standard vs Stringent
  - Side-by-side plots
  - Difference visualization

- [ ] **Task 13.2:** Compatibility Checker
  - Check if pseudo functional matches XC functional (from session state)
  - Show warning if mismatch
  - Suggest compatible combination

- [ ] **Task 13.3:** Metadata Display
  - Show cutoff energy recommendation
  - Display functional used to generate pseudo
  - Show reference citation

### **Day 14: Testing & Polish**

- [ ] **Task 14.1:** Create `tests/unit/test_pseudopotentials.py`
  - Test UPF parsing with sample file
  - Test Coulomb potential calculation
  - Test caching mechanism

- [ ] **Task 14.2:** Create `tests/integration/test_pseudo_fetch.py`
  - Test fetching from PseudoDojo
  - Test cache hit/miss
  - Test error handling (invalid element)

- [ ] **Task 14.3:** Polish UI
  - Add loading spinners
  - Improve plot aesthetics
  - Add helpful tooltips

---

## ✅ **SPRINT 3: XC FUNCTIONALS MODULE** (Days 15-21)

### **Day 15: XC Backend - Enhancement Factors**

- [ ] **Task 15.1:** Create `modules/xc_functionals.py` - Part 1 (Math)
  - `calculate_lda_enhancement(s) -> np.ndarray`
    - F_x^LDA = 1.0 (constant)
  - `calculate_pbe_enhancement(s) -> np.ndarray`
    - PBE formula with κ=0.804, μ=0.21951
  - `calculate_b88_enhancement(s) -> np.ndarray`
    - Becke88 formula with β=0.0042
  - `calculate_blyp_enhancement(s) -> np.ndarray`
    - BLYP combination

- [ ] **Task 15.2:** Enhancement Factor Utilities
  - `get_enhancement_comparison(functionals, s_range) -> dict`
    - Return: {functional: {'s': array, 'F': array}}
  - `get_functional_metadata(functional) -> dict`
    - Return: type, description, reference, parameters

### **Day 16-17: XC Backend - PySCF Integration**

- [ ] **Task 16.1:** Create `modules/xc_functionals.py` - Part 2 (Atoms)
  - `setup_pyscf_atom(element, basis) -> gto.Mole | None`
    - Create PySCF molecule object
    - Return None if invalid input
  - `calculate_atom_density(element, basis) -> dict | None`
    - Use dft.init_guess_by_atom
    - Return: {'r': array, 'rho': array, 'dm': matrix}

- [ ] **Task 16.2:** XC Potential Calculations
  - `calculate_xc_potential(element, functional, basis) -> dict | None`
    - Evaluate V_xc using PySCF
    - Return: {'r': array, 'v_xc': array}
  - `calculate_xc_energy(element, functional, basis) -> dict | None`
    - Calculate E_xc
    - Return: {'E_x': float, 'E_c': float, 'E_xc': float}

- [ ] **Task 16.3:** Comparison Functions
  - `get_xc_difference(element, func1, func2, basis) -> dict | None`
    - Calculate ΔV_xc = V_xc(func1) - V_xc(func2)
    - Return: {'r': array, 'delta_v': array, 'max_diff': float}
  - `get_xc_energy_difference(element, func1, func2, basis) -> dict | None`
    - Calculate ΔE_xc
    - Return: {'delta_E_x': float, 'delta_E_c': float}

### **Day 18: XC Frontend - Sub-Tab 1 (Mathematical)**

- [ ] **Task 18.1:** Create `pages/3_🔧_XC_Functionals.py` - Structure
  - Page title and description
  - Two sub-tabs: "Mathematical View" and "Real Atom View"

- [ ] **Task 18.2:** Sub-Tab 1: Jacob's Ladder
  - Checkboxes for functionals: LDA, PBE, B88, BLYP, PW91
  - Plot F_x(s) vs s for selected functionals
  - Interactive legend
  - Hover tooltips with formulas

- [ ] **Task 18.3:** Educational Content - Math
  - Explain reduced gradient s = |∇ρ|/(2k_F ρ)
  - Explain enhancement factor F_x
  - Show Jacob's Ladder diagram
  - Explain each rung (LDA → GGA → meta-GGA → Hybrid)

### **Day 19: XC Frontend - Sub-Tab 2 (Real Atoms)**

- [ ] **Task 19.1:** Sub-Tab 2: Controls
  - Element selector
  - Basis set selector
  - Functional 1 dropdown
  - Functional 2 dropdown
  - "Calculate" button

- [ ] **Task 19.2:** Sub-Tab 2: Visualizations
  - Plot 1: V_xc(r) for both functionals
  - Plot 2: ΔV_xc(r) = V_xc(func1) - V_xc(func2)
  - Annotations: Highlight shell regions
  - Show where difference is maximum

- [ ] **Task 19.3:** Educational Content - Physics
  - Explain what V_xc means physically
  - Why GGAs correct LDA at shell boundaries
  - When to use each functional
  - Computational cost comparison

### **Day 20: XC Features & Integration**

- [ ] **Task 20.1:** Functional Database
  - Create comprehensive functional info
  - Add references and citations
  - Include computational cost estimates

- [ ] **Task 20.2:** Compatibility Features
  - Link to pseudopotential page
  - Show recommended pseudo for selected functional
  - Warning if mismatch detected

- [ ] **Task 20.3:** Performance Optimization
  - Cache PySCF calculations
  - Precompute common atoms
  - Optimize grid resolution

### **Day 21: Testing**

- [ ] **Task 21.1:** Create `tests/unit/test_xc_functionals.py`
  - Test enhancement factor calculations
  - Test PySCF integration
  - Test difference calculations

- [ ] **Task 21.2:** Create `tests/integration/test_xc_full.py`
  - Test full workflow: element → density → V_xc
  - Test comparison mode
  - Test caching

---

## ✅ **SPRINT 4: INTEGRATION & POLISH** (Days 22-28)

### **Day 22-23: Cross-Module Integration**

- [ ] **Task 22.1:** Session State Management
  - Create `utils/session.py`
  - `init_session_state() -> None`
  - `update_element_selection(element) -> None`
  - `get_current_selections() -> dict`

- [ ] **Task 22.2:** Cross-Module Navigation
  - Add "Go to Pseudopotentials" button in Basis Sets
  - Add "Go to XC Functionals" button in Pseudopotentials
  - Auto-populate element when navigating

- [ ] **Task 22.3:** Consistency Checker
  - `check_consistency(basis, pseudo_func, xc_func) -> dict`
    - Return: {'consistent': bool, 'warnings': list, 'suggestions': list}
  - Display warnings in sidebar
  - Highlight inconsistencies

### **Day 24: Landing Page Enhancement**

- [ ] **Task 24.1:** Improve `app.py`
  - Add hero image/diagram
  - Create interactive learning path
  - Add "Quick Tour" button

- [ ] **Task 24.2:** Resources Section
  - Link to relevant papers
  - Embed educational videos
  - Glossary of terms
  - FAQ section

- [ ] **Task 24.3:** Progress Tracking
  - Show which modules student has explored
  - Suggest next steps
  - Achievement badges (optional, fun)

### **Day 25-26: UI/UX Polish**

- [ ] **Task 25.1:** Consistent Styling
  - Apply theme across all pages
  - Consistent color scheme
  - Uniform button styles
  - Standardized plot layouts

- [ ] **Task 25.2:** Responsive Design
  - Test on different screen sizes
  - Optimize for tablets
  - Ensure plots are readable

- [ ] **Task 25.3:** Accessibility
  - Add alt text for images
  - Ensure good color contrast
  - Keyboard navigation support

- [ ] **Task 25.4:** Performance
  - Optimize caching
  - Reduce initial load time
  - Lazy load heavy components

### **Day 27: Documentation**

- [ ] **Task 27.1:** User Documentation
  - Create `docs/USER_GUIDE.md`
  - Installation instructions
  - Tutorial for each module
  - Troubleshooting section

- [ ] **Task 27.2:** Developer Documentation
  - Create `docs/DEVELOPER_GUIDE.md`
  - Architecture overview
  - API documentation
  - Contributing guidelines

- [ ] **Task 27.3:** Code Documentation
  - Ensure all functions have docstrings
  - Add type hints everywhere
  - Create API reference

### **Day 28: Final Testing & Deployment**

- [ ] **Task 28.1:** Comprehensive Testing
  - Run full test suite
  - Manual testing of all features
  - Cross-browser testing
  - Performance testing

- [ ] **Task 28.2:** Deployment Preparation
  - Create deployment checklist
  - Set up environment variables
  - Prepare production config

- [ ] **Task 28.3:** Release
  - Tag version 2.0.0
  - Create release notes
  - Deploy to production
  - Announce to users

---

## 📊 **PROGRESS TRACKING**

### **Sprint 1: Foundation**
- [ ] 0/20 tasks completed
- [ ] Estimated: 7 days
- [ ] Status: Not started

### **Sprint 2: Pseudopotentials**
- [ ] 0/25 tasks completed
- [ ] Estimated: 7 days
- [ ] Status: Not started

### **Sprint 3: XC Functionals**
- [ ] 0/22 tasks completed
- [ ] Estimated: 7 days
- [ ] Status: Not started

### **Sprint 4: Integration**
- [ ] 0/18 tasks completed
- [ ] Estimated: 7 days
- [ ] Status: Not started

### **Total Progress**
- [ ] 0/85 tasks completed (0%)
- [ ] Estimated: 28 days
- [ ] Status: Ready to begin

---

## 🎯 **NEXT IMMEDIATE STEPS**

1. Review and approve this task list
2. Begin Task 1.1: Create directory structure
3. Set up development environment
4. Start Sprint 1, Day 1

**Ready to start implementation?** 🚀
