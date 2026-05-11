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
    clv_estimate,
    retention_score,
    revenue_at_risk,
    satisfaction_index,
    split_compare,
    support_ratio,
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
    
    # Calculate churn rate - ensure float scalar
    prev_churn = float(h1["churn"].mean()) if "churn" in h1.columns and len(h1) > 0 else None
    churn_rate = float(df_f["churn"].mean()) if "churn" in df_f.columns and len(df_f) > 0 else 0.0
    
    # Calculate delta percentage - ensure float scalar
    if prev_churn is not None and prev_churn > 0:
        delta_pct = (churn_rate - prev_churn) / prev_churn * 100
    else:
        delta_pct = 0.0
    delta_pct = float(delta_pct)  # Ensure scalar

    n = len(df_f)
    mean_proba = float(df_f["churn_proba"].mean()) if "churn_proba" in df_f.columns and len(df_f) > 0 else churn_rate
    rar = revenue_at_risk(df_f)
    clv = clv_estimate(df_f)
    ret = retention_score(mean_proba)
    prem_users = int(df_f["is_premium"].astype(str).str.lower().eq("yes").sum()) if "is_premium" in df_f.columns else 0
    
    # Calculate ARPU - ensure float scalar
    if "avg_order_value" in df_f.columns and "churn_proba" in df_f.columns and n > 0:
        aov_vals = pd.to_numeric(df_f.get("avg_order_value", 0), errors="coerce").fillna(0)
        arpu = float((aov_vals * df_f["churn_proba"]).sum() / max(n, 1))
    else:
        arpu = 0.0

    # --- HERO
    summary = executive_summary_paragraph(df_f, prev_churn)
    st.markdown(
        f"""
        <div class="exec-hero-shell">
          <div class="exec-hero-title">Executive AI Analytics</div>
          <p style="color:#94a3b8;margin:0.5rem 0 0 0;font-size:0.95rem;">{summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    spark_vals = [float(x) for x in np.linspace(max(0.05, churn_rate - 0.08), churn_rate + 0.02, 8)]

    hero_cols = st.columns(5)
    metrics_hero = [
        ("Total pelanggan", f"{n:,}", None, None, "👥"),
        ("Revenue at risk (6m)", f"${rar:,.0f}", f"Churn mom {delta_pct:+.1f}%*", delta_pct <= 0, "💸"),
        ("Retention score", f"{ret:.0f}/100", None, None, "🛡️"),
        ("CLV rata-rata (proxy)", f"${clv:,.0f}", None, None, "💎"),
        ("Premium aktif", f"{prem_users:,}", None, None, "⭐"),
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
        _tab_summary(df_f, churn_rate, prev_churn, mean_proba, arpu)
    elif view == "Analytics":
        _tab_analytics(df_f)
    elif view == "Intelligence":
        _tab_intelligence(df_f)
    elif view == "Operations":
        _tab_operations(df_f, pipe)
    else:
        _tab_live(df_f, mean_proba)


def _tab_summary(df_f: pd.DataFrame, churn_rate: float, prev_churn: float | None, mean_proba: float, arpu: float) -> None:
    st.subheader("Advanced KPI cards")
    prev_h1, _prev_h2 = split_compare(df_f)

    def d(cur, prev):
        if prev is None or prev == 0:
            return None, None
        p = (cur - prev) / abs(prev) * 100
        return f"{p:+.1f}% vs baseline", p <= 0

    churn_prev = float(prev_h1["churn"].mean()) if "churn" in prev_h1.columns else churn_rate
    tx_prev = float(pd.to_numeric(prev_h1.get("total_transactions"), errors="coerce").mean())
    tx_cur = float(pd.to_numeric(df_f.get("total_transactions"), errors="coerce").mean())
    sup_prev = support_ratio(prev_h1)
    sup_cur = support_ratio(df_f)
    sat = satisfaction_index(df_f)
    ret_cur = 1.0 - churn_rate
    ret_prev = 1.0 - churn_prev if churn_prev is not None else ret_cur

    strokes = ["#fb7185", "#22d3ee", "#818cf8", "#34d399", "#fbbf24", "#4ade80", "#38bdf8", "#c084fc"]
    kpis = [
        ("Churn rate", f"{churn_rate:.1%}", *d(churn_rate, churn_prev)),
        ("Active users", f"{len(df_f):,}", None, None),
        ("Avg revenue / user", f"${arpu:.0f}", None, None),
        ("Avg tenure", f"{df_f['tenure_months'].mean():.1f} bln" if "tenure_months" in df_f.columns else "—", None, None),
        ("Support ratio", f"{sup_cur:.2f}", *d(sup_cur, sup_prev)),
        ("Retention rate", f"{ret_cur:.1%}", *d(ret_cur, ret_prev)),
        ("Monthly tx (avg)", f"{tx_cur:.1f}", *d(tx_cur, tx_prev)),
        ("Satisfaction idx", f"{sat:.0f}", None, None),
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
    st.subheader("Executive risk panel")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(fig_gauge_risk(mean_proba), use_container_width=True, config={"displayModeBar": False})
        st.progress(min(1.0, mean_proba), text=f"Churn pressure index ({mean_proba:.1%})")
    with c2:
        st.metric("Revenue at risk (6m est.)", f"${revenue_at_risk(df_f):,.0f}")
        st.metric("Retention opportunity", f"{(1 - mean_proba) * len(df_f) * clv_estimate(df_f) / max(len(df_f),1):,.0f} $ proxy")
        if mean_proba >= 0.35:
            st.error("Alert: tekanan churn agregat menengah–tinggi.")
        else:
            st.success("Alert level: terkendali.")

    st.altair_chart(
        alt.Chart(pd.DataFrame({"m": range(1, 13), "v": np.clip(np.random.default_rng(7).normal(mean_proba, 0.04, 12), 0.02, 0.9)}))
        .mark_line(point=True, color="#22d3ee")
        .encode(x="m:O", y="v:Q", tooltip=["m", alt.Tooltip("v:Q", format=".2f")])
        .properties(height=160, title="Altair spark trend (demo)")
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
            "customer_age",
            "account_balance",
            "tenure_months",
            "total_transactions",
            "support_tickets",
            "avg_order_value",
            "churn",
            "churn_proba",
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
        show["churn_proba"],
        bins=[-0.01, 0.35, 0.65, 0.85, 1.0],
        labels=["Low", "Medium", "High", "Critical"],
    ).astype(str)
    show["revenue_value"] = pd.to_numeric(show.get("avg_order_value"), errors="coerce").fillna(0) * pd.to_numeric(
        show.get("total_transactions"), errors="coerce"
    ).fillna(0)
    show["support_score"] = pd.to_numeric(show.get("support_tickets"), errors="coerce").fillna(0)
    cols = [
        "customer_id",
        "churn_proba",
        "risk_level",
        "revenue_value",
        "support_score",
        "is_premium",
        "tenure_months",
    ]
    cols = [c for c in cols if c in show.columns]
    t = show[cols].sort_values("churn_proba", ascending=False)
    st.dataframe(
        t.head(500),
        use_container_width=True,
        hide_index=True,
        column_config={
            "churn_proba": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
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
                f"**Live churn pressure** `{jitter:.2%}` · _tick {datetime.now().strftime('%H:%M:%S')}_ — "
                f"Pelanggan dipantau: **{len(df_f)}**"
            )

        _pulse()
    else:
        slot.metric("Churn pressure (statis)", f"{mean_proba:.2%}")
    st.caption("Panel live memakai `st.fragment` bila tersedia (Streamlit ≥ 1.33); jika tidak, tampil statis.")

    st.markdown("##### Churn ticker (synthetic)")
    risky = df_f.nlargest(8, "churn_proba") if "churn_proba" in df_f.columns else df_f.head(8)
    for _, row in risky.iterrows():
        st.markdown(
            f"<span class='exec-chip'>ID {row.get('customer_id', '?')}</span> "
            f"<span class='exec-chip'>proba {row.get('churn_proba', 0):.0%}</span> "
            f"<span class='exec-chip'>premium {row.get('is_premium', '')}</span>",
            unsafe_allow_html=True,
        )