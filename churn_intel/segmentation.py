"""KMeans customer segments (heuristic labels)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def add_segments(df: pd.DataFrame, n_clusters: int = 4, random_state: int = 42) -> pd.DataFrame:
    """Append column `segment_id` and `segment_label` using churn + value proxies."""
    out = df.copy()
    num_cols = [
        c
        for c in [
            "customer_age",
            "account_balance",
            "tenure_months",
            "total_transactions",
            "support_tickets",
            "avg_order_value",
        ]
        if c in out.columns
    ]
    if len(num_cols) < 3:
        out["segment_label"] = "Unknown"
        out["segment_id"] = 0
        return out

    X = out[num_cols].fillna(0).to_numpy(dtype=float)
    Xs = StandardScaler().fit_transform(X)
    km = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    out["segment_id"] = km.fit_predict(Xs)

    # Name clusters by mean churn + balance heuristics
    if "churn" in out.columns:
        prof = out.groupby("segment_id").agg(churn_rate=("churn", "mean"), bal=("account_balance", "mean"))
    else:
        prof = out.groupby("segment_id").agg(bal=("account_balance", "mean"))
        prof["churn_rate"] = 0.0

    label_map: dict[int, str] = {}
    for sid, row in prof.iterrows():
        cr = float(row["churn_rate"])
        bal = float(row["bal"])
        if cr >= 0.45 and bal < 40000:
            label_map[int(sid)] = "At Risk"
        elif bal >= 70000 and cr < 0.25:
            label_map[int(sid)] = "High Value"
        elif cr < 0.2:
            label_map[int(sid)] = "Loyal"
        else:
            label_map[int(sid)] = "Inactive / Mixed"

    out["segment_label"] = out["segment_id"].map(label_map)
    return out


def segment_counts(df: pd.DataFrame) -> pd.DataFrame:
    if "segment_label" not in df.columns:
        return pd.DataFrame()
    return df["segment_label"].value_counts().rename_axis("segment").reset_index(name="count")
