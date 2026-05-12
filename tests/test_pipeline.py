"""
Smoke tests for the Texas K-12 TEA data pipeline.

These tests validate the core data transformation logic without requiring
the live TEA data source — they use small in-memory DataFrames.

Run: pytest tests/test_pipeline.py
"""

from __future__ import annotations

import pytest
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# Helpers that mirror the notebook's transformation logic
# ---------------------------------------------------------------------------

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase and strip column names."""
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def zero_pad_district_id(df: pd.DataFrame, col: str = "district", width: int = 6) -> pd.DataFrame:
    """Zero-pad district ID column to a fixed width."""
    df = df.copy()
    df[col] = df[col].astype(str).str.zfill(width)
    return df


def compute_dropout_rate(df: pd.DataFrame, dropout_col: str, enrollment_col: str) -> pd.Series:
    """Return dropout rate as a percentage, handling zero enrollment."""
    return df[dropout_col] / df[enrollment_col].replace(0, np.nan) * 100


def drop_duplicates_and_nulls(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    """Drop rows with null key and deduplicate."""
    return df.dropna(subset=[key_col]).drop_duplicates(subset=[key_col])


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestNormalizeColumnNames:
    def test_lowercases_columns(self):
        df = pd.DataFrame(columns=["District", "ENROLLMENT", "Dropout Count"])
        result = normalize_column_names(df)
        assert list(result.columns) == ["district", "enrollment", "dropout_count"]

    def test_strips_whitespace(self):
        df = pd.DataFrame(columns=[" District ", " Count "])
        result = normalize_column_names(df)
        assert list(result.columns) == ["district", "count"]

    def test_empty_dataframe(self):
        df = pd.DataFrame()
        result = normalize_column_names(df)
        assert list(result.columns) == []


class TestZeroPadDistrictId:
    def test_pads_short_ids(self):
        df = pd.DataFrame({"district": ["1", "123", "12345"]})
        result = zero_pad_district_id(df)
        assert list(result["district"]) == ["000001", "000123", "012345"]

    def test_does_not_truncate_long_ids(self):
        df = pd.DataFrame({"district": ["1234567"]})
        result = zero_pad_district_id(df)
        assert result["district"].iloc[0] == "1234567"

    def test_already_padded_unchanged(self):
        df = pd.DataFrame({"district": ["001001"]})
        result = zero_pad_district_id(df)
        assert result["district"].iloc[0] == "001001"


class TestComputeDropoutRate:
    def test_basic_rate(self):
        df = pd.DataFrame({"dropouts": [100], "enrollment": [1000]})
        rate = compute_dropout_rate(df, "dropouts", "enrollment")
        assert abs(rate.iloc[0] - 10.0) < 1e-9

    def test_zero_enrollment_returns_nan(self):
        df = pd.DataFrame({"dropouts": [5], "enrollment": [0]})
        rate = compute_dropout_rate(df, "dropouts", "enrollment")
        assert pd.isna(rate.iloc[0])

    def test_zero_dropouts_returns_zero(self):
        df = pd.DataFrame({"dropouts": [0], "enrollment": [500]})
        rate = compute_dropout_rate(df, "dropouts", "enrollment")
        assert rate.iloc[0] == 0.0

    def test_rate_never_exceeds_100(self):
        df = pd.DataFrame({"dropouts": [50, 200, 1000], "enrollment": [1000, 1000, 1000]})
        rate = compute_dropout_rate(df, "dropouts", "enrollment")
        assert (rate.dropna() <= 100).all()


class TestDropDuplicatesAndNulls:
    def test_removes_null_key_rows(self):
        df = pd.DataFrame({"district": ["001", None, "003"], "value": [1, 2, 3]})
        result = drop_duplicates_and_nulls(df, "district")
        assert len(result) == 2
        assert result["district"].notna().all()

    def test_removes_duplicate_keys(self):
        df = pd.DataFrame({"district": ["001", "001", "002"], "value": [1, 2, 3]})
        result = drop_duplicates_and_nulls(df, "district")
        assert len(result) == 2

    def test_empty_dataframe_returns_empty(self):
        df = pd.DataFrame({"district": pd.Series([], dtype=str)})
        result = drop_duplicates_and_nulls(df, "district")
        assert len(result) == 0
