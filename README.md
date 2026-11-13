# DataLens

**A lightweight data intelligence platform for profiling, inspecting, cleaning, and reporting on tabular datasets.**

DataLens is a Python application with a Streamlit interface. Upload a CSV or Excel workbook, explore dataset quality, inspect individual columns, apply cleaning operations, and export the cleaned data and a cleaning report.

> **Project status:** Version 2.0 UI. Documentation milestone draft. Add real application screenshots and verify the dependency versions before publishing the repository.

## Features

- **Overview** — dataset-level summary and quality indicators.
- **Data Profiling** — row/column counts, missing-value information, duplicate-row count, data-type inspection, and quality visualizations.
- **Column Statistics** — inspect a selected column, including its data type, missing/non-null counts, uniqueness, representative values, and type-appropriate statistics or distributions.
- **Data Cleaning** — remove duplicates, handle missing values, and convert multiple selected columns to supported types.
- **Date conversion** — choose Auto Detect, `DD-MM-YYYY`, `MM-DD-YYYY`, or `YYYY-MM-DD` when converting date columns.
- **Integer conversion** — choose a rounding approach (Round, Floor, or Ceil) when converting decimal values to integers.
- **Cleaning Report** — review run-level and column-level outcomes; export the report to Excel or PDF.
- **Exports** — download cleaned data as CSV or Excel. The UI indicates when each export is ready.

## Technology

- Python
- pandas and NumPy
- Streamlit
- Plotly
- openpyxl (Excel reading/writing)
- ReportLab (PDF cleaning-report export)
- pytest and pytest-cov (testing)

## Project structure

```text
DataLens/
├── datalens/
│   ├── __init__.py
│   ├── profiling.py
│   ├── cleaning.py
│   ├── pipeline.py
│   └── validation.py
├── tests/
│   ├── date_test.py
│   ├── test_cleaning.py
│   ├── test_pipeline.py
│   ├── test_profiling.py
│   ├── test_type_conversion.py
│   └── test_validation.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── USER_GUIDE.md
│   ├── TESTING.md
│   └── screenshots/
├── app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DataLens
```

### 2. Create and activate a virtual environment

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the requirements file is not yet finalized, the current app imports or uses these packages:

```bash
pip install streamlit pandas numpy plotly openpyxl reportlab
```

### 4. Run the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

## Quick start

1. Upload a `.csv` or `.xlsx` dataset.
2. Review the Overview and Data Profiling screens.
3. Select a column in Column Statistics to inspect it.
4. Open Data Cleaning and configure duplicate removal, missing-value handling, and optional type conversions.
5. Run cleaning.
6. Download the cleaned dataset as CSV or prepare and download it as Excel.
7. Open Cleaning Report to review outcomes and export the report as Excel or PDF.

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for more detail.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [User guide](docs/USER_GUIDE.md)
- [Testing guide](docs/TESTING.md)
- [Screenshots](docs/screenshots/README.md)

## Testing

```bash
python -m pytest
python -m pytest --cov=datalens --cov-report=term-missing
```

The core package previously reached **51 passing tests and 100% statement coverage** in the recorded test run. This is a historical project result, not a guarantee for every later change. Re-run the commands against the exact commit you publish. UI behavior and Streamlit integration should also be manually regression-tested.

## Current limitations / notes

- DataLens is intended for tabular CSV and Excel input.
- Large-file performance depends on available memory and file complexity.
- Date parsing depends on the selected format and the consistency of source values.
- A successful core test suite does not replace manual testing of uploads, exports, and interactive UI behavior.
- Add screenshots captured from the actual running application before publishing.

## License

Choose and add a license before making the repository public.
