"""Utilities for creating professional comparison tables"""
import streamlit as st

def create_comparison_table(basis_data1, basis_data2, basis_name1, basis_name2, analysis1, analysis2):
    """Create a professional color-coded comparison table"""
    
    elem_data1 = list(basis_data1['elements'].values())[0]
    elem_data2 = list(basis_data2['elements'].values())[0]
    
    # Extract metrics
    shells1 = elem_data1['electron_shells']
    shells2 = elem_data2['electron_shells']
    
    s_shells_1 = sum(1 for s in shells1 if s['angular_momentum'][0] == 0)
    s_shells_2 = sum(1 for s in shells2 if s['angular_momentum'][0] == 0)
    
    p_shells_1 = sum(1 for s in shells1 if s['angular_momentum'][0] == 1)
    p_shells_2 = sum(1 for s in shells2 if s['angular_momentum'][0] == 1)
    
    d_shells_1 = sum(1 for s in shells1 if s['angular_momentum'][0] == 2)
    d_shells_2 = sum(1 for s in shells2 if s['angular_momentum'][0] == 2)
    
    f_shells_1 = sum(1 for s in shells1 if s['angular_momentum'][0] == 3)
    f_shells_2 = sum(1 for s in shells2 if s['angular_momentum'][0] == 3)
    
    total_prim_1 = sum(len(s['exponents']) for s in shells1)
    total_prim_2 = sum(len(s['exponents']) for s in shells2)
    
    total_contr_1 = sum(len(s['coefficients']) for s in shells1)
    total_contr_2 = sum(len(s['coefficients']) for s in shells2)
    
    # Create comparison data
    comparison_data = []
    
    # Zeta level
    zeta_same = analysis1['zeta'] == analysis2['zeta']
    comparison_data.append({
        'Property': 'Zeta Level',
        basis_name1: analysis1['zeta'],
        basis_name2: analysis2['zeta'],
        'Status': 'Same' if zeta_same else 'Different',
        'Explanation': 'Number of functions per orbital - affects accuracy'
    })
    
    # Polarization
    pol_same = analysis1['has_polarization'] == analysis2['has_polarization']
    comparison_data.append({
        'Property': 'Polarization',
        basis_name1: 'Yes' if analysis1['has_polarization'] else 'No',
        basis_name2: 'Yes' if analysis2['has_polarization'] else 'No',
        'Status': 'Same' if pol_same else 'Different',
        'Explanation': 'Ability to describe molecular bonding'
    })
    
    # Diffuse functions
    diffuse_same = analysis1['has_diffuse'] == analysis2['has_diffuse']
    comparison_data.append({
        'Property': 'Diffuse Functions',
        basis_name1: 'Yes' if analysis1['has_diffuse'] else 'No',
        basis_name2: 'Yes' if analysis2['has_diffuse'] else 'No',
        'Status': 'Same' if diffuse_same else 'Different',
        'Explanation': 'For anions and excited states'
    })
    
    # Total primitives
    prim_same = total_prim_1 == total_prim_2
    comparison_data.append({
        'Property': 'Total Primitives',
        basis_name1: str(total_prim_1),
        basis_name2: str(total_prim_2),
        'Status': 'Same' if prim_same else 'Different',
        'Explanation': 'Raw Gaussian functions - more = more flexible'
    })
    
    # Total contractions
    contr_same = total_contr_1 == total_contr_2
    comparison_data.append({
        'Property': 'Total Contractions',
        basis_name1: str(total_contr_1),
        basis_name2: str(total_contr_2),
        'Status': 'Same' if contr_same else 'Different',
        'Explanation': 'Optimized combinations - affects speed'
    })
    
    # s-shells
    s_same = s_shells_1 == s_shells_2
    comparison_data.append({
        'Property': 's-shells',
        basis_name1: str(s_shells_1),
        basis_name2: str(s_shells_2),
        'Status': 'Same' if s_same else 'Different',
        'Explanation': 'Spherical orbitals for core/valence'
    })
    
    # p-shells
    p_same = p_shells_1 == p_shells_2
    comparison_data.append({
        'Property': 'p-shells',
        basis_name1: str(p_shells_1),
        basis_name2: str(p_shells_2),
        'Status': 'Same' if p_same else 'Different',
        'Explanation': 'Dumbbell-shaped orbitals for bonding'
    })
    
    # d-shells
    d_same = d_shells_1 == d_shells_2
    comparison_data.append({
        'Property': 'd-shells',
        basis_name1: str(d_shells_1),
        basis_name2: str(d_shells_2),
        'Status': 'Same' if d_same else 'Different',
        'Explanation': 'Polarization functions for accurate bonding'
    })
    
    return comparison_data

def display_comparison_table(comparison_data, basis_name1, basis_name2):
    """Display the comparison table with CLEAR labeling"""
    
    # Count similarities and differences
    same_count = sum(1 for item in comparison_data if item['Status'] == 'Same')
    diff_count = sum(1 for item in comparison_data if item['Status'] == 'Different')
    
    # Display as CLEAR table with columns
    for item in comparison_data:
        is_same = item['Status'] == 'Same'
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**{item['Property']}**")
            st.caption(item['Explanation'])
        
        with col2:
            if is_same:
                st.success(f"**{basis_name1}**\n\n{item[basis_name1]}")
            else:
                st.info(f"**{basis_name1}**\n\n{item[basis_name1]}")
        
        with col3:
            if is_same:
                st.success(f"**{basis_name2}**\n\n{item[basis_name2]}")
            else:
                st.warning(f"**{basis_name2}**\n\n{item[basis_name2]}")
        
        st.markdown("---")
    
    # Summary
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Similarities", same_count)
    with col2:
        st.metric("Differences", diff_count)
