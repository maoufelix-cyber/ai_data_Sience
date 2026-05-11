"""Synthetic customer personality dataset (aligned with marketing campaign data)."""

from __future__ import annotations

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

from churn_intel.settings import CUSTOMERS_CSV, DATA_RAW_DIR


def create_synthetic_customer_data(n_samples: int = 2240, random_state: int = 42) -> pd.DataFrame:
    """Generate synthetic customer personality analysis dataset."""
    rng = np.random.RandomState(random_state)

    # Base customer data
    data = {
        "ID": np.arange(1000, 1000 + n_samples),
        "Year_Birth": rng.randint(1940, 2001, size=n_samples),
        "Education": rng.choice(["Basic", "2n Cycle", "Graduation", "Master", "PhD"],
                               size=n_samples, p=[0.05, 0.1, 0.5, 0.2, 0.15]),
        "Marital_Status": rng.choice(["Single", "Married", "Together", "Divorced", "Widow"],
                                    size=n_samples, p=[0.25, 0.35, 0.25, 0.1, 0.05]),
        "Income": rng.normal(55000, 25000, size=n_samples).clip(1000, 200000),
        "Kidhome": rng.choice([0, 1, 2], size=n_samples, p=[0.6, 0.3, 0.1]),
        "Teenhome": rng.choice([0, 1, 2], size=n_samples, p=[0.7, 0.25, 0.05]),
    }

    df = pd.DataFrame(data)

    # Add missing income values (similar to real dataset)
    missing_indices = rng.choice(n_samples, size=int(n_samples * 0.01), replace=False)
    df.loc[missing_indices, "Income"] = np.nan

    # Customer enrollment dates (last 2 years)
    start_date = datetime.now() - timedelta(days=730)
    df["Dt_Customer"] = [start_date + timedelta(days=rng.randint(0, 730))
                        for _ in range(n_samples)]
    df["Dt_Customer"] = df["Dt_Customer"].dt.strftime("%d-%m-%Y")

    # Recency (days since last purchase)
    df["Recency"] = rng.randint(0, 100, size=n_samples)

    # Spending amounts (product categories)
    df["MntWines"] = rng.poisson(300, size=n_samples) + rng.normal(0, 100, size=n_samples).clip(0)
    df["MntFruits"] = rng.poisson(30, size=n_samples) + rng.normal(0, 20, size=n_samples).clip(0)
    df["MntMeatProducts"] = rng.poisson(150, size=n_samples) + rng.normal(0, 50, size=n_samples).clip(0)
    df["MntFishProducts"] = rng.poisson(40, size=n_samples) + rng.normal(0, 15, size=n_samples).clip(0)
    df["MntSweetProducts"] = rng.poisson(30, size=n_samples) + rng.normal(0, 10, size=n_samples).clip(0)
    df["MntGoldProds"] = rng.poisson(40, size=n_samples) + rng.normal(0, 15, size=n_samples).clip(0)

    # Convert spending to integers
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    df[spending_cols] = df[spending_cols].astype(int).clip(0)

    # Purchase counts by channel
    df["NumDealsPurchases"] = rng.poisson(2, size=n_samples)
    df["NumWebPurchases"] = rng.poisson(4, size=n_samples)
    df["NumCatalogPurchases"] = rng.poisson(3, size=n_samples)
    df["NumStorePurchases"] = rng.poisson(6, size=n_samples)
    df["NumWebVisitsMonth"] = rng.poisson(5, size=n_samples)

    # Campaign acceptance (binary)
    campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
    for col in campaign_cols:
        df[col] = rng.choice([0, 1], size=n_samples, p=[0.85, 0.15])

    # Complain and response
    df["Complain"] = rng.choice([0, 1], size=n_samples, p=[0.95, 0.05])
    df["Z_CostContact"] = 3  # Constant
    df["Z_Revenue"] = 11     # Constant

    # Create response target (campaign response)
    # More likely to respond if: higher income, more spending, accepted previous campaigns, younger
    response_score = (
        (df["Income"].fillna(df["Income"].median()) / 100000) * 0.3 +
        (df["MntWines"] / 1000) * 0.2 +
        (df[campaign_cols].sum(axis=1) / 5) * 0.2 +
        ((2024 - df["Year_Birth"]) / 50) * 0.1 +
        rng.normal(0, 0.1, size=n_samples)
    )

    df["Response"] = (response_score > 0.4).astype(int)

    return df


def ensure_sample_csv(n_samples: int = 2240) -> Path:
    """Write customers.csv if missing; return path."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    if not CUSTOMERS_CSV.exists():
        create_synthetic_customer_data(n_samples).to_csv(CUSTOMERS_CSV, index=False, sep='\t')
    return CUSTOMERS_CSV
