"""Rule-based AI executive insights from population + scores."""

from __future__ import annotations

import pandas as pd


def executive_summary_paragraph(df: pd.DataFrame, prev_churn_rate: float | None) -> str:
    """Generate executive summary from population metrics (always returns float scalars)."""
    n = len(df)
    # Ensure churn is a float scalar, not Series
    churn = float(df["churn"].mean()) if "churn" in df.columns and len(df) > 0 else 0.0
    parts = []
    
    if prev_churn_rate is not None and prev_churn_rate > 0:
        delta = (churn - prev_churn_rate) / prev_churn_rate * 100
        if abs(delta) >= 2:
            parts.append(f"Churn **{'naik' if delta > 0 else 'turun'} {abs(delta):.1f}%** dibanding baseline periode pembanding.")
    
    if "is_premium" in df.columns and "churn" in df.columns:
        # Get scalar float for non-premium churn rate
        non_premium_mask = df["is_premium"].astype(str).str.lower().eq("no")
        if non_premium_mask.any():
            cr_np = float(df.loc[non_premium_mask, "churn"].mean())
            share = float((df["is_premium"].astype(str).str.lower().ne("yes")).mean())
            parts.append(f"Pelanggan **non-premium** (~{share:.0%} populasi) memiliki churn rate **{cr_np:.1%}**.")
    
    if "tenure_months" in df.columns and "churn" in df.columns:
        short = df["tenure_months"] < 6
        if short.any():
            cr_s = float(df.loc[short, "churn"].mean())
            parts.append(f"Tenure **< 6 bulan** menunjukkan churn **{cr_s:.1%}** — fase onboarding kritis.")
    
    if "support_tickets" in df.columns and "churn" in df.columns:
        hi = df["support_tickets"] >= 3
        if hi.any():
            cr_h = float(df.loc[hi, "churn"].mean())
            parts.append(f"Support ticket **tinggi (≥3)** berkorelasi dengan churn **{cr_h:.1%}**.")
    
    if not parts:
        parts.append(f"Populasi **{n:,}** pelanggan stabil; pantau segment risiko menengah secara berkala.")
    
    return " ".join(parts)


def insight_feed(df: pd.DataFrame) -> list[tuple[str, str]]:
    """List of (severity, markdown) for cards: info | warn | danger.
    
    Always returns float scalars for metrics, never Series.
    """
    out: list[tuple[str, str]] = []
    
    if "churn" in df.columns and "is_premium" in df.columns:
        non_premium_mask = df["is_premium"].astype(str).str.lower().eq("no")
        if non_premium_mask.any():
            p_np = float(df.loc[non_premium_mask, "churn"].mean())
            if p_np >= 0.35:
                out.append(("warn", f"**{p_np:.0%}** churn berasal dari konteks non-premium — pertimbangkan upsell."))
    
    if "churn_proba" in df.columns:
        hi = float((df["churn_proba"] >= 0.65).mean())
        out.append(("info", f"**{hi:.1%}** pelanggan berada di zona proba churn tinggi (model)."))
    
    if "churn" in df.columns and "support_tickets" in df.columns:
        corr_result = df[["support_tickets", "churn"]].corr()
        if not corr_result.empty:
            c = float(corr_result.iloc[0, 1])
            if c == c and abs(c) >= 0.08:  # c == c checks for NaN
                out.append(("warn", f"Tiket support berkorelasi dengan churn (**r ≈ {c:.2f}**)."))
    
    if "tenure_months" in df.columns and "churn" in df.columns:
        short_mask = df["tenure_months"] < 6
        if short_mask.any():
            cr = float(df.loc[short_mask, "churn"].mean())
            severity = "danger" if cr > 0.4 else "info"
            out.append((severity, f"Tenure < 6 bln: churn **{cr:.1%}** — prioritas retensi dini."))
    
    out.append(("info", "Gunakan halaman **Explainability** untuk faktor SHAP per skenario prediksi."))
    return out[:10]


def action_recommendations(df: pd.DataFrame) -> list[tuple[str, str, str]]:
    """(priority, title, body) - always returns float scalars."""
    recs: list[tuple[str, str, str]] = []
    
    if "churn_proba" in df.columns and len(df) > 0:
        mean_proba = float(df["churn_proba"].mean())
        if mean_proba >= 0.35:
            recs.append(("HIGH", "Retention wave", "Luncurkan kampanye retention terarah ke segmen proba ≥ 0.35."))
    
    if "total_transactions" in df.columns and len(df) > 0:
        mean_tx = float(df["total_transactions"].mean())
        if mean_tx < 10:
            recs.append(("MED", "Repeat order", "Aktifkan promo repeat purchase untuk meningkatkan frekuensi transaksi."))
    
    if "is_premium" in df.columns and len(df) > 0:
        non_premium_share = float((df["is_premium"].astype(str).str.lower().eq("no")).mean())
        if non_premium_share > 0.65:
            recs.append(("MED", "Premium upsell", "Bundling premium untuk pelanggan bernilai namun belum premium."))
    
    if "support_tickets" in df.columns and len(df) > 0:
        mean_tickets = float(df["support_tickets"].mean())
        if mean_tickets >= 2:
            recs.append(("HIGH", "Support SLA", "Prioritaskan resolusi tiket — friksi servis memperburuk churn."))
    
    if not recs:
        recs.append(("LOW", "Pemantauan", "Pertahankan ritme review bulanan; risiko agregat relatif terkendali."))
    
    return recs
