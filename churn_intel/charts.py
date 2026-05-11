"""Shared Plotly figures."""

from __future__ import annotations

import plotly.graph_objects as go


def churn_gauge(probability: float) -> go.Figure:
    pct = probability * 100
    bar = "#22d3ee" if probability < 0.35 else "#fbbf24" if probability < 0.65 else "#f87171"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=pct,
            number={"suffix": " %", "font": {"size": 28}},
            title={"text": "Probabilitas churn", "font": {"size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1},
                "bar": {"color": bar},
                "bgcolor": "rgba(255,255,255,0.04)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 35], "color": "rgba(34, 211, 238, 0.12)"},
                    {"range": [35, 65], "color": "rgba(251, 191, 36, 0.12)"},
                    {"range": [65, 100], "color": "rgba(248, 113, 113, 0.15)"},
                ],
                "threshold": {
                    "line": {"color": "#f43f5e", "width": 2},
                    "thickness": 0.8,
                    "value": 65,
                },
            },
        )
    )
    fig.update_layout(
        height=300,
        margin=dict(l=24, r=24, t=44, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#eef0f7", "family": "Inter, sans-serif"},
        transition=dict(duration=950, easing="cubic-in-out"),
    )
    return fig
