"""Plotly charts — dark enterprise theme."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

_LAYOUT_BASE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(8,12,28,0.6)",
    font=dict(color="#e2e8f0", family="Inter, sans-serif"),
    margin=dict(l=40, r=24, t=48, b=40),
    hoverlabel=dict(bgcolor="#111928", font_size=12),
)


def fig_churn_timeline(df: pd.DataFrame) -> go.Figure:
    if "_month" not in df.columns or "churn" not in df.columns:
        return go.Figure()
    g = df.groupby("_month")["churn"].mean().reset_index()
    g.columns = ["month", "churn_rate"]
    fig = px.line(
        g,
        x="month",
        y="churn_rate",
        markers=True,
        title="Churn trend (periode sintetis)",
    )
    fig.update_traces(line=dict(width=3, color="#22d3ee"), marker=dict(size=8))
    fig.update_yaxes(tickformat=".0%")
    fig.update_layout(**_LAYOUT_BASE, height=380, xaxis_title="Periode (_month)")
    return fig


def fig_segment_donut(df: pd.DataFrame) -> go.Figure:
    if "segment_label" not in df.columns:
        return go.Figure()
    vc = df["segment_label"].value_counts().reset_index()
    vc.columns = ["segment", "count"]
    fig = px.pie(
        vc,
        names="segment",
        values="count",
        hole=0.55,
        title="Churn lens — segment pelanggan",
        color_discrete_sequence=px.colors.sequential.Teal_r,
    )
    fig.update_traces(textposition="outside", textinfo="percent+label")
    fig.update_layout(**_LAYOUT_BASE, height=400, showlegend=True)
    return fig


def fig_correlation(df: pd.DataFrame, cols: list[str]) -> go.Figure:
    sub = df[[c for c in cols if c in df.columns]].select_dtypes(include=[np.number])
    if sub.shape[1] < 2:
        return go.Figure()
    corr = sub.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        title="Heatmap korelasi fitur",
        color_continuous_scale="Turbo",
    )
    fig.update_layout(**_LAYOUT_BASE, height=420)
    return fig


def fig_revenue_bubble(df: pd.DataFrame) -> go.Figure:
    if "response_proba" not in df.columns:
        return go.Figure()
    d = df.copy()
    d["revenue_proxy"] = d.get("Total_Spending", 0)
    d["risk_loss"] = (1 - d["response_proba"]) * d["revenue_proxy"]  # Risk is lower response
    kw = dict(
        data_frame=d,
        x="Age",
        y="response_proba",
        size="risk_loss",
        title="Revenue opportunity — bubble ∝ potensi response (proba × spending)",
        opacity=0.75,
    )
    if "Education" in d.columns:
        kw["color"] = "Education"
    if "support_tickets" in d.columns:
        kw["hover_data"] = ["support_tickets"]
    fig = px.scatter(**kw)
    fig.update_layout(**_LAYOUT_BASE, height=420)
    fig.update_yaxes(tickformat=".0%")
    return fig


def fig_clv_distribution(df: pd.DataFrame) -> go.Figure:
    d = df.copy()
    # Use Total_Spending for marketing campaign CLV proxy
    d["clv_proxy"] = d.get("Total_Spending", 0) * 0.15  # 15% margin as CLV proxy
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Histogram CLV proxy", "Violin"))
    fig.add_trace(go.Histogram(x=d["clv_proxy"], nbinsx=35, marker_color="#818cf8", name=""), row=1, col=1)
    fig.add_trace(
        go.Violin(y=d["clv_proxy"], box_visible=True, meanline_visible=True, fillcolor="#22d3ee", line_color="#22d3ee", name=""),
        row=1,
        col=2,
    )
    fig.update_layout(**_LAYOUT_BASE, height=400, showlegend=False, title_text="Distribusi nilai aktivitas (proxy CLV)")
    return fig


def fig_retention_funnel(df: pd.DataFrame) -> go.Figure:
    if "tenure_months" not in df.columns:
        return go.Figure()
    d = df.copy()
    d["stage"] = pd.cut(
        d["tenure_months"],
        bins=[-1, 3, 12, 36, 200],
        labels=["Onboarding", "Growth", "Stable", "Champion"],
    )
    vc = d["stage"].value_counts().reindex(["Onboarding", "Growth", "Stable", "Champion"]).fillna(0).astype(int)
    fig = go.Figure(go.Funnel(y=vc.index.tolist(), x=vc.values.tolist(), textinfo="value+percent initial"))
    fig.update_traces(marker=dict(color=["#22d3ee", "#38bdf8", "#818cf8", "#c084fc"]))
    fig.update_layout(**_LAYOUT_BASE, height=400, title="Funnel retensi (berbasis tenure)")
    return fig


def fig_gauge_risk(mean_proba: float) -> go.Figure:
    val = float(np.clip(mean_proba * 100, 0, 100))
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": " %"},
            title={"text": "Executive churn pressure"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#22d3ee"},
                "steps": [
                    {"range": [0, 35], "color": "rgba(52,211,153,0.25)"},
                    {"range": [35, 65], "color": "rgba(251,191,36,0.2)"},
                    {"range": [65, 100], "color": "rgba(251,113,133,0.28)"},
                ],
                "threshold": {"line": {"color": "white", "width": 2}, "thickness": 0.8, "value": 65},
            },
        )
    )
    fig.update_layout(**_LAYOUT_BASE, height=320)
    return fig


def fig_pca_segments(df: pd.DataFrame) -> go.Figure:
    need = {"segment_label", "Response"}
    if not need.issubset(set(df.columns)):
        return go.Figure()
    num = df.select_dtypes(include=[np.number]).drop(columns=["Response"], errors="ignore")
    num = num.drop(columns=["response_proba"], errors="ignore")
    if num.shape[1] < 2:
        return go.Figure()
    from sklearn.decomposition import PCA

    X = num.fillna(0).to_numpy()
    pca = PCA(n_components=2, random_state=42)
    xy = pca.fit_transform(X)
    d = df.copy()
    d["pc1"], d["pc2"] = xy[:, 0], xy[:, 1]
    fig = px.scatter(
        d,
        x="pc1",
        y="pc2",
        color="segment_label",
        symbol="churn",
        title="PCA — proyeksi cluster & churn",
        opacity=0.82,
    )
    fig.update_layout(**_LAYOUT_BASE, height=440)
    return fig
