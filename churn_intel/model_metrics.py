"""Load offline model evaluation metrics (exported from training notebook)."""

from __future__ import annotations

import json
from typing import Any

from churn_intel.settings import METRICS_JSON


def load_metrics() -> dict[str, Any]:
    if not METRICS_JSON.exists():
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1": None,
            "roc_auc": None,
            "cv_mean": None,
            "cv_std": None,
            "train_accuracy": None,
            "test_accuracy": None,
            "note": "Jalankan notebook evaluasi dan simpan metrics ke metrics/model_metrics.json",
        }
    with open(METRICS_JSON, encoding="utf-8") as f:
        return json.load(f)
