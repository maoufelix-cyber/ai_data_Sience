"""Streamlit-cached I/O for model and tabular data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import streamlit as st

from churn_intel.settings import MODEL_PATH
from churn_intel.synthetic_data import ensure_sample_csv


@st.cache_resource
def load_pipeline():
    if not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_customer_table() -> pd.DataFrame:
    path = ensure_sample_csv()
    return pd.read_csv(path)
