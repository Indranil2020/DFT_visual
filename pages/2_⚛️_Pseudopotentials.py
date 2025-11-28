"""
Pseudopotentials Module - DFT Flight Simulator
Interactive visualization and comparison of pseudopotentials.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Import our modules
from modules.pseudopotentials import (
    get_available_pseudos,
    get_pseudo_data,
    compare_pseudos,
    check_pseudo_exists
)
from utils.constants import ELEMENTS
from utils.plotting import create_comparison_plot, create_radial_plot
from utils.session import init_session_state, show_consistency_checker, show_current_selections

# Page configuration
st.set_page_config(
    page_title="Pseudopotentials - DFT Flight Simulator",
    page_icon="⚛️",
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
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">⚛️ Pseudopotentials: The Core</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Simplifying the Nucleus - Understanding Core vs Valence</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚛️ Pseudopotential Controls")
    
    # Mode selection
    mode = st.radio(
        "**Mode:**",
        ["Single Pseudopotential", "Comparison Mode"],
        help="Choose to explore one pseudopotential or compare two"
    )
    
    st.markdown("---")
    
    # Element selection
    st.markdown("### Select Element")
    
    # Quick element selector
    common_elements = {
        'H': 1, 'C': 6, 'N': 7, 'O': 8, 'F': 9,
        'Si': 14, 'P': 15, 'S': 16, 'Cl': 17, 'Fe': 26
    }
    
    col1, col2, col3 = st.columns(3)
    for i, (symbol, z) in enumerate(list(common_elements.items())):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(symbol, key=f"elem_{symbol}", use_container_width=True):
                st.session_state.selected_element = z
    
    # Or select from dropdown
    available_pseudos = get_available_pseudos()
    available_elements = {f"{symbol} ({z})": z for symbol, data in available_pseudos.items() for z in [data['Z']]}
    
    selected_elem_str = st.selectbox(
        "Or choose from all elements:",
        options=list(available_elements.keys()),
        index=list(available_elements.values()).index(st.session_state.selected_element) if st.session_state.selected_element in available_elements.values() else 0
    )
    st.session_state.selected_element = available_elements[selected_elem_str]
    
    current_element = st.session_state.selected_element
    element_symbol = ELEMENTS.get(current_element, 'Unknown')
    
    st.info(f"**Selected:** {element_symbol} (Z={current_element})")
    
    st.markdown("---")
    
    # Functional selection
    st.markdown("### Select Functional")
    
    functional = st.selectbox(
        "**XC Functional:**",
        options=['PBE', 'LDA', 'PW'],
        index=0,
        help="Exchange-correlation functional used to generate pseudopotential"
    )
    st.session_state.selected_pseudo_functional = functional
    
    if mode == "Single Pseudopotential":
        # Accuracy selection
        accuracy = st.selectbox(
            "**Accuracy Level:**",
            options=['standard', 'stringent'],
            index=0,
            help="Standard = softer (faster), Stringent = harder (more accurate)"
        )
        st.session_state.selected_pseudo_accuracy = accuracy
    else:
        st.info("Comparing **standard** vs **stringent** accuracy")
    
    # Show current selections
    show_current_selections()
    
    # Show consistency checker
    show_consistency_checker()
    
    st.markdown("---")
    
    # Educational info
    with st.expander("📚 What are Pseudopotentials?"):
        st.markdown("""
        **Pseudopotentials** replace the strong Coulomb potential of the nucleus 
        and core electrons with a weaker effective potential.
        
        **Why?**
        - Core electrons don't participate in bonding
        - Saves computational time
        - Reduces basis set size needed
        
        **Trade-off:**
        - Lose some accuracy
        - Can't study core properties
        - Must match functional used in calculation
        """)

# Main content
if mode == "Single Pseudopotential":
    # ==================== SINGLE PSEUDOPOTENTIAL MODE ====================
    
    st.markdown(f"## 📊 Pseudopotential: {element_symbol} ({functional}, {accuracy})")
    
    # Check if exists
    exists = check_pseudo_exists(element_symbol, accuracy, functional)
    
    if not exists:
        st.error(f"❌ Pseudopotential not available for **{element_symbol}** with **{functional}** functional and **{accuracy}** accuracy")
        st.info("💡 Try a different element, functional, or accuracy level.")
        st.stop()
    
    # Fetch pseudopotential data
    with st.spinner(f"Fetching pseudopotential for {element_symbol}..."):
        pseudo_data = get_pseudo_data(element_symbol, accuracy, functional)
    
    if pseudo_data is None:
        st.error("❌ Failed to fetch pseudopotential data")
        st.info("This might be a network issue. Please try again.")
        st.stop()
    
    # Display overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{pseudo_data['Z']}</div>
            <div class="metric-label">Atomic Number</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        z_val = pseudo_data['header'].get('z_valence', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{z_val:.0f}</div>
            <div class="metric-label">Valence Electrons</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{pseudo_data['r_core']:.2f}</div>
            <div class="metric-label">Core Radius (Bohr)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        mesh_size = pseudo_data['header'].get('mesh_size', 0)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{mesh_size}</div>
            <div class="metric-label">Grid Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Educational explanation
    st.markdown("### 📚 Understanding This Pseudopotential")
    
    core_electrons = pseudo_data['Z'] - z_val
    
    st.markdown(f"""
    <div class="info-card">
        <h4>What's happening here?</h4>
        <p><b>{element_symbol}</b> has <b>{pseudo_data['Z']} total electrons</b>.</p>
        <p>This pseudopotential treats:</p>
        <ul>
            <li><b>{core_electrons:.0f} electrons</b> as "frozen core" (not explicitly calculated)</li>
            <li><b>{z_val:.0f} electrons</b> as "valence" (explicitly calculated)</li>
        </ul>
        <p><b>Core radius:</b> {pseudo_data['r_core']:.2f} Bohr = {pseudo_data['r_core']*0.529:.2f} Å</p>
        <p>Inside this radius, the pseudopotential differs significantly from the Coulomb potential.</p>
        <p><b>Accuracy level:</b> {accuracy.capitalize()} - {'Softer, faster calculations' if accuracy == 'standard' else 'Harder, more accurate but slower'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualization tabs
    tab1, tab2, tab3 = st.tabs(["📈 Potential Comparison", "📊 Difference Plot", "ℹ️ Details"])
    
    with tab1:
        st.markdown("### Coulomb vs Pseudopotential")
        st.markdown("The **red line** shows the true Coulomb potential (-Z/r). The **blue line** shows the pseudopotential.")
        
        # Create comparison plot
        r_plot = pseudo_data['r'][:500]  # Limit for visualization
        v_coulomb_plot = pseudo_data['v_coulomb'][:500]
        v_pseudo_plot = pseudo_data['v_local'][:500]
        
        fig = go.Figure()
        
        # Coulomb potential
        fig.add_trace(go.Scatter(
            x=r_plot,
            y=v_coulomb_plot,
            mode='lines',
            name='Coulomb (-Z/r)',
            line=dict(color='#e74c3c', width=2),
            hovertemplate='r: %{x:.3f} Bohr<br>V: %{y:.3f} Ha<extra></extra>'
        ))
        
        # Pseudopotential
        fig.add_trace(go.Scatter(
            x=r_plot,
            y=v_pseudo_plot,
            mode='lines',
            name=f'Pseudopotential ({accuracy})',
            line=dict(color='#667eea', width=2),
            hovertemplate='r: %{x:.3f} Bohr<br>V: %{y:.3f} Ha<extra></extra>'
        ))
        
        # Core radius marker
        fig.add_vline(
            x=pseudo_data['r_core'],
            line_dash="dash",
            line_color="green",
            annotation_text=f"Core radius ({pseudo_data['r_core']:.2f} Bohr)",
            annotation_position="top"
        )
        
        fig.update_layout(
            title=f"Potential Comparison for {element_symbol}",
            xaxis_title="Distance from nucleus (Bohr)",
            yaxis_title="Potential (Hartree)",
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("""
        **Key observations:**
        - **Close to nucleus (r < core radius):** Pseudopotential is much weaker (less negative)
        - **Far from nucleus (r > core radius):** Both potentials converge to -Z_val/r
        - **Green dashed line:** Marks the core radius where significant deviation occurs
        """)
    
    with tab2:
        st.markdown("### Difference: Pseudopotential - Coulomb")
        st.markdown("This shows **where** and **how much** the pseudopotential differs from the true Coulomb potential.")
        
        # Difference plot
        diff_plot = pseudo_data['v_diff'][:500]
        
        fig_diff = create_radial_plot(
            r_plot,
            diff_plot,
            'Difference',
            f'Pseudopotential Difference for {element_symbol}',
            'Distance from nucleus (Bohr)',
            'V_pseudo - V_coulomb (Hartree)'
        )
        
        # Add zero line
        fig_diff.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add core radius marker
        fig_diff.add_vline(
            x=pseudo_data['r_core'],
            line_dash="dash",
            line_color="green",
            annotation_text=f"Core radius",
            annotation_position="top"
        )
        
        st.plotly_chart(fig_diff, use_container_width=True)
        
        st.info("""
        **Interpretation:**
        - **Positive values:** Pseudopotential is less attractive (weaker) than Coulomb
        - **Near zero:** Pseudopotential matches Coulomb potential well
        - **Maximum difference:** Occurs around the core radius
        """)
    
    with tab3:
        st.markdown("### 📋 Detailed Information")
        
        header = pseudo_data['header']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Element Information:**
            - **Symbol:** {element_symbol}
            - **Atomic Number:** {pseudo_data['Z']}
            - **Valence Electrons:** {z_val:.0f}
            - **Core Electrons:** {core_electrons:.0f}
            
            **Pseudopotential Properties:**
            - **Type:** {header.get('pseudo_type', 'Norm-conserving')}
            - **Functional:** {functional}
            - **Accuracy:** {accuracy.capitalize()}
            - **Core Radius:** {pseudo_data['r_core']:.3f} Bohr ({pseudo_data['r_core']*0.529:.3f} Å)
            """)
        
        with col2:
            st.markdown(f"""
            **Technical Details:**
            - **l_max:** {header.get('l_max', 'N/A')} (maximum angular momentum)
            - **Mesh Size:** {mesh_size} points
            - **Grid Type:** Logarithmic radial mesh
            - **Source:** PseudoDojo database
            
            **File Format:**
            - **Format:** UPF (Unified Pseudopotential Format)
            - **Version:** UPF v2
            - **Cached:** Yes (local storage)
            """)
        
        with st.expander("📄 Show Pseudopotential Info"):
            info_text = header.get('info', 'No additional information available')
            st.text(info_text[:500] + "..." if len(info_text) > 500 else info_text)

else:
    # ==================== COMPARISON MODE ====================
    
    st.markdown(f"## ⚖️ Comparison: Standard vs Stringent for {element_symbol}")
    
    # Fetch comparison data
    with st.spinner(f"Fetching pseudopotentials for {element_symbol}..."):
        comparison = compare_pseudos(element_symbol, 'standard', 'stringent', functional)
    
    if comparison is None:
        st.error(f"❌ Unable to compare pseudopotentials for **{element_symbol}**")
        st.info("One or both accuracy levels may not be available for this element.")
        st.stop()
    
    # Overview
    st.markdown("### 📊 Comparison Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{comparison['r_core1']:.2f}</div>
            <div class="metric-label">Standard Core Radius (Bohr)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{comparison['r_core2']:.2f}</div>
            <div class="metric-label">Stringent Core Radius (Bohr)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        core_diff = abs(comparison['r_core2'] - comparison['r_core1'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{core_diff:.2f}</div>
            <div class="metric-label">Core Radius Difference</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Explanation
    st.markdown(f"""
    <div class="info-card">
        <h4>Standard vs Stringent: What's the difference?</h4>
        <p><b>Standard (soft):</b></p>
        <ul>
            <li>Larger core radius ({comparison['r_core1']:.2f} Bohr)</li>
            <li>Smoother potential (fewer plane waves needed)</li>
            <li>Faster calculations</li>
            <li>Good for most applications</li>
        </ul>
        <p><b>Stringent (hard):</b></p>
        <ul>
            <li>Smaller core radius ({comparison['r_core2']:.2f} Bohr)</li>
            <li>More accurate (closer to all-electron)</li>
            <li>Requires more plane waves (slower)</li>
            <li>Better for high-pressure, magnetic properties</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Visualization
    st.markdown("### 📈 Potential Comparison")
    
    r_plot = comparison['r'][:500]
    v1_plot = comparison['v1'][:500]
    v2_plot = comparison['v2'][:500]
    diff_plot = comparison['diff'][:500]
    
    fig_comp = go.Figure()
    
    # Standard
    fig_comp.add_trace(go.Scatter(
        x=r_plot,
        y=v1_plot,
        mode='lines',
        name='Standard',
        line=dict(color='#3498db', width=2),
        hovertemplate='r: %{x:.3f} Bohr<br>V: %{y:.3f} Ha<extra></extra>'
    ))
    
    # Stringent
    fig_comp.add_trace(go.Scatter(
        x=r_plot,
        y=v2_plot,
        mode='lines',
        name='Stringent',
        line=dict(color='#e74c3c', width=2),
        hovertemplate='r: %{x:.3f} Bohr<br>V: %{y:.3f} Ha<extra></extra>'
    ))
    
    # Core radius markers
    fig_comp.add_vline(
        x=comparison['r_core1'],
        line_dash="dash",
        line_color="#3498db",
        annotation_text="Standard core",
        annotation_position="top left"
    )
    
    fig_comp.add_vline(
        x=comparison['r_core2'],
        line_dash="dash",
        line_color="#e74c3c",
        annotation_text="Stringent core",
        annotation_position="top right"
    )
    
    fig_comp.update_layout(
        title=f"Standard vs Stringent Pseudopotentials for {element_symbol} ({functional})",
        xaxis_title="Distance from nucleus (Bohr)",
        yaxis_title="Potential (Hartree)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Difference plot
    st.markdown("### 📊 Difference: Stringent - Standard")
    
    fig_diff = create_radial_plot(
        r_plot,
        diff_plot,
        'Difference',
        f'Pseudopotential Difference: Stringent - Standard',
        'Distance from nucleus (Bohr)',
        'Difference (Hartree)'
    )
    
    fig_diff.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    st.plotly_chart(fig_diff, use_container_width=True)
    
    # Recommendation
    st.markdown("### 💡 Which Should You Use?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="success-box">
            <h4>✓ Use Standard if:</h4>
            <ul>
                <li>You need fast calculations</li>
                <li>Studying molecular systems</li>
                <li>Standard DFT calculations</li>
                <li>Testing/prototyping</li>
                <li>Limited computational resources</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="warning-box">
            <h4>⚠ Use Stringent if:</h4>
            <ul>
                <li>You need high accuracy</li>
                <li>Studying high-pressure systems</li>
                <li>Magnetic or strongly correlated systems</li>
                <li>Benchmark calculations</li>
                <li>Publication-quality results</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><b>Pseudopotentials Module</b> - Part of DFT Flight Simulator</p>
    <p style="font-size: 0.9rem;">Data from <a href="http://www.pseudo-dojo.org/" target="_blank">PseudoDojo</a></p>
</div>
""", unsafe_allow_html=True)
