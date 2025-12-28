"""
Spectra Visualization for Psi4 MCP Server.

Generates visualization data for various spectra.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Peak:
    """A spectral peak."""
    position: float
    intensity: float
    width: float = 0.0
    label: str = ""


@dataclass
class SpectrumData:
    """Spectrum data for plotting."""
    x_values: List[float]
    y_values: List[float]
    peaks: List[Peak]
    x_label: str
    y_label: str
    title: str = ""
    x_unit: str = ""
    y_unit: str = ""


class SpectrumVisualizer:
    """Generates spectrum visualization data."""
    
    def __init__(self):
        pass
    
    def generate_ir_spectrum(
        self,
        frequencies: List[float],
        intensities: List[float],
        x_range: Tuple[float, float] = (400, 4000),
        n_points: int = 1000,
        broadening: float = 10.0,
    ) -> SpectrumData:
        """Generate IR spectrum with Lorentzian broadening."""
        x_min, x_max = x_range
        x_values = [x_min + i * (x_max - x_min) / n_points for i in range(n_points)]
        y_values = [0.0] * n_points
        
        # Apply Lorentzian broadening
        for freq, intensity in zip(frequencies, intensities):
            if freq < 0:  # Skip imaginary frequencies
                continue
            for i, x in enumerate(x_values):
                y_values[i] += intensity * broadening**2 / ((x - freq)**2 + broadening**2)
        
        # Build peaks
        peaks = [Peak(position=f, intensity=i, label=f"{f:.1f}") 
                 for f, i in zip(frequencies, intensities) if f > 0]
        
        return SpectrumData(
            x_values=x_values,
            y_values=y_values,
            peaks=peaks,
            x_label="Wavenumber",
            y_label="Intensity",
            title="IR Spectrum",
            x_unit="cm⁻¹",
            y_unit="km/mol",
        )
    
    def generate_uv_vis_spectrum(
        self,
        wavelengths: List[float],
        oscillator_strengths: List[float],
        x_range: Tuple[float, float] = (200, 800),
        n_points: int = 1000,
        broadening: float = 0.4,
    ) -> SpectrumData:
        """Generate UV-Vis spectrum with Gaussian broadening."""
        x_min, x_max = x_range
        x_values = [x_min + i * (x_max - x_min) / n_points for i in range(n_points)]
        y_values = [0.0] * n_points
        
        # Apply Gaussian broadening
        sigma = broadening
        for wl, osc in zip(wavelengths, oscillator_strengths):
            if x_min <= wl <= x_max:
                for i, x in enumerate(x_values):
                    y_values[i] += osc * math.exp(-((x - wl)**2) / (2 * sigma**2 * wl**2))
        
        # Normalize
        max_y = max(y_values) if y_values else 1.0
        if max_y > 0:
            y_values = [y / max_y for y in y_values]
        
        peaks = [Peak(position=wl, intensity=osc, label=f"{wl:.1f} nm")
                 for wl, osc in zip(wavelengths, oscillator_strengths)]
        
        return SpectrumData(
            x_values=x_values,
            y_values=y_values,
            peaks=peaks,
            x_label="Wavelength",
            y_label="Absorbance",
            title="UV-Vis Absorption Spectrum",
            x_unit="nm",
            y_unit="a.u.",
        )
    
    def generate_nmr_spectrum(
        self,
        shifts: List[float],
        intensities: Optional[List[float]] = None,
        x_range: Tuple[float, float] = (0, 12),
        n_points: int = 1000,
        broadening: float = 0.02,
    ) -> SpectrumData:
        """Generate NMR spectrum."""
        if intensities is None:
            intensities = [1.0] * len(shifts)
        
        x_min, x_max = x_range
        x_values = [x_max - i * (x_max - x_min) / n_points for i in range(n_points)]  # Reversed
        y_values = [0.0] * n_points
        
        for shift, intensity in zip(shifts, intensities):
            for i, x in enumerate(x_values):
                y_values[i] += intensity * math.exp(-((x - shift)**2) / (2 * broadening**2))
        
        peaks = [Peak(position=s, intensity=i, label=f"{s:.2f} ppm")
                 for s, i in zip(shifts, intensities)]
        
        return SpectrumData(
            x_values=x_values,
            y_values=y_values,
            peaks=peaks,
            x_label="Chemical Shift",
            y_label="Intensity",
            title="¹H NMR Spectrum",
            x_unit="ppm",
            y_unit="a.u.",
        )
    
    def to_plot_data(self, spectrum: SpectrumData) -> Dict[str, Any]:
        """Convert spectrum to plot-ready dict."""
        return {
            "x": spectrum.x_values,
            "y": spectrum.y_values,
            "peaks": [{"position": p.position, "intensity": p.intensity, "label": p.label}
                     for p in spectrum.peaks],
            "x_label": f"{spectrum.x_label} ({spectrum.x_unit})",
            "y_label": f"{spectrum.y_label} ({spectrum.y_unit})",
            "title": spectrum.title,
        }


def generate_spectrum_plot_data(
    spectrum_type: str,
    positions: List[float],
    intensities: List[float],
    **kwargs: Any,
) -> Dict[str, Any]:
    """Generate spectrum plot data."""
    visualizer = SpectrumVisualizer()
    
    if spectrum_type.lower() == "ir":
        spectrum = visualizer.generate_ir_spectrum(positions, intensities, **kwargs)
    elif spectrum_type.lower() in ("uv", "uv-vis", "uvvis"):
        spectrum = visualizer.generate_uv_vis_spectrum(positions, intensities, **kwargs)
    elif spectrum_type.lower() == "nmr":
        spectrum = visualizer.generate_nmr_spectrum(positions, intensities, **kwargs)
    else:
        spectrum = visualizer.generate_ir_spectrum(positions, intensities, **kwargs)
    
    return visualizer.to_plot_data(spectrum)
