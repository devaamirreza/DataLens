# DataLens — Testing Guide

## 1. Automated core tests

Run the complete test suite from the project root:

```bash
python -m pytest
```

Run tests with statement coverage:

```bash
python -m pytest --cov=datalens --cov-report=term-missing
```

The recorded baseline for the core `datalens` package was:

- **51 tests passed**
- **100% statement coverage** across the core package modules in that run.

This is a historical baseline. Re-run tests against the exact source revision being released. Coverage of the core package does not imply that every Streamlit UI path, file export, or browser interaction is covered.

## 2. Core areas to test

| Area | Example checks |
|---|---|
| Profiling | Row/column counts, missing counts, duplicate counts, dtypes |
| Validation | Invalid dataframe, strategy, column, and conversion type |
| Cleaning | Duplicate removal, drop/mean/median behavior |
| Type conversion | Integer, float, string, datetime |
| Date parsing | Supported explicit formats and auto detection |
| Pipeline | Combined operations, report values, source dataframe preservation |

## 3. Manual UI regression checklist

Run:

```cmd
streamlit run app.py
```

Then verify:

### Upload and profiling
- [ ] Upload a valid CSV.
- [ ] Upload a valid XLSX file.
- [ ] Confirm row and column counts.
- [ ] Confirm missing and duplicate counts.
- [ ] Confirm a different upload resets results from the previous dataset.
- [ ] Confirm repeated navigation does not repeatedly incur the full initial load cost.

### Column Statistics
- [ ] Select a numeric column and inspect numeric statistics/chart.
- [ ] Select a categorical column and inspect category frequencies.
- [ ] Select a date column and inspect date range/distribution.
- [ ] Change the sample column multiple times.
- [ ] Confirm sample inspection does not run cleaning or replace the active dataset.

### Data Cleaning
- [ ] Run cleaning with duplicate removal enabled.
- [ ] Run cleaning with duplicate removal disabled.
- [ ] Test Drop, Mean, and Median strategies on suitable test data.
- [ ] Convert multiple columns in one run.
- [ ] Test integer Round, Floor, and Ceil.
- [ ] Test each supported explicit date format.
- [ ] Test a mismatched date format and verify a clear validation/error message.
- [ ] Confirm mean imputation can retain fractional values for integer-like input columns.
- [ ] Confirm the cleaned preview matches the cleaning report.

### Exports
- [ ] Confirm CSV becomes ready after a successful cleaning run.
- [ ] Confirm CSV download opens and contains the cleaned data.
- [ ] Click Prepare Excel and wait for completion.
- [ ] Confirm Excel button changes to its green ready state.
- [ ] Download and open the XLSX workbook.
- [ ] Navigate to another screen and return; confirm prepared exports remain available.
- [ ] Run cleaning again; confirm stale exports are invalidated and regenerated for the new result.

### Cleaning Report
- [ ] Confirm no-report message appears before the first cleaning run.
- [ ] Confirm summary metrics match the cleaning run.
- [ ] Confirm column-level outcomes are consistent with the cleaned dataframe.
- [ ] Download and open the Excel report.
- [ ] Download and open the PDF report.

## 4. Performance test dataset

The project has a generated performance dataset containing **50,500 rows** (50,000 base rows plus 500 duplicate rows) and 8 columns. It includes missing values in selected numeric and categorical fields and date strings in `DD-MM-YYYY` format.

Use this dataset to manually check:
- Initial upload/profiling time.
- Duplicate detection.
- Missing-value handling.
- Type conversion.
- Export preparation time.
- Responsiveness when navigating between screens.

Record actual timings on the release machine rather than publishing unmeasured performance claims.

## 5. Release gate

Before tagging a release:

- [ ] Automated tests pass on the release commit.
- [ ] Coverage report is regenerated.
- [ ] Manual UI checklist is completed.
- [ ] CSV, XLSX, and PDF exports are opened and verified.
- [ ] `requirements.txt` contains all runtime dependencies.
- [ ] README setup instructions work in a clean virtual environment.
- [ ] Screenshots are captured from the actual app.
- [ ] Known limitations are documented.
