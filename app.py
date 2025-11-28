"""
DFT Flight Simulator - Main Landing Page

A comprehensive interactive learning platform for Density Functional Theory.
"""

import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="DFT Flight Simulator",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding: 1rem 0;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.3rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .module-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
    }
    .module-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .module-desc {
        font-size: 1.1rem;
        opacity: 0.95;
        line-height: 1.6;
    }
    .feature-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .stat-box {
        background: white;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #667eea;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">⚛️ DFT Flight Simulator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interactive Visual Learning Platform for Density Functional Theory</p>', unsafe_allow_html=True)

# Introduction
st.markdown("""
Welcome to the **DFT Flight Simulator** – your comprehensive toolkit for understanding 
the three pillars of DFT calculations through interactive visualizations!
""")

st.markdown("---")

# Three Modules Section
st.markdown("## 🎯 Three Interactive Modules")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">📦 The Input</div>
        <div class="module-title" style="font-size: 1.5rem;">Basis Sets</div>
        <div class="module-desc">
            Explore where electrons live! Visualize atomic orbitals in 3D, 
            compare different basis sets, and understand zeta levels.
            <br><br>
            <b>Features:</b><br>
            • 748 basis sets<br>
            • 3D orbital visualization<br>
            • Comparison mode<br>
            • Shell analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">⚛️ The Core</div>
        <div class="module-title" style="font-size: 1.5rem;">Pseudopotentials</div>
        <div class="module-desc">
            See how we simplify the nucleus! Compare Coulomb potential with 
            pseudopotentials, understand core vs valence regions.
            <br><br>
            <b>Features:</b><br>
            • 432 pseudopotentials<br>
            • Standard vs Stringent<br>
            • Visual comparison<br>
            • Core radius analysis
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="module-card">
        <div class="module-title">🔧 The Engine</div>
        <div class="module-title" style="font-size: 1.5rem;">XC Functionals</div>
        <div class="module-desc">
            Understand how functionals work! Explore Jacob's Ladder, compare 
            enhancement factors, see real-space effects.
            <br><br>
            <b>Features:</b><br>
            • 18+ functionals<br>
            • Enhancement factors<br>
            • Jacob's Ladder<br>
            • Functional comparison
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Statistics
st.markdown("## 📊 Platform Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">748</div>
        <div class="stat-label">Basis Sets</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">432</div>
        <div class="stat-label">Pseudopotentials</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">18+</div>
        <div class="stat-label">XC Functionals</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="stat-box">
        <div class="stat-number">86</div>
        <div class="stat-label">Elements (H-Rn)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Learning Path
st.markdown("## 🎓 Suggested Learning Path")

st.markdown("""
<div class="feature-box">
    <h3>👉 For Students New to DFT:</h3>
    <ol>
        <li><b>Start with Basis Sets</b> – Understand where electrons are and how we represent them</li>
        <li><b>Move to Pseudopotentials</b> – Learn how we simplify the problem for efficiency</li>
        <li><b>Explore XC Functionals</b> – Discover how different approximations affect accuracy</li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="feature-box">
    <h3>👉 For Researchers:</h3>
    <ul>
        <li><b>Compare basis sets</b> for your system to find the best accuracy/cost balance</li>
        <li><b>Check pseudopotential consistency</b> with your chosen functional</li>
        <li><b>Visualize functional differences</b> to understand their behavior</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Key Features
st.markdown("## ✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🎨 Interactive Visualizations
    - **3D Orbital Rendering** – Rotate and explore orbitals
    - **Comparison Plots** – Side-by-side analysis
    - **Real-time Updates** – Instant feedback
    - **Educational Annotations** – Learn as you explore
    """)
    
    st.markdown("""
    ### 📚 Comprehensive Database
    - **748 Basis Sets** from basis-set-exchange
    - **432 Pseudopotentials** from PseudoDojo
    - **18+ XC Functionals** with full metadata
    - **86 Elements** supported (H to Rn)
    """)

with col2:
    st.markdown("""
    ### 🔬 Advanced Features
    - **Comparison Mode** – Compare any two sets
    - **Consistency Checker** – Ensure compatible choices
    - **Cross-Module Navigation** – Seamless workflow
    - **Caching System** – Fast performance
    """)
    
    st.markdown("""
    ### 🎯 Educational Focus
    - **Detailed Explanations** – Understand every concept
    - **Use Case Recommendations** – Know when to use what
    - **Jacob's Ladder** – Climb the accuracy ladder
    - **Best Practices** – Learn from experts
    """)

st.markdown("---")

# Quick Start
st.markdown("## 🚀 Quick Start")

st.info("""
**👈 Use the sidebar** to navigate between modules:
- 📦 **Basis Sets** – Start here to explore atomic orbitals
- ⚛️ **Pseudopotentials** – Understand core simplification
- 🔧 **XC Functionals** – Compare functional performance

Each module is independent but works together for a complete DFT understanding!
""")

st.markdown("---")

# Footer
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem 0;">
    <p><b>DFT Flight Simulator</b> – Making Density Functional Theory Visual and Accessible</p>
    <p style="font-size: 0.9rem;">Built with ❤️ using Streamlit, Plotly, and basis-set-exchange</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    st.info("""
    Select a module from the sidebar to begin your DFT journey!
    
    **Recommended order:**
    1. Basis Sets
    2. Pseudopotentials  
    3. XC Functionals
    """)
    
    st.markdown("---")
    
    st.markdown("### 📖 Resources")
    st.markdown("""
    - [Basis Set Exchange](https://www.basissetexchange.org/)
    - [PseudoDojo](http://www.pseudo-dojo.org/)
    - [Libxc](https://www.tddft.org/programs/libxc/)
    """)
    
    st.markdown("---")
    
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Version:** 2.0.0  
    **Status:** Production Ready  
    **Modules:** 3/3 Complete
    """)
