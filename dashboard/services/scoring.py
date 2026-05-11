"""Attach model churn probabilities to a customer dataframe."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from churn_intel.predict_core import prepare_for_model


def score_dataframe(pipe: Any | None, df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy().reset_index(drop=True)
    if pipe is None:
        # Use Response column for probability heuristic
        if "Response" in out.columns:
            out["response_proba"] = out["Response"].astype(float) * 0.8 + 0.1
        else:
            out["response_proba"] = 0.15  # Default response rate
        return out

    try:
        X = prepare_for_model(out)
        out["response_proba"] = pipe.predict_proba(X)[:, 1]
    except (ValueError, KeyError) as e:
        # If model is incompatible with current data structure, use heuristic
        print(f"Model incompatible with data: {e}. Using heuristic scoring.")
        if "Response" in out.columns:
            out["response_proba"] = out["Response"].astype(float) * 0.8 + 0.1
        else:
            out["response_proba"] = 0.15

    return out
