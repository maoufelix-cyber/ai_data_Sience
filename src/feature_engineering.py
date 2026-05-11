import pandas as pd


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add domain-specific derived features to the customer dataset."""
    df = df.copy()
    df["transactions_per_month"] = df["total_transactions"] / (df["tenure_months"].replace(0, 1))
    df["avg_balance_per_month"] = df["account_balance"] / (df["tenure_months"].replace(0, 1))
    df["ticket_per_transaction"] = df["support_tickets"] / (df["total_transactions"].replace(0, 1))
    df["is_premium_flag"] = df["is_premium"].map({"yes": 1, "no": 0})
    return df
