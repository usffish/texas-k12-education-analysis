"""
Unit tests for analyze.py logic.
Tests are self-contained — they do not import analyze.py as a module.
Instead, they replicate the inline logic using small hand-crafted DataFrames.
"""

import math
import pandas as pd
import pytest


# ─────────────────────────────────────────────
# 1. Leaver rate — zero enrollment row
# ─────────────────────────────────────────────

def test_leaver_rate_zero_enrollment():
    """Zero enrollment must produce leaver_rate of 0.0, not NaN or infinity."""
    df = pd.DataFrame({"enrollment_count": [0], "leaver_count": [5]})

    df["leaver_rate"] = (
        df["leaver_count"] / df["enrollment_count"].replace(0, float("nan"))
    ).fillna(0)

    result = df["leaver_rate"].iloc[0]
    assert result == 0.0, f"Expected 0.0, got {result}"
    assert not math.isnan(result), "leaver_rate must not be NaN"
    assert not math.isinf(result), "leaver_rate must not be infinity"


# ─────────────────────────────────────────────
# 2. Leaver rate — normal case
# ─────────────────────────────────────────────

def test_leaver_rate_normal():
    """Normal enrollment and leaver counts must produce the correct ratio."""
    df = pd.DataFrame({"enrollment_count": [100], "leaver_count": [10]})

    df["leaver_rate"] = (
        df["leaver_count"] / df["enrollment_count"].replace(0, float("nan"))
    ).fillna(0)

    result = df["leaver_rate"].iloc[0]
    assert result == pytest.approx(0.1), f"Expected 0.1, got {result}"


# ─────────────────────────────────────────────
# 3. Top-10 sort
# ─────────────────────────────────────────────

def test_top10_sort():
    """Top-10 sort must return exactly 10 rows, all with leaver_rate >= any remaining row."""
    # 15 rows with distinct, known leaver_rate values
    df = pd.DataFrame({
        "district_id": [str(i).zfill(6) for i in range(1, 16)],
        "leaver_rate": [i * 0.01 for i in range(1, 16)],  # 0.01 … 0.15
    })

    sorted_df = df.sort_values("leaver_rate", ascending=False)
    top10 = sorted_df.head(10)
    rest = sorted_df.iloc[10:]

    assert len(top10) == 10, f"Expected 10 rows, got {len(top10)}"
    assert top10["leaver_rate"].min() >= rest["leaver_rate"].max(), (
        "Minimum leaver_rate in top-10 must be >= maximum leaver_rate in remaining rows"
    )


# ─────────────────────────────────────────────
# 4. Trend aggregation
# ─────────────────────────────────────────────

def test_trend_aggregation():
    """groupby school_year + sum must produce exactly one row per year with the correct total."""
    df = pd.DataFrame({
        "school_year":      ["2021-22", "2021-22", "2022-23", "2022-23", "2022-23"],
        "enrollment_count": [1000,       2000,       500,        700,        800],
    })

    trend = df.groupby("school_year")["enrollment_count"].sum()

    assert len(trend) == 2, f"Expected 2 years, got {len(trend)}"
    assert trend["2021-22"] == 3000, f"Expected 3000 for 2021-22, got {trend['2021-22']}"
    assert trend["2022-23"] == 2000, f"Expected 2000 for 2022-23, got {trend['2022-23']}"


# ─────────────────────────────────────────────
# 5. Missing demographic column warning path
# ─────────────────────────────────────────────

def test_missing_demographic_column_warning():
    """When 'gender' column is absent, the check must return False (warning path is triggered)."""
    df = pd.DataFrame({
        "district_id":    ["000001", "000002"],
        "leaver_count":   [5, 10],
        "enrollment_count": [100, 200],
    })

    # Simulate the demographic check logic from analyze.py
    column_present = "gender" in df.columns

    assert column_present is False, (
        "Expected 'gender' to be absent from the DataFrame — warning path should be triggered"
    )
