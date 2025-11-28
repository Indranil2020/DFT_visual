"""
Basis Sets Module - DFT Flight Simulator
Interactive visualization and comparison of quantum chemistry basis sets.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# Import our modules
from modules.basis_sets import (
    get_available_basis_sets,
    get_basis_for_element,
    get_available_elements_for_basis,
    analyze_basis_set,
    calculate_orbital_wavefunction,
    count_shells_by_type
)
from utils.constants import ELEMENTS
from utils.plotting import create_3d_orbital_plot, create_shell_visualization
from utils.session import init_session_state, show_consistency_checker, show_current_selections
from comparison_utils import create_comparison_table, display_comparison_table

# Helper function for basis type detection
def detect_basis_type(name):
    """Detect basis set type and return description"""
    name_upper = name.upper()
    if 'STO' in name_upper:
        return 'STO', 'Slater-Type Orbitals'
    elif 'CC-P' in name_upper or 'AUG-CC' in name_upper:
        return 'Correlation-Consistent', 'Dunning Correlation-Consistent'
    elif any(x in name_upper for x in ['POPLE', '6-31', '6-311', '3-21', '4-31']):
        return 'Pople', 'Pople Split-Valence'
    elif 'DEF2' in name_upper:
        return 'Def2', 'Karlsruhe Def2'
    elif 'ANO' in name_upper:
        return 'ANO', 'Atomic Natural Orbitals'
    elif any(x in name_upper for x in ['LANL', 'ECP']):
        return 'ECP', 'Effective Core Potential'
    else:
        return 'GTO', 'Gaussian-Type Orbitals'

# Page configuration
st.set_page_config(
    page_title="Basis Sets - DFT Flight Simulator",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .metric-card {
        background: white;
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.3rem;
    }
    .element-button {
        width: 100%;
        padding: 0.5rem;
        margin: 0.2rem 0;
        border-radius: 6px;
        border: 2px solid #667eea;
        background: white;
        color: #667eea;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }
    .element-button:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">📦 Basis Sets: The Input</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Where Electrons Live - Explore Atomic Orbitals in 3D</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📦 Basis Set Controls")
    
    # Mode selection
    mode = st.radio(
        "**Mode:**",
        ["Single Basis Set", "Comparison Mode"],
        help="Choose to explore one basis set or compare two"
    )
    
    st.markdown("---")
    
    # Element selection - PERIODIC TABLE
    st.markdown("### Select Element")
    
    current_element = st.session_state.selected_element
    element_symbol = ELEMENTS.get(current_element, 'C')
    
    st.info(f"**Selected:** {element_symbol} (Z={current_element})")
    
    st.markdown("---")
    
    # Basis set selection
    st.markdown("### Select Basis Set")
    
    # Get available basis sets
    all_basis_sets = get_available_basis_sets()
    
    # Categorize basis sets
    pople_sets = [b for b in all_basis_sets if any(x in b for x in ['STO', '3-21G', '6-31G', '6-311G'])]
    dunning_sets = [b for b in all_basis_sets if 'cc-p' in b.lower()]
    ahlrichs_sets = [b for b in all_basis_sets if 'def2' in b.lower()]
    
    basis_category = st.selectbox(
        "**Basis Set Family:**",
        ["All", "Pople (STO-3G, 6-31G, etc.)", "Dunning (cc-pVXZ)", "Ahlrichs (def2)", "Other"],
        help="Filter basis sets by family"
    )
    
    # Filter basis sets
    if basis_category == "Pople (STO-3G, 6-31G, etc.)":
        filtered_sets = pople_sets
    elif basis_category == "Dunning (cc-pVXZ)":
        filtered_sets = dunning_sets
    elif basis_category == "Ahlrichs (def2)":
        filtered_sets = ahlrichs_sets
    elif basis_category == "Other":
        filtered_sets = [b for b in all_basis_sets if b not in pople_sets + dunning_sets + ahlrichs_sets]
    else:
        filtered_sets = all_basis_sets
    
    if mode == "Single Basis Set":
        basis_name = st.selectbox(
            "**Choose Basis Set:**",
            options=filtered_sets,
            index=filtered_sets.index('6-31G') if '6-31G' in filtered_sets else 0
        )
        st.session_state.selected_basis = basis_name
    else:
        basis_name_1 = st.selectbox(
            "**First Basis Set:**",
            options=filtered_sets,
            index=filtered_sets.index('6-31G') if '6-31G' in filtered_sets else 0,
            key="basis1"
        )
        basis_name_2 = st.selectbox(
            "**Second Basis Set:**",
            options=filtered_sets,
            index=filtered_sets.index('6-311G') if '6-311G' in filtered_sets else min(1, len(filtered_sets)-1),
            key="basis2"
        )
    
    # Show current selections
    show_current_selections()
    
    # Show consistency checker
    show_consistency_checker()

# Periodic Table for Element Selection
PERIODIC_TABLE = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10],
    [11, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
    [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
    [55, 56, 57, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
]

st.markdown("## 🔬 Select Element from Periodic Table")

# Get available elements for selected basis set(s)
if mode == "Single Basis Set":
    available_elements = get_available_elements_for_basis(basis_name)
    st.info(f"🎯 **{basis_name}** is available for **{len(available_elements)}** elements (highlighted in green below)")
else:
    available_elements_1 = get_available_elements_for_basis(basis_name_1)
    available_elements_2 = get_available_elements_for_basis(basis_name_2)
    available_elements = list(set(available_elements_1) & set(available_elements_2))
    st.info(f"🎯 Both basis sets available for **{len(available_elements)}** elements (highlighted in green)")

# Custom CSS for element highlighting
st.markdown("""
<style>
    .element-available {
        background-color: #90EE90 !important;
        border: 2px solid #228B22 !important;
    }
    .element-unavailable {
        opacity: 0.4 !important;
    }
</style>
""", unsafe_allow_html=True)

# Pre-compute basis set families for quick lookup (cache in session state)
if 'element_families_cache' not in st.session_state:
    st.session_state.element_families_cache = {}

def get_basis_families_for_element(z):
    """Get which basis set families are available for an element"""
    if z in st.session_state.element_families_cache:
        return st.session_state.element_families_cache[z]
    
    families = {
        'Pople': [],
        'Dunning': [],
        'Ahlrichs': [],
        'ECP': [],
        'ANO': [],
        'Jensen': [],
        'Karlsruhe': []
    }
    
    # Sample representative basis sets from each family
    test_sets = {
        'Pople': ['STO-3G', '3-21G', '6-31G', '6-311G'],
        'Dunning': ['cc-pVDZ', 'cc-pVTZ', 'aug-cc-pVDZ'],
        'Ahlrichs': ['def2-SVP', 'def2-TZVP', 'def2-QZVP'],
        'ECP': ['LANL2DZ', 'SDD', 'CRENBL'],
        'ANO': ['ANO-RCC', 'ANO-VDZ'],
        'Jensen': ['pc-1', 'pc-2', 'aug-pc-1'],
        'Karlsruhe': ['def-SV(P)', 'def-TZVP']
    }
    
    for family, basis_list in test_sets.items():
        for bs in basis_list:
            try:
                if bs in all_basis_sets:
                    data = get_basis_for_element(bs, z)
                    if data is not None:
                        families[family].append(bs)
                        break  # Found one, move to next family
            except:
                continue
    
    # Create summary
    available_families = [f for f, bsets in families.items() if bsets]
    st.session_state.element_families_cache[z] = available_families
    return available_families

with st.expander("📊 Periodic Table (Click to select element)", expanded=True):
    for row in PERIODIC_TABLE:
        cols = st.columns(18)
        for col_idx, z in enumerate(row):
            with cols[col_idx]:
                if z > 0:
                    symbol = ELEMENTS.get(z, '')
                    is_available = z in available_elements
                    is_selected = st.session_state.selected_element == z
                    
                    # Get available basis families for this element
                    families = get_basis_families_for_element(z)
                    
                    # Format families in column (one per line)
                    if families:
                        family_list = '\n'.join(f"  - {f}" for f in families)
                        family_text = f"Available families:\n{family_list}"
                    else:
                        family_text = "No families available"
                    
                    # Determine button type and help text
                    if is_selected:
                        btn_type = "primary"
                        help_text = f"{symbol} (Z={z}) - SELECTED\n{family_text}"
                    elif is_available:
                        btn_type = "secondary"
                        help_text = f"{symbol} (Z={z})\n{family_text}"
                    else:
                        btn_type = "secondary"
                        help_text = f"{symbol} (Z={z})\n{family_text}"
                    
                    if st.button(
                        f"**{symbol}**\n{z}",
                        key=f"elem_{z}",
                        use_container_width=True,
                        type=btn_type,
                        help=help_text,
                        disabled=not is_available
                    ):
                        st.session_state.selected_element = z
                        st.rerun()

st.markdown("---")

# Show available basis sets for selected element
if current_element:
    with st.expander(f"Available Basis Sets for {element_symbol} (Z={current_element})", expanded=False):
        # Check all basis sets
        available_for_element = []
        for bs in all_basis_sets:
            try:
                test_data = get_basis_for_element(bs, current_element)
                if test_data is not None:
                    available_for_element.append(bs)
            except:
                pass
        
        if available_for_element:
            st.success(f"Found **{len(available_for_element)}** basis sets available for **{element_symbol}**")
            
            # Categorize them
            pople = [b for b in available_for_element if any(x in b for x in ['STO', '3-21G', '6-31G', '6-311G'])]
            dunning = [b for b in available_for_element if 'cc-p' in b.lower()]
            ahlrichs = [b for b in available_for_element if 'def2' in b.lower()]
            other = [b for b in available_for_element if b not in pople + dunning + ahlrichs]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if pople:
                    st.markdown("**Pople:**")
                    for bs in pople[:10]:
                        st.markdown(f"- {bs}")
                    if len(pople) > 10:
                        st.caption(f"...and {len(pople)-10} more")
            
            with col2:
                if dunning:
                    st.markdown("**Dunning:**")
                    for bs in dunning[:10]:
                        st.markdown(f"- {bs}")
                    if len(dunning) > 10:
                        st.caption(f"...and {len(dunning)-10} more")
            
            with col3:
                if ahlrichs:
                    st.markdown("**Ahlrichs:**")
                    for bs in ahlrichs[:10]:
                        st.markdown(f"- {bs}")
                    if len(ahlrichs) > 10:
                        st.caption(f"...and {len(ahlrichs)-10} more")
            
            with col4:
                if other:
                    st.markdown("**Other:**")
                    for bs in other[:10]:
                        st.markdown(f"- {bs}")
                    if len(other) > 10:
                        st.caption(f"...and {len(other)-10} more")
        else:
            st.warning(f"⚠️ No basis sets found for **{element_symbol}**")

st.markdown("---")

# Main content
if mode == "Single Basis Set":
    # ==================== SINGLE BASIS SET MODE ====================
    
    # Fetch basis set data
    basis_data = get_basis_for_element(basis_name, current_element)
    
    if basis_data is None:
        st.error(f"❌ Basis set **{basis_name}** is not available for **{element_symbol}**")
        st.info("💡 Try a different basis set or element. Common basis sets like STO-3G and 6-31G work for most elements.")
        st.stop()
    
    # Analyze basis set
    analysis = analyze_basis_set(basis_data, basis_name)
    
    # Display overview
    st.markdown(f"## 📊 Overview: {basis_name} for {element_symbol}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analysis['total_shells']}</div>
            <div class="metric-label">Total Shells</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analysis['zeta'][:10]}</div>
            <div class="metric-label">Zeta Level</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        pol_status = "✓ Yes" if analysis['has_polarization'] else "✗ No"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{pol_status}</div>
            <div class="metric-label">Polarization</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        diff_status = "✓ Yes" if analysis['has_diffuse'] else "✗ No"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{diff_status}</div>
            <div class="metric-label">Diffuse</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Educational explanation
    st.markdown("### 📚 What This Means")
    st.markdown(f"""
    <div class="info-card">
        {analysis['explanation']}
    </div>
    """, unsafe_allow_html=True)
    
    # Shell composition
    st.markdown("### 🎯 Shell Composition")
    
    shell_counts = analysis['shell_counts']
    fig_shells = create_shell_visualization(shell_counts, f"Orbital Shells in {basis_name}")
    st.plotly_chart(fig_shells, use_container_width=True)
    
    # Mathematical Foundation with Radial Plots
    with st.expander(f"Mathematical Foundation: {basis_name}", expanded=True):
        basis_type, desc = detect_basis_type(basis_name)
        
        st.markdown(f"""
        ### Mathematical Functions in {basis_name}
        
        **Type:** {desc}
        """)
        
        if basis_type == 'STO':
            st.latex(r"\psi_{STO}(r) = N \cdot r^{n-1} \cdot e^{-\zeta r}")
            st.markdown("Approximated by multiple Gaussians:")
            st.latex(r"\psi_{GTO}(r) = \sum_{i=1}^{N} c_i \cdot e^{-\alpha_i r^2}")
        elif basis_type == 'Correlation-Consistent':
            st.latex(r"\psi(r) = \sum_{i=1}^{N_{prim}} c_i \cdot r^l \cdot e^{-\alpha_i r^2}")
            st.markdown("Systematically improvable: cc-pVDZ → cc-pVTZ → cc-pVQZ → cc-pV5Z")
        elif basis_type == 'Pople':
            st.latex(r"\psi_{core}(r) = \sum_{i=1}^{N_1} c_i \cdot e^{-\alpha_i r^2}")
            st.latex(r"\psi_{valence}(r) = \sum_{j=1}^{N_2} d_j \cdot e^{-\beta_j r^2}")
            st.markdown("Split-valence: separate functions for core and valence")
        else:
            st.latex(r"\psi(r) = \sum_{i=1}^{N} c_i \cdot r^l \cdot e^{-\alpha_i r^2}")
        
        # Get ALL shell types
        elem_data = list(basis_data['elements'].values())[0]
        shells_by_type = {
            's': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 0],
            'p': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 1],
            'd': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 2],
            'f': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 3]
        }
        
        # Show each shell type with radial plots
        r = np.linspace(0, 5, 200)
        shell_names = {'s': 's-orbitals (spherical)', 'p': 'p-orbitals (dumbbell)', 
                       'd': 'd-orbitals (polarization)', 'f': 'f-orbitals (high polarization)'}
        
        for shell_type in ['s', 'p', 'd', 'f']:
            shells = shells_by_type[shell_type]
            
            if shells:
                st.markdown(f"#### {shell_names[shell_type]}")
                
                fig = go.Figure()
                
                for i, shell in enumerate(shells):
                    exponents = [float(e) for e in shell['exponents']]
                    coefficients = [float(c) for c in shell['coefficients'][0]]
                    n_prim = len(exponents)
                    
                    psi = np.zeros_like(r)
                    for exp, coef in zip(exponents, coefficients):
                        psi += coef * np.exp(-exp * r**2)
                    
                    fig.add_trace(go.Scatter(
                        x=r, y=psi,
                        name=f'{shell_type}-shell #{i+1} ({n_prim} primitives)',
                        line=dict(color='#3b82f6', width=2.5, dash=['solid', 'dash', 'dot', 'dashdot'][i % 4])
                    ))
                
                fig.update_layout(
                    title=f'<b>{shell_names[shell_type].title()} in {basis_name}</b>',
                    xaxis_title='Distance from nucleus (Bohr)',
                    yaxis_title='Radial wavefunction R(r)',
                    height=400,
                    hovermode='x unified',
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True, key=f"single_shell_{shell_type}")
                
                # Technical details
                st.info(f"""
                **{basis_name}**: {len(shells)} {shell_type}-shells
                - Total primitives: {sum(len(s['exponents']) for s in shells)}
                - Contractions: {len(shells)}
                - Exponent range: {min(float(e) for s in shells for e in s['exponents']):.2e} to {max(float(e) for s in shells for e in s['exponents']):.2e}
                """)
                
                st.markdown("---")
    
    # 3D Visualization
    st.markdown("### 🌌 3D Orbital Visualization")
    
    # Orbital type selector
    available_orbitals = []
    if shell_counts['s'] > 0:
        available_orbitals.append('s')
    if shell_counts['p'] > 0:
        available_orbitals.extend(['p_x', 'p_y', 'p_z'])
    if shell_counts['d'] > 0:
        available_orbitals.append('d')
    if shell_counts['f'] > 0:
        available_orbitals.append('f')
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        orbital_type = st.selectbox(
            "**Select Orbital:**",
            options=available_orbitals,
            help="Choose which orbital to visualize in 3D"
        )
        
        grid_resolution = st.slider(
            "**Grid Resolution:**",
            min_value=20,
            max_value=60,
            value=40,
            step=5,
            help="Higher = better quality but slower"
        )
        
        st.info(f"""
        **Viewing:** {orbital_type}-orbital
        
        **Controls:**
        - 🖱️ Drag to rotate
        - 🔍 Scroll to zoom
        - 📌 Double-click to reset
        """)
    
    with col2:
        # Calculate wavefunction
        with st.spinner("Calculating wavefunction..."):
            wf_data = calculate_orbital_wavefunction(basis_data, orbital_type, grid_resolution)
        
        if wf_data is not None:
            # Create 3D plot
            fig_3d = create_3d_orbital_plot(
                wf_data['X'],
                wf_data['Y'],
                wf_data['Z'],
                wf_data['psi'],
                f"{orbital_type}-orbital for {element_symbol} ({basis_name})"
            )
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.error("Unable to calculate wavefunction for this orbital type")
    
    # Additional Information
    with st.expander("📖 Learn More About This Basis Set"):
        st.markdown(f"""
        ### Detailed Information
        
        **Basis Set:** {basis_name}  
        **Element:** {element_symbol} (Z={current_element})
        
        #### Shell Breakdown:
        - **s-shells:** {shell_counts['s']} (spherical, l=0)
        - **p-shells:** {shell_counts['p']} (dumbbell, l=1)
        - **d-shells:** {shell_counts['d']} (cloverleaf, l=2)
        - **f-shells:** {shell_counts['f']} (complex, l=3)
        
        #### When to Use This Basis Set:
        {analysis['explanation']}
        
        #### Computational Cost:
        - **Total shells:** {analysis['total_shells']}
        - **Relative cost:** {'Low' if analysis['total_shells'] < 5 else 'Medium' if analysis['total_shells'] < 10 else 'High'}
        
        #### Best For:
        - **Geometry optimization:** {'✓ Good' if not analysis['has_diffuse'] else '✓ Excellent'}
        - **Energy calculations:** {'✓ Good' if analysis['total_shells'] >= 5 else '⚠ Fair'}
        - **Excited states:** {'✓ Excellent' if analysis['has_diffuse'] else '⚠ Limited'}
        - **Anions:** {'✓ Excellent' if analysis['has_diffuse'] else '✗ Poor'}
        """)

else:
    # ==================== COMPARISON MODE ====================
    
    st.markdown(f"## ⚖️ Comparison: {basis_name_1} vs {basis_name_2}")
    
    # Fetch both basis sets
    basis_data_1 = get_basis_for_element(basis_name_1, current_element)
    basis_data_2 = get_basis_for_element(basis_name_2, current_element)
    
    if basis_data_1 is None:
        st.error(f"❌ **{basis_name_1}** not available for {element_symbol}")
        st.stop()
    
    if basis_data_2 is None:
        st.error(f"❌ **{basis_name_2}** not available for {element_symbol}")
        st.stop()
    
    # Analyze both
    analysis_1 = analyze_basis_set(basis_data_1, basis_name_1)
    analysis_2 = analyze_basis_set(basis_data_2, basis_name_2)
    
    # SECTION 1: Basis Set Details (Collapsible)
    with st.expander("Basis Set Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### {basis_name_1}")
            st.markdown(f"""
            **Total Shells:** {analysis_1['total_shells']}  
            **Zeta Level:** {analysis_1['zeta']}  
            **Polarization:** {'✓ Yes' if analysis_1['has_polarization'] else '✗ No'}  
            **Diffuse:** {'✓ Yes' if analysis_1['has_diffuse'] else '✗ No'}
            """)
            st.markdown("#### Understanding This Basis Set")
            st.info(f"**{analysis_1['zeta']}**\n\n{analysis_1['explanation']}")
        with col2:
            st.markdown(f"### {basis_name_2}")
            st.markdown(f"""
            **Total Shells:** {analysis_2['total_shells']}  
            **Zeta Level:** {analysis_2['zeta']}  
            **Polarization:** {'✓ Yes' if analysis_2['has_polarization'] else '✗ No'}  
            **Diffuse:** {'✓ Yes' if analysis_2['has_diffuse'] else '✗ No'}
            """)
            st.markdown("#### Understanding This Basis Set")
            st.info(f"**{analysis_2['zeta']}**\n\n{analysis_2['explanation']}")
    
    # SECTION 2: Detailed Comparison Table
    with st.expander("Detailed Comparison Table", expanded=False):
        comp_data = create_comparison_table(basis_data_1, basis_data_2, basis_name_1, basis_name_2, analysis_1, analysis_2)
        display_comparison_table(comp_data, basis_name_1, basis_name_2)
    
    # SECTION 3: Visual Differences Analysis
    st.markdown("---")
    st.markdown("### Visual Differences Analysis")
    
    # Get shell counts
    elem_data1 = list(basis_data_1['elements'].values())[0]
    elem_data2 = list(basis_data_2['elements'].values())[0]
    s_shells_1 = sum(1 for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 0)
    s_shells_2 = sum(1 for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 0)
    p_shells_1 = sum(1 for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 1)
    p_shells_2 = sum(1 for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 1)
    d_shells_1 = sum(1 for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 2)
    d_shells_2 = sum(1 for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 2)
    
    # Orbital count bar graph
    fig_orbital_count = go.Figure()
    categories = ['s-shells', 'p-shells', 'd-shells']
    values1 = [s_shells_1, p_shells_1, d_shells_1]
    values2 = [s_shells_2, p_shells_2, d_shells_2]
    
    fig_orbital_count.add_trace(go.Bar(
        name=basis_name_1,
        x=categories,
        y=values1,
        marker_color='#3b82f6',
        text=values1,
        textposition='auto',
        textfont=dict(size=14, color='white', family='Arial Black'),
    ))
    
    fig_orbital_count.add_trace(go.Bar(
        name=basis_name_2,
        x=categories,
        y=values2,
        marker_color='#f59e0b',
        text=values2,
        textposition='auto',
        textfont=dict(size=14, color='white', family='Arial Black'),
    ))
    
    fig_orbital_count.update_layout(
        barmode='group',
        title='<b>Orbital Shell Count Comparison</b>',
        xaxis_title='Shell Type',
        yaxis_title='Number of Shells',
        height=350,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    st.plotly_chart(fig_orbital_count, use_container_width=True, key="orbital_count_bar")
    
    # SECTION 4: Mathematical Foundation
    with st.expander(f"Mathematical Foundation: {basis_name_1} vs {basis_name_2}", expanded=True):
        type1, desc1 = detect_basis_type(basis_name_1)
        type2, desc2 = detect_basis_type(basis_name_2)
        
        st.markdown(f"""
        ### Mathematical Functions from Your Selected Basis Sets
        
        **{basis_name_1}** ({desc1}):
        """)
        
        if type1 == 'STO':
            st.latex(r"\psi_{STO}(r) = N \cdot r^{n-1} \cdot e^{-\zeta r}")
            st.markdown("Approximated by multiple Gaussians:")
            st.latex(r"\psi_{GTO}(r) = \sum_{i=1}^{N} c_i \cdot e^{-\alpha_i r^2}")
        elif type1 == 'Correlation-Consistent':
            st.latex(r"\psi(r) = \sum_{i=1}^{N_{prim}} c_i \cdot r^l \cdot e^{-\alpha_i r^2}")
            st.markdown("Systematically improvable: cc-pVDZ → cc-pVTZ → cc-pVQZ → cc-pV5Z")
        elif type1 == 'Pople':
            st.latex(r"\psi_{core}(r) = \sum_{i=1}^{N_1} c_i \cdot e^{-\alpha_i r^2}")
            st.latex(r"\psi_{valence}(r) = \sum_{j=1}^{N_2} d_j \cdot e^{-\beta_j r^2}")
            st.markdown("Split-valence: separate functions for core and valence")
        else:
            st.latex(r"\psi(r) = \sum_{i=1}^{N} c_i \cdot r^l \cdot e^{-\alpha_i r^2}")
        
        st.markdown(f"""
        **{basis_name_2}** ({desc2}):
        """)
        
        if type2 == 'STO':
            st.latex(r"\psi_{STO}(r) = N \cdot r^{n-1} \cdot e^{-\zeta r}")
            st.markdown("Approximated by multiple Gaussians:")
            st.latex(r"\psi_{GTO}(r) = \sum_{i=1}^{N} c_i \cdot e^{-\alpha_i r^2}")
        elif type2 == 'Correlation-Consistent':
            st.latex(r"\psi(r) = \sum_{i=1}^{N_{prim}} c_i \cdot r^l \cdot e^{-\alpha_i r^2}")
            st.markdown("Systematically improvable: cc-pVDZ → cc-pVTZ → cc-pVQZ → cc-pV5Z")
        elif type2 == 'Pople':
            st.latex(r"\psi_{core}(r) = \sum_{i=1}^{N_1} c_i \cdot e^{-\alpha_i r^2}")
            st.latex(r"\psi_{valence}(r) = \sum_{j=1}^{N_2} d_j \cdot e^{-\beta_j r^2}")
            st.markdown("Split-valence: separate functions for core and valence")
        else:
            st.latex(r"\psi(r) = \sum_{i=1}^{N} c_i \cdot r^l \cdot e^{-\alpha_i r^2}")
        
        # Get ALL shell types from both basis sets
        shells_by_type_1 = {
            's': [s for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 0],
            'p': [s for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 1],
            'd': [s for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 2],
            'f': [s for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 3]
        }
        shells_by_type_2 = {
            's': [s for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 0],
            'p': [s for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 1],
            'd': [s for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 2],
            'f': [s for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 3]
        }
        
        # Show comparison for EACH shell type
        r = np.linspace(0, 5, 200)
        shell_names = {'s': 's-orbitals (spherical)', 'p': 'p-orbitals (dumbbell)', 
                       'd': 'd-orbitals (polarization)', 'f': 'f-orbitals (high polarization)'}
        
        for shell_type in ['s', 'p', 'd', 'f']:
            shells_1 = shells_by_type_1[shell_type]
            shells_2 = shells_by_type_2[shell_type]
            
            if shells_1 or shells_2:
                st.markdown(f"#### {shell_names[shell_type]}")
                
                fig = go.Figure()
                
                # Plot from basis 1
                if shells_1:
                    for i, shell in enumerate(shells_1):
                        exponents = [float(e) for e in shell['exponents']]
                        coefficients = [float(c) for c in shell['coefficients'][0]]
                        n_prim = len(exponents)
                        
                        psi = np.zeros_like(r)
                        for exp, coef in zip(exponents, coefficients):
                            psi += coef * np.exp(-exp * r**2)
                        
                        fig.add_trace(go.Scatter(
                            x=r, y=psi,
                            name=f'{basis_name_1} {shell_type}-shell #{i+1} ({n_prim} primitives)',
                            line=dict(color='#3b82f6', width=2.5, dash=['solid', 'dash', 'dot', 'dashdot'][i % 4])
                        ))
                else:
                    st.warning(f"**{basis_name_1}** has NO {shell_type}-shells")
                
                # Plot from basis 2
                if shells_2:
                    for i, shell in enumerate(shells_2):
                        exponents = [float(e) for e in shell['exponents']]
                        coefficients = [float(c) for c in shell['coefficients'][0]]
                        n_prim = len(exponents)
                        
                        psi = np.zeros_like(r)
                        for exp, coef in zip(exponents, coefficients):
                            psi += coef * np.exp(-exp * r**2)
                        
                        fig.add_trace(go.Scatter(
                            x=r, y=psi,
                            name=f'{basis_name_2} {shell_type}-shell #{i+1} ({n_prim} primitives)',
                            line=dict(color='#f59e0b', width=2.5, dash=['solid', 'dash', 'dot', 'dashdot'][i % 4])
                        ))
                else:
                    st.warning(f"**{basis_name_2}** has NO {shell_type}-shells")
                
                if shells_1 or shells_2:
                    fig.update_layout(
                        title=f'<b>{shell_names[shell_type].title()}: {basis_name_1} vs {basis_name_2}</b>',
                        xaxis_title='Distance from nucleus (Bohr)',
                        yaxis_title='Radial wavefunction R(r)',
                        height=400,
                        hovermode='x unified',
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"shell_{shell_type}")
                    
                    # Technical details
                    col1, col2 = st.columns(2)
                    with col1:
                        if shells_1:
                            st.info(f"""
                            **{basis_name_1}**: {len(shells_1)} {shell_type}-shells
                            - Total primitives: {sum(len(s['exponents']) for s in shells_1)}
                            - Contractions: {len(shells_1)}
                            """)
                    with col2:
                        if shells_2:
                            st.info(f"""
                            **{basis_name_2}**: {len(shells_2)} {shell_type}-shells
                            - Total primitives: {sum(len(s['exponents']) for s in shells_2)}
                            - Contractions: {len(shells_2)}
                            """)
                
                st.markdown("---")
    
    # SECTION 5: Recommendation
    with st.expander(f"Which Basis Set Should You Use?", expanded=True):
        st.markdown("### Recommendation Based on Your Selection")
        
        # Calculate quality score
        quality_1 = s_shells_1 + d_shells_1 * 2
        quality_2 = s_shells_2 + d_shells_2 * 2
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{basis_name_1} Quality Score", quality_1)
            st.caption(f"{s_shells_1} s-shells + {d_shells_1} d-shells")
        with col2:
            st.metric(f"{basis_name_2} Quality Score", quality_2)
            st.caption(f"{s_shells_2} s-shells + {d_shells_2} d-shells")
        
        if quality_1 > quality_2:
            st.success(f"✓ **Use {basis_name_1}** for higher accuracy (but slower)")
            st.info(f"✓ **Use {basis_name_2}** for faster calculations (but less accurate)")
        elif quality_2 > quality_1:
            st.success(f"✓ **Use {basis_name_2}** for higher accuracy (but slower)")
            st.info(f"✓ **Use {basis_name_1}** for faster calculations (but less accurate)")
        else:
            st.info(f"Both basis sets have similar quality - choose based on availability")
    
    # SECTION 6: 3D Orbital Comparison
    st.markdown("### 3D Orbital Comparison")
    st.markdown("Compare the actual orbital shapes from both basis sets side-by-side")
    
    # Get available orbitals
    shells1 = elem_data1['electron_shells']
    shells2 = elem_data2['electron_shells']
    
    # Build orbital list
    orbital_options = []
    orbital_labels = []
    s_count = 0
    p_count = 0
    d_count = 0
    f_count = 0
    
    for i, s in enumerate(shells1):
        am = s['angular_momentum'][0]
        if am == 0:
            s_count += 1
            orbital_options.append('s')
            orbital_labels.append(f"Shell #{i+1}: {s_count}s orbital (spherical, core/valence)")
        elif am == 1:
            p_count += 1
            orbital_options.extend(['p_x', 'p_y', 'p_z'])
            orbital_labels.extend([
                f"Shell #{i+1}: {p_count}p_x orbital (dumbbell along x-axis)",
                f"Shell #{i+1}: {p_count}p_y orbital (dumbbell along y-axis)",
                f"Shell #{i+1}: {p_count}p_z orbital (dumbbell along z-axis)"
            ])
        elif am == 2:
            d_count += 1
            orbital_options.append('d')
            orbital_labels.append(f"Shell #{i+1}: {d_count}d orbital (cloverleaf, polarization)")
        elif am == 3:
            f_count += 1
            orbital_options.append('f')
            orbital_labels.append(f"Shell #{i+1}: {f_count}f orbital (complex shape, high polarization)")
    
    if orbital_options:
        orbital_dict = {label: opt for label, opt in zip(orbital_labels, orbital_options)}
        
        selected_label = st.selectbox(
            "Select Orbital Type for Comparison:",
            orbital_labels,
            help="Choose which orbital to compare in 3D",
            key="comparison_orbital_select"
        )
        
        orbital = orbital_dict[selected_label]
        
        # Show side-by-side comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### {basis_name_1}")
            
            # Check if this basis has this orbital
            has_orbital = False
            for s in shells1:
                am = s['angular_momentum'][0]
                if (am == 0 and 's' in orbital) or \
                   (am == 1 and 'p' in orbital) or \
                   (am == 2 and 'd' in orbital) or \
                   (am == 3 and 'f' in orbital):
                    has_orbital = True
                    exps = [float(e) for e in s['exponents']]
                    coeffs = [float(c) for c in s['coefficients'][0]]
                    
                    st.caption(f"""
                    **Basis Set Parameters:**
                    - Primitives: {len(exps)}
                    - Exponents: {min(exps):.2e} to {max(exps):.2e}
                    """)
                    break
            
            if has_orbital:
                with st.spinner("Calculating..."):
                    wf_1 = calculate_orbital_wavefunction(basis_data_1, orbital, 35)
                if wf_1 is not None:
                    fig_3d_1 = create_3d_orbital_plot(
                        wf_1['X'], wf_1['Y'], wf_1['Z'], wf_1['psi'],
                        f"{orbital} - {basis_name_1}"
                    )
                    st.plotly_chart(fig_3d_1, use_container_width=True, key="comp_orbital_1")
            else:
                st.warning(f"{basis_name_1} does not have {orbital} orbitals")
        
        with col2:
            st.markdown(f"#### {basis_name_2}")
            
            # Check if this basis has this orbital
            has_orbital = False
            for s in shells2:
                am = s['angular_momentum'][0]
                if (am == 0 and 's' in orbital) or \
                   (am == 1 and 'p' in orbital) or \
                   (am == 2 and 'd' in orbital) or \
                   (am == 3 and 'f' in orbital):
                    has_orbital = True
                    exps = [float(e) for e in s['exponents']]
                    coeffs = [float(c) for c in s['coefficients'][0]]
                    
                    st.caption(f"""
                    **Basis Set Parameters:**
                    - Primitives: {len(exps)}
                    - Exponents: {min(exps):.2e} to {max(exps):.2e}
                    """)
                    break
            
            if has_orbital:
                with st.spinner("Calculating..."):
                    wf_2 = calculate_orbital_wavefunction(basis_data_2, orbital, 35)
                if wf_2 is not None:
                    fig_3d_2 = create_3d_orbital_plot(
                        wf_2['X'], wf_2['Y'], wf_2['Z'], wf_2['psi'],
                        f"{orbital} - {basis_name_2}"
                    )
                    st.plotly_chart(fig_3d_2, use_container_width=True, key="comp_orbital_2")
            else:
                st.warning(f"{basis_name_2} does not have {orbital} orbitals")
        
        st.info("""
        **How to interpret the comparison:**
        - **Tighter orbitals** (smaller, more compact) = higher exponents = better for core electrons
        - **Looser orbitals** (larger, more diffuse) = lower exponents = better for valence/bonding
        - **Different shapes** = different contraction coefficients = different accuracy
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><b>Basis Sets Module</b> - Part of DFT Flight Simulator</p>
    <p style="font-size: 0.9rem;">Data from <a href="https://www.basissetexchange.org/" target="_blank">Basis Set Exchange</a></p>
</div>
""", unsafe_allow_html=True)
