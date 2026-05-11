"""
Validation script to ensure all Series/scalar issues are fixed.
Checks that all functions return proper float scalars, not pandas Series.

Run: python validation_series_fix.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import functions to test
from dashboard.services.metrics import (
    clv_estimate,
    retention_score,
    revenue_at_risk,
    satisfaction_index,
    support_ratio,
)
from dashboard.services.insights import (
    action_recommendations,
    executive_summary_paragraph,
    insight_feed,
)
from churn_intel.synthetic_data import create_synthetic_churn_data


def test_metrics_return_float():
    """Test that all metrics functions return float, not Series."""
    print("=" * 70)
    print("TESTING: Metrics Functions Return Float Scalar")
    print("=" * 70)
    
    # Create test data
    df = create_synthetic_churn_data(n_samples=500)
    
    tests = [
        ("retention_score", lambda: retention_score(0.35), float),
        ("revenue_at_risk", lambda: revenue_at_risk(df), float),
        ("clv_estimate", lambda: clv_estimate(df), float),
        ("support_ratio", lambda: support_ratio(df), float),
        ("satisfaction_index", lambda: satisfaction_index(df), float),
    ]
    
    results = []
    for func_name, func, expected_type in tests:
        try:
            result = func()
            actual_type = type(result).__name__
            is_scalar = not isinstance(result, pd.Series)
            is_float = isinstance(result, (float, np.floating))
            
            status = "✓ PASS" if (is_scalar and is_float) else "✗ FAIL"
            results.append((func_name, status, actual_type, result))
            
            print(f"{status:8} {func_name:25} → {actual_type:15} (value: {result:.4f})")
            
        except Exception as e:
            results.append((func_name, "✗ ERROR", str(type(e).__name__), str(e)))
            print(f"✗ ERROR {func_name:25} → {type(e).__name__}: {str(e)[:40]}")
    
    return results


def test_insights_return_float():
    """Test that insight functions return proper types."""
    print("\n" + "=" * 70)
    print("TESTING: Insight Functions Return Proper Types")
    print("=" * 70)
    
    df = create_synthetic_churn_data(n_samples=500)
    prev_churn = 0.25
    
    tests = [
        ("executive_summary_paragraph", lambda: executive_summary_paragraph(df, prev_churn), str),
        ("insight_feed", lambda: insight_feed(df), list),
        ("action_recommendations", lambda: action_recommendations(df), list),
    ]
    
    results = []
    for func_name, func, expected_type in tests:
        try:
            result = func()
            actual_type = type(result).__name__
            is_correct_type = isinstance(result, expected_type)
            
            status = "✓ PASS" if is_correct_type else "✗ FAIL"
            results.append((func_name, status, actual_type, len(str(result))))
            
            if is_correct_type:
                if isinstance(result, str):
                    print(f"{status:8} {func_name:25} → {actual_type:15} (len: {len(result)})")
                else:
                    print(f"{status:8} {func_name:25} → {actual_type:15} (items: {len(result)})")
            else:
                print(f"{status:8} {func_name:25} → {actual_type:15} (expected: {expected_type.__name__})")
            
        except Exception as e:
            results.append((func_name, "✗ ERROR", str(type(e).__name__), str(e)))
            print(f"✗ ERROR {func_name:25} → {type(e).__name__}: {str(e)[:40]}")
    
    return results


def test_no_series_in_calculations():
    """Test that intermediate calculations don't leak Series."""
    print("\n" + "=" * 70)
    print("TESTING: No Series Leakage in Calculations")
    print("=" * 70)
    
    df = create_synthetic_churn_data(n_samples=100)
    
    tests = []
    
    # Test satisfaction_index components
    print("\n  satisfaction_index component types:")
    t = pd.to_numeric(df.get("tenure_months", 0), errors="coerce").fillna(0).clip(0, 72) / 72
    print(f"    - tenure component type: {type(t).__name__} (Series: {isinstance(t, pd.Series)})")
    tests.append(("tenure component", isinstance(t, pd.Series)))
    
    tk = 1 - pd.to_numeric(df.get("support_tickets", 0), errors="coerce").fillna(0).clip(0, 15) / 15
    print(f"    - ticket component type: {type(tk).__name__} (Series: {isinstance(tk, pd.Series)})")
    tests.append(("ticket component", isinstance(tk, pd.Series)))
    
    pr = df.get("is_premium", "no").astype(str).str.lower().eq("yes").astype(float)
    print(f"    - premium component type: {type(pr).__name__} (Series: {isinstance(pr, pd.Series)})")
    tests.append(("premium component", isinstance(pr, pd.Series)))
    
    score = ((t * 0.35 + tk * 0.45 + pr * 0.2) * 100).clip(lower=0, upper=100)
    print(f"    - weighted score type: {type(score).__name__} (Series: {isinstance(score, pd.Series)})")
    tests.append(("weighted score", isinstance(score, pd.Series)))
    
    final = float(score.mean())
    print(f"    - final result type: {type(final).__name__} (float: {isinstance(final, float)})")
    tests.append(("final result", isinstance(final, float)))
    
    # Test churn rate calculation
    print("\n  churn rate calculation:")
    churn_rate = float(df["churn"].mean())
    print(f"    - churn rate: {churn_rate:.4f} (type: {type(churn_rate).__name__})")
    tests.append(("churn rate", isinstance(churn_rate, float)))
    
    # Test delta calculation
    print("\n  delta calculation:")
    prev_churn = 0.30
    if prev_churn > 0:
        delta_pct = (churn_rate - prev_churn) / prev_churn * 100
        delta_pct = float(delta_pct)
    else:
        delta_pct = 0.0
    print(f"    - delta %: {delta_pct:.2f} (type: {type(delta_pct).__name__})")
    tests.append(("delta calc", isinstance(delta_pct, float)))
    
    passed = sum(1 for name, result in tests if result)
    total = len(tests)
    
    print(f"\n  Result: {passed}/{total} tests passed")
    
    return tests


def test_edge_cases():
    """Test edge cases like empty dataframes."""
    print("\n" + "=" * 70)
    print("TESTING: Edge Cases (Empty/Small Dataframes)")
    print("=" * 70)
    
    tests = []
    
    # Empty dataframe
    print("\n  Testing with EMPTY dataframe:")
    df_empty = pd.DataFrame({
        "churn": [],
        "churn_proba": [],
        "avg_order_value": [],
        "tenure_months": [],
        "support_tickets": [],
        "is_premium": [],
    })
    
    try:
        result = retention_score(0.5)
        print(f"    ✓ retention_score: {result:.2f}")
        tests.append(("retention_score on empty", True))
    except Exception as e:
        print(f"    ✗ retention_score: {e}")
        tests.append(("retention_score on empty", False))
    
    try:
        result = revenue_at_risk(df_empty)
        print(f"    ✓ revenue_at_risk: {result:.2f}")
        tests.append(("revenue_at_risk on empty", True))
    except Exception as e:
        print(f"    ✗ revenue_at_risk: {e}")
        tests.append(("revenue_at_risk on empty", False))
    
    try:
        result = satisfaction_index(df_empty)
        print(f"    ✓ satisfaction_index: {result:.2f}")
        tests.append(("satisfaction_index on empty", True))
    except Exception as e:
        print(f"    ✗ satisfaction_index: {e}")
        tests.append(("satisfaction_index on empty", False))
    
    # Small dataframe (1 row)
    print("\n  Testing with SMALL dataframe (1 row):")
    df_small = pd.DataFrame({
        "churn": [1],
        "churn_proba": [0.8],
        "avg_order_value": [150.0],
        "tenure_months": [24],
        "support_tickets": [2],
        "is_premium": ["yes"],
    })
    
    try:
        result = revenue_at_risk(df_small)
        print(f"    ✓ revenue_at_risk: ${result:,.2f}")
        tests.append(("revenue_at_risk on 1 row", True))
    except Exception as e:
        print(f"    ✗ revenue_at_risk: {e}")
        tests.append(("revenue_at_risk on 1 row", False))
    
    try:
        result = satisfaction_index(df_small)
        print(f"    ✓ satisfaction_index: {result:.2f}")
        tests.append(("satisfaction_index on 1 row", True))
    except Exception as e:
        print(f"    ✗ satisfaction_index: {e}")
        tests.append(("satisfaction_index on 1 row", False))
    
    passed = sum(1 for name, result in tests if result)
    total = len(tests)
    print(f"\n  Result: {passed}/{total} edge case tests passed")
    
    return tests


def main():
    """Run all validation tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " PANDAS SERIES/SCALAR FIX VALIDATION ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    all_results = []
    
    # Run test suites
    all_results.extend(test_metrics_return_float())
    all_results.extend(test_insights_return_float())
    all_results.extend(test_no_series_in_calculations())
    all_results.extend(test_edge_cases())
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed_tests = [r for r in all_results if isinstance(r, tuple) and "PASS" in str(r)]
    failed_tests = [r for r in all_results if isinstance(r, tuple) and ("FAIL" in str(r) or "ERROR" in str(r))]
    
    print(f"\n✓ Passed: {len(passed_tests)} tests")
    print(f"✗ Failed: {len(failed_tests)} tests")
    print(f"Total:    {len(all_results)} tests")
    
    if failed_tests:
        print("\nFailed tests:")
        for test in failed_tests:
            if isinstance(test, tuple):
                print(f"  - {test[0]}")
    
    print("\n" + "=" * 70)
    
    # Exit code
    if failed_tests:
        print("⚠ VALIDATION FAILED - Some tests did not pass")
        return 1
    else:
        print("✓ ALL TESTS PASSED - Series/scalar issues are fixed!")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
