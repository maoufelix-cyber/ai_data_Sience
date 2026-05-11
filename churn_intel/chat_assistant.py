"""Rule-based assistant (no external LLM) using last session context."""

from __future__ import annotations

import re


def answer(question: str, ctx: dict | None) -> str:
    ctx = ctx or {}
    q = question.strip().lower()
    if not q:
        return "Tulis pertanyaan singkat tentang churn, faktor risiko, atau rekomendasi retensi."

    p = ctx.get("probability")
    top_up = ctx.get("top_toward_churn") or []
    top_down = ctx.get("top_toward_stay") or []
    recs = ctx.get("recommendations") or []

    if re.search(r"kenapa|mengapa|faktor|alasan", q):
        if p is None:
            return "Belum ada prediksi aktif. Buka halaman Prediksi & jalankan skenario dulu."
        parts = [f"Probabilitas churn model saat ini sekitar **{float(p):.1%}**."]
        if top_up:
            parts.append("Faktor yang **mendorong churn** (SHAP positif): " + ", ".join(f"`{n}`" for n, _ in top_up[:4]) + ".")
        if top_down:
            parts.append("Faktor yang **menahan churn** (SHAP negatif): " + ", ".join(f"`{n}`" for n, _ in top_down[:4]) + ".")
        return " ".join(parts)

    if re.search(r"retention|tahan|cegah", q):
        if recs:
            return "Saran retensi: " + " ".join(f"• {r}" for r in recs[:5])
        return "Gunakan diskon terarah, perbaikan support, dan kampanye repeat order untuk pelanggan risiko menengah–tinggi."

    if re.search(r"terbesar|paling|utama", q):
        if top_up:
            return "Kontributor positif terbesar ke skor churn: **" + top_up[0][0] + "**."
        return "Jalankan halaman Explainability setelah prediksi untuk melihat ranking SHAP."

    return (
        "Saya asisten aturan bawaan. Coba tanya: *Kenapa pelanggan ini churn?*, "
        "*Apa faktor terbesar?*, atau *Bagaimana cara retention?*. "
        "Pastikan Anda sudah menjalankan prediksi agar konteks terisi."
    )
