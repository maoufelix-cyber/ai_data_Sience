import pandas as pd
from datetime import datetime


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add domain-specific derived features for customer personality analysis."""
    df = df.copy()

    # Age calculation from Year_Birth
    current_year = datetime.now().year
    df["Age"] = current_year - df["Year_Birth"]

    # Total spending across all product categories
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    df["Total_Spending"] = df[spending_cols].sum(axis=1)

    # Average spending per category
    df["Avg_Spending"] = df["Total_Spending"] / len(spending_cols)

    # Total purchases across all channels
    purchase_cols = ["NumDealsPurchases", "NumWebPurchases", "NumCatalogPurchases", "NumStorePurchases"]
    df["Total_Purchases"] = df[purchase_cols].sum(axis=1)

    # Purchase frequency (purchases per month - approximate)
    # Assuming Dt_Customer represents enrollment date
    df["Dt_Customer"] = pd.to_datetime(df["Dt_Customer"], format="%d-%m-%Y", errors="coerce")
    df["Customer_Tenure_Days"] = (datetime.now() - df["Dt_Customer"]).dt.days
    df["Customer_Tenure_Months"] = df["Customer_Tenure_Days"] / 30.44  # Average days per month

    # Purchases per month (engagement metric)
    df["Purchases_Per_Month"] = df["Total_Purchases"] / df["Customer_Tenure_Months"].clip(lower=1)

    # Spending per month
    df["Spending_Per_Month"] = df["Total_Spending"] / df["Customer_Tenure_Months"].clip(lower=1)

    # Family size (1 + kids + teens)
    df["Family_Size"] = 1 + df["Kidhome"] + df["Teenhome"]

    # Has children flag
    df["Has_Children"] = (df["Kidhome"] + df["Teenhome"] > 0).astype(int)

    # Education level (ordinal encoding)
    education_map = {
        "Basic": 1,
        "2n Cycle": 2,
        "Graduation": 3,
        "Master": 4,
        "PhD": 5
    }
    df["Education_Level"] = df["Education"].map(education_map).fillna(3)

    # Marital status (simplified)
    df["Is_Single"] = df["Marital_Status"].isin(["Single", "Divorced", "Widow"]).astype(int)
    df["Is_Married"] = (df["Marital_Status"] == "Married").astype(int)
    df["Is_Together"] = (df["Marital_Status"] == "Together").astype(int)

    # Campaign acceptance (any campaign accepted)
    campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
    df["Accepted_Any_Campaign"] = df[campaign_cols].max(axis=1)

    # Total campaigns accepted
    df["Total_Campaigns_Accepted"] = df[campaign_cols].sum(axis=1)

    # Income per family member
    df["Income_Per_Family_Member"] = df["Income"] / df["Family_Size"]

    # Recency score (lower recency = more recent = better)
    df["Recency_Score"] = 100 - (df["Recency"] / df["Recency"].max() * 100)

    # Web engagement ratio
    df["Web_Engagement_Ratio"] = df["NumWebPurchases"] / df["NumWebVisitsMonth"].clip(lower=1)

    # Catalog vs Store preference
    df["Catalog_Preference"] = df["NumCatalogPurchases"] / df["Total_Purchases"].clip(lower=1)
    df["Store_Preference"] = df["NumStorePurchases"] / df["Total_Purchases"].clip(lower=1)

    # Deal sensitivity
    df["Deal_Sensitivity"] = df["NumDealsPurchases"] / df["Total_Purchases"].clip(lower=1)

    # Fill missing values
    df["Income"] = df["Income"].fillna(df["Income"].median())
    df["Income_Per_Family_Member"] = df["Income_Per_Family_Member"].fillna(df["Income_Per_Family_Member"].median())

    # Convert categorical to numeric where needed
    df["Education_Num"] = df["Education"].astype("category").cat.codes
    df["Marital_Status_Num"] = df["Marital_Status"].astype("category").cat.codes

    return df
