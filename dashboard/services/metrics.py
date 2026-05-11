"""Executive KPI computations for customer personality analysis."""

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


def response_rate(df: pd.DataFrame) -> float:
    """Calculate campaign response rate (0-100)."""
    if "Response" not in df.columns:
        return 0.0
    response_rate = float(df["Response"].mean() * 100)
    return response_rate


def total_revenue(df: pd.DataFrame) -> float:
    """Calculate total revenue from all product categories."""
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_cols = [col for col in spending_cols if col in df.columns]
    if not available_cols:
        return 0.0
    total = float(df[available_cols].sum().sum())
    return total


def avg_customer_value(df: pd.DataFrame) -> float:
    """Calculate average customer lifetime value based on total spending."""
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_cols = [col for col in spending_cols if col in df.columns]
    if not available_cols:
        return 0.0
    total_spending = df[available_cols].sum(axis=1)
    result = float(total_spending.mean())
    return result


def campaign_acceptance_rate(df: pd.DataFrame) -> float:
    """Calculate overall campaign acceptance rate."""
    campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
    available_cols = [col for col in campaign_cols if col in df.columns]
    if not available_cols:
        return 0.0
    acceptance_rate = float(df[available_cols].mean().mean() * 100)
    return acceptance_rate


def customer_engagement_score(df: pd.DataFrame) -> float:
    """Calculate customer engagement score (0-100) based on purchases and recency."""
    if "Recency" not in df.columns or "Total_Purchases" not in df.columns:
        # Fallback to available metrics
        purchase_cols = ["NumDealsPurchases", "NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
        available_cols = [col for col in purchase_cols if col in df.columns]
        if available_cols:
            total_purchases = df[available_cols].sum(axis=1)
            recency_score = 100 - (df.get("Recency", 50) / 100 * 100) if "Recency" in df.columns else 50
            engagement = (total_purchases / total_purchases.max() * 50) + (recency_score * 0.5)
            return float(engagement.mean())
        return 50.0

    # Recency score (lower recency = higher score)
    recency_score = 100 - (df["Recency"] / df["Recency"].max() * 100)

    # Purchase frequency score
    purchase_score = (df["Total_Purchases"] / df["Total_Purchases"].max() * 100)

    # Combined engagement score
    engagement = (recency_score * 0.4 + purchase_score * 0.6)
    result = float(engagement.mean())
    return result


def income_distribution_score(df: pd.DataFrame) -> float:
    """Calculate income diversity score (0-100, higher = more diverse)."""
    if "Income" not in df.columns:
        return 0.0
    income = pd.to_numeric(df["Income"], errors="coerce").fillna(df["Income"].median())
    if income.std() == 0:
        return 0.0
    # Coefficient of variation as diversity measure
    cv = float(income.std() / income.mean())
    score = float(np.clip(cv * 50, 0, 100))  # Scale to 0-100
    return score


def family_composition_index(df: pd.DataFrame) -> float:
    """Calculate family composition diversity index."""
    if "Kidhome" not in df.columns or "Teenhome" not in df.columns:
        return 0.0
    family_size = df["Kidhome"] + df["Teenhome"]
    diversity = float(family_size.value_counts().count() / len(family_size.unique()) * 100)
    return diversity
