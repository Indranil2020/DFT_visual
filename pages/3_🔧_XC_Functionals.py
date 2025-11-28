"""
XC Functionals Module - DFT Flight Simulator
Interactive visualization and comparison of exchange-correlation functionals.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Import our modules
from modules.xc_functionals import (
    get_available_functionals,
    get_functional_info,
    get_enhancement_comparison,
    compare_functionals_simple,
    get_functional_recommendations,
    get_jacobs_ladder_info
)
from utils.plotting import create_comparison_plot, create_multi_line_plot
from utils.session import init_session_state, show_consistency_checker, show_current_selections

# Page configuration
st.set_page_config(
    page_title="XC Functionals - DFT Flight Simulator",
    page_icon="🔧",
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
    .ladder-rung {
        background: white;
        border-left: 5px solid #667eea;
        padding: 1.2rem;
        margin: 0.8rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .ladder-rung:hover {
        transform: translateX(10px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .rung-number {
        display: inline-block;
        background: #667eea;
        color: white;
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border-radius: 50%;
        font-weight: 700;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    .functional-badge {
        display: inline-block;
        background: #f0f0f0;
        padding: 0.3rem 0.8rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #667eea;
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-title">🔧 XC Functionals: The Engine</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">The Heart of DFT - Understanding Exchange-Correlation Approximations</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🔧 XC Functional Controls")
    
    # View mode selection
    view_mode = st.radio(
        "**View Mode:**",
        ["Mathematical View", "Jacob's Ladder", "Comparison Mode", "Recommendations"],
        help="Choose how to explore XC functionals"
    )
    
    st.markdown("---")
    
    if view_mode == "Mathematical View":
        st.markdown("### Select Functionals")
        
        available_funcs = get_available_functionals()
        
        # Categorize functionals
        lda_funcs = [f for f in available_funcs if 'LDA' in f or 'SVWN' in f]
        gga_funcs = [f for f in available_funcs if any(x in f for x in ['PBE', 'BLYP', 'PW91', 'RPBE']) and 'HYB' not in f]
        hybrid_funcs = [f for f in available_funcs if 'B3LYP' in f or 'PBE0' in f or 'HSE' in f or 'CAM' in f or 'wB97' in f]
        meta_funcs = [f for f in available_funcs if any(x in f for x in ['TPSS', 'SCAN', 'M06'])]
        
        func_category = st.selectbox(
            "**Functional Family:**",
            ["All", "LDA", "GGA", "Hybrid", "meta-GGA"],
            help="Filter by functional type"
        )
        
        if func_category == "LDA":
            filtered_funcs = lda_funcs
        elif func_category == "GGA":
            filtered_funcs = gga_funcs
        elif func_category == "Hybrid":
            filtered_funcs = hybrid_funcs
        elif func_category == "meta-GGA":
            filtered_funcs = meta_funcs
        else:
            filtered_funcs = available_funcs
        
        selected_functionals = st.multiselect(
            "**Choose Functionals to Compare:**",
            options=filtered_funcs,
            default=[filtered_funcs[0]] if filtered_funcs else [],
            help="Select one or more functionals to visualize"
        )
        
        if not selected_functionals:
            st.warning("⚠️ Select at least one functional")
    
    elif view_mode == "Comparison Mode":
        st.markdown("### Select Two Functionals")
        
        available_funcs = get_available_functionals()
        
        func1 = st.selectbox(
            "**First Functional:**",
            options=available_funcs,
            index=available_funcs.index('PBE') if 'PBE' in available_funcs else 0,
            key="func1"
        )
        
        func2 = st.selectbox(
            "**Second Functional:**",
            options=available_funcs,
            index=available_funcs.index('B3LYP') if 'B3LYP' in available_funcs else min(1, len(available_funcs)-1),
            key="func2"
        )
        
        st.session_state.selected_xc_functional = func1
    
    elif view_mode == "Recommendations":
        st.markdown("### Select Use Case")
        
        use_case = st.selectbox(
            "**What are you studying?**",
            options=[
                'molecules',
                'solids',
                'fast',
                'accurate',
                'general',
                'thermochemistry',
                'band_gaps',
                'weak_interactions'
            ],
            format_func=lambda x: x.replace('_', ' ').title(),
            help="Get functional recommendations for your application"
        )
    
    # Show current selections
    show_current_selections()
    
    # Show consistency checker
    show_consistency_checker()
    
    st.markdown("---")
    
    # Educational info
    with st.expander("📚 What are XC Functionals?"):
        st.markdown("""
        **Exchange-Correlation (XC) functionals** approximate the quantum mechanical 
        exchange and correlation effects between electrons.
        
        **Why do we need them?**
        - Exact solution is impossible for >2 electrons
        - Different approximations → different accuracy
        - Trade-off between speed and accuracy
        
        **Jacob's Ladder:**
        - Rung 1: LDA (fastest, least accurate)
        - Rung 2: GGA (good balance)
        - Rung 3: meta-GGA (better)
        - Rung 4: Hybrid (very good, slower)
        - Rung 5: Double-hybrid (best, slowest)
        """)

# Main content
if view_mode == "Mathematical View":
    # ==================== MATHEMATICAL VIEW ====================
    
    if not selected_functionals:
        st.warning("⚠️ Please select at least one functional from the sidebar")
        st.stop()
    
    st.markdown("## 📐 Enhancement Factor Analysis")
    
    st.markdown("""
    The **enhancement factor** F_x(s) shows how the functional modifies the LDA exchange energy 
    based on the **reduced gradient** s = |∇ρ|/(2k_F ρ).
    
    - **s = 0:** Uniform electron gas (LDA limit)
    - **s > 0:** Non-uniform density (gradient corrections)
    - **Larger F_x:** More exchange energy
    """)
    
    # Calculate enhancement factors
    with st.spinner("Calculating enhancement factors..."):
        enhancement_data = get_enhancement_comparison(selected_functionals, s_range=(0.0, 4.0), n_points=200)
    
    if enhancement_data is None:
        st.error("❌ Failed to calculate enhancement factors")
        st.stop()
    
    # Create plot
    fig = go.Figure()
    
    colors = ['#667eea', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    for i, func_name in enumerate(selected_functionals):
        data = enhancement_data[func_name]
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=data['s'],
            y=data['F'],
            mode='lines',
            name=func_name,
            line=dict(color=color, width=3),
            hovertemplate=f'{func_name}<br>s: %{{x:.3f}}<br>F_x: %{{y:.3f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Exchange Enhancement Factor F_x(s)",
        xaxis_title="Reduced Gradient s = |∇ρ|/(2k_F ρ)",
        yaxis_title="Enhancement Factor F_x(s)",
        hovermode='x unified',
        height=600,
        template='plotly_white',
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#e5e7eb',
            borderwidth=1
        )
    )
    
    # Add reference line at F=1 (LDA)
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray", opacity=0.5,
                  annotation_text="LDA (F=1)", annotation_position="right")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretation
    st.markdown("### 🔍 Interpretation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Key Observations:**
        - **LDA:** Flat line at F=1 (no gradient dependence)
        - **GGAs:** Increase with s (gradient corrections)
        - **Different slopes:** Different treatment of non-uniformity
        - **Asymptotic behavior:** How functional behaves at large s
        """)
    
    with col2:
        st.markdown("""
        **Practical Implications:**
        - **Steeper curves:** More sensitive to density gradients
        - **Higher values:** More exchange energy
        - **Crossing points:** Functionals agree at specific densities
        - **Large s behavior:** Important for molecular tails
        """)
    
    # Functional details
    st.markdown("### 📋 Functional Details")
    
    for func_name in selected_functionals:
        with st.expander(f"ℹ️ {func_name}"):
            info = get_functional_info(func_name)
            if info:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **Type:** {info.get('type', 'Unknown')}  
                    **Description:** {info.get('description', 'N/A')}  
                    **Year:** {info.get('year', 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **Use Case:** {info.get('use_case', 'General purpose')}  
                    **Accuracy:** {info.get('accuracy', 'N/A')}  
                    **Cost:** {info.get('cost', 'N/A')}
                    """)
                
                if 'exact_exchange' in info:
                    st.info(f"💡 Contains **{info['exact_exchange']*100:.0f}%** exact exchange")
                
                if 'reference' in info:
                    st.caption(f"📚 Reference: {info['reference']}")

elif view_mode == "Jacob's Ladder":
    # ==================== JACOB'S LADDER ====================
    
    st.markdown("## 🪜 Jacob's Ladder of DFT Functionals")
    
    st.markdown("""
    **Jacob's Ladder** represents the hierarchy of DFT functionals, where each rung 
    adds more physical information and (usually) more accuracy.
    
    **Climbing the ladder = Better accuracy but higher computational cost**
    """)
    
    ladder_info = get_jacobs_ladder_info()
    
    # Display rungs in reverse order (5 to 1)
    for rung_num in sorted(ladder_info['rungs'].keys(), reverse=True):
        rung = ladder_info['rungs'][rung_num]
        
        st.markdown(f"""
        <div class="ladder-rung">
            <span class="rung-number">{rung_num}</span>
            <div style="display: inline-block; vertical-align: top; width: calc(100% - 60px);">
                <h3 style="margin-top: 0;">{rung['name']}</h3>
                <p><b>{rung['description']}</b></p>
                <p><b>Depends on:</b> {rung['depends_on']}</p>
                <p><b>Examples:</b> {', '.join([f'<span class="functional-badge">{ex}</span>' for ex in rung['examples']])}</p>
                <p><b>Accuracy:</b> {rung['accuracy']} | <b>Cost:</b> {rung['cost']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Climbing guide
    st.markdown("### 🎯 Which Rung Should You Use?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Start Here (Rung 2):**
        - GGA functionals (PBE, BLYP)
        - Good balance of speed/accuracy
        - Works for most systems
        - Industry standard
        """)
    
    with col2:
        st.markdown("""
        **Need More Accuracy? (Rung 4):**
        - Hybrid functionals (B3LYP, PBE0)
        - Better for molecules
        - Improved band gaps
        - Worth the extra cost
        """)
    
    with col3:
        st.markdown("""
        **Cutting Edge (Rung 3):**
        - meta-GGA (SCAN, TPSS)
        - Modern alternative to hybrids
        - No exact exchange (faster)
        - Very promising
        """)
    
    # Interactive comparison
    st.markdown("### 📊 Compare Rungs")
    
    rung_selection = st.multiselect(
        "Select rungs to compare:",
        options=[f"Rung {i}: {ladder_info['rungs'][i]['name']}" for i in range(1, 6)],
        default=["Rung 2: GGA", "Rung 4: Hybrid"]
    )
    
    if rung_selection:
        comparison_df_data = []
        for rung_str in rung_selection:
            rung_num = int(rung_str.split(':')[0].split()[1])
            rung = ladder_info['rungs'][rung_num]
            comparison_df_data.append({
                'Rung': rung_num,
                'Name': rung['name'],
                'Accuracy': rung['accuracy'],
                'Cost': rung['cost'],
                'Examples': ', '.join(rung['examples'][:2])
            })
        
        st.table(comparison_df_data)

elif view_mode == "Comparison Mode":
    # ==================== COMPARISON MODE ====================
    
    st.markdown(f"## ⚖️ Comparison: {func1} vs {func2}")
    
    # Get functional info
    info1 = get_functional_info(func1)
    info2 = get_functional_info(func2)
    
    # Overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {func1}")
        if info1:
            st.markdown(f"""
            <div class="info-card">
                <p><b>Type:</b> {info1.get('type', 'Unknown')}</p>
                <p><b>Year:</b> {info1.get('year', 'N/A')}</p>
                <p><b>Accuracy:</b> {info1.get('accuracy', 'N/A')}</p>
                <p><b>Cost:</b> {info1.get('cost', 'N/A')}</p>
                <p><b>Use Case:</b> {info1.get('use_case', 'General')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {func2}")
        if info2:
            st.markdown(f"""
            <div class="info-card">
                <p><b>Type:</b> {info2.get('type', 'Unknown')}</p>
                <p><b>Year:</b> {info2.get('year', 'N/A')}</p>
                <p><b>Accuracy:</b> {info2.get('accuracy', 'N/A')}</p>
                <p><b>Cost:</b> {info2.get('cost', 'N/A')}</p>
                <p><b>Use Case:</b> {info2.get('use_case', 'General')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhancement factor comparison
    st.markdown("### 📈 Enhancement Factor Comparison")
    
    with st.spinner("Calculating comparison..."):
        comparison = compare_functionals_simple(func1, func2, s_range=(0.0, 4.0), n_points=200)
    
    if comparison is None:
        st.error("❌ Failed to compare functionals")
        st.stop()
    
    # Create comparison plot
    fig_comp = go.Figure()
    
    # First functional
    fig_comp.add_trace(go.Scatter(
        x=comparison['s'],
        y=comparison['F1'],
        mode='lines',
        name=func1,
        line=dict(color='#667eea', width=3),
        hovertemplate=f'{func1}<br>s: %{{x:.3f}}<br>F_x: %{{y:.3f}}<extra></extra>'
    ))
    
    # Second functional
    fig_comp.add_trace(go.Scatter(
        x=comparison['s'],
        y=comparison['F2'],
        mode='lines',
        name=func2,
        line=dict(color='#e74c3c', width=3),
        hovertemplate=f'{func2}<br>s: %{{x:.3f}}<br>F_x: %{{y:.3f}}<extra></extra>'
    ))
    
    fig_comp.update_layout(
        title=f"Enhancement Factor: {func1} vs {func2}",
        xaxis_title="Reduced Gradient s",
        yaxis_title="Enhancement Factor F_x(s)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Difference plot
    st.markdown("### 📊 Difference Plot")
    
    fig_diff = go.Figure()
    
    fig_diff.add_trace(go.Scatter(
        x=comparison['s'],
        y=comparison['diff'],
        mode='lines',
        name='Difference',
        line=dict(color='#9b59b6', width=3),
        fill='tozeroy',
        fillcolor='rgba(155, 89, 182, 0.2)',
        hovertemplate='s: %{x:.3f}<br>ΔF_x: %{y:.3f}<extra></extra>'
    ))
    
    fig_diff.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig_diff.update_layout(
        title=f"Difference: {func1} - {func2}",
        xaxis_title="Reduced Gradient s",
        yaxis_title=f"ΔF_x = F_x({func1}) - F_x({func2})",
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig_diff, use_container_width=True)
    
    # Statistics
    st.markdown("### 📊 Comparison Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{comparison['max_diff']:.3f}</div>
            <div class="metric-label">Maximum Difference</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{comparison['max_diff_location']:.2f}</div>
            <div class="metric-label">Location of Max Diff (s)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_diff = np.mean(np.abs(comparison['diff']))
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_diff:.3f}</div>
            <div class="metric-label">Average |Difference|</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Interpretation
    st.markdown("### 🔍 What Does This Mean?")
    
    if comparison['max_diff'] < 0.1:
        st.success(f"✅ **{func1}** and **{func2}** are very similar (max difference < 0.1)")
    elif comparison['max_diff'] < 0.3:
        st.info(f"ℹ️ **{func1}** and **{func2}** show moderate differences")
    else:
        st.warning(f"⚠️ **{func1}** and **{func2}** are quite different (max difference > 0.3)")
    
    st.markdown(f"""
    **Key Points:**
    - Maximum difference occurs at s = {comparison['max_diff_location']:.2f}
    - This corresponds to {'low' if comparison['max_diff_location'] < 1 else 'moderate' if comparison['max_diff_location'] < 2 else 'high'} density gradients
    - {'Small' if comparison['max_diff'] < 0.2 else 'Large'} differences suggest {'similar' if comparison['max_diff'] < 0.2 else 'different'} behavior for real systems
    """)

else:
    # ==================== RECOMMENDATIONS ====================
    
    st.markdown(f"## 💡 Functional Recommendations for: {use_case.replace('_', ' ').title()}")
    
    # Get recommendations
    recommended = get_functional_recommendations(use_case)
    
    st.markdown(f"""
    Based on your use case (**{use_case.replace('_', ' ')}**), here are the recommended functionals:
    """)
    
    # Display recommendations
    for i, func_name in enumerate(recommended, 1):
        info = get_functional_info(func_name)
        
        if info:
            st.markdown(f"""
            <div class="ladder-rung">
                <span class="rung-number">{i}</span>
                <div style="display: inline-block; vertical-align: top; width: calc(100% - 60px);">
                    <h3 style="margin-top: 0;">{func_name}</h3>
                    <p><b>Type:</b> {info.get('type', 'Unknown')}</p>
                    <p><b>Description:</b> {info.get('description', 'N/A')}</p>
                    <p><b>Best for:</b> {info.get('use_case', 'General purpose')}</p>
                    <p><b>Accuracy:</b> {info.get('accuracy', 'N/A')} | <b>Cost:</b> {info.get('cost', 'N/A')}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Use case specific advice
    st.markdown("### 🎯 Specific Advice")
    
    advice_map = {
        'molecules': """
        For **molecular systems**:
        - B3LYP is the gold standard (most benchmarked)
        - PBE0 is a good alternative with better thermochemistry
        - wB97X includes dispersion corrections (important for large molecules)
        - Start with B3LYP, then try others if needed
        """,
        'solids': """
        For **solid-state systems**:
        - PBE is the workhorse (fast, reliable)
        - PBEsol improves lattice constants
        - HSE06 for band gaps (screened hybrid, affordable)
        - SCAN is modern and accurate (no exact exchange)
        """,
        'fast': """
        For **fast calculations**:
        - LDA is fastest but least accurate
        - PBE is best balance (fast GGA)
        - Avoid hybrids (4-10x slower)
        - Use for geometry optimization, then refine with better functional
        """,
        'accurate': """
        For **high accuracy**:
        - wB97X for molecules (range-separated)
        - M06-2X for thermochemistry
        - SCAN for general purpose (no exact exchange)
        - PBE0 for solids with band gaps
        """,
        'thermochemistry': """
        For **thermochemistry**:
        - B3LYP is well-benchmarked
        - M06-2X often outperforms B3LYP
        - wB97X includes dispersion
        - Always use large basis sets (def2-TZVP or better)
        """,
        'band_gaps': """
        For **band gap calculations**:
        - HSE06 is the standard (screened hybrid)
        - PBE0 also works well
        - GGAs severely underestimate gaps
        - meta-GGAs (SCAN) are better than GGA but still underestimate
        """,
        'weak_interactions': """
        For **weak interactions** (van der Waals):
        - wB97X includes dispersion corrections
        - M06-2X designed for non-covalent interactions
        - Standard GGAs (PBE, BLYP) fail for dispersion
        - Consider DFT-D3 corrections with any functional
        """
    }
    
    if use_case in advice_map:
        st.info(advice_map[use_case])
    else:
        st.info(advice_map['general'])
    
    # Quick comparison
    st.markdown("### ⚖️ Quick Comparison")
    
    if len(recommended) >= 2:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Compare {recommended[0]} vs {recommended[1]}", use_container_width=True):
                st.session_state.view_mode_override = "Comparison Mode"
                st.session_state.func1_override = recommended[0]
                st.session_state.func2_override = recommended[1]
                st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><b>XC Functionals Module</b> - Part of DFT Flight Simulator</p>
    <p style="font-size: 0.9rem;">Functional data from <a href="https://www.tddft.org/programs/libxc/" target="_blank">Libxc</a></p>
</div>
""", unsafe_allow_html=True)
