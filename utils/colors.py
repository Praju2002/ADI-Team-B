"""Color palette helpers for accessible/colorblind-safe charts.

Exports:
- `OKABE_ITO`: qualitative, colorblind-safe palette (Okabe & Ito)
- `CB_SEQUENTIAL`: perceptually-uniform sequential palette (Viridis)
- `CB_SEQUENTIAL_REV`: reversed Viridis
- helper `apply_okabe_to_traces(fig)` (future use)
"""
from __future__ import annotations

import plotly.express as px

# Okabe-Ito colorblind-safe palette
# Source: Okabe & Ito (suitable for categorical color use)
OKABE_ITO = [
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
    "#000000",  # black
]

# Perceptually-uniform sequential palette (colorblind-friendly)
CB_SEQUENTIAL = px.colors.sequential.Viridis
CB_SEQUENTIAL_REV = CB_SEQUENTIAL[::-1]

__all__ = ["OKABE_ITO", "CB_SEQUENTIAL", "CB_SEQUENTIAL_REV"]
