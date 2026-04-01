# Implementation Plan: Texas K–12 Education Analysis

## Overview

Three flat Python scripts (`collect.py`, `clean.py`, `analyze.py`) plus an annotated Jupyter notebook. Each script is top-to-bottom inline pandas/matplotlib code — no custom functions or classes. Tests use pytest and Hypothesis.

## Tasks

- [x] 1. Set up project structure and dependencies
  - Create directories: `data/raw/`, `data/cleaned/`, `outputs/figures/`, `scripts/`, `notebooks/`, `tests/`
  - Create `requirements.txt` with: `pandas`, `matplotlib`, `seaborn`, `openpyxl`, `requests`, `pytest`, `hypothesis`, `pytest-mock`
  - _Requirements: 10.2, 10.3_

- [x] 2. Implement `scripts/collect.py`
  - [x] 2.1 Write collect.py — download TEA datasets and write manifest
    - `os.makedirs("data/raw/", exist_ok=True)` at top
    - For each URL: `requests.get(url)`, check status, save file to `data/raw/` with stable filename
    - On non-200 or exception: print `ERROR: Failed to download {url} — HTTP {status_code}` and stop
    - Build manifest list of dicts with `dataset`, `source_url`, `file_format`, `local_path`, `collected_at`
    - Write manifest to `data/raw/manifest.json`
    - Halt if fewer than 2 datasets downloaded
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 10.1, 10.2_

  - [ ]* 2.2 Write property test for saved file paths (Property 1)
    - **Property 1: Downloaded files are saved under data/raw/ with a relative path**
    - **Validates: Requirements 1.3, 10.1**

  - [ ]* 2.3 Write property test for download failure logging (Property 2)
    - **Property 2: Download failure log contains URL and status code**
    - **Validates: Requirements 1.4**

  - [ ]* 2.4 Write property test for manifest completeness (Property 3)
    - **Property 3: Manifest contains required fields for every dataset**
    - **Validates: Requirements 1.5**

  - [ ]* 2.5 Write unit tests for collect.py
    - Mock `requests.get` to return 200 — assert file saved to `data/raw/`
    - Mock `requests.get` to return 404 — assert error message printed
    - Assert manifest JSON contains all required fields after a successful run
    - _Requirements: 1.3, 1.4, 1.5_

- [x] 3. Checkpoint — ensure collect tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [~] 4. Implement `scripts/clean.py`
  - [x] 4.1 Write clean.py — load, normalize, fill, deduplicate, zero-pad
    - `os.makedirs("data/cleaned/", exist_ok=True)` at top
    - Read `data/raw/leavers_2023_24.xlsx` with `pd.read_excel(..., engine="openpyxl")`
    - Read `data/raw/enrollment_2023_24.xlsx` (or `.csv`) with `pd.read_csv` / `pd.read_excel`
    - Normalize columns: `df.columns = df.columns.str.lower().str.replace(r"[^a-z0-9]", "_", regex=True)`
    - Fill numeric NaN with `0`, string NaN with `"Unknown"`, print column name + count for each
    - Drop duplicate rows, print count removed
    - Zero-pad district ID: `df["district_id"] = df["district_id"].astype(str).str.zfill(6)`
    - Save `data/cleaned/leavers_2023_24.csv` and `data/cleaned/enrollment_2023_24.csv`
    - Print summary: row count, column count, missing value counts per output file
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 10.1, 10.2_

  - [ ]* 4.2 Write property test for column normalization (Property 7)
    - **Property 7: Column names are normalized after cleaning**
    - **Validates: Requirements 3.3**

  - [ ]* 4.3 Write property test for no missing values after filling (Property 8)
    - **Property 8: No missing values remain after filling**
    - **Validates: Requirements 3.4, 3.5**

  - [ ]* 4.4 Write property test for deduplication idempotency (Property 9)
    - **Property 9: No duplicate rows remain after deduplication**
    - **Validates: Requirements 3.6**

  - [ ]* 4.5 Write property test for district ID zero-padding (Property 10)
    - **Property 10: District IDs are zero-padded 6-digit strings**
    - **Validates: Requirements 3.7**

  - [ ]* 4.6 Write unit tests for clean.py normalization and filling
    - Test column normalization on a small hand-crafted DataFrame
    - Test NaN filling with known missing positions
    - Test district ID zero-padding on edge cases (1-digit, 5-digit, already 6-digit)
    - _Requirements: 3.3, 3.4, 3.5, 3.7_

  - [x] 4.7 Extend clean.py — outer join and save merged dataset
    - Outer-join leavers and enrollment DataFrames on `district_id`
    - Fill unmatched numeric fields with `0`
    - Print unmatched district IDs from each side
    - Save `data/cleaned/merged_district_2023_24.csv`
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 4.8 Write property test for merged dataset completeness (Property 11)
    - **Property 11: Merged dataset retains all district IDs from both inputs**
    - **Validates: Requirements 4.1, 4.3, 4.4**

  - [ ]* 4.9 Write property test for cleaning idempotency (Property 6)
    - **Property 6: Cleaning is idempotent**
    - **Validates: Requirements 2.3**

  - [ ]* 4.10 Write property test for raw data preservation (Property 4)
    - **Property 4: Cleaner never modifies files in data/raw/**
    - **Validates: Requirements 2.1**

  - [ ]* 4.11 Write property test for output file locations (Property 5)
    - **Property 5: All cleaner outputs are CSVs in data/cleaned/**
    - **Validates: Requirements 2.2**

  - [ ]* 4.12 Write unit tests for the outer join logic
    - Test with two small DataFrames with known left-only, right-only, and matched rows
    - Assert unmatched rows have `0` for missing fields
    - _Requirements: 4.1, 4.3, 4.4_

- [x] 5. Checkpoint — ensure clean tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [~] 6. Implement `scripts/analyze.py`
  - [x] 6.1 Write analyze.py — trend analysis and line charts
    - `os.makedirs("outputs/figures/", exist_ok=True)` at top
    - Load `data/cleaned/merged_district_2023_24.csv` and `data/cleaned/enrollment_2023_24.csv`
    - Compute statewide enrollment per year: `df.groupby("school_year")["enrollment_count"].sum()`
    - Plot line chart, add title + axis labels, save to `outputs/figures/enrollment_trend.png`
    - Compute statewide leaver count per year the same way, plot and save `outputs/figures/leaver_trend.png`
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.1, 10.2_

  - [ ]* 6.2 Write property test for trend aggregation (Property 12)
    - **Property 12: Trend aggregation returns one row per year with the correct sum**
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 6.3 Write property test for figure labels (Property 13)
    - **Property 13: All figures have non-empty axis labels and a title**
    - **Validates: Requirements 5.5**

  - [x] 6.4 Extend analyze.py — leaver rate, ESC region chart, top-10 chart
    - Add `leaver_rate` column: `df["leaver_rate"] = df["leaver_count"] / df["enrollment_count"].replace(0, float("nan"))` then `.fillna(0)`
    - Group by `esc_region`, compute mean leaver rate, plot bar chart with labeled bars, save `outputs/figures/leaver_rate_by_esc_region.png`
    - Sort by `leaver_rate` descending, take top 10, plot bar chart with district name labels, save `outputs/figures/top10_leaver_districts.png`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 6.5 Write property test for leaver rate formula (Property 14)
    - **Property 14: Leaver rate formula is correct and handles zero enrollment**
    - **Validates: Requirements 6.1**

  - [ ]* 6.6 Write property test for top-N ranking (Property 15)
    - **Property 15: Top-N districts are correctly ranked**
    - **Validates: Requirements 6.2**

  - [x] 6.7 Extend analyze.py — demographic breakdown chart
    - For each demographic column (race/ethnicity, gender, eco_dis): compute leaver counts and rates
    - If column absent, print `WARNING: column '{col}' not found — skipping` and continue
    - Plot bar chart of leaver rates by demographic group, save `outputs/figures/leaver_rate_by_demographic.png`
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [ ]* 6.8 Write property test for demographic column coverage (Property 16)
    - **Property 16: Demographic breakdown covers all qualifying columns**
    - **Validates: Requirements 7.1, 7.3**

  - [x] 6.9 Extend analyze.py — print 3+ insight summaries
    - After all charts, print at least 3 insight strings referencing specific district names and numeric values
    - Each insight derived from a computed statistic produced earlier in the script
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 6.10 Write unit tests for analyze.py
    - Test leaver rate computation with a zero-enrollment row
    - Test that top-10 sort returns correct rows from a known DataFrame
    - Test that missing demographic column triggers warning and does not raise
    - _Requirements: 6.1, 6.2, 7.4_

- [x] 7. Checkpoint — ensure analyze tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [~] 8. Write property tests for path and directory constraints
  - [ ]* 8.1 Write property test for no absolute paths (Property 17)
    - **Property 17: No absolute paths appear in any script or notebook**
    - **Validates: Requirements 10.1**

  - [ ]* 8.2 Write property test for auto-created directories (Property 18)
    - **Property 18: Required directories are auto-created before any file write**
    - **Validates: Requirements 10.2**

- [~] 9. Create `notebooks/analysis.ipynb`
  - [x] 9.1 Build notebook structure with Markdown and code cells
    - Cell 1 (Markdown): title, dataset sources, URLs, file formats, collection method
    - Cell 2 (Markdown): "Data Collection" section description
    - Cell 3 (Markdown): "Data Cleaning" section description
    - Cell 4 (Code): load cleaned CSVs, display `.shape` and `.head()` — one `#` comment per logical step
    - Cell 5 (Markdown): "Trend Analysis" section description
    - Cell 6 (Code): enrollment and leaver trend charts (same logic as analyze.py) — inline comments
    - Cell 7 (Markdown): "Regional & District Variation" section description
    - Cell 8 (Code): ESC region bar chart and top-10 districts chart — inline comments
    - Cell 9 (Markdown): "Demographic Analysis" section description
    - Cell 10 (Code): demographic breakdown chart — inline comments
    - Cell 11 (Markdown): "Key Insights" — 3+ written insights with specific district/region names and numeric values
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4_

- [x] 10. Final checkpoint — full pipeline end-to-end
  - Ensure all tests pass, ask the user if questions arise.
  - Verify running `collect.py` → `clean.py` → `analyze.py` in sequence produces all CSVs and figures without error.
  - _Requirements: 10.4_

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each property-based test should use `@settings(max_examples=100)` and include a comment referencing the property number
- All scripts are flat — no helper functions, no classes, just inline pandas/matplotlib
- Use relative paths everywhere; `os.makedirs(..., exist_ok=True)` before every file write
