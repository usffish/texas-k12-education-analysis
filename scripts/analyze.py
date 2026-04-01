import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt

# Step 1: Ensure the output directory exists before writing any figures
os.makedirs("outputs/figures/", exist_ok=True)

# ─────────────────────────────────────────────
# LOAD CLEANED DATA
# ─────────────────────────────────────────────

# Step 2a: Load the merged district dataset (leavers + enrollment joined on district_id)
print("Loading data/cleaned/merged_district_2023_24.csv ...")
merged_df = pd.read_csv("data/cleaned/merged_district_2023_24.csv")
print(f"  merged_df shape: {merged_df.shape}")

# Step 2b: Load the standalone enrollment dataset for statewide enrollment trend
print("Loading data/cleaned/enrollment_2023_24.csv ...")
enrollment_df = pd.read_csv("data/cleaned/enrollment_2023_24.csv")
print(f"  enrollment_df shape: {enrollment_df.shape}")

# ─────────────────────────────────────────────
# ENROLLMENT TREND — statewide enrollment per year
# ─────────────────────────────────────────────

# Step 3: Identify the enrollment count column — it may be named differently across datasets
# Check for common variants and fall back gracefully if none are found
enrollment_col = None
for candidate in ["enrollment_count", "total_enrollment", "enrollment"]:
    if candidate in enrollment_df.columns:
        enrollment_col = candidate
        break

if enrollment_col is None:
    print("WARNING: No enrollment count column found in enrollment_df — skipping enrollment trend chart")
    print(f"  Available columns: {list(enrollment_df.columns)}")
else:
    # Step 4: Check that school_year column exists before grouping
    if "school_year" not in enrollment_df.columns:
        print("WARNING: 'school_year' column not found in enrollment_df — skipping enrollment trend chart")
    else:
        # Step 5: Compute statewide total enrollment per school year
        enrollment_trend = enrollment_df.groupby("school_year")[enrollment_col].sum()
        print(f"\nEnrollment trend by year:\n{enrollment_trend}")

        # Step 6: Plot line chart of statewide enrollment over time
        plt.figure(figsize=(10, 5))
        plt.plot(enrollment_trend.index.astype(str), enrollment_trend.values, marker="o", linewidth=2)
        plt.title("Statewide Enrollment Trend")
        plt.xlabel("School Year")
        plt.ylabel("Total Enrollment")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Step 7: Save the enrollment trend figure and free memory
        plt.savefig("outputs/figures/enrollment_trend.png")
        plt.close()
        print("Saved outputs/figures/enrollment_trend.png")

# ─────────────────────────────────────────────
# LEAVER TREND — statewide leaver count per year
# ─────────────────────────────────────────────

# Step 8: Check that leaver_count column exists in merged_df before grouping
if "leaver_count" not in merged_df.columns:
    print("WARNING: 'leaver_count' column not found in merged_df — skipping leaver trend chart")
    print(f"  Available columns: {list(merged_df.columns)}")
else:
    # Step 9: Check that school_year column exists in merged_df before grouping
    if "school_year" not in merged_df.columns:
        print("WARNING: 'school_year' column not found in merged_df — skipping leaver trend chart")
    else:
        # Step 10: Compute statewide total leaver count per school year
        leaver_trend = merged_df.groupby("school_year")["leaver_count"].sum()
        print(f"\nLeaver trend by year:\n{leaver_trend}")

        # Step 11: Plot line chart of statewide leaver count over time
        plt.figure(figsize=(10, 5))
        plt.plot(leaver_trend.index.astype(str), leaver_trend.values, marker="o", color="tomato", linewidth=2)
        plt.title("Statewide Leaver Count Trend")
        plt.xlabel("School Year")
        plt.ylabel("Total Leaver Count")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Step 12: Save the leaver trend figure and free memory
        plt.savefig("outputs/figures/leaver_trend.png")
        plt.close()
        print("Saved outputs/figures/leaver_trend.png")

# ─────────────────────────────────────────────
# LEAVER RATE — compute leaver_rate column
# ─────────────────────────────────────────────

# Step 13: Verify required columns exist before computing leaver rate
_leaver_rate_cols_ok = True
for _col in ["leaver_count", "enrollment_count"]:
    if _col not in merged_df.columns:
        print(f"WARNING: column '{_col}' not found in merged_df — skipping leaver rate computation")
        _leaver_rate_cols_ok = False

if _leaver_rate_cols_ok:
    # Step 14: Compute leaver rate; replace 0 enrollment with NaN to avoid ZeroDivisionError, then fill NaN with 0
    merged_df["leaver_rate"] = (
        merged_df["leaver_count"] / merged_df["enrollment_count"].replace(0, float("nan"))
    ).fillna(0)
    print(f"\nleaver_rate column added. Sample:\n{merged_df[['leaver_count', 'enrollment_count', 'leaver_rate']].head()}")

    # ─────────────────────────────────────────────
    # ESC REGION BAR CHART — mean leaver rate per region
    # ─────────────────────────────────────────────

    # Step 15: Check that esc_region column exists before grouping
    if "esc_region" not in merged_df.columns:
        print("WARNING: column 'esc_region' not found in merged_df — skipping ESC region chart")
    else:
        # Step 16: Group by ESC region and compute mean leaver rate per region
        esc_leaver_rate = merged_df.groupby("esc_region")["leaver_rate"].mean().sort_index()
        print(f"\nMean leaver rate by ESC region:\n{esc_leaver_rate}")

        # Step 17: Plot vertical bar chart of mean leaver rate by ESC region
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(esc_leaver_rate.index.astype(str), esc_leaver_rate.values, color="steelblue")

        # Step 18: Add value labels on top of each bar for readability
        ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=8)

        ax.set_title("Mean Leaver Rate by ESC Region")
        ax.set_xlabel("ESC Region")
        ax.set_ylabel("Mean Leaver Rate")
        plt.tight_layout()

        # Step 19: Save the ESC region chart and free memory
        plt.savefig("outputs/figures/leaver_rate_by_esc_region.png")
        plt.close()
        print("Saved outputs/figures/leaver_rate_by_esc_region.png")

    # ─────────────────────────────────────────────
    # TOP-10 DISTRICTS — highest leaver rate
    # ─────────────────────────────────────────────

    # Step 20: Sort merged_df by leaver_rate descending and take the top 10 rows
    top10_df = merged_df.sort_values("leaver_rate", ascending=False).head(10)

    # Step 21: Determine label column — prefer district_name, fall back to district_id
    if "district_name" in top10_df.columns:
        _label_col = "district_name"
    elif "district_id" in top10_df.columns:
        _label_col = "district_id"
    else:
        print("WARNING: neither 'district_name' nor 'district_id' found — skipping top-10 chart")
        _label_col = None

    if _label_col is not None:
        # Step 22: Build label list; convert to string to handle numeric IDs safely
        _labels = top10_df[_label_col].astype(str).tolist()
        _values = top10_df["leaver_rate"].tolist()

        # Step 23: Plot horizontal bar chart (barh) so long district names are readable
        plt.figure(figsize=(10, 6))
        plt.barh(_labels[::-1], _values[::-1], color="tomato")  # reverse so highest is at top
        plt.title("Top 10 Districts by Leaver Rate")
        plt.xlabel("Leaver Rate")
        plt.ylabel("District")
        plt.tight_layout()

        # Step 24: Save the top-10 chart and free memory
        plt.savefig("outputs/figures/top10_leaver_districts.png")
        plt.close()
        print("Saved outputs/figures/top10_leaver_districts.png")

# ─────────────────────────────────────────────
# DEMOGRAPHIC BREAKDOWN — leaver rate by demographic group
# ─────────────────────────────────────────────

# Step 25: Check that leaver_rate column exists before attempting demographic breakdown
if "leaver_rate" not in merged_df.columns:
    print("WARNING: 'leaver_rate' column not found in merged_df — skipping demographic breakdown chart")
else:
    # Step 26: Define candidate demographic columns to search for in merged_df
    _demo_candidates = ["race_ethnicity", "gender", "eco_dis", "eco_dis_count", "race_eth", "ethnicity"]

    # Step 27: Collect qualifying demographic group → mean leaver_rate pairs into a single dict
    _demo_rates = {}

    for _col in _demo_candidates:
        # Step 28: Skip columns that don't exist in the DataFrame
        if _col not in merged_df.columns:
            print(f"WARNING: column '{_col}' not found — skipping")
            continue

        # Step 29: Only include columns with fewer than 5 distinct non-null values (categorical demographics)
        _n_unique = merged_df[_col].dropna().nunique()
        if _n_unique >= 5:
            # Not a categorical demographic column — skip silently
            continue

        # Step 30: Compute mean leaver_rate grouped by this demographic column
        _group_rates = merged_df.groupby(_col)["leaver_rate"].mean()

        # Step 31: Add each group label → rate pair into the combined dict
        for _group_label, _rate in _group_rates.items():
            _demo_rates[f"{_col}:{_group_label}"] = _rate

    # Step 32: Plot a single bar chart only if at least one qualifying demographic column was found
    if not _demo_rates:
        print("WARNING: no qualifying demographic columns found — skipping leaver_rate_by_demographic.png")
    else:
        # Step 33: Build sorted lists of labels and values for the bar chart
        _demo_labels = list(_demo_rates.keys())
        _demo_values = list(_demo_rates.values())

        # Step 34: Plot bar chart with all demographic groups on the x-axis
        plt.figure(figsize=(max(10, len(_demo_labels) * 1.2), 6))
        plt.bar(_demo_labels, _demo_values, color="mediumseagreen")
        plt.title("Leaver Rate by Demographic Group")
        plt.xlabel("Demographic Group")
        plt.ylabel("Mean Leaver Rate")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        # Step 35: Save the demographic breakdown chart and free memory
        plt.savefig("outputs/figures/leaver_rate_by_demographic.png")
        plt.close()
        print("Saved outputs/figures/leaver_rate_by_demographic.png")

# ─────────────────────────────────────────────
# KEY INSIGHTS — derived from computed statistics above
# ─────────────────────────────────────────────

# Step 36: Print a header to visually separate the insights section
print("\n========== KEY INSIGHTS ==========")

# ── Insight 1: District with the highest leaver rate ──────────────────────────
# Guard: top10_df must exist and contain leaver_rate plus a name/id column
if "top10_df" not in dir() or top10_df.empty:
    print("WARNING: top10_df not available — skipping Insight 1")
else:
    # Determine which label column is present (prefer district_name over district_id)
    _ins1_label_col = None
    for _c in ["district_name", "district_id"]:
        if _c in top10_df.columns:
            _ins1_label_col = _c
            break

    if _ins1_label_col is None:
        print("WARNING: no district name/id column in top10_df — skipping Insight 1")
    else:
        # Grab the top row — already sorted descending by leaver_rate
        _ins1_row = top10_df.iloc[0]
        _ins1_name = str(_ins1_row[_ins1_label_col])
        _ins1_rate = _ins1_row["leaver_rate"]
        print(f"INSIGHT 1: {_ins1_name} had the highest leaver rate at {_ins1_rate * 100:.2f}%")

# ── Insight 2: ESC region with the highest mean leaver rate ───────────────────
# Guard: esc_leaver_rate Series must exist and be non-empty
if "esc_leaver_rate" not in dir() or esc_leaver_rate.empty:
    print("WARNING: esc_leaver_rate not available — skipping Insight 2")
else:
    # Find the region index with the maximum mean leaver rate
    _ins2_region = esc_leaver_rate.idxmax()
    _ins2_rate = esc_leaver_rate.max()
    print(f"INSIGHT 2: ESC Region {_ins2_region} had the highest mean leaver rate at {_ins2_rate * 100:.2f}%")

# ── Insight 3: Year with the highest total leaver count ───────────────────────
# Guard: leaver_trend Series must exist and be non-empty
if "leaver_trend" not in dir() or leaver_trend.empty:
    print("WARNING: leaver_trend not available — skipping Insight 3")
else:
    # Find the school year with the maximum total leaver count
    _ins3_year = leaver_trend.idxmax()
    _ins3_count = int(leaver_trend.max())
    print(f"INSIGHT 3: {_ins3_year} had the highest total leaver count with {_ins3_count:,} leavers")

# ── Insight 4 (optional): District with the lowest non-zero leaver rate ───────
# Guard: merged_df must exist and leaver_rate column must be present
if "merged_df" not in dir() or "leaver_rate" not in merged_df.columns:
    print("WARNING: merged_df or leaver_rate not available — skipping Insight 4")
else:
    # Filter to rows with a positive leaver rate to exclude districts with no leavers recorded
    _nonzero_df = merged_df[merged_df["leaver_rate"] > 0]

    if _nonzero_df.empty:
        print("WARNING: no districts with non-zero leaver rate — skipping Insight 4")
    else:
        # Determine label column for the lowest-rate district
        _ins4_label_col = None
        for _c in ["district_name", "district_id"]:
            if _c in _nonzero_df.columns:
                _ins4_label_col = _c
                break

        if _ins4_label_col is None:
            print("WARNING: no district name/id column in merged_df — skipping Insight 4")
        else:
            # Find the row with the minimum non-zero leaver rate
            _ins4_row = _nonzero_df.loc[_nonzero_df["leaver_rate"].idxmin()]
            _ins4_name = str(_ins4_row[_ins4_label_col])
            _ins4_rate = _ins4_row["leaver_rate"]
            print(f"INSIGHT 4: {_ins4_name} had the lowest non-zero leaver rate at {_ins4_rate * 100:.2f}%")

print("\nanalyze.py complete.")
