import streamlit as st
import basis_set_exchange as bse
import numpy as np
import plotly.graph_objects as go
from collections import defaultdict
import json
from pathlib import Path
from datetime import datetime

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Basis Set Visualizer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CACHE_DIR = Path(__file__).parent / "basis_cache"
METADATA_FILE = CACHE_DIR / "metadata.json"

# ==================== STYLING ====================
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
    }
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .comparison-card {
        background: #f8f9fa;
        border: 2px solid #667eea;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    th {
        background-color: #667eea !important;
        color: white !important;
        padding: 12px !important;
        text-align: center !important;
        font-weight: 600 !important;
    }
    td {
        padding: 10px !important;
        text-align: center !important;
        border-bottom: 1px solid #ddd !important;
        background-color: white !important;
        color: #333 !important;
    }
    tr:hover td {
        background-color: #f5f5f5 !important;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .element-available {
        background-color: #667eea !important;
        color: white !important;
    }
    .element-available:hover {
        background-color: #5568d3 !important;
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# ==================== CACHE FUNCTIONS ====================
@st.cache_data
def load_cache():
    """Load local cache - FAST!"""
    if not METADATA_FILE.exists():
        st.error("⚠️ Cache not found! Run: `python3 download_basis_cache.py`")
        st.stop()
    
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

@st.cache_data
def get_basis_data(basis_name, element_z):
    """Fetch basis data with caching"""
    return bse.get_basis(basis_name, elements=str(element_z))

# ==================== ELEMENT DATA ====================
ELEMENTS = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar',
    19: 'K', 20: 'Ca', 21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 
    27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
    37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 
    45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn', 51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe',
    55: 'Cs', 56: 'Ba', 57: 'La', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 
    77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg', 81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn'
}

ELEMENT_NAMES = {
    1: 'Hydrogen', 2: 'Helium', 3: 'Lithium', 4: 'Beryllium', 5: 'Boron', 6: 'Carbon', 
    7: 'Nitrogen', 8: 'Oxygen', 9: 'Fluorine', 10: 'Neon', 11: 'Sodium', 12: 'Magnesium',
    13: 'Aluminum', 14: 'Silicon', 15: 'Phosphorus', 16: 'Sulfur', 17: 'Chlorine', 18: 'Argon',
    19: 'Potassium', 20: 'Calcium', 21: 'Scandium', 22: 'Titanium', 23: 'Vanadium', 24: 'Chromium',
    25: 'Manganese', 26: 'Iron', 27: 'Cobalt', 28: 'Nickel', 29: 'Copper', 30: 'Zinc',
    31: 'Gallium', 32: 'Germanium', 33: 'Arsenic', 34: 'Selenium', 35: 'Bromine', 36: 'Krypton',
    37: 'Rubidium', 38: 'Strontium', 39: 'Yttrium', 40: 'Zirconium', 41: 'Niobium', 42: 'Molybdenum',
    43: 'Technetium', 44: 'Ruthenium', 45: 'Rhodium', 46: 'Palladium', 47: 'Silver', 48: 'Cadmium',
    49: 'Indium', 50: 'Tin', 51: 'Antimony', 52: 'Tellurium', 53: 'Iodine', 54: 'Xenon',
    55: 'Cesium', 56: 'Barium', 57: 'Lanthanum', 72: 'Hafnium', 73: 'Tantalum', 74: 'Tungsten',
    75: 'Rhenium', 76: 'Osmium', 77: 'Iridium', 78: 'Platinum', 79: 'Gold', 80: 'Mercury',
    81: 'Thallium', 82: 'Lead', 83: 'Bismuth', 84: 'Polonium', 85: 'Astatine', 86: 'Radon'
}

PERIODIC_TABLE = [
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 7, 8, 9, 10],
    [11, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 14, 15, 16, 17, 18],
    [19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
    [37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54],
    [55, 56, 57, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86],
]

# ==================== VISUALIZATION ====================
def create_orbital_3d(basis_data, orbital_type='s'):
    """Fast 3D orbital visualization"""
    element_data = list(basis_data['elements'].values())[0]
    shells = element_data['electron_shells']
    
    # Find shell
    shell = None
    for s in shells:
        am = s['angular_momentum'][0]
        if (am == 0 and 's' in orbital_type) or \
           (am == 1 and 'p' in orbital_type) or \
           (am == 2 and 'd' in orbital_type):
            shell = s
            break
    
    if not shell:
        return None
    
    # Smaller grid for speed
    grid_range = 2.5
    grid_points = 35
    x = np.linspace(-grid_range, grid_range, grid_points)
    y = np.linspace(-grid_range, grid_range, grid_points)
    z = np.linspace(-grid_range, grid_range, grid_points)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    
    r_sq = X**2 + Y**2 + Z**2
    r = np.sqrt(r_sq + 1e-10)
    
    # Get Gaussian parameters
    exps = np.array([float(e) for e in shell['exponents']])
    coeffs = np.array([float(c) for c in shell['coefficients'][0]])
    
    # Radial part
    psi = np.zeros_like(X)
    for exp, coeff in zip(exps, coeffs):
        psi += coeff * np.exp(-exp * r_sq)
    
    # Angular part
    am = shell['angular_momentum'][0]
    if am == 1:  # p-orbital
        if 'x' in orbital_type:
            psi *= X / r
        elif 'y' in orbital_type:
            psi *= Y / r
        else:
            psi *= Z / r
    elif am == 2:  # d-orbital (simplified)
        psi *= (3*Z**2 - r_sq) / (r_sq + 1e-10)
    
    # Create figure
    fig = go.Figure(data=go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=psi.flatten(),
        isomin=-0.05,
        isomax=0.05,
        surface_count=4,
        colorscale='RdBu',
        opacity=0.7,
        caps=dict(x_show=False, y_show=False, z_show=False),
        showscale=False
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='cube',
            camera=dict(eye=dict(x=1.3, y=1.3, z=1.3))
        ),
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_comparison_visual(data1, data2, name1, name2):
    """Visual comparison of two basis sets"""
    
    def analyze_basis(data):
        elem_data = list(data['elements'].values())[0]
        shells = elem_data['electron_shells']
        
        total_prim = sum(len(s['exponents']) for s in shells)
        total_contr = sum(len(s['coefficients']) for s in shells)
        
        # Count by angular momentum (handle all types including g, h, etc.)
        am_count = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for s in shells:
            am = s['angular_momentum'][0]
            if am in am_count:
                am_count[am] += 1
            else:
                am_count[am] = 1
        
        return {
            'primitives': total_prim,
            'contracted': total_contr,
            's_shells': am_count.get(0, 0),
            'p_shells': am_count.get(1, 0),
            'd_shells': am_count.get(2, 0),
            'f_shells': am_count.get(3, 0),
            'g_shells': am_count.get(4, 0)
        }
    
    info1 = analyze_basis(data1)
    info2 = analyze_basis(data2)
    
    # Create comparison chart
    fig = go.Figure()
    
    categories = ['Primitives', 'Contracted', 's-shells', 'p-shells', 'd-shells', 'f-shells', 'g-shells']
    values1 = [info1['primitives'], info1['contracted'], info1['s_shells'], 
               info1['p_shells'], info1['d_shells'], info1['f_shells'], info1['g_shells']]
    values2 = [info2['primitives'], info2['contracted'], info2['s_shells'], 
               info2['p_shells'], info2['d_shells'], info2['f_shells'], info2['g_shells']]
    
    fig.add_trace(go.Bar(
        name=name1,
        x=categories,
        y=values1,
        marker_color='#667eea',
        text=values1,
        textposition='auto',
    ))
    
    fig.add_trace(go.Bar(
        name=name2,
        x=categories,
        y=values2,
        marker_color='#764ba2',
        text=values2,
        textposition='auto',
    ))
    
    fig.update_layout(
        barmode='group',
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(text='<b>Basis Set Comparison</b>', x=0.5, xanchor='center'),
        xaxis_title='Property',
        yaxis_title='Count',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig, info1, info2

def show_basis_details(basis_data, basis_name):
    """Display basis set information with educational context"""
    elem_data = list(basis_data['elements'].values())[0]
    shells = elem_data['electron_shells']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_prim = sum(len(s['exponents']) for s in shells)
    total_contr = sum(len(s['coefficients']) for s in shells)
    
    with col1:
        st.metric("Family", basis_data.get('family', 'N/A'))
    with col2:
        st.metric("Total Shells", len(shells))
    with col3:
        st.metric("Primitives", total_prim)
    with col4:
        st.metric("Contracted", total_contr)
    
    # Shell table - using native Streamlit instead of HTML
    st.markdown("#### 📊 Shell Structure")
    
    am_map = {0: 's', 1: 'p', 2: 'd', 3: 'f', 4: 'g', 5: 'h'}
    
    # Create data for table
    table_data = []
    for i, shell in enumerate(shells):
        am = shell['angular_momentum'][0]
        am_letter = am_map.get(am, '?')
        n_prim = len(shell['exponents'])
        n_contr = len(shell['coefficients'])
        
        exps = [float(e) for e in shell['exponents']]
        exp_range = f"{min(exps):.2e} - {max(exps):.2e}"
        
        table_data.append({
            'Shell': f"#{i+1}",
            'Type': am_letter.upper(),
            'Primitives': n_prim,
            'Contractions': n_contr,
            'Exponent Range': exp_range
        })
    
    # Display as columns for better visibility
    cols = st.columns([1, 1, 2, 2, 3])
    with cols[0]:
        st.markdown("**Shell**")
        for row in table_data:
            st.text(row['Shell'])
    with cols[1]:
        st.markdown("**Type**")
        for row in table_data:
            st.markdown(f"**:blue[{row['Type']}]**")
    with cols[2]:
        st.markdown("**Primitives**")
        for row in table_data:
            st.text(row['Primitives'])
    with cols[3]:
        st.markdown("**Contractions**")
        for row in table_data:
            st.text(row['Contractions'])
    with cols[4]:
        st.markdown("**Exponent Range**")
        for row in table_data:
            st.code(row['Exponent Range'], language=None)
    
    # Educational info
    with st.expander("📚 What do these numbers mean?"):
        st.markdown("""
        **Primitives (Gaussian Functions):** The basic building blocks - individual Gaussian functions.
        More primitives = more flexible but more expensive.
        
        **Contractions:** Linear combinations of primitives. Reduces computational cost while maintaining accuracy.
        
        **Shell Types:**
        - **s-shells:** Spherical, describe core electrons
        - **p-shells:** Dumbbell-shaped, describe valence electrons  
        - **d-shells:** Polarization functions, improve bonding description
        - **f-shells:** Higher polarization, for very accurate calculations
        
        **Zeta (ζ):**
        - **Single-ζ (SZ):** One function per orbital (e.g., STO-3G)
        - **Double-ζ (DZ):** Two functions per orbital (e.g., 6-31G)
        - **Triple-ζ (TZ):** Three functions per orbital (e.g., cc-pVTZ)
        
        **More functions = More accurate but slower calculations**
        """)

# ==================== MAIN APP ====================
def main():
    # Header
    st.markdown('<h1 class="main-header">⚛️ Basis Set Visualizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Learning Tool for Quantum Chemistry</p>', unsafe_allow_html=True)
    
    # Load cache
    cache = load_cache()
    
    # Cache info
    age_days = (datetime.now() - datetime.fromisoformat(cache['download_date'])).days
    st.sidebar.success(f"✅ Loaded {len(cache['basis_sets'])} basis sets (cache: {age_days} days old)")
    
    # Organize by family
    basis_by_family = defaultdict(list)
    for name, meta in cache['basis_sets'].items():
        basis_by_family[meta['family']].append(name)
    
    # ==================== SIDEBAR ====================
    st.sidebar.markdown("## ⚙️ Configuration")
    
    # Family filter
    families = sorted(basis_by_family.keys())
    family = st.sidebar.selectbox(
        "📁 Filter by Family:",
        ['All'] + families,
        help="Basis sets grouped by mathematical family"
    )
    
    # Get available basis sets
    if family == 'All':
        available = sorted(cache['basis_sets'].keys())
    else:
        available = sorted(basis_by_family[family])
    
    # Basis selection
    basis_name = st.sidebar.selectbox(
        "🎯 Select Basis Set:",
        available,
        help="Choose a basis set to explore"
    )
    
    # Show basis info
    if basis_name in cache['basis_sets']:
        meta = cache['basis_sets'][basis_name]
        st.sidebar.markdown(f"""
        <div class="info-card">
            <b>Family:</b> {meta['family']}<br>
            <b>Role:</b> {meta['role']}<br>
            <b>Elements:</b> {len(meta['available_elements'])}
        </div>
        """, unsafe_allow_html=True)
    
    # Comparison mode
    st.sidebar.markdown("---")
    compare_mode = st.sidebar.checkbox("🔬 Enable Comparison Mode", help="Compare two basis sets")
    
    basis_name_2 = None
    if compare_mode:
        basis_name_2 = st.sidebar.selectbox(
            "Second Basis Set:",
            available,
            key='basis2'
        )
    
    # Export format
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥 Export Format")
    formats = {
        'Gaussian': 'gaussian94',
        'ORCA': 'orca',
        'NWChem': 'nwchem',
        'PySCF': 'pyscf',
        'Psi4': 'psi4',
        'GAMESS-US': 'gamess_us',
    }
    export_tool = st.sidebar.selectbox("Software:", list(formats.keys()))
    export_fmt = formats[export_tool]
    
    # ==================== PERIODIC TABLE ====================
    st.markdown("## 🧪 Select Element")
    
    available_elements = cache['basis_sets'][basis_name]['available_elements']
    
    # Display table
    for row in PERIODIC_TABLE:
        cols = st.columns(18)
        for col_idx, z in enumerate(row):
            with cols[col_idx]:
                if z > 0:
                    symbol = ELEMENTS.get(z, '')
                    is_avail = z in available_elements
                    
                    if is_avail:
                        if st.button(
                            f"**{symbol}**\n{z}",
                            key=f"e_{z}",
                            use_container_width=True,
                            type="primary" if st.session_state.get('element') == z else "secondary"
                        ):
                            st.session_state.element = z
                            st.rerun()
                    else:
                        st.button(f"{symbol}\n{z}", key=f"e_{z}", disabled=True, use_container_width=True)
    
    st.caption(f"✅ {len(available_elements)} elements available")
    
    # ==================== VISUALIZATION ====================
    if 'element' in st.session_state:
        z = st.session_state.element
        symbol = ELEMENTS.get(z, f"Z={z}")
        full_name = ELEMENT_NAMES.get(z, symbol)
        
        st.markdown("---")
        st.markdown(f"## 🎨 {full_name} ({symbol}) - Atomic Number {z}")
        
        # Fetch data
        basis_data = get_basis_data(basis_name, z)
        
        if compare_mode and basis_name_2:
            try:
                basis_data_2 = get_basis_data(basis_name_2, z)
            except:
                st.warning(f"{symbol} not available in {basis_name_2}")
                basis_data_2 = None
        else:
            basis_data_2 = None
        
        # Show details
        if compare_mode and basis_data_2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"### {basis_name}")
                show_basis_details(basis_data, basis_name)
            with col2:
                st.markdown(f"### {basis_name_2}")
                show_basis_details(basis_data_2, basis_name_2)
            
            # Visual comparison
            st.markdown("### 📊 Visual Comparison")
            fig_comp, info1, info2 = create_comparison_visual(basis_data, basis_data_2, basis_name, basis_name_2)
            st.plotly_chart(fig_comp, use_container_width=True)
            
            # Side-by-side orbitals
            st.markdown("### 🌌 Orbital Comparison")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{basis_name}**")
                fig1 = create_orbital_3d(basis_data, 's')
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.markdown(f"**{basis_name_2}**")
                fig2 = create_orbital_3d(basis_data_2, 's')
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Educational comparison
            st.markdown("### 📚 What's the Difference?")
            
            diff_text = ""
            if info1['primitives'] > info2['primitives']:
                diff_text += f"✓ **{basis_name}** uses more primitive Gaussians ({info1['primitives']} vs {info2['primitives']}) → More flexible but slower\n\n"
            elif info1['primitives'] < info2['primitives']:
                diff_text += f"✓ **{basis_name_2}** uses more primitive Gaussians ({info2['primitives']} vs {info1['primitives']}) → More flexible but slower\n\n"
            
            if info1['d_shells'] > 0 and info2['d_shells'] == 0:
                diff_text += f"✓ **{basis_name}** includes polarization (d-functions) → Better for bonding\n\n"
            elif info2['d_shells'] > 0 and info1['d_shells'] == 0:
                diff_text += f"✓ **{basis_name_2}** includes polarization (d-functions) → Better for bonding\n\n"
            
            if diff_text:
                st.info(diff_text)
        
        else:
            # Single basis view
            show_basis_details(basis_data, basis_name)
            
            # Orbital visualization
            st.markdown("### 🌌 3D Orbital Visualization")
            
            # Get available orbitals with proper labeling
            elem_data = list(basis_data['elements'].values())[0]
            shells = elem_data['electron_shells']
            
            orbital_options = []
            orbital_labels = []
            s_count = 0
            p_count = 0
            d_count = 0
            
            for i, s in enumerate(shells):
                am = s['angular_momentum'][0]
                if am == 0:
                    s_count += 1
                    orbital_options.append('s')
                    orbital_labels.append(f"Shell #{i+1}: {s_count}s orbital (spherical)")
                elif am == 1:
                    p_count += 1
                    orbital_options.extend(['p_x', 'p_y', 'p_z'])
                    orbital_labels.extend([
                        f"Shell #{i+1}: {p_count}p_x orbital (along x-axis)",
                        f"Shell #{i+1}: {p_count}p_y orbital (along y-axis)",
                        f"Shell #{i+1}: {p_count}p_z orbital (along z-axis)"
                    ])
                elif am == 2:
                    d_count += 1
                    orbital_options.append('d')
                    orbital_labels.append(f"Shell #{i+1}: {d_count}d orbital (cloverleaf)")
            
            if orbital_options:
                # Create mapping for display
                orbital_dict = {label: opt for label, opt in zip(orbital_labels, orbital_options)}
                
                selected_label = st.selectbox(
                    "Select Orbital Type:",
                    orbital_labels,
                    help="Choose which orbital to visualize in 3D"
                )
                
                orbital = orbital_dict[selected_label]
                
                # Show info about selected orbital
                st.info(f"**Visualizing:** {selected_label}")
                
                fig = create_orbital_3d(basis_data, orbital)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("3D visualization not available for this orbital type")
        
        # Download
        st.markdown("### 📥 Download")
        try:
            basis_text = bse.get_basis(basis_name, elements=str(z), fmt=export_fmt, header=True)
            st.download_button(
                f"Download {basis_name} for {symbol} ({export_tool})",
                basis_text,
                f"{basis_name}_{symbol}.txt",
                use_container_width=True
            )
            
            with st.expander("View Format"):
                st.code(basis_text, language='text')
        except Exception as e:
            st.error(f"Export error: {e}")

if __name__ == "__main__":
    main()
