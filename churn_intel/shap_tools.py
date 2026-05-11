"""SHAP explanations for sklearn Pipeline (ColumnTransformer + RandomForestClassifier)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

try:
    import shap
except ImportError:  # pragma: no cover
    shap = None


def explain_row(pipeline: Any, X_df: pd.DataFrame):
    """
    Return (shap_row, feature_names, matplotlib_figure).

    shap_row aligns with transformed feature space (after ColumnTransformer).
    """
    if shap is None:
        raise RuntimeError("Package `shap` is not installed.")

    if "preprocessor" not in pipeline.named_steps or "classifier" not in pipeline.named_steps:
        raise ValueError("Pipeline must have steps named 'preprocessor' and 'classifier'.")

    pre = pipeline.named_steps["preprocessor"]
    clf = pipeline.named_steps["classifier"]
    Xt = pre.transform(X_df)
    names = list(pre.get_feature_names_out())

    explainer = shap.TreeExplainer(clf)
    sv = explainer.shap_values(Xt)

    if isinstance(sv, list):
        sv_pos = np.asarray(sv[1])
    else:
        sv_pos = np.asarray(sv)

    if sv_pos.ndim == 1:
        row = sv_pos
    else:
        row = sv_pos[0]

    row = row.astype(float)

    fig = None
    try:
        import matplotlib.pyplot as plt

        plt.close("all")
        k = min(14, len(names))
        order = np.argsort(np.abs(row))[::-1][:k][::-1]
        colors = ["#f97316" if row[i] >= 0 else "#22d3ee" for i in order]
        fig, ax = plt.subplots(figsize=(9, 5.2))
        ax.barh([names[i] for i in order], row[order], color=colors, edgecolor="none")
        ax.axvline(0, color="white", linewidth=0.6, alpha=0.4)
        ax.set_title("SHAP values (positif → churn, negatif → tetap)")
        ax.set_xlabel("SHAP")
        fig.patch.set_facecolor("#0b0d12")
        ax.set_facecolor("#12151f")
        ax.tick_params(colors="#e8eaed")
        ax.title.set_color("#e8eaed")
        ax.xaxis.label.set_color("#e8eaed")
        fig.tight_layout()
    except Exception:
        fig = None

    return row, names, fig


def top_push_pull(
    shap_row: np.ndarray, names: list[str], k: int = 6
) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    pairs = list(zip(names, shap_row.astype(float)))
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    toward_churn = [(n, v) for n, v in pairs if v > 0][:k]
    toward_stay = [(n, v) for n, v in pairs if v < 0][:k]
    return toward_churn, toward_stay
