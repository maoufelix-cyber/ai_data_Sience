"""
AI Executive Analytics — main layout (hero, KPIs, charts, insights, risk, table, live).
"""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from churn_intel.segmentation import add_segments
from dashboard.services.charts import (
    fig_churn_timeline,
    fig_clv_distribution,
    fig_correlation,
    fig_gauge_risk,
    fig_pca_segments,
    fig_retention_funnel,
    fig_revenue_bubble,
    fig_segment_donut,
)
from dashboard.services.filters import apply_filters, render_sidebar_filters
from dashboard.services.insights import action_recommendations, executive_summary_paragraph, insight_feed
from dashboard.services.metrics import (
    add_synthetic_month,
    avg_customer_value,
    campaign_acceptance_rate,
    customer_engagement_score,
    response_rate,
    split_compare,
    total_revenue,
)
from dashboard.services.scoring import score_dataframe
from dashboard.services.sparkline import sparkline_svg
from dashboard.styles.executive_css import inject_executive_css, kpi_html


def _prep_base(df: pd.DataFrame, pipe: Any | None) -> pd.DataFrame:
    b = add_synthetic_month(df.copy())
    b = add_segments(b)
    b = score_dataframe(pipe, b)
    b["customer_id"] = np.arange(1, len(b) + 1)
    return b


def render_executive_dashboard(df: pd.DataFrame, pipe: Any | None) -> None:
    inject_executive_css()

    base = _prep_base(df, pipe)

    with st.sidebar:
        st.markdown("---")
        st.markdown("Sidebar content")
        st.button("Submit")
        filt = render_sidebar_filters(base)

    df_f = apply_filters(base, filt)
    if len(df_f) < 5:
        st.warning("Filter terlalu ketat — longgarkan rentang untuk melihat analitik.")
        df_f = base

    h1, h2 = split_compare(df_f)

    # Calculate response rate - ensure float scalar
    prev_response = float(h1["Response"].mean()) if "Response" in h1.columns and len(h1) > 0 else None
    response_rate_val = float(df_f["Response"].mean()) if "Response" in df_f.columns and len(df_f) > 0 else 0.0

    # Calculate delta percentage - ensure float scalar
    if prev_response is not None and prev_response > 0:
        delta_pct = (response_rate_val - prev_response) / prev_response * 100
    else:
        delta_pct = 0.0
    delta_pct = float(delta_pct)  # Ensure scalar

    n = len(df_f)
    total_rev = total_revenue(df_f)
    avg_cust_val = avg_customer_value(df_f)
    campaign_acc_rate = campaign_acceptance_rate(df_f)
    engagement_score = customer_engagement_score(df_f)

    # Calculate high-value customers (top 25% by spending)
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_spending = [col for col in spending_cols if col in df_f.columns]
    if available_spending:
        total_spending = df_f[available_spending].sum(axis=1)
        high_value_pct = (total_spending > total_spending.quantile(0.75)).mean()
        high_value_customers = int(high_value_pct * n)
    else:
        high_value_customers = 0

    # --- HERO
    summary = executive_summary_paragraph(df_f, prev_response)
    st.markdown(
        f"""
        <div class="exec-hero-shell">
          <div class="exec-hero-title">Customer Personality Analytics</div>
          <p style="color:#94a3b8;margin:0.5rem 0 0 0;font-size:0.95rem;">{summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    spark_vals = [float(x) for x in np.linspace(max(0.05, response_rate_val - 0.08), response_rate_val + 0.02, 8)]

    hero_cols = st.columns(5)
    metrics_hero = [
        ("Total pelanggan", f"{n:,}", None, None, "👥"),
        ("Total revenue", f"${total_rev:,.0f}", f"Response mom {delta_pct:+.1f}%*", delta_pct >= 0, "💸"),
        ("Response rate", f"{response_rate_val:.1%}", None, None, "🎯"),
        ("Avg customer value", f"${avg_cust_val:,.0f}", None, None, "💎"),
        ("High-value customers", f"{high_value_customers:,}", None, None, "⭐"),
    ]
    for col, (lab, val, dlt, dpos, ic) in zip(hero_cols, metrics_hero):
        with col:
            sp = sparkline_svg(spark_vals, stroke="#a5b4fc")
            st.markdown(kpi_html(lab, val, dlt, dpos, sp, ic), unsafe_allow_html=True)
    st.caption("*Mom = pembagian data (50/50) sebagai proxy tren — ganti dengan time index nyata bila tersedia.")

    # --- option menu (optional dependency)
    try:
        from streamlit_option_menu import option_menu

        view = option_menu(
            None,
            ["Summary", "Analytics", "Intelligence", "Operations", "Live"],
            icons=["speedometer2", "graph-up-arrow", "cpu", "table", "activity"],
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "gap": "0.35rem"},
                "nav-link": {
                    "font-size": "0.85rem",
                    "padding": "0.45rem 0.9rem",
                    "border-radius": "12px",
                    "background-color": "rgba(17,25,40,0.55)",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(90deg,#22d3ee,#818cf8)",
                    "color": "#050816",
                    "font-weight": "600",
                },
            },
        )
    except Exception:
        view = st.radio("Section", ["Summary", "Analytics", "Intelligence", "Operations", "Live"], horizontal=True)

    try:
        from streamlit_extras.metric_cards import style_metric_cards

        style_metric_cards(
            background_color="rgba(17,25,40,0.55)",
            border_left_color="#22d3ee",
            border_color="rgba(129,140,248,0.25)",
            border_size_px=1,
            box_shadow=True,
        )
    except Exception:
        pass

    if view == "Summary":
        _tab_summary(df_f, response_rate_val, prev_response, total_rev, avg_cust_val)
    elif view == "Analytics":
        _tab_analytics(df_f)
    elif view == "Intelligence":
        _tab_intelligence(df_f)
    elif view == "Operations":
        _tab_operations(df_f, pipe)
    else:
        _tab_live(df_f, mean_proba)


def _tab_summary(df_f: pd.DataFrame, response_rate_val: float, prev_response: float | None, total_rev: float, avg_cust_val: float) -> None:
    st.subheader("Advanced KPI cards")
    prev_h1, _prev_h2 = split_compare(df_f)

    def d(cur, prev):
        if prev is None or prev == 0:
            return None, None
        p = (cur - prev) / abs(prev) * 100
        return f"{p:+.1f}% vs baseline", p >= 0  # Positive change is good for response rate

    response_prev = float(prev_h1["Response"].mean()) if "Response" in prev_h1.columns else response_rate_val
    rev_prev = total_revenue(prev_h1)
    rev_cur = total_rev
    acc_prev = campaign_acceptance_rate(prev_h1)
    acc_cur = campaign_acceptance_rate(df_f)
    eng_cur = customer_engagement_score(df_f)

    # Calculate spending metrics
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_spending = [col for col in spending_cols if col in df_f.columns]
    if available_spending:
        total_spending = df_f[available_spending].sum(axis=1)
        avg_spending = float(total_spending.mean())
        spending_prev = prev_h1[available_spending].sum(axis=1).mean() if available_spending[0] in prev_h1.columns else avg_spending
    else:
        avg_spending = 0.0
        spending_prev = 0.0

    strokes = ["#fb7185", "#22d3ee", "#818cf8", "#34d399", "#fbbf24", "#4ade80", "#38bdf8", "#c084fc"]
    kpis = [
        ("Response rate", f"{response_rate_val:.1%}", *d(response_rate_val, response_prev)),
        ("Active customers", f"{len(df_f):,}", None, None),
        ("Total revenue", f"${rev_cur:,.0f}", *d(rev_cur, rev_prev)),
        ("Avg spending", f"${avg_spending:.0f}", *d(avg_spending, spending_prev)),
        ("Campaign acceptance", f"{acc_cur:.1%}", *d(acc_cur, acc_prev)),
        ("Engagement score", f"{eng_cur:.0f}/100", None, None),
        ("High-value customers", f"{high_value_customers:,}", None, None),
        ("Avg customer value", f"${avg_cust_val:,.0f}", None, None),
    ]
    r1 = st.columns(4)
    r2 = st.columns(4)
    rng = np.random.default_rng(42)
    for i, pack in enumerate(kpis):
        lab, val, dlt, dpos = pack
        row = r1 if i < 4 else r2
        col = row[i % 4]
        with col:
            spark_vals_local = list(np.clip(rng.normal(0.48 + i * 0.015, 0.07, 8), 0.05, 0.95))
            sp = sparkline_svg(spark_vals_local, stroke=strokes[i % len(strokes)])
            st.markdown(kpi_html(lab, val, dlt, dpos, sp, "●"), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Campaign performance panel")
    c1, c2 = st.columns([1, 1])
    with c1:
        # Create a simple gauge for response rate
        fig_gauge = {
            "data": [{
                "type": "indicator",
                "mode": "gauge+number",
                "value": response_rate_val * 100,
                "title": {"text": "Response Rate"},
                "gauge": {
                    "axis": {"range": [0, 30]},
                    "bar": {"color": "#22d3ee"},
                    "steps": [
                        {"range": [0, 10], "color": "#fee2e2"},
                        {"range": [10, 20], "color": "#fef3c7"},
                        {"range": [20, 30], "color": "#d1fae5"}
                    ]
                }
            }],
            "layout": {"height": 200, "margin": {"t": 50, "b": 0, "l": 0, "r": 0}}
        }
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
        st.progress(min(1.0, response_rate_val), text=f"Campaign response rate ({response_rate_val:.1%})")
    with c2:
        st.metric("Total campaign revenue", f"${total_rev:,.0f}")
        st.metric("Avg customer value", f"${avg_cust_val:,.0f}")
        st.metric("Campaign acceptance rate", f"{acc_cur:.1%}")
        if response_rate_val >= 0.15:
            st.success("Campaign performance: excellent.")
        elif response_rate_val >= 0.10:
            st.info("Campaign performance: good.")
        else:
            st.warning("Campaign performance: needs optimization.")

    # Campaign trend chart
    st.altair_chart(
        alt.Chart(pd.DataFrame({"month": range(1, 13), "response": np.clip(np.random.default_rng(7).normal(response_rate_val, 0.02, 12), 0.02, 0.3)}))
        .mark_line(point=True, color="#22d3ee")
        .encode(x="month:O", y="response:Q", tooltip=["month", alt.Tooltip("response:Q", format=".2%")])
        .properties(height=160, title="Campaign response trend (demo)")
        .configure_view(strokeWidth=0)
        .configure(background="transparent"),
        use_container_width=True,
    )


def _tab_analytics(df_f: pd.DataFrame) -> None:
    st.subheader("Interactive analytics")
    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(fig_churn_timeline(df_f), use_container_width=True)
        st.plotly_chart(fig_segment_donut(df_f), use_container_width=True)
        st.plotly_chart(fig_retention_funnel(df_f), use_container_width=True)
    with g2:
        cols = [
            "Income",
            "Recency",
            "MntWines",
            "Total_Spending",
            "Response",
            "response_proba",
        ]
        st.plotly_chart(fig_correlation(df_f, cols), use_container_width=True)
        st.plotly_chart(fig_revenue_bubble(df_f), use_container_width=True)
        st.plotly_chart(fig_clv_distribution(df_f), use_container_width=True)
    st.plotly_chart(fig_pca_segments(df_f), use_container_width=True)


def _tab_intelligence(df_f: pd.DataFrame) -> None:
    st.subheader("AI insight engine")
    for sev, text in insight_feed(df_f):
        cls = "exec-insight-card"
        if sev == "warn":
            cls += " warn"
        elif sev == "danger":
            cls += " danger"
        st.markdown(f'<div class="{cls}">{text}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Executive action center")
    for prio, title, body in action_recommendations(df_f):
        color = "#fb7185" if prio == "HIGH" else "#fbbf24" if prio == "MED" else "#94a3b8"
        st.markdown(
            f"""
            <div style="border-radius:14px;padding:1rem;margin-bottom:0.6rem;background:rgba(17,25,40,0.75);
            border:1px solid rgba(129,140,248,0.2);border-left:4px solid {color};">
              <div style="font-size:0.72rem;font-weight:700;color:{color};">{prio}</div>
              <div style="font-weight:600;color:#f1f5f9;">{title}</div>
              <div style="color:#94a3b8;font-size:0.9rem;">{body}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _tab_operations(df_f: pd.DataFrame, pipe: Any | None) -> None:
    st.subheader("Customer analytics table")
    show = df_f.copy()
    show["risk_level"] = pd.cut(
        show["response_proba"],
        bins=[-0.01, 0.35, 0.65, 0.85, 1.0],
        labels=["Low", "Medium", "High", "Critical"],
    ).astype(str)
    show["revenue_value"] = show.get("Total_Spending", 0)
    show["engagement_score"] = show.get("Purchases_Per_Month", 0)
    cols = [
        "ID",
        "response_proba",
        "risk_level",
        "revenue_value",
        "engagement_score",
        "Education",
        "Age",
    ]
    cols = [c for c in cols if c in show.columns]
    t = show[cols].sort_values("response_proba", ascending=False)
    st.dataframe(
        t.head(500),
        use_container_width=True,
        hide_index=True,
        column_config={
            "response_proba": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "revenue_value": st.column_config.NumberColumn(format="$%d"),
        },
    )
    st.download_button("Export CSV (500 baris atas)", t.head(500).to_csv(index=False).encode("utf-8"), "executive_export.csv")


def _tab_live(df_f: pd.DataFrame, mean_proba: float) -> None:
    st.subheader("Realtime monitoring (simulasi)")
    slot = st.empty()
    frag = getattr(st, "fragment", None)
    if callable(frag):

        @frag(run_every=20)
        def _pulse():
            jitter = float(
                np.clip(mean_proba + np.random.default_rng(int(time.time()) % 1000).normal(0, 0.012), 0, 1)
            )
            slot.markdown(
                f"**Live response pressure** `{jitter:.2%}` · _tick {datetime.now().strftime('%H:%M:%S')}_ — "
                f"Pelanggan dipantau: **{len(df_f)}**"
            )

        _pulse()
    else:
        slot.metric("Response pressure (statis)", f"{mean_proba:.2%}")
    st.caption("Panel live memakai `st.fragment` bila tersedia (Streamlit ≥ 1.33); jika tidak, tampil statis.")

    st.markdown("##### Response ticker (synthetic)")
    risky = df_f.nlargest(8, "response_proba") if "response_proba" in df_f.columns else df_f.head(8)
    for _, row in risky.iterrows():
        st.markdown(
            f"<span class='exec-chip'>ID {row.get('ID', '?')}</span> "
            f"<span class='exec-chip'>proba {row.get('response_proba', 0):.0%}</span> "
            f"<span class='exec-chip'>spending ${row.get('Total_Spending', 0):.0f}</span>",
            unsafe_allow_html=True,
        )