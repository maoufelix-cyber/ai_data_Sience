"""Executive KPI computations & comparisons."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_synthetic_month(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    bins = min(12, max(1, len(out) // 50 or 1))
    out["_month"] = (np.arange(len(out)) % bins) + 1
    return out


def split_compare(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mid = len(df) // 2
    return df.iloc[:mid], df.iloc[mid:]


def safe_delta(cur: float, prev: float) -> tuple[float, bool | None]:
    if prev == 0:
        return 0.0, None
    d = (cur - prev) / abs(prev) * 100
    return d, d >= 0


def retention_score(mean_proba: float) -> float:
    """Convert churn probability to retention score (0-100)."""
    p = float(mean_proba)  # Ensure scalar
    return float(np.clip((1.0 - p) * 100, 0, 100))


def revenue_at_risk(df: pd.DataFrame, proba_col: str = "churn_proba") -> float:
    """Calculate 6-month revenue at risk from churn."""
    if proba_col not in df.columns:
        return 0.0
    proba = pd.to_numeric(df[proba_col], errors="coerce").fillna(0)
    aov = pd.to_numeric(df.get("avg_order_value", 0), errors="coerce").fillna(0)
    result = float((proba * aov * 6).sum())
    return result


def clv_estimate(df: pd.DataFrame) -> float:
    """Estimate customer lifetime value."""
    if "avg_order_value" not in df.columns or "total_transactions" not in df.columns:
        return 0.0
    aov = pd.to_numeric(df["avg_order_value"], errors="coerce").fillna(0)
    tx = pd.to_numeric(df["total_transactions"], errors="coerce").fillna(0)
    result = float((aov * tx * 0.18).mean())
    return result


def support_ratio(df: pd.DataFrame) -> float:
    """Calculate support ticket ratio per transaction."""
    if "support_tickets" not in df.columns or "total_transactions" not in df.columns:
        return 0.0
    st_ = pd.to_numeric(df["support_tickets"], errors="coerce").fillna(0)
    tr = pd.to_numeric(df["total_transactions"], errors="coerce").replace(0, np.nan)
    result = float((st_ / tr).fillna(0).mean())
    return result


def satisfaction_index(df: pd.DataFrame) -> float:
    """Heuristic 0–100: lower tickets + higher tenure + premium (float scalar).
    
    Combines:
    - Tenure score (35% weight): normalized 0-72 months
    - Support inverse score (45% weight): 1 - (tickets / 15) capped
    - Premium flag (20% weight): 1 if premium, 0 if not
    
    Always returns a single float value, never a Series.
    """
    # Get Series data, ensure they're numeric
    t = pd.to_numeric(df.get("tenure_months", 0), errors="coerce").fillna(0).clip(0, 72) / 72
    tk = 1 - pd.to_numeric(df.get("support_tickets", 0), errors="coerce").fillna(0).clip(0, 15) / 15
    pr = df.get("is_premium", "no").astype(str).str.lower().eq("yes").astype(float)
    
    # Calculate weighted score (works on Series)
    score = ((t * 0.35 + tk * 0.45 + pr * 0.2) * 100).clip(lower=0, upper=100)
    
    # Handle edge cases
    if score.empty:
        return 0.0
    
    # Always return scalar float
    result = float(score.mean())
    return result
