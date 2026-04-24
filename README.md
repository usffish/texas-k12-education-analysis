# School Projects

End-to-end data analytics pipelines from the University of South Florida M.S. in AI & Business Analytics program.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![matplotlib](https://img.shields.io/badge/matplotlib-3776AB?style=flat-square&logo=python&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=jupyter&logoColor=white)

## Notebooks

### Texas K-12 Education Data Analysis
An end-to-end data pipeline analyzing Texas Education Agency (TEA) K-12 leaver and dropout data for the 2023-24 school year across 1,169 districts.

**What it does:**
- Collects raw data directly from TEA via HTTP (Excel + HTML sources) with a JSON manifest for reproducibility
- Cleans and normalizes the dataset — column normalization, missing value imputation, deduplication, district ID zero-padding
- Computes leaver rates per district and aggregates statewide trends
- Produces visualizations: enrollment trends, leaver count trends, top-10 districts by dropout rate, and statewide leaver reason breakdown

**Key findings:**
- 28,923 total dropouts across Texas in 2023-24
- The Excel Center had the highest raw dropout count (836)
- Killeen ISD had the highest dropout rate among districts with 10+ leavers
- Rio Grande City Grulla ISD had the lowest non-zero dropout rate at 0.06%

**Stack:** Python · pandas · matplotlib · seaborn · openpyxl · requests

## Project Structure

```
School-Projects/
├── notebooks/
│   ├── analysis.ipynb        # Texas K-12 TEA data analysis pipeline
│   └── data/                 # Raw and cleaned datasets (not committed)
├── scripts/                  # Utility scripts
└── tests/                    # Test files
```

## Setup

```bash
git clone https://github.com/usffish/School-Projects.git
cd School-Projects
pip install -r requirements.txt
jupyter notebook notebooks/analysis.ipynb
```

## Author

**Ismail Jhaveri** — [LinkedIn](https://www.linkedin.com/in/ismail-jhaveri-2021/) · [ismailj@usf.edu](mailto:ismailj@usf.edu)
