"""Premium executive dashboard — additional CSS (layers on global theme)."""

from __future__ import annotations

import streamlit as st


def inject_executive_css() -> None:
    st.markdown(
        r"""
        <style>
        .exec-ambient {
            position: fixed; inset: 0; pointer-events: none; z-index: 0;
            background-image:
                radial-gradient(circle at 20% 30%, rgba(34, 211, 238, 0.07) 0%, transparent 45%),
                radial-gradient(circle at 80% 20%, rgba(129, 140, 248, 0.09) 0%, transparent 40%),
                radial-gradient(circle at 60% 90%, rgba(244, 63, 94, 0.05) 0%, transparent 35%);
            animation: execAmbient 22s ease-in-out infinite alternate;
        }
        @keyframes execAmbient {
            from { opacity: 0.85; filter: saturate(1); }
            to { opacity: 1; filter: saturate(1.15); }
        }
        .exec-hero-shell {
            position: relative;
            border-radius: 22px;
            padding: 1.35rem 1.5rem 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
            background: linear-gradient(135deg, rgba(17,25,40,0.92) 0%, rgba(8,12,28,0.88) 55%, rgba(17,24,39,0.9) 100%);
            border: 1px solid rgba(129, 140, 248, 0.28);
            box-shadow: 0 0 0 1px rgba(34,211,238,0.08) inset, 0 20px 60px rgba(0,0,0,0.45);
            backdrop-filter: blur(18px);
            overflow: hidden;
        }
        .exec-hero-shell::before {
            content: ""; position: absolute; inset: 0;
            background: linear-gradient(120deg, transparent 30%, rgba(34,211,238,0.06) 50%, transparent 70%);
            animation: execSheen 6s ease-in-out infinite;
            pointer-events: none;
        }
        @keyframes execSheen {
            0% { transform: translateX(-30%); opacity: 0; }
            30% { opacity: 1; }
            100% { transform: translateX(30%); opacity: 0; }
        }
        .exec-hero-title {
            font-family: 'Poppins', 'Inter', sans-serif;
            font-size: 1.65rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            background: linear-gradient(90deg, #e0f2fe, #a5b4fc, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .exec-kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.75rem; }
        .exec-kpi {
            position: relative;
            border-radius: 16px;
            padding: 0.85rem 1rem;
            background: rgba(11, 17, 32, 0.65);
            border: 1px solid rgba(129, 140, 248, 0.22);
            box-shadow: 0 8px 28px rgba(0,0,0,0.35);
            transition: transform 0.35s cubic-bezier(0.16,1,0.3,1), box-shadow 0.35s ease, border-color 0.35s ease;
        }
        .exec-kpi:hover {
            transform: translateY(-3px);
            border-color: rgba(34, 211, 238, 0.45);
            box-shadow: 0 0 32px rgba(34, 211, 238, 0.18), 0 14px 40px rgba(0,0,0,0.45);
        }
        .exec-kpi .label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; }
        .exec-kpi .value { font-size: 1.35rem; font-weight: 700; color: #f8fafc; margin-top: 0.2rem; }
        .exec-kpi .delta-up { color: #34d399; font-size: 0.78rem; font-weight: 600; }
        .exec-kpi .delta-down { color: #fb7185; font-size: 0.78rem; font-weight: 600; }
        .exec-kpi .spark { margin-top: 0.45rem; opacity: 0.95; }
        .exec-insight-card {
            border-radius: 14px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.5rem;
            background: rgba(17, 25, 40, 0.75);
            border-left: 4px solid #22d3ee;
            border: 1px solid rgba(129,140,248,0.15);
            border-left-width: 4px;
        }
        .exec-insight-card.warn { border-left-color: #fbbf24; }
        .exec-insight-card.danger { border-left-color: #fb7185; }
        .exec-chip {
            display: inline-block;
            padding: 0.2rem 0.55rem;
            border-radius: 999px;
            font-size: 0.72rem;
            margin: 0.15rem 0.25rem 0 0;
            background: rgba(129,140,248,0.15);
            border: 1px solid rgba(129,140,248,0.35);
            color: #c7d2fe;
        }
        .exec-counter {
            display: inline-block;
            animation: execCountFade 0.9s cubic-bezier(0.16,1,0.3,1) both;
        }
        @keyframes execCountFade {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        div[data-testid="stHorizontalBlock"]:has(.exec-kpi) { align-items: stretch; }
        </style>
        <div class="exec-ambient" aria-hidden="true"></div>
        """,
        unsafe_allow_html=True,
    )


def kpi_html(label: str, value: str, delta: str | None, delta_pos: bool | None, spark_svg: str, icon: str) -> str:
    dcls = ""
    if delta is not None and delta_pos is True:
        dcls = "delta-up"
    elif delta is not None and delta_pos is False:
        dcls = "delta-down"
    delta_html = f'<div class="{dcls}">{delta}</div>' if delta else ""
    return f"""
    <div class="exec-kpi">
      <div class="label">{icon} &nbsp; {label}</div>
      <div class="value"><span class="exec-counter">{value}</span></div>
      {delta_html}
      <div class="spark">{spark_svg}</div>
    </div>
    """
