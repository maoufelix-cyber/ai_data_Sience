"""Premium dark theme + motion (Streamlit `st.markdown` CSS)."""

from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        r"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');

        :root {
            --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
            --ease-smooth: cubic-bezier(0.16, 1, 0.3, 1);
            --ease-soft: cubic-bezier(0.33, 1, 0.68, 1);
            --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
            --glow: 0 0 48px rgba(34, 211, 254, 0.1);
        }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }

        html { scroll-behavior: smooth; }

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
        }

        .stApp {
            background-color: #050816;
            background-image:
                radial-gradient(ellipse 90% 55% at 50% -25%, rgba(99, 102, 241, 0.28), transparent),
                radial-gradient(ellipse 55% 45% at 100% 10%, rgba(34, 211, 238, 0.1), transparent),
                radial-gradient(ellipse 45% 35% at 0% 95%, rgba(192, 132, 252, 0.08), transparent);
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1240px;
            animation: pageEnter 1.12s var(--ease-smooth) both;
        }

        @keyframes pageEnter {
            0% { opacity: 0; transform: translateY(22px) scale(0.995); }
            58% { opacity: 1; transform: translateY(6px) scale(0.998); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        h1 {
            font-family: 'Poppins', 'Inter', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.04em !important;
            line-height: 1.15 !important;
            background: linear-gradient(125deg, #e0e7ff 0%, #a5b4fc 35%, #22d3ee 70%, #c4b5fd 100%);
            background-size: 280% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titleIn 1s var(--ease-smooth) 0.08s both, shimmer 18s var(--ease-soft) 1.05s infinite;
        }

        @keyframes titleIn {
            0% { opacity: 0; transform: translateY(12px); filter: blur(8px); }
            100% { opacity: 1; transform: translateY(0); filter: blur(0); }
        }

        @keyframes shimmer {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(165deg, rgba(17, 24, 39, 0.92) 0%, rgba(5, 8, 22, 0.96) 100%) !important;
            border-right: 1px solid rgba(129, 140, 248, 0.15) !important;
            backdrop-filter: blur(16px);
            animation: sidebarIn 0.85s var(--ease-smooth) both;
        }
        @keyframes sidebarIn {
            from { opacity: 0; transform: translateX(-12px); }
            to { opacity: 1; transform: translateX(0); }
        }
        [data-testid="stSidebar"] .block-container { padding-top: 1.75rem; }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 20px !important;
            border: 1px solid rgba(129, 140, 248, 0.22) !important;
            background: rgba(17, 25, 40, 0.75) !important;
            box-shadow: var(--glow), 0 16px 48px rgba(0, 0, 0, 0.45);
            backdrop-filter: blur(14px);
            animation: cardAppear 0.95s var(--ease-smooth) both;
            transition:
                border-color 0.55s var(--ease-soft),
                box-shadow 0.55s var(--ease-soft),
                transform 0.55s var(--ease-soft),
                filter 0.45s var(--ease-soft);
        }
        @keyframes cardAppear {
            0% { opacity: 0; transform: translateY(16px); }
            70% { opacity: 1; transform: translateY(3px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(34, 211, 238, 0.35) !important;
            box-shadow: 0 0 56px rgba(129, 140, 248, 0.18), 0 20px 56px rgba(0, 0, 0, 0.5);
            transform: translateY(-3px);
        }

        div[data-testid="stFormSubmitButton"] button {
            border-radius: 14px !important;
            font-weight: 600 !important;
            padding: 0.65rem 1.5rem !important;
            background: linear-gradient(135deg, #22d3ee, #818cf8 50%, #a78bfa) !important;
            background-size: 160% auto !important;
            border: none !important;
            box-shadow: 0 6px 24px rgba(99, 102, 241, 0.45);
            transition:
                transform 0.45s var(--ease-spring),
                box-shadow 0.5s var(--ease-soft),
                filter 0.4s var(--ease-soft),
                background-position 0.6s var(--ease-soft) !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 36px rgba(34, 211, 238, 0.35);
            filter: brightness(1.08);
            background-position: 85% center !important;
        }
        div[data-testid="stFormSubmitButton"] button:active {
            transform: translateY(0) scale(0.985);
            transition-duration: 0.12s !important;
        }

        div[data-testid="stMetric"] {
            background: rgba(129, 140, 248, 0.07) !important;
            border: 1px solid rgba(129, 140, 248, 0.22) !important;
            border-radius: 16px !important;
            padding: 0.85rem 1rem !important;
            animation: metricPop 0.8s var(--ease-smooth) both;
            transition:
                background 0.5s var(--ease-soft),
                border-color 0.5s var(--ease-soft),
                transform 0.5s var(--ease-soft),
                box-shadow 0.5s var(--ease-soft);
        }
        @keyframes metricPop {
            0% { opacity: 0; transform: translateY(14px) scale(0.96); }
            72% { opacity: 1; transform: translateY(-2px) scale(1.01); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        div[data-testid="stMetric"]:hover {
            background: rgba(129, 140, 248, 0.12) !important;
            border-color: rgba(34, 211, 238, 0.4) !important;
            transform: scale(1.025);
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.25);
        }

        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(1) div[data-testid="stMetric"] { animation-delay: 0.05s; }
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(2) div[data-testid="stMetric"] { animation-delay: 0.11s; }
        div[data-testid="stHorizontalBlock"] div[data-testid="column"]:nth-child(3) div[data-testid="stMetric"] { animation-delay: 0.17s; }

        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border-radius: 10px !important;
            transition: border-color 0.4s var(--ease-soft), box-shadow 0.45s var(--ease-soft) !important;
        }
        div[data-testid="stNumberInput"] input:focus-within,
        div[data-testid="stSelectbox"] *:focus-within {
            box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.25) !important;
        }

        [data-testid="stExpander"] details {
            border-radius: 12px !important;
            border: 1px solid rgba(129, 140, 248, 0.14) !important;
            transition: border-color 0.45s var(--ease-soft), background 0.45s var(--ease-soft);
        }
        [data-testid="stExpander"] details:hover {
            border-color: rgba(34, 211, 238, 0.35) !important;
        }

        [data-testid="stAlert"] {
            animation: alertRise 0.85s var(--ease-smooth) both;
        }
        @keyframes alertRise {
            0% { opacity: 0; transform: translateY(16px); }
            100% { opacity: 1; transform: translateY(0); }
        }

        [data-testid="stPlotlyChart"] {
            animation: chartReveal 1s var(--ease-smooth) 0.12s both;
        }
        @keyframes chartReveal {
            0% { opacity: 0; transform: translateY(18px) scale(0.98); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            animation: chartReveal 0.9s var(--ease-smooth) 0.08s both;
        }

        hr {
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(34, 211, 238, 0.35), transparent);
            margin: 2rem 0;
        }

        .hero-underline {
            height: 3px;
            width: min(240px, 45vw);
            border-radius: 999px;
            background: linear-gradient(90deg, #22d3ee, #818cf8, transparent);
            margin: 0.75rem 0 1.25rem 0;
            opacity: 0.95;
            transform-origin: left center;
            animation: lineGrow 1.15s var(--ease-smooth) 0.2s both;
        }
        @keyframes lineGrow {
            0% { transform: scaleX(0); opacity: 0; filter: blur(4px); }
            55% { opacity: 0.85; filter: blur(0); }
            100% { transform: scaleX(1); opacity: 0.95; filter: blur(0); }
        }

        .ci-progress-bar {
            transform-origin: left center !important;
            animation: ciProgressFill 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
        }
        @keyframes ciProgressFill {
            from { transform: scaleX(0); }
            to { transform: scaleX(1); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
