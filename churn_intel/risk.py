"""Risk tiers, confidence, and badge styling."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskProfile:
    probability: float
    level: str  # Low | Medium | High | Critical
    color_hex: str
    badge_class: str
    confidence: float  # 0–1 heuristic from max(p, 1-p)


def risk_profile(probability: float) -> RiskProfile:
    """Map churn probability to four-tier risk + display color."""
    p = float(probability)
    conf = max(p, 1.0 - p)

    if p >= 0.85:
        return RiskProfile(p, "Critical", "#fb7185", "critical", conf)
    if p >= 0.65:
        return RiskProfile(p, "High", "#f97316", "high", conf)
    if p >= 0.35:
        return RiskProfile(p, "Medium", "#facc15", "medium", conf)
    return RiskProfile(p, "Low", "#4ade80", "low", conf)


def risk_progress_html(percent: float) -> str:
    """Animated glass progress bar (inline HTML for st.markdown)."""
    pct = max(0.0, min(100.0, percent * 100))
    return f"""
    <div class="ci-progress-wrap" style="margin:0.5rem 0 1rem 0;">
      <div style="height:10px;border-radius:999px;background:rgba(255,255,255,0.06);overflow:hidden;border:1px solid rgba(129,140,248,0.2);">
        <div class="ci-progress-bar" style="width:{pct:.1f}%;height:100%;border-radius:999px;background:linear-gradient(90deg,#22d3ee,#818cf8,#c084fc);box-shadow:0 0 18px rgba(129,140,248,0.45);"></div>
      </div>
    </div>
    """
