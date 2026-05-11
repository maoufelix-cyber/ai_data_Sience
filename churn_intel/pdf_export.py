"""Minimal PDF report (ReportLab)."""

from __future__ import annotations

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def build_prediction_pdf(
    *,
    title: str,
    lines: list[str],
    probability: float,
    risk_level: str,
) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 50
    c.setTitle(title)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 28
    c.setFont("Helvetica", 11)
    c.drawString(50, y, f"Probabilitas churn: {probability:.2%}")
    y -= 18
    c.drawString(50, y, f"Risk level: {risk_level}")
    y -= 28
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Ringkasan")
    y -= 18
    c.setFont("Helvetica", 10)
    for line in lines:
        for chunk in _wrap(line, 95):
            c.drawString(50, y, chunk)
            y -= 14
            if y < 80:
                c.showPage()
                y = h - 50
                c.setFont("Helvetica", 10)
    c.showPage()
    c.save()
    return buf.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur: list[str] = []
    for word in words:
        trial = " ".join(cur + [word])
        if len(trial) <= width:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    return lines
