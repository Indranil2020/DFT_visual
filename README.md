# ⚛️ Basis Set Visualizer

Interactive learning tool for quantum chemistry basis sets with 3D visualization and educational comparisons.

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
```bash
streamlit run basis_visualizer_app.py
```

Open http://localhost:8501 in your browser.

## ✨ Features

### 🎯 Fast Local Access
- All basis set metadata cached locally
- No waiting for network requests
- Instant loading and switching

### 🧪 Interactive Periodic Table
- Click any element to explore
- Visual highlighting of available elements
- Organized by family (Pople, Dunning, etc.)

### 🌌 3D Orbital Visualization
- Interactive 3D isosurfaces
- Rotate, zoom, pan
- s, p, d orbital types

### 🔬 Comparison Mode
- Compare two basis sets side-by-side
- Visual orbital differences
- Educational explanations of technical terms

### 📚 Educational Content
- Explains Zeta (ζ): Single, Double, Triple
- Primitives vs Contractions
- Polarization functions
- Computational cost trade-offs

### 📥 Export to Any Software
- Gaussian, ORCA, NWChem, PySCF, Psi4, GAMESS-US
- One-click download
- Properly formatted for each tool

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
