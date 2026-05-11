"""Plotly charts for analytics dashboard."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def fig_churn_distribution(df: pd.DataFrame) -> go.Figure:
    vc = df["churn"].value_counts()
    lab_map = {0: "Tetap", 1: "Churn", "0": "Tetap", "1": "Churn"}
    labels = [lab_map.get(i, lab_map.get(str(i), str(i))) for i in vc.index]
    d = pd.DataFrame({"label": labels, "count": vc.values})
    fig = px.bar(d, x="label", y="count", color="label", title="Distribusi churn")
    fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def fig_correlation_heatmap(df: pd.DataFrame, cols: list[str]) -> go.Figure:
    sub = df[[c for c in cols if c in df.columns]].select_dtypes(include=[np.number])
    if sub.shape[1] < 2:
        fig = go.Figure()
        fig.update_layout(title="Korelasi — kolom numerik tidak cukup")
        return fig
    corr = sub.corr()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", title="Heatmap korelasi fitur numerik")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
    return fig


def fig_premium_churn(df: pd.DataFrame) -> go.Figure:
    if "is_premium" not in df.columns or "churn" not in df.columns:
        return go.Figure()
    g = df.groupby("is_premium")["churn"].mean().reset_index()
    g.columns = ["is_premium", "churn_rate"]
    fig = px.bar(g, x="is_premium", y="churn_rate", title="Rata-rata churn rate vs premium", color="is_premium")
    fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(tickformat=".0%")
    return fig


def fig_tenure_churn(df: pd.DataFrame) -> go.Figure:
    if "tenure_months" not in df.columns:
        return go.Figure()
    fig = px.box(df, x="churn", y="tenure_months", color="churn", title="Tenure vs churn")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig


def fig_feature_importance(names: list[str], values: np.ndarray, top_k: int = 12) -> go.Figure:
    order = np.argsort(values)[::-1][:top_k]
    fig = go.Figure(
        go.Bar(
            x=values[order][::-1],
            y=[names[i] for i in order][::-1],
            orientation="h",
            marker=dict(color=values[order][::-1], colorscale="Viridis"),
        )
    )
    fig.update_layout(title="Feature importance (Random Forest)", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig
