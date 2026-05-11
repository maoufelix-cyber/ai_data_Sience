"""Feature prep aligned with training pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.feature_engineering import engineer_features


def prepare_for_model(df: pd.DataFrame) -> pd.DataFrame:
    out = engineer_features(df.copy())
    return out.drop(columns=["is_premium_flag"], errors="ignore")
