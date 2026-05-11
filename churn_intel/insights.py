"""Rule-based business insights from raw row + probability."""

from __future__ import annotations

import pandas as pd


def generate_insights(raw_row: pd.Series, probability: float) -> list[str]:
    """Return ordered bullet strings (Indonesian) for UI."""
    insights: list[str] = []
    p = float(probability)

    tpm = raw_row.get("total_transactions", 0) / max(int(raw_row.get("tenure_months", 1) or 1), 1)
    if tpm < 0.5:
        insights.append("Frekuensi transaksi relatif rendah vs tenure — sinyal engagement lemah.")
    elif tpm > 2:
        insights.append("Frekuensi transaksi sehat dibanding masa berlangganan.")

    if int(raw_row.get("tenure_months", 0) or 0) >= 24:
        insights.append("Tenure cukup panjang; biasanya berkorelasi dengan risiko churn lebih rendah.")
    elif int(raw_row.get("tenure_months", 0) or 0) < 6:
        insights.append("Tenure pendek — fase onboarding; churn sering muncul di periode ini.")

    tickets = int(raw_row.get("support_tickets", 0) or 0)
    if tickets >= 4:
        insights.append("Volume tiket support tinggi — risiko frikasi pengalaman pelanggan.")
    elif tickets == 0:
        insights.append("Tidak ada tiket support; pengalaman servis terlihat tenang.")

    if str(raw_row.get("is_premium", "no")).lower() == "no" and p >= 0.4:
        insights.append("Non-premium dengan probabilitas churn menengah+ — pertimbangkan upsell premium.")

    bal = float(raw_row.get("account_balance", 0) or 0)
    if bal < 15000:
        insights.append("Saldo akun rendah — bisa mencerminkan aktivitas atau minat menurun.")
    if bal > 80000 and p < 0.3:
        insights.append("Saldo besar dengan risiko model rendah — pelanggan bernilai stabil.")

    aov = float(raw_row.get("avg_order_value", 0) or 0)
    if aov < 50:
        insights.append("Nilai order rata-rata rendah; kampanye repeat purchase dapat membantu.")

    if not insights:
        insights.append("Profil pelanggan relatif seimbang; fokus pada komunikasi proaktif rutin.")

    if p >= 0.65:
        insights.insert(0, "Model menempatkan pelanggan di zona risiko churn **tinggi** — prioritas retensi.")
    elif p <= 0.25:
        insights.insert(0, "Probabilitas churn model **rendah** — peluang upsell/cross-sell lebih relevan.")

    return insights[:8]
