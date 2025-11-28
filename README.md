# ⚛️ DFT Flight Simulator

**Complete Interactive Learning Platform for Density Functional Theory**

Explore the three pillars of DFT calculations: Basis Sets, Pseudopotentials, and XC Functionals through stunning visualizations and comprehensive comparisons.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Basis Set Cache (One-time, ~2-3 minutes)
```bash
python3 download_basis_cache.py
```

This downloads metadata for 500+ basis sets locally for fast access.

### 3. Run the App

**New Multi-Page App (Recommended):**
```bash
streamlit run app.py
```

**Legacy Single-Page App:**
```bash
streamlit run basis_visualizer_app.py
```

Open http://localhost:8501 in your browser.

## ✨ Features

### 📦 Module 1: Basis Sets
- **748 basis sets** from basis-set-exchange
- **3D orbital visualization** with interactive rotation
- **Comparison mode** for side-by-side analysis
- **Shell analysis** and zeta level determination
- **Export to any software** (Gaussian, ORCA, PySCF, etc.)

### ⚛️ Module 2: Pseudopotentials
- **432 pseudopotentials** from PseudoDojo
- **3 functionals:** PBE, LDA, PW
- **2 accuracies:** Standard (soft) and Stringent (hard)
- **Visual comparison** of Coulomb vs Pseudopotential
- **Core radius analysis** and smoothing visualization

### 🔧 Module 3: XC Functionals
- **18+ functionals** (LDA, GGA, Hybrid, meta-GGA)
- **Jacob's Ladder** visualization
- **Enhancement factor plots** for mathematical understanding
- **Functional comparison** with difference analysis
- **Use case recommendations** for each functional

### 🎯 Cross-Module Features
- **Consistency checker** – Ensures compatible selections
- **Session state** – Selections persist across modules
- **Educational content** – Learn as you explore
- **Fast caching** – Optimized performance

## 🎓 Learning Features

The app helps you understand:

- **What is a basis set?** Mathematical functions describing electron orbitals
- **Single vs Double vs Triple-ζ:** More functions = more accuracy but slower
- **Polarization:** d and f functions for better bonding description
- **STO vs GTO:** Slater vs Gaussian type orbitals
- **Why some are expensive:** More primitives = more calculations

## 🔄 Updating Cache

The cache shows its age in the sidebar. To update:

```bash
python3 download_basis_cache.py
```

Recommended: Update monthly to get new basis sets.

## 📁 Project Structure

```
DFT_TOOLS/
├── basis_visualizer_app.py      # Main application
├── download_basis_cache.py      # Cache downloader
├── basis_cache/                 # Local cache directory
│   └── metadata.json           # Cached basis set info
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🐛 Troubleshooting

**"Cache not found" error:**
```bash
python3 download_basis_cache.py
```

**App is slow:**
- Make sure cache is downloaded
- Reduce grid points in visualization (edit line 177)

**Element not available:**
- Some basis sets don't support all elements
- Try a different basis set (e.g., STO-3G, 6-31G)

## 💡 Tips

1. Start with simple basis sets (STO-3G, 3-21G) to understand concepts
2. Use comparison mode to see differences between similar basis sets
3. Read the educational tooltips (? icons)
4. Export basis sets for your quantum chemistry calculations

## 🎯 Best Basis Sets to Start With

- **STO-3G:** Minimal, fast, educational
- **6-31G:** Classic double-zeta
- **6-31G*:** With polarization
- **cc-pVDZ:** Correlation-consistent double-zeta
- **cc-pVTZ:** Triple-zeta, more accurate

## 📊 Technical Details

- Built with Streamlit + Plotly
- Uses Basis Set Exchange (BSE) library
- 3D visualization with isosurfaces
- Gaussian-type orbital (GTO) rendering

## 🙏 Credits

- **Basis Set Exchange:** https://www.basissetexchange.org/
- Data from the MolSSI BSE project

---

Made for learning quantum chemistry! 🧪✨
