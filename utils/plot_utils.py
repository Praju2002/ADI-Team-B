"""Small plotting helpers to adjust Plotly y-axes for better visual ranges.

Provides `set_smart_yaxis(fig, primary=None, secondary=None, pad_frac=0.08, min_pad=0.5)`
which computes a sensible min/max with padding and applies it to the provided
figure. `primary` and `secondary` are array-like numeric series (pandas/numpy).
If series is None, that axis is left unchanged.
"""
from __future__ import annotations

import numpy as np
from typing import Optional, Sequence, Tuple


def _compute_range(vals: Sequence[float], pad_frac: float = 0.08, min_pad: float = 0.5) -> Optional[Tuple[float, float]]:
    if vals is None:
        return None
    try:
        arr = np.asarray(vals, dtype=float)
    except Exception:
        return None
    if arr.size == 0 or np.all(np.isnan(arr)):
        return None
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    lo = float(np.nanmin(finite))
    hi = float(np.nanmax(finite))
    span = hi - lo
    if span == 0:
        pad = max(abs(lo) * 0.05, min_pad)
        return lo - pad, hi + pad
    pad = max(span * pad_frac, min_pad)
    return lo - pad, hi + pad


def set_smart_yaxis(fig, primary: Optional[Sequence[float]] = None, secondary: Optional[Sequence[float]] = None, pad_frac: float = 0.08, min_pad: float = 0.5):
    """Adjust `fig` y-axes ranges using provided series.

    - `primary`: values to use for the primary y-axis.
    - `secondary`: values for the secondary y-axis (if present).
    The function updates `fig` in-place.
    """
    rpri = _compute_range(primary, pad_frac=pad_frac, min_pad=min_pad)
    rsec = _compute_range(secondary, pad_frac=pad_frac, min_pad=min_pad)

    try:
        if rpri is not None:
            fig.update_yaxes(range=[rpri[0], rpri[1]])
        if rsec is not None:
            # secondary y-axes in plotly are typically specified via 'secondary_y=True'
            # update_yaxes accepts secondary_y argument to target the secondary axis.
            fig.update_yaxes(range=[rsec[0], rsec[1]], secondary_y=True)
    except Exception:
        # Be defensive: do not fail the app if updating axes fails.
        pass


__all__ = ['set_smart_yaxis']
