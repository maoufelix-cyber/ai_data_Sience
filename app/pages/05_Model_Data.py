"""Metrik model, monitoring ringan, explorer data."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.auth import current_role, login_form
from churn_intel.drift_simple import mean_shift_table
from churn_intel.model_metrics import load_metrics
from churn_intel.streamlit_io import load_customer_table
from churn_intel.ui_theme import inject_styles

inject_styles()
if not login_form():
    st.stop()

st.markdown("# Model quality & data")
st.caption("Metrik offline + eksplorasi dataset + drift sederhana.")

m = load_metrics()
df = load_customer_table()

tab_a, tab_b, tab_c = st.tabs(["Model performance", "Data explorer", "Drift & threshold"])

with tab_a:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Accuracy", "—" if m.get("accuracy") is None else f"{float(m['accuracy']):.3f}")
    c2.metric("Precision", "—" if m.get("precision") is None else f"{float(m['precision']):.3f}")
    c3.metric("Recall", "—" if m.get("recall") is None else f"{float(m['recall']):.3f}")
    c4.metric("F1", "—" if m.get("f1") is None else f"{float(m['f1']):.3f}")
    c5.metric("ROC-AUC", "—" if m.get("roc_auc") is None else f"{float(m['roc_auc']):.3f}")
    st.markdown(
        f"**CV mean ± std:** {m.get('cv_mean', '—')} / {m.get('cv_std', '—')}  \n"
        f"**Train / test acc:** {m.get('train_accuracy', '—')} / {m.get('test_accuracy', '—')}  \n"
        f"_{m.get('notes', '')}_"
    )
    st.info(
        "Untuk confusion matrix, kurva ROC, dan PR curve lengkap, ekspor angka dari notebook evaluasi "
        "atau tambahkan plot statis ke folder `reports/`."
    )

with tab_b:
    st.dataframe(df, use_container_width=True, height=360)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Ringkasan numerik**")
        st.dataframe(df.describe().T, use_container_width=True)
    with c2:
        st.markdown("**Null count**")
        st.dataframe(df.isnull().sum().rename("nulls").to_frame(), use_container_width=True)
    st.markdown("**Outlier proxy (z>|3|) pada saldo**")
    if "account_balance" in df.columns:
        s = pd.to_numeric(df["account_balance"], errors="coerce")
        z = (s - s.mean()) / (s.std(ddof=1) or 1.0)
        st.metric("Jumlah baris |z|>3", int((z.abs() > 3).sum()))

with tab_c:
    st.markdown("#### Drift sederhana (mean shift)")
    ref = df.sample(min(500, len(df)), random_state=42) if len(df) > 20 else df
    cur = df.sample(min(200, len(df)), random_state=7)
    cols = [c for c in df.columns if c not in ("churn", "is_premium")]
    drift_tbl = mean_shift_table(ref, cur, [c for c in cols if df[c].dtype != "object"][:8])
    st.dataframe(drift_tbl, use_container_width=True)

    st.markdown("#### Threshold tuning (demo)")
    th = st.slider("Ambang probabilitas churn", 0.1, 0.9, float(m.get("threshold_default", 0.5)), 0.05)
    st.caption(
        f"Dengan threshold **{th:.2f}**, proporsi prediksi positif pada label historis ≈ "
        f"{((df['churn'] == 1).mean() if 'churn' in df.columns else 0):.1%} (label) — "
        "sesuaikan dengan biaya false positive/negative bisnis."
    )
    st.caption(f"Role login: **{current_role()}** — sesuaikan threshold dengan kebijakan risiko bisnis.")
