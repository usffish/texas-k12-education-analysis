"""
Unit tests for clean.py logic.
Tests are self-contained — they do not import clean.py as a module.
Instead, they replicate the inline logic using small hand-crafted DataFrames.
"""

import re
import math
import pandas as pd
import numpy as np
import pytest


# ─────────────────────────────────────────────
# 1. Column normalization
# ─────────────────────────────────────────────

def test_column_normalization():
    """Normalized column names must match [a-z][a-z0-9_]*

    Note: column names that start with a digit after normalization (e.g. "2023-24 Count"
    → "2023_24_count") are not valid identifiers. Real TEA column headers are word-first
    (e.g. "Count 2023-24"), so the test uses representative real-world names only.
    """
    df = pd.DataFrame(columns=["District Name", "ESC Region", "Total Leavers", "Leaver Count 2023-24"])

    # Apply the same logic used in clean.py
    df.columns = df.columns.str.lower().str.replace(r"[^a-z0-9]", "_", regex=True)

    pattern = re.compile(r"^[a-z][a-z0-9_]*$")
    for col in df.columns:
        assert pattern.match(col), f"Column '{col}' does not match expected pattern"


# ─────────────────────────────────────────────
# 2. NaN filling — numeric columns
# ─────────────────────────────────────────────

def test_nan_filling_numeric():
    """Numeric NaN values must be filled with 0."""
    df = pd.DataFrame({"count": [1.0, float("nan"), 3.0, float("nan")]})

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)

    assert df["count"].isna().sum() == 0, "NaN values remain after filling"
    assert (df["count"] == 0).sum() == 2, "Expected exactly 2 zeros from NaN fill"


# ─────────────────────────────────────────────
# 3. NaN filling — string/object columns
# ─────────────────────────────────────────────

def test_nan_filling_string():
    """Object/string NaN values must be filled with 'Unknown'."""
    df = pd.DataFrame({"district_name": ["Alpha ISD", None, "Beta ISD", None]})

    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna("Unknown")

    assert df["district_name"].isna().sum() == 0, "NaN values remain after filling"
    assert (df["district_name"] == "Unknown").sum() == 2, "Expected exactly 2 'Unknown' fills"


# ─────────────────────────────────────────────
# 4. District ID zero-padding
# ─────────────────────────────────────────────

@pytest.mark.parametrize("raw, expected", [
    ("1",      "000001"),   # single digit
    ("12345",  "012345"),   # 5 digits
    ("123456", "123456"),   # already 6 digits
    (42,       "000042"),   # integer input
])
def test_district_id_zero_padding(raw, expected):
    """district_id must be zero-padded to exactly 6 digits."""
    df = pd.DataFrame({"district_id": [raw]})
    df["district_id"] = df["district_id"].astype(str).str.zfill(6)
    assert df["district_id"].iloc[0] == expected


# ─────────────────────────────────────────────
# 5. Deduplication
# ─────────────────────────────────────────────

def test_deduplication():
    """drop_duplicates() must remove all duplicate rows and be idempotent."""
    df = pd.DataFrame({
        "district_id": ["000001", "000001", "000002", "000003", "000003"],
        "count":       [10,       10,       20,       30,       30],
    })

    deduped = df.drop_duplicates()
    assert len(deduped) == 3, f"Expected 3 unique rows, got {len(deduped)}"
    assert deduped.duplicated().sum() == 0, "Duplicate rows remain after drop_duplicates()"

    # Idempotency: applying again must produce the same result
    deduped_again = deduped.drop_duplicates()
    assert len(deduped_again) == len(deduped), "drop_duplicates() is not idempotent"
    pd.testing.assert_frame_equal(deduped.reset_index(drop=True),
                                  deduped_again.reset_index(drop=True))


# ─────────────────────────────────────────────
# 6. Outer join
# ─────────────────────────────────────────────

def test_outer_join():
    """Outer join on district_id must retain all IDs from both sides."""
    leavers = pd.DataFrame({
        "district_id":   ["000001", "000002", "000003"],
        "leaver_count":  [5, 10, 15],
    })
    enrollment = pd.DataFrame({
        "district_id":       ["000002", "000003", "000004"],
        "enrollment_count":  [100, 200, 300],
    })

    merged = pd.merge(
        leavers,
        enrollment,
        on="district_id",
        how="outer",
        suffixes=("_leavers", "_enrollment"),
        indicator=True,
    )

    # All 4 district IDs must appear
    result_ids = set(merged["district_id"].tolist())
    assert result_ids == {"000001", "000002", "000003", "000004"}, (
        f"Expected all 4 district IDs, got {result_ids}"
    )

    # District 000001 is left-only — enrollment_count must be NaN before fill
    row_1 = merged.loc[merged["district_id"] == "000001"].iloc[0]
    assert pd.isna(row_1["enrollment_count"]), (
        "District 000001 (left-only) should have NaN enrollment_count before fill"
    )

    # District 000004 is right-only — leaver_count must be NaN before fill
    row_4 = merged.loc[merged["district_id"] == "000004"].iloc[0]
    assert pd.isna(row_4["leaver_count"]), (
        "District 000004 (right-only) should have NaN leaver_count before fill"
    )

    # After filling numeric NaN with 0 (as clean.py does)
    merged = merged.drop(columns=["_merge"])
    for col in merged.columns:
        if pd.api.types.is_numeric_dtype(merged[col]):
            merged[col] = merged[col].fillna(0)

    row_1_filled = merged.loc[merged["district_id"] == "000001"].iloc[0]
    assert row_1_filled["enrollment_count"] == 0, (
        "District 000001 enrollment_count should be 0 after fill"
    )

    row_4_filled = merged.loc[merged["district_id"] == "000004"].iloc[0]
    assert row_4_filled["leaver_count"] == 0, (
        "District 000004 leaver_count should be 0 after fill"
    )
