"""
Session state management for DFT Flight Simulator.

Handles cross-module state sharing and consistency checking.
"""

import streamlit as st
from typing import Optional, Dict, Any


def init_session_state():
    """
    Initialize session state variables.
    Should be called at the start of each page.
    """
    # Element selection (shared across modules)
    if 'selected_element' not in st.session_state:
        st.session_state.selected_element = 6  # Default: Carbon
    
    # Basis set selection
    if 'selected_basis' not in st.session_state:
        st.session_state.selected_basis = '6-31G'
    
    # Pseudopotential selection
    if 'selected_pseudo_functional' not in st.session_state:
        st.session_state.selected_pseudo_functional = 'PBE'
    
    if 'selected_pseudo_accuracy' not in st.session_state:
        st.session_state.selected_pseudo_accuracy = 'standard'
    
    # XC functional selection
    if 'selected_xc_functional' not in st.session_state:
        st.session_state.selected_xc_functional = 'PBE'
    
    # Comparison mode flags
    if 'basis_comparison_mode' not in st.session_state:
        st.session_state.basis_comparison_mode = False
    
    if 'pseudo_comparison_mode' not in st.session_state:
        st.session_state.pseudo_comparison_mode = False
    
    if 'xc_comparison_mode' not in st.session_state:
        st.session_state.xc_comparison_mode = False


def update_element(element: int):
    """
    Update selected element across all modules.
    
    Args:
        element: Atomic number
    """
    st.session_state.selected_element = element


def get_current_selections() -> Dict[str, Any]:
    """
    Get current selections from all modules.
    
    Returns:
        Dictionary with current selections
    """
    return {
        'element': st.session_state.get('selected_element', 6),
        'basis': st.session_state.get('selected_basis', '6-31G'),
        'pseudo_functional': st.session_state.get('selected_pseudo_functional', 'PBE'),
        'pseudo_accuracy': st.session_state.get('selected_pseudo_accuracy', 'standard'),
        'xc_functional': st.session_state.get('selected_xc_functional', 'PBE')
    }


def check_consistency() -> Dict[str, Any]:
    """
    Check consistency between module selections.
    
    Returns:
        Dictionary with consistency status and warnings
    """
    selections = get_current_selections()
    
    warnings = []
    consistent = True
    
    # Check if pseudopotential functional matches XC functional
    if selections['pseudo_functional'] != selections['xc_functional']:
        warnings.append(
            f"⚠️ **Inconsistency detected:** Pseudopotential uses {selections['pseudo_functional']} "
            f"but XC functional is {selections['xc_functional']}. "
            f"For best results, these should match!"
        )
        consistent = False
    
    # Check if basis set is appropriate for element
    # (This would require checking basis-set-exchange, simplified here)
    
    return {
        'consistent': consistent,
        'warnings': warnings,
        'suggestions': get_suggestions(selections) if not consistent else []
    }


def get_suggestions(selections: Dict[str, Any]) -> list:
    """
    Get suggestions for improving consistency.
    
    Args:
        selections: Current selections
        
    Returns:
        List of suggestion strings
    """
    suggestions = []
    
    if selections['pseudo_functional'] != selections['xc_functional']:
        suggestions.append(
            f"💡 **Suggestion:** Change XC functional to {selections['pseudo_functional']} "
            f"or change pseudopotential to {selections['xc_functional']}"
        )
    
    return suggestions


def show_consistency_checker():
    """
    Display consistency checker in sidebar.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔍 Consistency Checker")
        
        consistency = check_consistency()
        
        if consistency['consistent']:
            st.success("✅ All selections are consistent!")
        else:
            st.warning("⚠️ Inconsistencies detected")
            for warning in consistency['warnings']:
                st.markdown(warning)
            
            if consistency['suggestions']:
                st.markdown("**Suggestions:**")
                for suggestion in consistency['suggestions']:
                    st.info(suggestion)


def show_current_selections():
    """
    Display current selections in sidebar.
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 📋 Current Selections")
        
        selections = get_current_selections()
        
        from utils.constants import ELEMENTS
        element_symbol = ELEMENTS.get(selections['element'], 'Unknown')
        
        st.markdown(f"""
        - **Element:** {element_symbol} (Z={selections['element']})
        - **Basis Set:** {selections['basis']}
        - **Pseudopotential:** {selections['pseudo_functional']} ({selections['pseudo_accuracy']})
        - **XC Functional:** {selections['xc_functional']}
        """)


# ==================== EXPORT ====================

__all__ = [
    'init_session_state',
    'update_element',
    'get_current_selections',
    'check_consistency',
    'show_consistency_checker',
    'show_current_selections',
]
