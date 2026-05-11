"""Visual analytics + segmentasi (KMeans)."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.analytics import (
    fig_churn_distribution,
    fig_correlation_heatmap,
    fig_premium_churn,
    fig_tenure_churn,
)
from churn_intel.auth import login_form
from churn_intel.segmentation import add_segments, segment_counts
from churn_intel.streamlit_io import load_pipeline, load_customer_table
from churn_intel.ui_theme import inject_styles
from src.feature_engineering import engineer_features

inject_styles()
if not login_form():
    st.stop()

st.markdown("# Analytics & segmentasi")
st.caption("EDA interaktif pada dataset pelanggan + cluster KMeans.")

df = load_customer_table()
df_eng = engineer_features(df.copy())
if "is_premium_flag" in df_eng.columns:
    df_seg = add_segments(df_eng.drop(columns=["is_premium_flag"], errors="ignore"))
else:
    df_seg = add_segments(df_eng)

tab1, tab2, tab3 = st.tabs(["Distribusi & korelasi", "Premium & tenure", "Segmentasi"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_churn_distribution(df), use_container_width=True)
    with c2:
        num_cols = [
            "customer_age",
            "account_balance",
            "tenure_months",
            "total_transactions",
            "support_tickets",
            "avg_order_value",
            "churn",
        ]
        st.plotly_chart(fig_correlation_heatmap(df, num_cols), use_container_width=True)

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(fig_premium_churn(df), use_container_width=True)
    with c2:
        st.plotly_chart(fig_tenure_churn(df), use_container_width=True)

with tab3:
    if "segment_label" in df_seg.columns:
        st.plotly_chart(
            px.scatter(
                df_seg,
                x="tenure_months",
                y="account_balance",
                color="segment_label",
                size="total_transactions",
                hover_data=["churn"] if "churn" in df_seg.columns else None,
                title="Segmentasi (tenure vs saldo)",
            ).update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"),
            use_container_width=True,
        )
        sc = segment_counts(df_seg)
        if not sc.empty:
            st.plotly_chart(
                px.pie(sc, names="segment", values="count", title="Distribusi segmen").update_layout(
                    paper_bgcolor="rgba(0,0,0,0)"
                ),
                use_container_width=True,
            )

pipe = load_pipeline()
if pipe is not None and hasattr(pipe, "named_steps") and "classifier" in pipe.named_steps:
    clf = pipe.named_steps["classifier"]
    pre = pipe.named_steps["preprocessor"]
    if hasattr(clf, "feature_importances_"):
        names = list(pre.get_feature_names_out())
        vals = clf.feature_importances_
        import plotly.graph_objects as go

        order = sorted(range(len(vals)), key=lambda i: vals[i], reverse=True)[:12]
        fig = go.Figure(
            go.Bar(
                x=[vals[i] for i in order][::-1],
                y=[names[i] for i in order][::-1],
                orientation="h",
                marker=dict(color=[vals[i] for i in order][::-1], colorscale="Turbo"),
            )
        )
        fig.update_layout(
            title="Feature importance (model terpasang)",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef0f7"),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
