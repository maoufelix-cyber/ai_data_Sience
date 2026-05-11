"""Rule-based AI executive insights for customer personality analysis."""

from __future__ import annotations

import pandas as pd


def executive_summary_paragraph(df: pd.DataFrame, prev_response_rate: float | None) -> str:
    """Generate executive summary from population metrics for marketing campaigns."""
    n = len(df)
    response_rate = float(df["Response"].mean()) if "Response" in df.columns and len(df) > 0 else 0.0
    parts = []

    if prev_response_rate is not None and prev_response_rate > 0:
        delta = (response_rate - prev_response_rate) / prev_response_rate * 100
        if abs(delta) >= 2:
            parts.append(f"Response rate **{'naik' if delta > 0 else 'turun'} {abs(delta):.1f}%** dibanding baseline periode pembanding.")

    # Campaign acceptance analysis
    campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
    available_campaigns = [col for col in campaign_cols if col in df.columns]
    if available_campaigns:
        acceptance_rates = df[available_campaigns].mean()
        best_campaign = acceptance_rates.idxmax() if not acceptance_rates.empty else None
        best_rate = float(acceptance_rates.max()) if not acceptance_rates.empty else 0.0
        if best_rate > 0:
            parts.append(f"Campaign **{best_campaign}** memiliki acceptance rate tertinggi **{best_rate:.1%}**.")

    # Spending analysis
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_spending = [col for col in spending_cols if col in df.columns]
    if available_spending:
        total_spending = df[available_spending].sum(axis=1)
        avg_spending = float(total_spending.mean())
        parts.append(f"Rata-rata spending pelanggan **${avg_spending:,.0f}** per kategori produk.")

    # Recency analysis
    if "Recency" in df.columns:
        avg_recency = float(df["Recency"].mean())
        parts.append(f"Rata-rata recency **{avg_recency:.0f} hari** sejak pembelian terakhir.")

    # Income analysis
    if "Income" in df.columns:
        avg_income = float(df["Income"].fillna(df["Income"].median()).mean())
        parts.append(f"Income rata-rata pelanggan **${avg_income:,.0f}**.")

    if not parts:
        parts.append(f"Populasi **{n:,}** pelanggan aktif; fokus pada campaign optimization dan customer engagement.")

    return " ".join(parts)


def insight_feed(df: pd.DataFrame) -> list[tuple[str, str]]:
    """List of (severity, markdown) for cards: info | warn | danger."""
    out: list[tuple[str, str]] = []

    # Response rate analysis
    if "Response" in df.columns:
        response_rate = float(df["Response"].mean())
        if response_rate < 0.1:
            out.append(("warn", f"Response rate **{response_rate:.1%}** rendah — perlu optimasi campaign targeting."))
        elif response_rate > 0.2:
            out.append(("info", f"Response rate **{response_rate:.1%}** baik — campaign strategy efektif."))

    # Campaign acceptance patterns
    campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
    available_campaigns = [col for col in campaign_cols if col in df.columns]
    if available_campaigns:
        acceptance_rates = df[available_campaigns].mean()
        low_acceptance = acceptance_rates[acceptance_rates < 0.05]
        if not low_acceptance.empty:
            campaign = low_acceptance.index[0]
            rate = float(low_acceptance.iloc[0])
            out.append(("warn", f"Campaign **{campaign}** acceptance rendah (**{rate:.1%}**) — evaluasi konten/messaging."))

    # Spending concentration
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_spending = [col for col in spending_cols if col in df.columns]
    if available_spending:
        spending_by_category = df[available_spending].mean()
        top_category = spending_by_category.idxmax() if not spending_by_category.empty else None
        top_amount = float(spending_by_category.max()) if not spending_by_category.empty else 0.0
        if top_amount > 0:
            out.append(("info", f"Kategori **{top_category}** dominan dengan spending rata-rata **${top_amount:.0f}**."))

    # Recency insights
    if "Recency" in df.columns:
        high_recency = (df["Recency"] > 60).mean()
        if high_recency > 0.3:
            out.append(("danger", f"**{high_recency:.1%}** pelanggan belum berbelanja >60 hari — risiko churn tinggi."))

    # Income segmentation
    if "Income" in df.columns:
        income = df["Income"].fillna(df["Income"].median())
        high_income_response = df.loc[income > income.median(), "Response"].mean()
        low_income_response = df.loc[income <= income.median(), "Response"].mean()
        if high_income_response > low_income_response + 0.05:
            out.append(("info", "Pelanggan high-income lebih responsif — fokus targeting premium segments."))

    # Family composition insights
    if "Kidhome" in df.columns and "Teenhome" in df.columns:
        families_with_kids = ((df["Kidhome"] + df["Teenhome"]) > 0).mean()
        if families_with_kids > 0.5:
            out.append(("info", f"**{families_with_kids:.1%}** pelanggan memiliki anak — opportunity untuk family-oriented campaigns."))

    out.append(("info", "Gunakan halaman **Explainability** untuk faktor SHAP per skenario prediksi."))
    return out[:10]


def action_recommendations(df: pd.DataFrame) -> list[tuple[str, str, str]]:
    """(priority, title, body) recommendations."""
    recs: list[tuple[str, str, str]] = []

    # Response rate optimization
    if "Response" in df.columns:
        response_rate = float(df["Response"].mean())
        if response_rate < 0.15:
            recs.append(("HIGH", "Campaign Optimization", "Tingkatkan targeting precision dan personalize messaging untuk meningkatkan response rate."))

    # Campaign sequencing
    campaign_cols = ["AcceptedCmp1", "AcceptedCmp2", "AcceptedCmp3", "AcceptedCmp4", "AcceptedCmp5"]
    available_campaigns = [col for col in campaign_cols if col in df.columns]
    if available_campaigns and len(available_campaigns) > 1:
        acceptance_corr = df[available_campaigns].corr()
        if not acceptance_corr.empty:
            # Find campaigns that work well together
            high_corr = acceptance_corr.where(np.triu(np.ones_like(acceptance_corr), k=1).astype(bool))
            max_corr_idx = high_corr.stack().idxmax() if not high_corr.stack().empty else None
            if max_corr_idx:
                recs.append(("MED", "Campaign Sequencing", f"Campaign {max_corr_idx[0]} dan {max_corr_idx[1]} memiliki sinergi — buat campaign sequence."))

    # Spending-based targeting
    spending_cols = ["MntWines", "MntFruits", "MntMeatProducts", "MntFishProducts",
                     "MntSweetProducts", "MntGoldProds"]
    available_spending = [col for col in spending_cols if col in df.columns]
    if available_spending:
        total_spending = df[available_spending].sum(axis=1)
        high_spenders = (total_spending > total_spending.quantile(0.8)).mean()
        if high_spenders > 0.1:
            recs.append(("MED", "High-Value Targeting", f"**{high_spenders:.1%}** high-spenders identified — develop exclusive loyalty program."))

    # Recency-based reactivation
    if "Recency" in df.columns:
        dormant = (df["Recency"] > 90).mean()
        if dormant > 0.2:
            recs.append(("HIGH", "Reactivation Campaign", f"**{dormant:.1%}** pelanggan dormant >90 hari — launch win-back campaign dengan special offers."))

    # Demographic targeting
    if "Education" in df.columns and "Response" in df.columns:
        education_response = df.groupby("Education")["Response"].mean()
        best_education = education_response.idxmax() if not education_response.empty else None
        if best_education:
            recs.append(("LOW", "Demographic Targeting", f"Segment **{best_education}** menunjukkan response tertinggi — optimize messaging untuk demographic ini."))
    
    if "support_tickets" in df.columns and len(df) > 0:
        mean_tickets = float(df["support_tickets"].mean())
        if mean_tickets >= 2:
            recs.append(("HIGH", "Support SLA", "Prioritaskan resolusi tiket — friksi servis memperburuk churn."))
    
    if not recs:
        recs.append(("LOW", "Pemantauan", "Pertahankan ritme review bulanan; risiko agregat relatif terkendali."))
    
    return recs
