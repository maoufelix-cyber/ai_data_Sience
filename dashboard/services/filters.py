"""Global executive filters."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_sidebar_filters(df: pd.DataFrame) -> dict:
    """Return filter dict + apply to dataframe."""
    st.markdown("##### Smart filters")
    with st.expander("Rentang & segmen", expanded=False):
        month_range = st.slider("Periode sintetis (_month)", 1, 12, (1, 12))
        prem = st.multiselect("Premium", options=sorted(df["is_premium"].dropna().unique().tolist()), default=sorted(df["is_premium"].dropna().unique().tolist()))
        t_min, t_max = int(df["tenure_months"].min()), int(df["tenure_months"].max())
        tenure = st.slider("Tenure (bulan)", t_min, t_max, (t_min, t_max))
        tr_min, tr_max = int(df["total_transactions"].min()), int(df["total_transactions"].max())
        tx = st.slider("Total transaksi", tr_min, tr_max, (tr_min, tr_max))
        risk = st.multiselect(
            "Risk level (dari proba)",
            ["Low", "Medium", "High", "Critical"],
            default=["Low", "Medium", "High", "Critical"],
        )
    return {
        "month_range": month_range,
        "premium": prem,
        "tenure": tenure,
        "transactions": tx,
        "risk_levels": risk,
    }


def apply_filters(df: pd.DataFrame, f: dict, proba_col: str = "response_proba") -> pd.DataFrame:
    out = df.copy()
    if "_month" in out.columns:
        lo, hi = f["month_range"]
        out = out[(out["_month"] >= lo) & (out["_month"] <= hi)]
    if "is_premium" in out.columns and f.get("premium"):
        out = out[out["is_premium"].isin(f["premium"])]
    if "tenure_months" in out.columns:
        out = out[(out["tenure_months"] >= f["tenure"][0]) & (out["tenure_months"] <= f["tenure"][1])]
    if "total_transactions" in out.columns:
        out = out[(out["total_transactions"] >= f["transactions"][0]) & (out["total_transactions"] <= f["transactions"][1])]
    if proba_col in out.columns and f.get("risk_levels"):
        lvl = out[proba_col].apply(_risk_bucket)
        out = out[lvl.isin(f["risk_levels"])]
    return out.reset_index(drop=True)


def _risk_bucket(p: float) -> str:
    if p >= 0.85:
        return "Critical"
    if p >= 0.65:
        return "High"
    if p >= 0.35:
        return "Medium"
    return "Low"
