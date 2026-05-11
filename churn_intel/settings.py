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
    "customer_age",
    "account_balance",
    "tenure_months",
    "total_transactions",
    "is_premium",
    "support_tickets",
    "avg_order_value",
]
