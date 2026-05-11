"""Rough business KPIs from a single prediction (portfolio / demo)."""

from __future__ import annotations

import pandas as pd


def estimate_financials(
    raw_row: pd.Series,
    probability: float,
    *,
    monthly_revenue: float = 180.0,
    months_horizon: int = 12,
    retention_cost: float = 25.0,
) -> dict[str, float]:
    """Very simple CLV / loss / ROI proxies — not financial advice."""
    p = float(probability)
    expected_loss = p * monthly_revenue * months_horizon
    savings_if_retained = (1.0 - p) * monthly_revenue * 3
    roi_hint = (savings_if_retained - retention_cost) / max(retention_cost, 1e-6)
    clv_proxy = float(raw_row.get("avg_order_value", 0) or 0) * float(raw_row.get("total_transactions", 0) or 0) * 0.15
    return {
        "expected_revenue_at_risk": expected_loss,
        "retention_savings_3m_proxy": savings_if_retained,
        "retention_roi_hint": roi_hint,
        "clv_activity_proxy": clv_proxy,
    }
