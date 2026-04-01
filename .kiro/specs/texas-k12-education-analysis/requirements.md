# Requirements Document

## Introduction

This feature implements a K–12 education data collection, processing, and analysis pipeline targeting the state of Texas. Data is sourced exclusively from the Texas Education Agency (TEA) — a primary government source. The pipeline downloads raw datasets (Annual Leavers 2023-24 and Enrollment Trends 2023-24), cleans and integrates them, and produces an annotated Jupyter notebook with visualizations and at least three meaningful insights covering trends over time, regional/district variation, and demographic patterns.

## Glossary

- **TEA**: Texas Education Agency — the state agency responsible for public K–12 education data in Texas.
- **Pipeline**: The end-to-end sequence of scripts that collect, clean, and analyze education data.
- **Collector**: The `scripts/collect.py` module responsible for downloading raw data from TEA URLs.
- **Cleaner**: The `scripts/clean.py` module responsible for transforming raw data into analysis-ready CSVs.
- **Analyzer**: The `scripts/analyze.py` module and `notebooks/analysis.ipynb` responsible for producing insights and figures.
- **Raw_Data**: Files downloaded directly from TEA, stored in `data/raw/`, never modified in place.
- **Cleaned_Data**: Processed output stored in `data/cleaned/` as `.csv` files.
- **Leaver_Dataset**: The Annual Leavers 2023-24 district-level Excel file from TEA.
- **Enrollment_Dataset**: The Enrollment Trends 2023-24 data (PDF/PEIMS) from TEA.
- **ESC_Region**: Education Service Center region — a geographic grouping of Texas school districts.
- **PEIMS**: Public Education Information Management System — TEA's official data reporting system.
- **Insight**: A finding that references a specific district, county, or ESC region and is supported by data.

---

## Requirements

### Requirement 1: Data Collection from TEA Primary Sources

**User Story:** As a data analyst, I want to download raw datasets directly from TEA URLs, so that all data originates from a verified primary government source with no pre-cleaning applied.

#### Acceptance Criteria

1. WHEN the Collector is executed, THE Collector SHALL download the Annual Leavers 2023-24 district-level Excel file from `https://tea.texas.gov/reports-and-data/school-performance/accountability-research/completion-graduation-and-dropout/annual-leavers-2023-24`.
2. WHEN the Collector is executed, THE Collector SHALL download the Enrollment Trends 2023-24 data from `https://tea.texas.gov/reports-and-data/school-performance/accountability-research/enrollment-trends`.
3. WHEN a file is successfully downloaded, THE Collector SHALL save it to `data/raw/` using a relative path.
4. WHEN a download request fails due to a network error or non-200 HTTP response, THE Collector SHALL log a descriptive error message including the URL and HTTP status code, and SHALL halt execution for that dataset.
5. THE Collector SHALL record the source URL, file format, and collection timestamp for each downloaded dataset in a manifest file at `data/raw/manifest.json`.
6. THE Collector SHALL collect a minimum of 2 datasets before the pipeline proceeds to cleaning.

---

### Requirement 2: Raw Data Preservation

**User Story:** As a data analyst, I want raw downloaded files to remain unmodified, so that I can always re-run cleaning from the original source data.

#### Acceptance Criteria

1. THE Cleaner SHALL read input exclusively from `data/raw/` and SHALL NOT overwrite any file in `data/raw/`.
2. THE Cleaner SHALL write all output files to `data/cleaned/` as `.csv` format.
3. WHEN a cleaned output file already exists, THE Cleaner SHALL overwrite it with the latest cleaned result.

---

### Requirement 3: Data Cleaning and Standardization

**User Story:** As a data analyst, I want raw TEA files cleaned and standardized, so that the data is consistent and ready for analysis without manual intervention.

#### Acceptance Criteria

1. WHEN the Cleaner processes the Leaver_Dataset, THE Cleaner SHALL parse the Excel file using `openpyxl` and load it into a pandas DataFrame.
2. WHEN the Cleaner processes the Enrollment_Dataset, THE Cleaner SHALL parse the source file and load it into a pandas DataFrame.
3. THE Cleaner SHALL normalize all column names to lowercase with underscores (e.g., `district_name`, `leaver_count`).
4. WHEN a numeric column contains missing values, THE Cleaner SHALL fill those values with `0` and SHALL log the column name and count of filled values.
5. WHEN a string column contains missing values, THE Cleaner SHALL fill those values with `"Unknown"` and SHALL log the column name and count of filled values.
6. THE Cleaner SHALL remove duplicate rows from each dataset and SHALL log the count of duplicates removed.
7. WHEN district identifiers are present in both datasets, THE Cleaner SHALL standardize the district ID format to a zero-padded 6-digit string to enable joining across datasets.
8. THE Cleaner SHALL save the cleaned Leaver_Dataset to `data/cleaned/leavers_2023_24.csv`.
9. THE Cleaner SHALL save the cleaned Enrollment_Dataset to `data/cleaned/enrollment_2023_24.csv`.
10. WHEN cleaning is complete, THE Cleaner SHALL print a summary report stating the row count, column count, and missing-value counts for each output file.

---

### Requirement 4: Data Integration

**User Story:** As a data analyst, I want enrollment and leaver data joined at the district level, so that I can analyze dropout and completion rates in context of enrollment size.

#### Acceptance Criteria

1. WHEN both cleaned datasets are available, THE Cleaner SHALL produce a merged dataset joined on the standardized district ID field.
2. THE Cleaner SHALL save the merged dataset to `data/cleaned/merged_district_2023_24.csv`.
3. WHEN a district appears in the Leaver_Dataset but not in the Enrollment_Dataset, THE Cleaner SHALL retain the district row with enrollment fields set to `0` and SHALL log the unmatched district IDs.
4. WHEN a district appears in the Enrollment_Dataset but not in the Leaver_Dataset, THE Cleaner SHALL retain the district row with leaver fields set to `0` and SHALL log the unmatched district IDs.

---

### Requirement 5: Trend Analysis

**User Story:** As a data analyst, I want to identify trends over time in enrollment and leaver data, so that I can report on how Texas K–12 outcomes have changed.

#### Acceptance Criteria

1. WHEN the Analyzer processes the Enrollment_Dataset, THE Analyzer SHALL compute total statewide enrollment per year for all available years in the dataset.
2. WHEN the Analyzer processes the Leaver_Dataset, THE Analyzer SHALL compute total statewide leaver counts per year for all available years in the dataset.
3. THE Analyzer SHALL produce a line chart showing statewide enrollment trends over time, saved to `outputs/figures/enrollment_trend.png`.
4. THE Analyzer SHALL produce a line chart showing statewide leaver counts over time, saved to `outputs/figures/leaver_trend.png`.
5. WHEN generating figures, THE Analyzer SHALL use `matplotlib` or `seaborn` and SHALL label axes, include a title, and save using relative paths.

---

### Requirement 6: Regional and District Variation Analysis

**User Story:** As a data analyst, I want to compare enrollment and leaver rates across ESC regions and districts, so that I can identify geographic disparities in Texas K–12 outcomes.

#### Acceptance Criteria

1. THE Analyzer SHALL compute the leaver rate per district as `leaver_count / enrollment_count` where enrollment is greater than 0.
2. THE Analyzer SHALL identify the top 10 districts by leaver rate and the bottom 10 districts by leaver rate from the merged dataset.
3. THE Analyzer SHALL produce a bar chart of leaver rates by ESC region, saved to `outputs/figures/leaver_rate_by_esc_region.png`.
4. THE Analyzer SHALL produce a bar chart of the top 10 districts by leaver rate, saved to `outputs/figures/top10_leaver_districts.png`.
5. WHEN producing regional charts, THE Analyzer SHALL label each bar with the ESC region number or district name.

---

### Requirement 7: Demographic Pattern Analysis

**User Story:** As a data analyst, I want to examine leaver and enrollment data broken down by demographic group, so that I can identify equity gaps across student populations.

#### Acceptance Criteria

1. WHEN demographic columns (e.g., race/ethnicity, economic disadvantage, gender) are present in the Leaver_Dataset, THE Analyzer SHALL compute leaver counts and rates disaggregated by each available demographic group.
2. THE Analyzer SHALL produce at least one chart showing leaver rates by demographic group, saved to `outputs/figures/leaver_rate_by_demographic.png`.
3. WHEN a demographic column contains fewer than 5 distinct non-null values, THE Analyzer SHALL include it in the demographic breakdown.
4. IF a demographic column is absent from the dataset, THEN THE Analyzer SHALL log a warning stating which demographic dimension could not be analyzed and SHALL skip that chart.

---

### Requirement 8: Insight Generation

**User Story:** As a data analyst, I want the notebook to surface at least 3 data-backed insights, so that the analysis goes beyond charts and provides actionable findings.

#### Acceptance Criteria

1. THE Analyzer SHALL produce a minimum of 3 written insights in the Jupyter notebook, each referencing a specific district name, county, or ESC region by name.
2. WHEN an insight references a numeric finding (e.g., leaver rate, enrollment count), THE Analyzer SHALL include the specific numeric value in the insight text.
3. THE Analyzer SHALL derive each insight from a chart or computed statistic produced earlier in the notebook.
4. WHEN insights are written, THE Analyzer SHALL present them in a dedicated Markdown cell titled "Key Insights" within the notebook.

---

### Requirement 9: Annotated Jupyter Notebook

**User Story:** As a student submitting an assignment, I want every code cell in the notebook to have explanatory comments, so that the grader can follow the logic without additional documentation.

#### Acceptance Criteria

1. THE Analyzer SHALL implement all analysis steps in `notebooks/analysis.ipynb`.
2. WHEN a code cell performs a data operation, THE Analyzer SHALL include at least one inline comment per logical step within that cell.
3. THE Analyzer SHALL include a Markdown cell before each major section (collection, cleaning, analysis, insights) describing the purpose of that section.
4. THE Analyzer SHALL document the source URL, file format, and collection method for each dataset in a Markdown cell at the top of the notebook.

---

### Requirement 10: Reproducibility and Path Standards

**User Story:** As a developer or grader, I want the pipeline to run end-to-end without modification on any machine, so that results are reproducible without environment-specific configuration.

#### Acceptance Criteria

1. THE Pipeline SHALL use only relative file paths throughout all scripts and the notebook.
2. WHEN a required output directory (`data/raw/`, `data/cleaned/`, `outputs/figures/`) does not exist, THE Pipeline SHALL create it automatically before writing any file.
3. THE Pipeline SHALL declare all third-party dependencies (`pandas`, `matplotlib`, `seaborn`, `openpyxl`, `requests`) and SHALL be executable using Python 3.
4. WHEN `scripts/collect.py` is run, followed by `scripts/clean.py`, followed by `scripts/analyze.py`, THE Pipeline SHALL produce all cleaned CSVs and figures without manual intervention between steps.
