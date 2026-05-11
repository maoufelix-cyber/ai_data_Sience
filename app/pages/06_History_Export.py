"""Riwayat prediksi, export CSV/JSON/PDF, asisten Q&A rule-based."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from churn_intel.auth import login_form
from churn_intel.chat_assistant import answer as chat_answer
from churn_intel.history_store import load_history
from churn_intel.pdf_export import build_prediction_pdf
from churn_intel.ui_theme import inject_styles

inject_styles()
if not login_form():
    st.stop()

st.markdown("# History & export")
st.caption("Riwayat prediksi tersimpan di SQLite lokal (`data/processed/`).")

tab1, tab2 = st.tabs(["Riwayat & unduhan", "Asisten (rule-based)"])

with tab1:
    hist = load_history(300)
    if hist.empty:
        st.info("Belum ada riwayat — jalankan simulasi di halaman Prediksi.")
    else:
        st.dataframe(hist, use_container_width=True, height=320)
        c1, c2, c3 = st.columns(3)
        csv_bytes = hist.to_csv(index=False).encode("utf-8")
        c1.download_button("Download CSV", csv_bytes, "prediction_history.csv", "text/csv")
        c2.download_button(
            "Download JSON",
            json.dumps(hist.to_dict(orient="records"), indent=2).encode("utf-8"),
            "prediction_history.json",
            "application/json",
        )
        if st.button("Generate PDF ringkas (prediksi terakhir)"):
            ctx = st.session_state
            if "ci_last_proba" not in ctx:
                st.error("Belum ada prediksi terakhir di sesi.")
            else:
                lines = list(ctx.get("ci_insights", [])) + list(ctx.get("ci_recs", []))
                st.session_state["_pdf_bytes"] = build_prediction_pdf(
                    title="Churn Intelligence — laporan singkat",
                    lines=lines,
                    probability=float(ctx["ci_last_proba"]),
                    risk_level=str(ctx.get("ci_last_risk", "")),
                )
        if st.session_state.get("_pdf_bytes"):
            st.download_button(
                "Unduh PDF",
                st.session_state["_pdf_bytes"],
                "churn_report.pdf",
                "application/pdf",
            )

with tab2:
    st.markdown("Tanya berdasarkan prediksi terakhir (tanpa LLM eksternal).")
    q = st.text_input("Pertanyaan", placeholder="Kenapa pelanggan ini churn?")
    if st.button("Jawab"):
        ctx = {
            "probability": st.session_state.get("ci_last_proba"),
            "top_toward_churn": st.session_state.get("ci_top_up"),
            "top_toward_stay": st.session_state.get("ci_top_down"),
            "recommendations": st.session_state.get("ci_recs"),
        }
        st.markdown(chat_answer(q, ctx))
