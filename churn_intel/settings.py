"""Central paths and constants."""

from pathlib import Path

# churn_intel/settings.py → project root is parent.parent
ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = ROOT / "models" / "customer_churn_model.joblib"
DATA_RAW_DIR = ROOT / "data" / "raw"
DATA_PROCESSED_DIR = ROOT / "data" / "processed"
CUSTOMERS_CSV = DATA_RAW_DIR / "customers.csv"
HISTORY_DB = DATA_PROCESSED_DIR / "prediction_history.sqlite"
METRICS_JSON = ROOT / "metrics" / "model_metrics.json"

RAW_INPUT_COLUMNS = [
    "ID",
    "Year_Birth",
    "Education",
    "Marital_Status",
    "Income",
    "Kidhome",
    "Teenhome",
    "Dt_Customer",
    "Recency",
    "MntWines",
    "MntFruits",
    "MntMeatProducts",
    "MntFishProducts",
    "MntSweetProducts",
    "MntGoldProds",
    "NumDealsPurchases",
    "NumWebPurchases",
    "NumCatalogPurchases",
    "NumStorePurchases",
    "NumWebVisitsMonth",
    "AcceptedCmp3",
    "AcceptedCmp4",
    "AcceptedCmp5",
    "AcceptedCmp1",
    "AcceptedCmp2",
    "Complain",
    "Z_CostContact",
    "Z_Revenue",
    "Response",  # Target: Response to last campaign
]
