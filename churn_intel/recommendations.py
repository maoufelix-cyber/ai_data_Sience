"""Rule-based retention recommendations."""

from __future__ import annotations

import pandas as pd

from churn_intel.risk import risk_profile


def retention_actions(raw_row: pd.Series, probability: float) -> list[str]:
    rp = risk_profile(probability)
    recs: list[str] = []

    if rp.level in ("High", "Critical") and str(raw_row.get("is_premium", "no")).lower() == "no":
        recs.append("Tawarkan diskon atau trial **membership premium** untuk meningkatkan kunci loyalitas.")

    if int(raw_row.get("support_tickets", 0) or 0) >= 3:
        recs.append("**Prioritaskan customer support** — SLA cepat untuk menurunkan frikasi.")

    tpm = raw_row.get("total_transactions", 0) / max(int(raw_row.get("tenure_months", 1) or 1), 1)
    if tpm < 0.6:
        recs.append("Kirim **promo repeat order** atau bundling untuk meningkatkan frekuensi transaksi.")

    if int(raw_row.get("tenure_months", 0) or 0) < 12 and rp.level in ("Medium", "High", "Critical"):
        recs.append("Jalankan **program onboarding** (check-in mingguan) untuk pelanggan muda.")

    if float(raw_row.get("avg_order_value", 0) or 0) < 80:
        recs.append("Aktifkan **rekomendasi produk** / keranjang minimum untuk menaikkan AOV.")

    if rp.level == "Low":
        recs.append("Pertahankan hubungan dengan **komunikasi nilai** (tips, early access) tanpa diskon agresif.")

    if not recs:
        recs.append("Pantau metrik perilaku bulanan dan segmentasi ulang bila ada perubahan pola.")

    return recs
