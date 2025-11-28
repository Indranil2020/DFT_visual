"""
Common plotting functions and themes for DFT Flight Simulator.

Provides consistent styling and reusable plot components across all modules.
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from utils.constants import PLOT_COLORS, ORBITAL_COLORS


def get_plot_theme() -> dict:
    """
    Get consistent Plotly theme for all visualizations.
    
    Returns:
        Dictionary of layout parameters for Plotly figures
    """
    return {
        'template': 'plotly_white',
        'font': {
            'family': 'Arial, sans-serif',
            'size': 14,
            'color': '#1f2937'
        },
        'title': {
            'font': {'size': 18, 'color': '#111827', 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'showgrid': True,
            'gridwidth': 1,
            'gridcolor': '#e5e7eb',
            'zeroline': True,
            'zerolinewidth': 2,
            'zerolinecolor': '#9ca3af'
        },
        'yaxis': {
            'showgrid': True,
            'gridwidth': 1,
            'gridcolor': '#e5e7eb',
            'zeroline': True,
            'zerolinewidth': 2,
            'zerolinecolor': '#9ca3af'
        },
        'plot_bgcolor': 'white',
        'paper_bgcolor': 'white',
        'hovermode': 'closest',
        'hoverlabel': {
            'bgcolor': 'white',
            'font_size': 12,
            'font_family': 'Arial'
        }
    }


def create_comparison_plot(
    data1: Dict[str, np.ndarray],
    data2: Dict[str, np.ndarray],
    labels: Tuple[str, str],
    title: str,
    xlabel: str,
    ylabel: str,
    show_difference: bool = True
) -> go.Figure:
    """
    Create a standard comparison plot for two datasets.
    
    Args:
        data1: First dataset {'x': array, 'y': array}
        data2: Second dataset {'x': array, 'y': array}
        labels: Tuple of (label1, label2)
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        show_difference: If True, add difference trace
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    # Add first dataset
    fig.add_trace(go.Scatter(
        x=data1['x'],
        y=data1['y'],
        mode='lines',
        name=labels[0],
        line=dict(color=PLOT_COLORS['primary'], width=3),
        hovertemplate=f'{labels[0]}<br>x: %{{x:.3f}}<br>y: %{{y:.3e}}<extra></extra>'
    ))
    
    # Add second dataset
    fig.add_trace(go.Scatter(
        x=data2['x'],
        y=data2['y'],
        mode='lines',
        name=labels[1],
        line=dict(color=PLOT_COLORS['secondary'], width=3, dash='dash'),
        hovertemplate=f'{labels[1]}<br>x: %{{x:.3f}}<br>y: %{{y:.3e}}<extra></extra>'
    ))
    
    # Add difference if requested
    if show_difference and len(data1['x']) == len(data2['x']):
        diff = data1['y'] - data2['y']
        fig.add_trace(go.Scatter(
            x=data1['x'],
            y=diff,
            mode='lines',
            name='Difference',
            line=dict(color=PLOT_COLORS['accent'], width=2, dash='dot'),
            hovertemplate='Difference<br>x: %{x:.3f}<br>Δy: %{y:.3e}<extra></extra>',
            visible='legendonly'  # Hidden by default
        ))
    
    # Apply theme
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'xaxis_title': xlabel,
        'yaxis_title': ylabel,
        'height': 500,
        'showlegend': True,
        'legend': dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='#e5e7eb',
            borderwidth=1
        )
    })
    fig.update_layout(**theme)
    
    return fig


def create_3d_orbital_plot(
    X: np.ndarray,
    Y: np.ndarray,
    Z: np.ndarray,
    psi: np.ndarray,
    title: str,
    isovalue: Optional[float] = None
) -> go.Figure:
    """
    Create 3D isosurface plot for orbital visualization.
    
    Args:
        X, Y, Z: 3D meshgrid arrays
        psi: Wavefunction values
        title: Plot title
        isovalue: Isosurface value (auto-calculated if None)
        
    Returns:
        Plotly Figure object
    """
    # Auto-calculate isovalue if not provided
    if isovalue is None:
        isovalue = 0.05 * np.max(np.abs(psi))
    
    fig = go.Figure()
    
    # Positive isosurface
    fig.add_trace(go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=psi.flatten(),
        isomin=isovalue,
        isomax=np.max(psi),
        surface_count=1,
        colorscale='Blues',
        showscale=False,
        caps=dict(x_show=False, y_show=False, z_show=False),
        name='Positive',
        opacity=0.8
    ))
    
    # Negative isosurface
    fig.add_trace(go.Isosurface(
        x=X.flatten(),
        y=Y.flatten(),
        z=Z.flatten(),
        value=psi.flatten(),
        isomin=np.min(psi),
        isomax=-isovalue,
        surface_count=1,
        colorscale='Reds',
        showscale=False,
        caps=dict(x_show=False, y_show=False, z_show=False),
        name='Negative',
        opacity=0.8
    ))
    
    # Layout
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'scene': dict(
            xaxis_title='X (Bohr)',
            yaxis_title='Y (Bohr)',
            zaxis_title='Z (Bohr)',
            aspectmode='cube',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        'height': 600,
        'showlegend': True
    })
    fig.update_layout(**theme)
    
    return fig


def add_educational_annotation(
    fig: go.Figure,
    text: str,
    position: Tuple[float, float],
    arrow_position: Optional[Tuple[float, float]] = None,
    bgcolor: str = 'rgba(255, 255, 255, 0.9)'
) -> go.Figure:
    """
    Add educational annotation to a plot.
    
    Args:
        fig: Plotly figure to annotate
        text: Annotation text
        position: (x, y) position in data coordinates
        arrow_position: Optional (x, y) for arrow pointing
        bgcolor: Background color for annotation box
        
    Returns:
        Modified figure
    """
    annotation = dict(
        text=text,
        x=position[0],
        y=position[1],
        showarrow=arrow_position is not None,
        bgcolor=bgcolor,
        bordercolor='#3b82f6',
        borderwidth=2,
        borderpad=8,
        font=dict(size=12, color='#1f2937'),
        align='left'
    )
    
    if arrow_position is not None:
        annotation.update(dict(
            ax=arrow_position[0],
            ay=arrow_position[1],
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='#3b82f6'
        ))
    
    fig.add_annotation(annotation)
    return fig


def create_bar_comparison(
    categories: List[str],
    values1: List[float],
    values2: List[float],
    labels: Tuple[str, str],
    title: str,
    ylabel: str
) -> go.Figure:
    """
    Create grouped bar chart for comparing two datasets.
    
    Args:
        categories: Category labels
        values1: First dataset values
        values2: Second dataset values
        labels: (label1, label2)
        title: Plot title
        ylabel: Y-axis label
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values1,
        name=labels[0],
        marker_color=PLOT_COLORS['primary'],
        text=values1,
        textposition='auto',
        texttemplate='%{text:.1f}'
    ))
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values2,
        name=labels[1],
        marker_color=PLOT_COLORS['secondary'],
        text=values2,
        textposition='auto',
        texttemplate='%{text:.1f}'
    ))
    
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'xaxis_title': '',
        'yaxis_title': ylabel,
        'barmode': 'group',
        'height': 400
    })
    fig.update_layout(**theme)
    
    return fig


def create_radial_plot(
    r: np.ndarray,
    values: np.ndarray,
    label: str,
    title: str,
    xlabel: str = 'r (Bohr)',
    ylabel: str = 'Value',
    log_scale: bool = False
) -> go.Figure:
    """
    Create radial plot (e.g., for potentials, densities).
    
    Args:
        r: Radial coordinate array
        values: Values to plot
        label: Data label
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        log_scale: Use log scale for y-axis
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=r,
        y=values,
        mode='lines',
        name=label,
        line=dict(color=PLOT_COLORS['primary'], width=3),
        hovertemplate=f'{label}<br>r: %{{x:.3f}}<br>Value: %{{y:.3e}}<extra></extra>'
    ))
    
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'xaxis_title': xlabel,
        'yaxis_title': ylabel,
        'height': 400
    })
    fig.update_layout(**theme)
    
    if log_scale:
        fig.update_yaxis(type='log')
    
    return fig


def create_heatmap(
    data: np.ndarray,
    x_labels: List[str],
    y_labels: List[str],
    title: str,
    colorscale: str = 'RdBu',
    symmetric: bool = True
) -> go.Figure:
    """
    Create heatmap for matrix data.
    
    Args:
        data: 2D array of values
        x_labels: Labels for x-axis
        y_labels: Labels for y-axis
        title: Plot title
        colorscale: Plotly colorscale name
        symmetric: If True, center colorscale at zero
        
    Returns:
        Plotly Figure object
    """
    if symmetric:
        max_abs = np.max(np.abs(data))
        zmin, zmax = -max_abs, max_abs
    else:
        zmin, zmax = np.min(data), np.max(data)
    
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        zmin=zmin,
        zmax=zmax,
        hovertemplate='%{y} vs %{x}<br>Value: %{z:.3e}<extra></extra>'
    ))
    
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'height': 500
    })
    fig.update_layout(**theme)
    
    return fig


def create_multi_line_plot(
    x: np.ndarray,
    y_data: Dict[str, np.ndarray],
    title: str,
    xlabel: str,
    ylabel: str,
    colors: Optional[Dict[str, str]] = None
) -> go.Figure:
    """
    Create plot with multiple lines.
    
    Args:
        x: Common x-axis data
        y_data: Dictionary of {label: y_array}
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        colors: Optional dictionary of {label: color}
        
    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    
    default_colors = [
        PLOT_COLORS['primary'],
        PLOT_COLORS['secondary'],
        PLOT_COLORS['accent'],
        PLOT_COLORS['danger'],
        PLOT_COLORS['info']
    ]
    
    for i, (label, y) in enumerate(y_data.items()):
        color = colors.get(label) if colors else default_colors[i % len(default_colors)]
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=label,
            line=dict(color=color, width=3),
            hovertemplate=f'{label}<br>x: %{{x:.3f}}<br>y: %{{y:.3e}}<extra></extra>'
        ))
    
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'xaxis_title': xlabel,
        'yaxis_title': ylabel,
        'height': 500,
        'hovermode': 'x unified',
        'legend': dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        )
    })
    fig.update_layout(**theme)
    
    return fig


def create_shell_visualization(
    shell_counts: Dict[str, int],
    title: str = 'Orbital Shell Composition'
) -> go.Figure:
    """
    Create bar chart for shell composition.
    
    Args:
        shell_counts: Dictionary of {shell_type: count}
        title: Plot title
        
    Returns:
        Plotly Figure object
    """
    shell_types = list(shell_counts.keys())
    counts = list(shell_counts.values())
    
    colors = [ORBITAL_COLORS.get(s[0], PLOT_COLORS['primary']) for s in shell_types]
    
    fig = go.Figure(data=[
        go.Bar(
            x=shell_types,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto',
            textfont=dict(size=16, color='white', family='Arial Black'),
            hovertemplate='%{x}: %{y} shells<extra></extra>'
        )
    ])
    
    theme = get_plot_theme()
    theme.update({
        'title': title,
        'xaxis_title': 'Shell Type',
        'yaxis_title': 'Number of Shells',
        'height': 400,
        'showlegend': False
    })
    fig.update_layout(**theme)
    
    return fig


# ==================== EXPORT ====================

__all__ = [
    'get_plot_theme',
    'create_comparison_plot',
    'create_3d_orbital_plot',
    'add_educational_annotation',
    'create_bar_comparison',
    'create_radial_plot',
    'create_heatmap',
    'create_multi_line_plot',
    'create_shell_visualization',
]
