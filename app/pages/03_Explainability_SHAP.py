"""Explainable AI — SHAP bar + faktor dorong / tahan."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.auth import login_form
from churn_intel.shap_tools import explain_row, top_push_pull
from churn_intel.streamlit_io import load_pipeline
from churn_intel.ui_theme import inject_styles

inject_styles()
if not login_form():
    st.stop()

st.markdown("# Explainability (SHAP)")
st.caption("Jalankan simulasi di halaman **Prediksi & What-if** terlebih dahulu.")

pipe = load_pipeline()
if pipe is None:
    st.error("Model tidak tersedia.")
    st.stop()

if "ci_last_sample_df" not in st.session_state:
    st.warning("Belum ada prediksi tersimpan. Buka halaman Prediksi & jalankan simulasi.")
    st.stop()

sample = st.session_state["ci_last_sample_df"]

try:
    row_sv, names, fig = explain_row(pipe, sample)
    up, down = top_push_pull(row_sv, names, k=8)
    if fig is not None:
        st.pyplot(fig, clear_figure=True)
        plt.close(fig)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Mendorong churn (SHAP > 0)**")
        for n, v in up:
            st.markdown(f"- `{n}` → **{v:+.3f}**")
    with col2:
        st.markdown("**Menurunkan churn (SHAP < 0)**")
        for n, v in down:
            st.markdown(f"- `{n}` → **{v:+.3f}**")
except Exception as e:
    st.error(f"Tidak dapat menghitung SHAP: {e}")
    st.markdown("Pastikan `shap` terinstal dan pipeline berisi `RandomForestClassifier`.")
