---
inclusion: always
---

# Texas K–12 Education Data Analysis — Project Steering

## Project Overview
This project collects, cleans, and analyzes K–12 education data from the **Texas Education Agency (TEA)** — a primary government source — to satisfy a data analysis assignment.

## Data Sources (Primary Only)
All data must come exclusively from official TEA sources:

| Dataset | URL | Format |
|---|---|---|
| Annual Leavers 2023-24 (District-level) | https://tea.texas.gov/reports-and-data/school-performance/accountability-research/completion-graduation-and-dropout/annual-leavers-2023-24 | Excel (.xlsx) |
| Enrollment Trends 2023-24 | https://tea.texas.gov/reports-and-data/school-performance/accountability-research/enrollment-trends | PDF / PEIMS |
| PEIMS Standard Reports | https://rptsvr1.tea.texas.gov/perfreport/peim/index.html | Excel / CSV |

**Do NOT use**: Kaggle, FRED, NCES, or any pre-aggregated/pre-cleaned datasets.

## Tech Stack
- Language: **Python 3**
- Libraries: `pandas`, `matplotlib`, `seaborn`, `openpyxl`, `requests`
- Output: cleaned `.csv` files + annotated Jupyter notebook (`.ipynb`)

## Project Structure
```
project/
├── data/
│   ├── raw/          # Downloaded directly from TEA — do not modify
│   └── cleaned/      # Output of cleaning scripts
├── notebooks/
│   └── analysis.ipynb
├── scripts/
│   ├── collect.py    # Data download/collection
│   ├── clean.py      # Cleaning and integration
│   └── analyze.py    # Analysis and visualizations
└── outputs/
    └── figures/      # Charts and plots
```

## Coding Standards
- Every code block must have a comment explaining the step
- Use `pandas` for all data manipulation
- Save all cleaned data to `data/cleaned/` as `.csv`
- All figures saved to `outputs/figures/`
- No hardcoded absolute paths — use relative paths only

## Analysis Requirements
- Identify at least 3 meaningful insights (not just charts)
- Cover: trends over time, regional/district variation, demographic patterns
- Insights must reference specific districts, counties, or ESC regions where possible

## Assignment Constraints
- Minimum 2 datasets collected
- Document source URL, format, and collection method for each dataset
- Handle missing values, inconsistent formats, and data integration explicitly in code
