import os
import pandas as pd

# Step 1: Ensure the output directory exists before writing anything
os.makedirs("data/cleaned/", exist_ok=True)

# ─────────────────────────────────────────────
# LOAD RAW DATA
# ─────────────────────────────────────────────

# Step 2: Load the leavers dataset from Excel using openpyxl engine
print("Loading data/raw/leavers_2023_24.xlsx ...")
try:
    leavers_df = pd.read_excel("data/raw/leavers_2023_24.xlsx", engine="openpyxl")
except Exception as e:
    print(f"ERROR: Could not read data/raw/leavers_2023_24.xlsx — {e}")
    raise

print(f"  Leavers raw shape: {leavers_df.shape}")

# Step 3: Load the enrollment dataset — try xlsx first, fall back to csv
print("Loading enrollment dataset ...")
try:
    enrollment_df = pd.read_excel("data/raw/enrollment_2023_24.xlsx", engine="openpyxl")
    print("  Loaded enrollment_2023_24.xlsx")
except Exception:
    try:
        enrollment_df = pd.read_csv("data/raw/enrollment_2023_24.csv")
        print("  Loaded enrollment_2023_24.csv (xlsx not found, used csv fallback)")
    except Exception as e:
        print(f"ERROR: Could not read enrollment dataset — {e}")
        raise

print(f"  Enrollment raw shape: {enrollment_df.shape}")

# ─────────────────────────────────────────────
# NORMALIZE COLUMN NAMES
# ─────────────────────────────────────────────

# Step 4: Lowercase all column names and replace any non-alphanumeric characters with underscores
leavers_df.columns = leavers_df.columns.str.lower().str.replace(r"[^a-z0-9]", "_", regex=True)
enrollment_df.columns = enrollment_df.columns.str.lower().str.replace(r"[^a-z0-9]", "_", regex=True)

print("\nNormalized leavers columns:", list(leavers_df.columns))
print("Normalized enrollment columns:", list(enrollment_df.columns))

# ─────────────────────────────────────────────
# FILL MISSING VALUES — LEAVERS
# ─────────────────────────────────────────────

# Step 5a: Fill NaN values in leavers_df — numeric cols get 0, string/object cols get "Unknown"
print("\n--- Filling missing values in leavers_df ---")
for col in leavers_df.columns:
    n_missing = leavers_df[col].isna().sum()
    if n_missing > 0:
        if pd.api.types.is_numeric_dtype(leavers_df[col]):
            # Fill numeric NaN with 0
            leavers_df[col] = leavers_df[col].fillna(0)
            print(f"  [leavers] {col}: filled {n_missing} numeric NaN(s) with 0")
        else:
            # Fill string/object NaN with "Unknown"
            leavers_df[col] = leavers_df[col].fillna("Unknown")
            print(f"  [leavers] {col}: filled {n_missing} string NaN(s) with 'Unknown'")

# ─────────────────────────────────────────────
# FILL MISSING VALUES — ENROLLMENT
# ─────────────────────────────────────────────

# Step 5b: Fill NaN values in enrollment_df — same logic
print("\n--- Filling missing values in enrollment_df ---")
for col in enrollment_df.columns:
    n_missing = enrollment_df[col].isna().sum()
    if n_missing > 0:
        if pd.api.types.is_numeric_dtype(enrollment_df[col]):
            # Fill numeric NaN with 0
            enrollment_df[col] = enrollment_df[col].fillna(0)
            print(f"  [enrollment] {col}: filled {n_missing} numeric NaN(s) with 0")
        else:
            # Fill string/object NaN with "Unknown"
            enrollment_df[col] = enrollment_df[col].fillna("Unknown")
            print(f"  [enrollment] {col}: filled {n_missing} string NaN(s) with 'Unknown'")

# ─────────────────────────────────────────────
# DROP DUPLICATE ROWS
# ─────────────────────────────────────────────

# Step 6: Remove exact duplicate rows from each DataFrame and report how many were dropped
leavers_before = len(leavers_df)
leavers_df = leavers_df.drop_duplicates()
leavers_dupes_removed = leavers_before - len(leavers_df)
print(f"\n[leavers] Duplicate rows removed: {leavers_dupes_removed}")

enrollment_before = len(enrollment_df)
enrollment_df = enrollment_df.drop_duplicates()
enrollment_dupes_removed = enrollment_before - len(enrollment_df)
print(f"[enrollment] Duplicate rows removed: {enrollment_dupes_removed}")

# ─────────────────────────────────────────────
# ZERO-PAD DISTRICT ID
# ─────────────────────────────────────────────

# Step 7: Zero-pad district_id to 6 digits so IDs are consistent across both datasets
# Check leavers first — the column may not exist if the raw file uses a different name
if "district_id" in leavers_df.columns:
    leavers_df["district_id"] = leavers_df["district_id"].astype(str).str.zfill(6)
    print("\n[leavers] district_id zero-padded to 6 digits")
else:
    print("\nWARNING: [leavers] 'district_id' column not found — skipping zero-pad")

# Check enrollment — same graceful handling
if "district_id" in enrollment_df.columns:
    enrollment_df["district_id"] = enrollment_df["district_id"].astype(str).str.zfill(6)
    print("[enrollment] district_id zero-padded to 6 digits")
else:
    print("WARNING: [enrollment] 'district_id' column not found — skipping zero-pad")

# ─────────────────────────────────────────────
# SAVE CLEANED FILES
# ─────────────────────────────────────────────

# Step 8: Write the cleaned DataFrames to CSV in data/cleaned/ using relative paths
leavers_out = "data/cleaned/leavers_2023_24.csv"
enrollment_out = "data/cleaned/enrollment_2023_24.csv"

leavers_df.to_csv(leavers_out, index=False)
print(f"\nSaved {leavers_out}")

enrollment_df.to_csv(enrollment_out, index=False)
print(f"Saved {enrollment_out}")

# ─────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────

# Step 9: Print a summary for each output file — row count, column count, remaining missing values
print("\n========== CLEANING SUMMARY ==========")

print(f"\n{leavers_out}")
print(f"  Rows   : {leavers_df.shape[0]}")
print(f"  Columns: {leavers_df.shape[1]}")
leavers_missing = leavers_df.isna().sum()
leavers_missing = leavers_missing[leavers_missing > 0]
if leavers_missing.empty:
    print("  Missing: none")
else:
    print("  Missing values per column:")
    for col, cnt in leavers_missing.items():
        print(f"    {col}: {cnt}")

print(f"\n{enrollment_out}")
print(f"  Rows   : {enrollment_df.shape[0]}")
print(f"  Columns: {enrollment_df.shape[1]}")
enrollment_missing = enrollment_df.isna().sum()
enrollment_missing = enrollment_missing[enrollment_missing > 0]
if enrollment_missing.empty:
    print("  Missing: none")
else:
    print("  Missing values per column:")
    for col, cnt in enrollment_missing.items():
        print(f"    {col}: {cnt}")

print("\n======================================")
print("clean.py complete.")

# ─────────────────────────────────────────────
# OUTER JOIN — MERGE LEAVERS AND ENROLLMENT
# ─────────────────────────────────────────────

# Step 10: Outer-join leavers and enrollment on district_id so every district from
# either dataset appears in the merged result. Unmatched rows will have NaN for the
# columns that came from the other side — those get filled with 0 below.

# Guard: only merge if district_id exists in both DataFrames; warn and skip otherwise
if "district_id" not in leavers_df.columns or "district_id" not in enrollment_df.columns:
    print("\nWARNING: 'district_id' missing from one or both DataFrames — skipping merge")
    merged_df = pd.DataFrame()
else:
    # Use indicator=True so we can identify left-only / right-only rows before dropping it
    merged_df = pd.merge(
        leavers_df,
        enrollment_df,
        on="district_id",
        how="outer",
        suffixes=("_leavers", "_enrollment"),
        indicator=True,
    )

    # Step 11: Report unmatched district IDs from each side
    left_only_ids = merged_df.loc[merged_df["_merge"] == "left_only", "district_id"].tolist()
    right_only_ids = merged_df.loc[merged_df["_merge"] == "right_only", "district_id"].tolist()

    print(f"\n[merge] Districts in leavers but NOT in enrollment ({len(left_only_ids)}): {left_only_ids}")
    print(f"[merge] Districts in enrollment but NOT in leavers ({len(right_only_ids)}): {right_only_ids}")

    # Step 12: Drop the helper indicator column — it's no longer needed
    merged_df = merged_df.drop(columns=["_merge"])

    # Step 13: Fill any NaN values introduced by the outer join with 0 for numeric columns
    # (unmatched rows will have NaN for the columns that came from the other side)
    for col in merged_df.columns:
        if pd.api.types.is_numeric_dtype(merged_df[col]):
            merged_df[col] = merged_df[col].fillna(0)

    # Step 14: Save the merged dataset to data/cleaned/ using a relative path
    merged_out = "data/cleaned/merged_district_2023_24.csv"
    merged_df.to_csv(merged_out, index=False)
    print(f"\nSaved {merged_out}")
    print(f"  Rows   : {merged_df.shape[0]}")
    print(f"  Columns: {merged_df.shape[1]}")
