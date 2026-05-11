"""Synthetic churn dataset (aligned with notebook logic)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from churn_intel.settings import CUSTOMERS_CSV, DATA_RAW_DIR


def create_synthetic_churn_data(n_samples: int = 2000, random_state: int = 42) -> pd.DataFrame:
    """Generate synthetic churn dataset with proper type handling."""
    rng = np.random.RandomState(random_state)
    data = {
        "customer_age": rng.randint(18, 70, size=n_samples),
        "account_balance": rng.normal(50000, 20000, size=n_samples).clip(0),
        "tenure_months": rng.randint(1, 60, size=n_samples),
        "total_transactions": rng.poisson(15, size=n_samples).clip(0),
        "is_premium": rng.choice(["yes", "no"], size=n_samples, p=[0.3, 0.7]),
        "support_tickets": rng.poisson(2, size=n_samples),
        "avg_order_value": rng.normal(150, 80, size=n_samples).clip(10),
    }
    df = pd.DataFrame(data)
    
    # Calculate churn score with proper type handling
    # All operations result in float Series - convert to numpy array for proper float calculation
    score = (
        df["support_tickets"].values.astype(float) * 0.35
        + (df["account_balance"].values.astype(float) < 20000).astype(float) * 0.25
        + (df["tenure_months"].values.astype(float) < 12).astype(float) * 0.25
        + (df["is_premium"].values != "yes").astype(float) * 0.15
        + rng.randn(n_samples) * 0.1
    )
    
    # Create churn binary column
    df["churn"] = (score > 0.7).astype(int)
    return df


def ensure_sample_csv(n_samples: int = 2000) -> Path:
    """Write customers.csv if missing; return path."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not CUSTOMERS_CSV.exists():
        create_synthetic_churn_data(n_samples).to_csv(CUSTOMERS_CSV, index=False)
    return CUSTOMERS_CSV
