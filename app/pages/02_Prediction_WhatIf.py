"""Prediksi churn + simulasi what-if (slider) + kartu risiko + insight bisnis."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.auth import login_form
from churn_intel.business_metrics import estimate_financials
from churn_intel.charts import churn_gauge
from churn_intel.history_store import log_prediction
from churn_intel.insights import generate_insights
from churn_intel.predict_core import prepare_for_model
from churn_intel.recommendations import retention_actions
from churn_intel.risk import risk_profile, risk_progress_html
from churn_intel.shap_tools import explain_row as shap_explain_row
from churn_intel.shap_tools import top_push_pull
from churn_intel.streamlit_io import load_pipeline
from churn_intel.ui_theme import inject_styles

inject_styles()
if not login_form():
    st.stop()

st.markdown("# Prediksi & What-if")
st.caption("Sesuaikan slider → **Perbarui simulasi** untuk melihat probabilitas, risiko, dan insight.")

pipe = load_pipeline()
if pipe is None:
    st.error("Model belum tersedia. Train & simpan `models/customer_churn_model.joblib`.")
    st.stop()

with st.container(border=True):
    st.markdown("##### Input & simulasi")
    c1, c2 = st.columns(2)
    with c1:
        customer_age = st.slider("Usia", 18, 75, 35)
        tenure_months = st.slider("Tenure (bulan)", 1, 72, 24)
        total_transactions = st.slider("Total transaksi", 0, 120, 12)
        support_tickets = st.slider("Tiket dukungan", 0, 25, 1)
    with c2:
        account_balance = st.slider("Saldo akun", 0, 150000, 54000, step=500)
        avg_order_value = st.slider("Nilai order rata-rata", 10.0, 400.0, 185.0)
        is_premium = st.selectbox("Premium", ["no", "yes"], index=0)

    run = st.button("Perbarui simulasi", type="primary")

if run:
    raw = pd.DataFrame(
        [
            {
                "customer_age": customer_age,
                "account_balance": account_balance,
                "tenure_months": tenure_months,
                "total_transactions": total_transactions,
                "is_premium": is_premium,
                "support_tickets": support_tickets,
                "avg_order_value": avg_order_value,
            }
        ]
    )
    sample = prepare_for_model(raw)
    pred = pipe.predict(sample)
    proba = float(pipe.predict_proba(sample)[:, 1][0])
    churn_yes = int(pred[0]) == 1
    rp = risk_profile(proba)

    st.session_state["ci_last_raw"] = raw.iloc[0].to_dict()
    st.session_state["ci_last_proba"] = proba
    st.session_state["ci_last_risk"] = rp.level
    st.session_state["ci_last_churn"] = churn_yes
    st.session_state["ci_last_sample_df"] = sample

    try:
        row_sv, names, _fig = shap_explain_row(pipe, sample)
        up, down = top_push_pull(row_sv, names, k=6)
        st.session_state["ci_top_up"] = up
        st.session_state["ci_top_down"] = down
        st.session_state.pop("ci_shap_err", None)
    except Exception as e:
        st.session_state["ci_top_up"] = []
        st.session_state["ci_top_down"] = []
        st.session_state["ci_shap_err"] = str(e)

    ins = generate_insights(raw.iloc[0], proba)
    recs = retention_actions(raw.iloc[0], proba)
    st.session_state["ci_insights"] = ins
    st.session_state["ci_recs"] = recs

    log_prediction(raw.iloc[0].to_dict(), proba, rp.level, int(churn_yes))

if "ci_last_proba" in st.session_state:
    proba = float(st.session_state["ci_last_proba"])
    rp = risk_profile(proba)
    raw_series = pd.Series(st.session_state.get("ci_last_raw", {}))

    badge_colors = {"Low": "#4ade80", "Medium": "#facc15", "High": "#fb923c", "Critical": "#fb7185"}
    bc = badge_colors.get(rp.level, "#94a3b8")

    st.markdown("---")
    with st.container(border=True):
        st.markdown("##### Customer risk score")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Probabilitas churn", f"{proba:.1%}")
        c2.metric("Risk level", rp.level)
        c3.metric("Confidence (heuristik)", f"{rp.confidence:.1%}")
        c4.markdown(
            f'<span style="display:inline-block;padding:0.35rem 0.75rem;border-radius:999px;'
            f'background:{bc}22;border:1px solid {bc};color:{bc};font-weight:600;">Status: {rp.level}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(risk_progress_html(proba), unsafe_allow_html=True)
        st.plotly_chart(churn_gauge(proba), use_container_width=True, config={"displayModeBar": False})

        fin = estimate_financials(raw_series, proba)
        st.markdown("##### Estimasi bisnis (demo)")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Revenue at risk (proxy)", f"{fin['expected_revenue_at_risk']:.0f}")
        f2.metric("Savings 3m (proxy)", f"{fin['retention_savings_3m_proxy']:.0f}")
        f3.metric("ROI retensi (hint)", f"{fin['retention_roi_hint']:.2f}")
        f4.metric("CLV aktivitas (proxy)", f"{fin['clv_activity_proxy']:.0f}")

        st.markdown("##### AI business insight")
        for line in st.session_state.get("ci_insights", []):
            st.markdown(f"- {line}")

        st.markdown("##### Rekomendasi retensi")
        for line in st.session_state.get("ci_recs", []):
            st.markdown(f"- {line}")

        if st.session_state.get("ci_shap_err"):
            st.caption(f"SHAP opsional gagal: {st.session_state['ci_shap_err']}")
else:
    st.info("Atur slider lalu klik **Perbarui simulasi**.")
