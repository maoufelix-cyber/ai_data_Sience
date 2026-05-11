"""Inline SVG sparklines for KPI cards."""

from __future__ import annotations


def sparkline_svg(values: list[float], w: int = 120, h: int = 28, stroke: str = "#22d3ee") -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    pts = []
    n = len(values)
    for i, v in enumerate(values):
        x = (i / max(n - 1, 1)) * (w - 4) + 2
        y = h - 2 - ((v - lo) / span) * (h - 8)
        pts.append(f"{x:.1f},{y:.1f}")
    d = "M " + " L ".join(pts)
    return f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="sg" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{stroke}" stop-opacity="0.2"/><stop offset="1" stop-color="{stroke}" stop-opacity="0.9"/></linearGradient></defs>
      <path d="{d}" fill="none" stroke="url(#sg)" stroke-width="2" stroke-linecap="round"/>
    </svg>"""
