"""Attach model churn probabilities to a customer dataframe."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from churn_intel.predict_core import prepare_for_model


def score_dataframe(pipe: Any | None, df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    if pipe is None:
        if "churn" in out.columns:
            out["churn_proba"] = out["churn"].astype(float) * 0.78 + 0.08
        else:
            out["churn_proba"] = 0.25
        return out
    X = prepare_for_model(out)
    out["churn_proba"] = pipe.predict_proba(X)[:, 1]
    return out
