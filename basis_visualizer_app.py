import streamlit as st
import basis_set_exchange as bse
import numpy as np
import plotly.graph_objects as go
from collections import defaultdict
import json
from pathlib import Path
from datetime import datetime
from comparison_utils import create_comparison_table, display_comparison_table

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
    """Fetch basis set data with caching - returns None if not available"""
    basis_info = bse.get_basis(basis_name)
    if str(element_z) not in basis_info['elements']:
        return None
    return bse.get_basis(basis_name, elements=str(element_z))

def analyze_basis_intelligence(basis_data, basis_name):
    """Intelligent analysis of basis set characteristics"""
    elem_data = list(basis_data['elements'].values())[0]
    shells = elem_data['electron_shells']
    
    analysis = {
        'type': 'Unknown',
        'zeta': 'Unknown',
        'polarization': False,
        'diffuse': False,
        'sto_or_gto': 'GTO',  # BSE only has GTOs
        'explanation': ''
    }
    
    # Count shells by type
    s_shells = sum(1 for s in shells if s['angular_momentum'][0] == 0)
    p_shells = sum(1 for s in shells if s['angular_momentum'][0] == 1)
    d_shells = sum(1 for s in shells if s['angular_momentum'][0] == 2)
    f_shells = sum(1 for s in shells if s['angular_momentum'][0] == 3)
    
    # Detect zeta level
    if s_shells == 1:
        analysis['zeta'] = 'Single-ζ (SZ)'
    elif s_shells == 2:
        analysis['zeta'] = 'Double-ζ (DZ)'
    elif s_shells == 3:
        analysis['zeta'] = 'Triple-ζ (TZ)'
    elif s_shells == 4:
        analysis['zeta'] = 'Quadruple-ζ (QZ)'
    elif s_shells >= 5:
        analysis['zeta'] = f'{s_shells}-ζ (Very High Quality)'
    
    # Detect polarization
    if d_shells > 0:
        analysis['polarization'] = True
        analysis['pol_level'] = 'd-polarization'
    if f_shells > 0:
        analysis['polarization'] = True
        analysis['pol_level'] = 'f-polarization (very high)'
    
    # Detect diffuse (check for very small exponents)
    min_exp = min(float(e) for s in shells for e in s['exponents'])
    if min_exp < 0.1:
        analysis['diffuse'] = True
    
    # Build explanation
    exp = f"**{basis_name}** is a **{analysis['zeta']}** basis set"
    
    if 'STO' in basis_name.upper():
        exp += " using **Slater-Type Orbitals (STO)** contracted with Gaussians"
    else:
        exp += " using **Gaussian-Type Orbitals (GTO)**"
    
    exp += f"\n\n**What this means:**\n"
    exp += f"- **Zeta ({analysis['zeta']}):** Uses {s_shells} functions per core orbital → "
    if s_shells == 1:
        exp += "Minimal basis, fast but less accurate"
    elif s_shells == 2:
        exp += "Good balance of speed and accuracy"
    elif s_shells >= 3:
        exp += "High accuracy, more expensive"
    
    if analysis['polarization']:
        exp += f"\n- **Polarization ({analysis['pol_level']}):** Includes {d_shells} d-shells"
        if f_shells > 0:
            exp += f" and {f_shells} f-shells"
        exp += " → Better for bonding and molecular properties"
    else:
        exp += "\n- **No polarization:** May struggle with bonding, good for isolated atoms"
    
    if analysis['diffuse']:
        exp += "\n- **Diffuse functions:** Includes very diffuse (spread out) functions → Better for anions, excited states"
    
    analysis['explanation'] = exp
    
    return analysis

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
@st.cache_data(show_spinner=False)
def create_orbital_3d(basis_data, orbital_type):
    """Fast 3D orbital visualization with caching"""
    element_data = list(basis_data['elements'].values())[0]
    shells = element_data['electron_shells']
    
    # Find shell
    shell = None
    for s in shells:
        am = s['angular_momentum'][0]
        if (am == 0 and 's' in orbital_type) or \
           (am == 1 and 'p' in orbital_type) or \
           (am == 2 and 'd' in orbital_type) or \
           (am == 3 and 'f' in orbital_type):
            shell = s
            break
    
    if not shell:
        return None
    
    # OPTIMIZED RESOLUTION - balance between quality and speed
    if 'p' in orbital_type:
        grid_range = 4.0
        grid_points = 45  # Reduced from 60 for speed
    elif 'd' in orbital_type:
        grid_range = 3.5
        grid_points = 50  # Reduced from 65 for speed
    elif 'f' in orbital_type:
        grid_range = 4.0
        grid_points = 50  # Reduced from 70 for speed
    else:
        grid_range = 3.0
        grid_points = 45  # Reduced from 60 for speed
    
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
    elif am == 2:  # d-orbital
        psi *= (3*Z**2 - r_sq) / (r_sq + 1e-10)
    elif am == 3:  # f-orbital (simplified - f_z3 type)
        psi *= Z * (5*Z**2 - 3*r_sq) / (r_sq**1.5 + 1e-10)
    
    # Create beautiful 3D orbital - separate positive and negative lobes
    fig = go.Figure()
    
    # Calculate adaptive threshold based on actual wavefunction values
    psi_max = np.max(np.abs(psi))
    threshold = psi_max * 0.15  # 15% of maximum value
    
    # Positive lobe (warm colors - orange/red)
    fig.add_trace(go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=psi.flatten(),
        isomin=threshold * 0.3,  # Show more of the lobe
        isomax=psi_max,
        surface_count=2,
        colorscale=[
            [0.0, '#FFCB8E'],   # Light orange
            [0.5, '#F58E53'],   # Medium orange
            [1.0, '#B40426']    # Deep red-orange
        ],
        opacity=0.88,
        caps=dict(x_show=False, y_show=False, z_show=False),
        showscale=False,
        lighting=dict(
            ambient=0.6,
            diffuse=0.9,
            specular=1.5,
            roughness=0.05,
            fresnel=0.5
        ),
        lightposition=dict(x=100, y=200, z=150),
        flatshading=False,
        contour=dict(show=False)
    ))
    
    # Negative lobe (cool colors - blue/cyan)
    psi_min = np.min(psi)
    fig.add_trace(go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=psi.flatten(),
        isomin=psi_min,
        isomax=-threshold * 0.3,  # Show more of the lobe
        surface_count=2,
        colorscale=[
            [0.0, '#3B4CC0'],    # Deep blue
            [0.5, '#6788EE'],    # Medium blue
            [1.0, '#9ABBFF']     # Light blue
        ],
        opacity=0.88,
        caps=dict(x_show=False, y_show=False, z_show=False),
        showscale=False,
        lighting=dict(
            ambient=0.6,
            diffuse=0.9,
            specular=1.5,
            roughness=0.05,
            fresnel=0.5
        ),
        lightposition=dict(x=100, y=200, z=150),
        flatshading=False,
        contour=dict(show=False)
    ))
    
    # Add XYZ coordinate axes
    axis_length = grid_range * 0.8
    
    # X-axis (red)
    fig.add_trace(go.Scatter3d(
        x=[0, axis_length], y=[0, 0], z=[0, 0],
        mode='lines+text',
        line=dict(color='red', width=4),
        text=['', 'X'],
        textposition='top center',
        textfont=dict(size=14, color='red', family='Arial Black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Y-axis (green)
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, axis_length], z=[0, 0],
        mode='lines+text',
        line=dict(color='green', width=4),
        text=['', 'Y'],
        textposition='top center',
        textfont=dict(size=14, color='green', family='Arial Black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Z-axis (blue)
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[0, axis_length],
        mode='lines+text',
        line=dict(color='blue', width=4),
        text=['', 'Z'],
        textposition='top center',
        textfont=dict(size=14, color='blue', family='Arial Black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Origin point
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(size=6, color='black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-grid_range, grid_range]),
            yaxis=dict(visible=False, range=[-grid_range, grid_range]),
            zaxis=dict(visible=False, range=[-grid_range, grid_range]),
            aspectmode='cube',
            bgcolor='rgb(245, 245, 250)',  # Light background for better contrast
            camera=dict(
                eye=dict(x=1.4, y=1.4, z=1.4),
                center=dict(x=0, y=0, z=0)
            )
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='white',
        showlegend=False
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
        marker_color='#3b82f6',  # Bright blue
        marker_line_color='#1e40af',
        marker_line_width=1.5,
        text=values1,
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial Black'),
    ))
    
    fig.add_trace(go.Bar(
        name=name2,
        x=categories,
        y=values2,
        marker_color='#f59e0b',  # Bright orange
        marker_line_color='#b45309',
        marker_line_width=1.5,
        text=values2,
        textposition='auto',
        textfont=dict(size=12, color='white', family='Arial Black'),
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
    st.markdown("#### Shell Structure")
    
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
    
    # DYNAMIC Educational info based on THIS basis set (NO EXPANDER - will be nested)
    # This is shown directly since it may be called from within an expander

# ==================== MAIN APP ====================
def main():
    # Header
    st.markdown('<h1 class="main-header">Basis Set Visualizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive Learning Tool for Quantum Chemistry</p>', unsafe_allow_html=True)
    
    # Load cache
    cache = load_cache()
    
    # Cache info
    age_days = (datetime.now() - datetime.fromisoformat(cache['download_date'])).days
    st.sidebar.success(f"Loaded {len(cache['basis_sets'])} basis sets (cache: {age_days} days old)")
    
    # Organize by family
    basis_by_family = defaultdict(list)
    for name, meta in cache['basis_sets'].items():
        basis_by_family[meta['family']].append(name)
    
    # ==================== SIDEBAR ====================
    st.sidebar.markdown("## Configuration")
    
    # Family filter
    families = sorted(basis_by_family.keys())
    family = st.sidebar.selectbox(
        "Filter by Family:",
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
        "Select Basis Set:",
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
    compare_mode = st.sidebar.checkbox("Enable Comparison Mode", help="Compare two basis sets")
    
    basis_name_2 = None
    if compare_mode:
        basis_name_2 = st.sidebar.selectbox(
            "Second Basis Set:",
            available,
            key='basis2'
        )
        
        # Show details for second basis set
        if basis_name_2:
            meta2 = cache['basis_sets'][basis_name_2]
            st.sidebar.markdown(f"""
            <div class="info-card">
                <b>Family:</b> {meta2['family']}<br>
                <b>Role:</b> {meta2['role']}<br>
                <b>Elements:</b> {len(meta2['available_elements'])}
            </div>
            """, unsafe_allow_html=True)
    
    # Export format
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Export Format")
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
    
    # ==================== PERIODIC TABLE (COLLAPSIBLE) ====================
    available_elements = cache['basis_sets'][basis_name]['available_elements']
    
    with st.expander(f"Select Element ({len(available_elements)} available)", expanded=False):
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
    
    # ==================== VISUALIZATION ====================
    if 'element' in st.session_state:
        z = st.session_state.element
        symbol = ELEMENTS.get(z, f"Z={z}")
        full_name = ELEMENT_NAMES.get(z, symbol)
        
        st.markdown("---")
        st.markdown(f"## {full_name} ({symbol}) - Atomic Number {z}")
        
        # Fetch data with error checking
        basis_data = get_basis_data(basis_name, z)
        if basis_data is None:
            st.error(f"Element {symbol} (Z={z}) not available in {basis_name}")
            st.info("Please select a different element from the periodic table above.")
            return
        
        if compare_mode and basis_name_2:
            basis_data_2 = get_basis_data(basis_name_2, z)
            if basis_data_2 is None:
                st.error(f"Element {symbol} (Z={z}) not available in {basis_name_2}")
                st.info("Showing only the first basis set. Select a different element or basis set for comparison.")
        else:
            basis_data_2 = None
        
        # Show details
        if compare_mode and basis_data_2:
            # Get intelligent analysis FIRST
            analysis1 = analyze_basis_intelligence(basis_data, basis_name)
            analysis2 = analyze_basis_intelligence(basis_data_2, basis_name_2)
            
            # SECTION 1: Basis Set Details (Collapsible)
            with st.expander("Basis Set Details", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {basis_name}")
                    show_basis_details(basis_data, basis_name)
                    st.markdown("#### Understanding This Basis Set")
                    st.info(f"**{analysis1['zeta']}**\n\n{analysis1['explanation']}")
                with col2:
                    st.markdown(f"### {basis_name_2}")
                    show_basis_details(basis_data_2, basis_name_2)
                    st.markdown("#### Understanding This Basis Set")
                    st.info(f"**{analysis2['zeta']}**\n\n{analysis2['explanation']}")
            
            # SECTION 2: Similarity & Difference Table (Collapsible)
            with st.expander("Detailed Comparison Table", expanded=False):
                comp_df = create_comparison_table(basis_data, basis_data_2, basis_name, basis_name_2, analysis1, analysis2)
                display_comparison_table(comp_df, basis_name, basis_name_2)
            
            # SECTION 3: Orbital Comparison with INDIVIDUAL dropdowns
            # st.markdown("### Orbital Comparison")
            
            # # Get available orbitals for EACH basis set
            # elem_data1 = list(basis_data['elements'].values())[0]
            # elem_data2 = list(basis_data_2['elements'].values())[0]
            
            # am_types_1 = set(s['angular_momentum'][0] for s in elem_data1['electron_shells'])
            # am_types_2 = set(s['angular_momentum'][0] for s in elem_data2['electron_shells'])
            
            # def get_orbital_choices(am_types):
            #     choices = []
            #     if 0 in am_types:
            #         choices.append(('s orbital (spherical)', 's'))
            #     if 1 in am_types:
            #         choices.extend([
            #             ('p_x orbital (along x-axis)', 'p_x'),
            #             ('p_y orbital (along y-axis)', 'p_y'),
            #             ('p_z orbital (along z-axis)', 'p_z')
            #         ])
            #     if 2 in am_types:
            #         choices.append(('d orbital (cloverleaf)', 'd'))
            #     return choices
            
            # orbital_choices_1 = get_orbital_choices(am_types_1)
            # orbital_choices_2 = get_orbital_choices(am_types_2)
            
            # col1, col2 = st.columns(2)
            
            # with col1:
            #     st.markdown(f"**{basis_name}**")
            #     if orbital_choices_1:
            #         selected_orbital_1 = st.selectbox(
            #             f"Select orbital for {basis_name}:",
            #             orbital_choices_1,
            #             format_func=lambda x: x[0],
            #             key="orbital_select_1"
            #         )
            #         orbital_type_1 = selected_orbital_1[1]
            #         fig1 = create_orbital_3d(basis_data, orbital_type_1)
            #         if fig1:
            #             st.plotly_chart(fig1, use_container_width=True, key="orbital_1")
            #     else:
            #         st.warning("No orbitals available")
            
            # with col2:
            #     st.markdown(f"**{basis_name_2}**")
            #     if orbital_choices_2:
            #         selected_orbital_2 = st.selectbox(
            #             f"Select orbital for {basis_name_2}:",
            #             orbital_choices_2,
            #             format_func=lambda x: x[0],
            #             key="orbital_select_2"
            #         )
            #         orbital_type_2 = selected_orbital_2[1]
            #         fig2 = create_orbital_3d(basis_data_2, orbital_type_2)
            #         if fig2:
            #             st.plotly_chart(fig2, use_container_width=True, key="orbital_2")
            #     else:
            #         st.warning("No orbitals available")
            
            # SECTION 4: DYNAMIC Visual Differences - ALWAYS shows something useful
            st.markdown("---")
            st.markdown("### Visual Differences Analysis")
            
            # Get shell counts for BOTH basis sets
            elem_data1 = list(basis_data['elements'].values())[0]
            elem_data2 = list(basis_data_2['elements'].values())[0]
            s_shells_1 = sum(1 for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 0)
            s_shells_2 = sum(1 for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 0)
            p_shells_1 = sum(1 for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 1)
            p_shells_2 = sum(1 for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 2)
            d_shells_1 = sum(1 for s in elem_data1['electron_shells'] if s['angular_momentum'][0] == 2)
            d_shells_2 = sum(1 for s in elem_data2['electron_shells'] if s['angular_momentum'][0] == 2)
            
            # ALWAYS show orbital count bar graph (integrated here)
            fig_orbital_count = go.Figure()
            categories = ['s-shells', 'p-shells', 'd-shells']
            values1 = [s_shells_1, p_shells_1, d_shells_1]
            values2 = [s_shells_2, p_shells_1, d_shells_2]
            
            fig_orbital_count.add_trace(go.Bar(
                name=basis_name,
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
            
            # Detect what's actually different
            zeta_diff = analysis1['zeta'] != analysis2['zeta']
            pol_diff = analysis1['polarization'] != analysis2['polarization']
            
            # COMPREHENSIVE VISUAL EXPLANATIONS - ALL technical details
            
            # 1. MATHEMATICAL FOUNDATION: Show ACTUAL functions from these basis sets
            with st.expander(f"Mathematical Foundation: {basis_name} vs {basis_name_2}", expanded=True):
                # Intelligent basis set type detection
                def detect_basis_type(name):
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
                
                type1, desc1 = detect_basis_type(basis_name)
                type2, desc2 = detect_basis_type(basis_name_2)
                
                st.markdown(f"""
                ### Mathematical Functions from Your Selected Basis Sets
                
                **{basis_name}** ({desc1}):
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
                
                # Show comparison for EACH shell type that exists in EITHER basis set
                r = np.linspace(0, 5, 200)
                shell_names = {'s': 's-orbitals (spherical)', 'p': 'p-orbitals (dumbbell)', 
                               'd': 'd-orbitals (polarization)', 'f': 'f-orbitals (high polarization)'}
                
                for shell_type in ['s', 'p', 'd', 'f']:
                    shells_1 = shells_by_type_1[shell_type]
                    shells_2 = shells_by_type_2[shell_type]
                    
                    if shells_1 or shells_2:  # Show if EITHER has this type
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
                                    name=f'{basis_name} {shell_type}-shell #{i+1} ({n_prim} primitives)',
                                    line=dict(color='#3b82f6', width=2.5, dash=['solid', 'dash', 'dot', 'dashdot'][i % 4])
                                ))
                        else:
                            st.warning(f"**{basis_name}** has NO {shell_type}-shells")
                        
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
                                title=f'<b>{shell_names[shell_type].title()}: {basis_name} vs {basis_name_2}</b>',
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
                                    **{basis_name}**: {len(shells_1)} {shell_type}-shells
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
            
            # 2. FINAL RECOMMENDATION
            with st.expander(f"Which Basis Set Should You Use?", expanded=True):
                st.markdown("### Recommendation Based on Your Selection")
                
                # Calculate quality score
                quality_1 = s_shells_1 + d_shells_1 * 2
                quality_2 = s_shells_2 + d_shells_2 * 2
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{basis_name} Quality Score", quality_1)
                    st.caption(f"{s_shells_1} s-shells + {d_shells_1} d-shells")
                with col2:
                    st.metric(f"{basis_name_2} Quality Score", quality_2)
                    st.caption(f"{s_shells_2} s-shells + {d_shells_2} d-shells")
                
                if quality_1 > quality_2:
                    st.success(f"✓ **Use {basis_name}** for higher accuracy (but slower)")
                    st.info(f"✓ **Use {basis_name_2}** for faster calculations (but less accurate)")
                elif quality_2 > quality_1:
                    st.success(f"✓ **Use {basis_name_2}** for higher accuracy (but slower)")
                    st.info(f"✓ **Use {basis_name}** for faster calculations (but less accurate)")
                else:
                    st.info(f"Both basis sets have similar quality - choose based on availability")
            
            # 3. SIDE-BY-SIDE 3D ORBITAL COMPARISON
            st.markdown("### 3D Orbital Comparison")
            st.markdown("Compare the actual orbital shapes from both basis sets side-by-side")
            
            # Get available orbitals - use FIRST basis set structure (same as single mode)
            elem_data1 = list(basis_data['elements'].values())[0]
            elem_data2 = list(basis_data_2['elements'].values())[0]
            shells1 = elem_data1['electron_shells']
            shells2 = elem_data2['electron_shells']
            
            # Build orbital list from FIRST basis set ONLY (exactly like single mode)
            orbital_options = []
            orbital_labels = []
            s_count = 0
            p_count = 0
            d_count = 0
            f_count = 0
            
            for i, s in enumerate(shells1):  # Loop through first basis set shells
                am = s['angular_momentum'][0]
                # Only add if we can actually visualize it
                if am == 0:  # s-orbital
                    s_count += 1
                    orbital_options.append('s')
                    orbital_labels.append(f"Shell #{i+1}: {s_count}s orbital (spherical, core/valence)")
                elif am == 1:  # p-orbital
                    p_count += 1
                    orbital_options.extend(['p_x', 'p_y', 'p_z'])
                    orbital_labels.extend([
                        f"Shell #{i+1}: {p_count}p_x orbital (dumbbell along x-axis)",
                        f"Shell #{i+1}: {p_count}p_y orbital (dumbbell along y-axis)",
                        f"Shell #{i+1}: {p_count}p_z orbital (dumbbell along z-axis)"
                    ])
                elif am == 2:  # d-orbital
                    d_count += 1
                    orbital_options.append('d')
                    orbital_labels.append(f"Shell #{i+1}: {d_count}d orbital (cloverleaf, polarization)")
                elif am == 3:  # f-orbital
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
                    st.markdown(f"#### {basis_name}")
                    
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
                        fig1 = create_orbital_3d(basis_data, orbital)
                        if fig1:
                            st.plotly_chart(fig1, use_container_width=True, key="comp_orbital_1")
                    else:
                        st.warning(f"{basis_name} does not have {orbital} orbitals")
                
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
                        fig2 = create_orbital_3d(basis_data_2, orbital)
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True, key="comp_orbital_2")
                    else:
                        st.warning(f"{basis_name_2} does not have {orbital} orbitals")
                
                st.info("""
                **How to interpret the comparison:**
                - **Tighter orbitals** (smaller, more compact) = higher exponents = better for core electrons
                - **Looser orbitals** (larger, more diffuse) = lower exponents = better for valence/bonding
                - **Different shapes** = different contraction coefficients = different accuracy
                """)
        
        else:
            # Single basis view - Show details in expander (same as comparison mode)
            analysis = analyze_basis_intelligence(basis_data, basis_name)
            
            # SECTION 1: Basis Set Details (Collapsible)
            with st.expander("Basis Set Details", expanded=False):
                st.markdown(f"### {basis_name}")
                show_basis_details(basis_data, basis_name)
                st.markdown("#### Understanding This Basis Set")
            st.info(f"**{analysis['zeta']}**\n\n{analysis['explanation']}")
            
            # COMPREHENSIVE VISUAL EXPLANATIONS for single basis (same as comparison mode)
            elem_data = list(basis_data['elements'].values())[0]
            
            # Count shells
            s_shells = sum(1 for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 0)
            p_shells = sum(1 for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 1)
            d_shells = sum(1 for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 2)
            f_shells = sum(1 for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 3)
            
            # Show orbital count
            st.markdown("### Orbital Shell Composition")
            fig_count = go.Figure(data=[
                go.Bar(
                    x=['s-shells', 'p-shells', 'd-shells', 'f-shells'],
                    y=[s_shells, p_shells, d_shells, f_shells],
                    marker_color=['#3b82f6', '#10b981', '#f59e0b', '#ef4444'],
                    text=[s_shells, p_shells, d_shells, f_shells],
                    textposition='auto',
                    textfont=dict(size=16, color='white', family='Arial Black')
                )
            ])
            fig_count.update_layout(
                title=f'<b>Shell Composition: {basis_name}</b>',
                xaxis_title='Shell Type',
                yaxis_title='Number of Shells',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig_count, use_container_width=True, key="single_orbital_count")
            
            # Mathematical Foundation
            with st.expander(f"Mathematical Foundation: {basis_name}", expanded=True):
                # Detect basis type
                def detect_basis_type(name):
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
                shells_by_type = {
                    's': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 0],
                    'p': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 1],
                    'd': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 2],
                    'f': [s for s in elem_data['electron_shells'] if s['angular_momentum'][0] == 3]
                }
                
                # Show each shell type
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
            
            # Orbital visualization
            st.markdown("### 3D Orbital Visualization")
            
            # Get available orbitals with proper labeling - ONLY EXISTING ONES
            elem_data = list(basis_data['elements'].values())[0]
            shells = elem_data['electron_shells']
            
            orbital_options = []
            orbital_labels = []
            s_count = 0
            p_count = 0
            d_count = 0
            f_count = 0
            
            for i, s in enumerate(shells):
                am = s['angular_momentum'][0]
                # Only add if we can actually visualize it
                if am == 0:  # s-orbital
                    s_count += 1
                    orbital_options.append('s')
                    orbital_labels.append(f"Shell #{i+1}: {s_count}s orbital (spherical, core/valence)")
                elif am == 1:  # p-orbital
                    p_count += 1
                    orbital_options.extend(['p_x', 'p_y', 'p_z'])
                    orbital_labels.extend([
                        f"Shell #{i+1}: {p_count}p_x orbital (dumbbell along x-axis)",
                        f"Shell #{i+1}: {p_count}p_y orbital (dumbbell along y-axis)",
                        f"Shell #{i+1}: {p_count}p_z orbital (dumbbell along z-axis)"
                    ])
                elif am == 2:  # d-orbital
                    d_count += 1
                    orbital_options.append('d')
                    orbital_labels.append(f"Shell #{i+1}: {d_count}d orbital (cloverleaf, polarization)")
                elif am == 3:  # f-orbital
                    f_count += 1
                    orbital_options.append('f')
                    orbital_labels.append(f"Shell #{i+1}: {f_count}f orbital (complex shape, high polarization)")
            
            if orbital_options:
                # Create mapping for display
                orbital_dict = {label: opt for label, opt in zip(orbital_labels, orbital_options)}
                
                selected_label = st.selectbox(
                    "Select Orbital Type:",
                    orbital_labels,
                    help="Choose which orbital to visualize in 3D"
                )
                
                orbital = orbital_dict[selected_label]
                
                # Show detailed info about the actual basis set being visualized
                elem_data = list(basis_data['elements'].values())[0]
                shells = elem_data['electron_shells']
                
                # Find the shell being visualized
                for s in shells:
                    am = s['angular_momentum'][0]
                    if (am == 0 and 's' in orbital) or \
                       (am == 1 and 'p' in orbital) or \
                       (am == 2 and 'd' in orbital) or \
                       (am == 3 and 'f' in orbital):
                        exps = [float(e) for e in s['exponents']]
                        coeffs = [float(c) for c in s['coefficients'][0]]
                        
                        st.info(f"""
                        **Visualizing:** {selected_label}
                        
                        **This is the ACTUAL {basis_name} basis set for {symbol}!**
                        - Number of primitive Gaussians: {len(exps)}
                        - Exponent range: {min(exps):.2e} to {max(exps):.2e}
                        - Coefficients: {len(coeffs)} contractions
                        
                        The shape you see is computed from the real exponents and coefficients of this basis set.
                        Different basis sets will show different shapes!
                        """)
                        break
                
                fig = create_orbital_3d(basis_data, orbital)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("3D visualization not available for this orbital type")
        
        # Download
        st.markdown("### Download Basis Set")
        basis_text = bse.get_basis(basis_name, elements=str(z), fmt=export_fmt, header=True)
        st.download_button(
            f"Download {basis_name} for {symbol} ({export_tool})",
            basis_text,
            f"{basis_name}_{symbol}.txt",
            use_container_width=True
        )
        
        with st.expander("View Format"):
            st.code(basis_text, language='text')

if __name__ == "__main__":
    main()
