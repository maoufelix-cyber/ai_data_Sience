"""SQLite prediction history + CSV/JSON export."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from churn_intel.settings import DATA_PROCESSED_DIR, HISTORY_DB


def init_db() -> None:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(HISTORY_DB) as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                inputs_json TEXT NOT NULL,
                probability REAL NOT NULL,
                risk_level TEXT NOT NULL,
                churn_pred INTEGER NOT NULL
            )
            """
        )


def log_prediction(inputs: dict, probability: float, risk_level: str, churn_pred: int) -> None:
    init_db()
    ts = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(HISTORY_DB) as c:
        c.execute(
            "INSERT INTO predictions (ts, inputs_json, probability, risk_level, churn_pred) VALUES (?,?,?,?,?)",
            (ts, json.dumps(inputs, default=str), float(probability), risk_level, int(churn_pred)),
        )


def load_history(limit: int = 200) -> pd.DataFrame:
    if not HISTORY_DB.exists():
        return pd.DataFrame(columns=["ts", "inputs_json", "probability", "risk_level", "churn_pred"])
    init_db()
    conn = sqlite3.connect(HISTORY_DB)
    try:
        return pd.read_sql_query(
            "SELECT ts, inputs_json, probability, risk_level, churn_pred FROM predictions ORDER BY id DESC LIMIT ?",
            conn,
            params=(limit,),
        )
    finally:
        conn.close()


def history_to_csv(path: Path) -> None:
    load_history(10_000).to_csv(path, index=False)
