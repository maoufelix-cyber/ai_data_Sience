"""
Churn Intelligence — Executive AI Analytics (home) + navigasi multipage.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from churn_intel.auth import auth_enabled, login_form, logout_button
from churn_intel.streamlit_io import load_customer_table, load_pipeline
from churn_intel.ui_theme import inject_styles
from dashboard.executive_app import render_executive_dashboard
from dashboard.styles.executive_css import inject_executive_css

st.set_page_config(
    page_title="Churn Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()
inject_executive_css()

if not login_form():
    st.stop()

pipe = load_pipeline()
df = load_customer_table()

with st.sidebar:
    st.markdown("### Churn Intelligence")
    st.caption("Enterprise AI / DS portfolio")
    st.markdown("---")
    if auth_enabled():
        st.caption(f"Role: **{st.session_state.get('_ci_role', 'analyst')}**")
        logout_button()
    st.markdown("---")
    st.markdown(
        "**Halaman:** gunakan daftar di atas area konten utama, atau navigasi multipage di sidebar. "
        "**Prediksi · Explainability · Analytics** tersedia sebagai halaman terpisah."
    )

if pipe is None:
    st.warning(
        "Model `models/customer_churn_model.joblib` belum ditemukan — skor churn memakai heuristik label. "
        "Train dari notebook lalu simpan ke `models/`."
    )

render_executive_dashboard(df, pipe)

st.markdown("---")
st.info(
    "**Halaman lanjutan:** **02 Prediksi & What-if** · **03 Explainability (SHAP)** · "
    "**04 Analytics** · **05 Model & Data** · **06 History & Export**."
)
