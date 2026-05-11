"""Simple population drift: z-score of means vs reference (demo)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def mean_shift_table(reference: pd.DataFrame, current: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for c in cols:
        if c not in reference.columns or c not in current.columns:
            continue
        r = pd.to_numeric(reference[c], errors="coerce").dropna()
        k = pd.to_numeric(current[c], errors="coerce").dropna()
        if len(r) < 2 or len(k) < 2:
            continue
        mr, mk = float(r.mean()), float(k.mean())
        sr = float(r.std(ddof=1) or 1.0)
        z = (mk - mr) / max(sr / np.sqrt(len(k)), 1e-9)
        rows.append({"feature": c, "ref_mean": mr, "cur_mean": mk, "mean_delta_pct": (mk - mr) / max(abs(mr), 1e-9) * 100, "z_approx": z})
    return pd.DataFrame(rows)
