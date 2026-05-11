"""
TROUBLESHOOTING & BEST PRACTICES: Pandas Series vs Scalar Issues
================================================================

PROBLEM SUMMARY
===============
Ketika menggunakan pandas DataFrame, operasi `.mean()`, `.sum()`, atau operasi lainnya
bisa mengembalikan Series (array 1D) daripada scalar (nilai tunggal). Ini menyebabkan error
ketika fungsi mengharapkan float tunggal.

CONTOH MASALAH
==============

❌ SALAH - Mengembalikan Series:
───────────────────────────────

    def satisfaction_index(df):
        t = df["tenure_months"] / 72           # Series
        tk = 1 - df["support_tickets"] / 15    # Series  
        pr = df["is_premium"].eq("yes")        # Series
        
        # Ini menghasilkan Series, bukan scalar!
        score = (t * 0.35 + tk * 0.45 + pr * 0.2) * 100
        return score                            # ❌ Returns Series!

✓ BENAR - Mengembalikan Float Scalar:
─────────────────────────────────────

    def satisfaction_index(df):
        t = df["tenure_months"] / 72           # Series
        tk = 1 - df["support_tickets"] / 15    # Series
        pr = df["is_premium"].eq("yes")        # Series
        
        # Calculation tetap Series
        score = (t * 0.35 + tk * 0.45 + pr * 0.2) * 100
        score = score.clip(0, 100)             # Still Series
        
        # ✓ Konversi ke scalar pada akhir!
        return float(score.mean())             # ✓ Returns float!


SOLUSI 1: Gunakan `.mean()` untuk Aggregate
===========================================

Jika ingin nilai rata-rata:

    ❌ SALAH:
    result = df["column"]  # Series

    ✓ BENAR:
    result = float(df["column"].mean())  # float


SOLUSI 2: Gunakan `.clip()` untuk Row-wise Processing
======================================================

Jika ingin output per baris (tetap Series), gunakan:

    # Operasi per baris tetap Series
    scores = ((t * 0.35 + tk * 0.45 + pr * 0.2) * 100)
    scores = scores.clip(lower=0, upper=100)  # Still Series
    
    # Konversi ke array jika perlu
    scores_array = scores.values
    
    # Aggregate ke scalar
    avg_score = float(scores.mean())


SOLUSI 3: Konversi DataFrame ke NumPy Array
===========================================

Untuk operasi yang tidak perlu Series:

    ❌ SALAH:
    score = (
        df["col1"] * 0.35 +
        df["col2"] * 0.45 +
        df["col3"] * 0.2
    )  # Series!

    ✓ BENAR:
    score = (
        df["col1"].values.astype(float) * 0.35 +
        df["col2"].values.astype(float) * 0.45 +
        df["col3"].values.astype(float) * 0.2
    )  # NumPy array


CHECKLIST: Kapan Harus Konversi ke Float
========================================

✓ SELALU konversi ke float jika:
  - Fungsi return type hint adalah `-> float`
  - Nilai akan digunakan dalam kondisi `if value > 0`
  - Nilai akan digunakan dalam perhitungan matematika
  - Nilai akan ditampilkan ke user

✓ BOLEH tetap Series jika:
  - Return type adalah `-> pd.Series`
  - Operasi masih row-wise (per baris)
  - Akan di-aggregate kemudian


POLA YANG BENAR
===============

Pola 1: Aggregate ke Scalar
───────────────────────────

    def calculate_metric(df: pd.DataFrame) -> float:
        # Calculate something
        result = df["col1"].mean()  # Series → scalar
        return float(result)  # ✓ Float


Pola 2: Per-row Processing (Tetap Series)
──────────────────────────────────────────

    def add_scores_per_row(df: pd.DataFrame) -> pd.DataFrame:
        # Work with Series (per row)
        scores = (df["col1"] * 0.35 + df["col2"] * 0.45)
        df["score"] = scores  # Assign Series to column
        return df  # ✓ Returns DataFrame


Pola 3: Conditional dengan Scalar Checks
─────────────────────────────────────────

    def validate_metric(df: pd.DataFrame, threshold: float) -> bool:
        metric = float(df["important_col"].mean())  # ✓ Convert!
        
        if metric > threshold:  # ✓ Works with scalar
            return True
        return False


DEBUGGING TIPS
==============

1. Check tipe dengan `print(type(variable))`
   ────────────────────────────────────────
   
   >>> print(type(df["col"].mean()))
   <class 'pandas.core.series.Series'>  # ❌ Wrong!
   
   >>> print(type(float(df["col"].mean())))
   <class 'float'>  # ✓ Correct!


2. Gunakan `isinstance()` untuk validasi:
   ─────────────────────────────────────
   
   >>> import pandas as pd
   >>> value = df["col"].mean()
   >>> isinstance(value, pd.Series)
   True  # ❌ Should be False!
   
   >>> isinstance(float(value), float)
   True  # ✓ Good!


3. Inspect DataFrame operations:
   ────────────────────────────
   
   >>> df["tenure"].dtype
   int64  # Column is numeric
   
   >>> (df["tenure"] / 72).dtype
   float64  # Operation produces float Series
   
   >>> (df["tenure"] / 72).mean()
   # Still returns scalar for mean()!


PERUBAHAN YANG DILAKUKAN DI PROJECT
===================================

File: dashboard/services/metrics.py
───────────────────────────────────

✓ retention_score()
  - Konversi input ke float: p = float(mean_proba)
  - Pastikan return float

✓ revenue_at_risk()
  - Konversi proba Series: proba = pd.to_numeric(...)
  - Return float: float((proba * aov * 6).sum())

✓ clv_estimate()
  - Konversi aov dan tx
  - Return float: float((aov * tx * 0.18).mean())

✓ support_ratio()
  - Konversi st_ dan tr
  - Return float: float((st_ / tr).fillna(0).mean())

✓ satisfaction_index()
  - Tetap Series untuk row-wise operations
  - Use .clip() untuk constraint
  - PENTING: Selalu .mean() kemudian float() pada akhir
  - Tambah docstring menjelaskan behavior


File: dashboard/services/insights.py
────────────────────────────────────

✓ executive_summary_paragraph()
  - Konversi churn_rate ke float: float(df["churn"].mean())
  - Konversi non_premium churn ke float
  - Konversi setiap metric dengan float()

✓ insight_feed()
  - Konversi p_np, hi, c, cr ke float
  - Check empty dataframe
  - Pastikan all means dikoversi

✓ action_recommendations()
  - Konversi mean_proba, mean_tx, non_premium_share, mean_tickets
  - Check len(df) > 0 sebelum .mean()


File: dashboard/executive_app.py
────────────────────────────────

✓ Perbaikan dalam render_executive_dashboard()
  - prev_churn: float(h1["churn"].mean())
  - churn_rate: float(df_f["churn"].mean())
  - delta_pct: float(delta_pct)
  - mean_proba: float(df_f["churn_proba"].mean())
  - arpu: float((aov_vals * df_f["churn_proba"]).sum() / n)


File: churn_intel/synthetic_data.py
──────────────────────────────────

✓ create_synthetic_churn_data()
  - Gunakan .values.astype(float) untuk konversi
  - Hindari mixing Series dengan scalar


TESTING TOOLS
=============

Jalankan validation script:

    python validation_series_fix.py

Script ini menguji:
  ✓ Semua metrics return float, bukan Series
  ✓ Semua insights return correct types
  ✓ Tidak ada Series leakage dalam calculations
  ✓ Edge cases (empty/small dataframes)


BEST PRACTICES UNTUK MASA DEPAN
===============================

1. Selalu specify return types:
   ──────────────────────────

   ✓ GOOD:
   def get_metric(df: pd.DataFrame) -> float:
       ...

   ❌ BAD (tanpa type hint):
   def get_metric(df):
       ...


2. Gunakan explicit conversions:
   ────────────────────────────

   ✓ GOOD:
   value = float(df["col"].mean())

   ❌ BAD (implicit):
   value = df["col"].mean()


3. Test dengan berbagai ukuran DataFrame:
   ────────────────────────────────────

   ✓ Empty dataframe
   ✓ Single row (n=1)
   ✓ Normal size (n=1000)
   ✓ Large size (n=100000)


4. Gunakan meaningful variable names:
   ──────────────────────────────────

   ✓ GOOD:
   churn_rate_scalar = float(df["churn"].mean())
   churn_scores_per_row = df["churn_proba"]

   ❌ BAD:
   churn = df["churn"].mean()  # Unclear type
   scores = df["churn_proba"]  # Is it scalar or Series?


REFERENSI PANDAS
================

Pandas methods yang return SCALAR:
  - .sum() → single value
  - .mean() → single value
  - .std() → single value
  - .max() → single value
  - .min() → single value
  - .count() → single value

Pandas methods yang return SERIES:
  - .apply() → Series/DataFrame
  - .map() → Series
  - .clip() → Series
  - .astype() → Series
  - .fillna() → Series
  - .round() → Series

Pandas methods yang return per-row BOOLEAN:
  - .eq() → Series[bool]
  - .gt() → Series[bool]
  - .lt() → Series[bool]
  - .ge() → Series[bool]


KONVERSI SHORTCUTS
==================

Float Scalar dari Series:
  float(series_value)
  float(series_value.mean())
  float(series_value.sum())
  float(series_value.iloc[0])

Integer Scalar dari Series:
  int(series_value.sum())
  int(series_value.count())

String dari Scalar:
  str(scalar_value)
  f"{scalar_value:.2f}"  # Formatted string


PENUTUP
=======

Kunci untuk menghindari Series vs Scalar issues:

1. SELALU gunakan type hints (-> float)
2. SELALU konversi ke float() jika return type adalah float
3. SELALU test dengan berbagai data sizes
4. SELALU validate tipe dengan isinstance() di debugging
5. SELALU doc bahwa function return float scalar, bukan Series

Dengan perubahan ini, project Anda sekarang robust terhadap
Series/scalar issues dan siap untuk production!
"""

if __name__ == "__main__":
    print(__doc__)
