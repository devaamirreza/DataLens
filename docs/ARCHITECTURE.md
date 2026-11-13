# DataLens — Architecture

## 1. High-level design

DataLens separates the user interface from the reusable data-processing package.

```text
                 ┌─────────────────────────┐
                 │       Streamlit UI      │
                 │         app.py          │
                 └────────────┬────────────┘
                              │
              upload / inspect / configure / export
                              │
                 ┌────────────▼────────────┐
                 │      DataFrame          │
                 │   CSV or Excel input    │
                 └────────────┬────────────┘
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
┌─────────▼────────┐ ┌────────▼────────┐ ┌─────────▼────────┐
│   profiling.py   │ │  validation.py  │ │   pipeline.py   │
│ Dataset/column   │ │ Input and       │ │ Orchestration   │
│ inspection       │ │ option checks   │ │ of cleaning     │
└──────────────────┘ └─────────────────┘ └─────────┬────────┘
                                                   │
                                         ┌─────────▼────────┐
                                         │   cleaning.py    │
                                         │ Cleaning         │
                                         │ transformations │
                                         └─────────┬────────┘
                                                   │
                                         ┌─────────▼────────┐
                                         │ Cleaned DataFrame│
                                         │ + run report     │
                                         └─────────┬────────┘
                                                   │
                                 ┌─────────────────┼────────────────┐
                                 │                 │                │
                            CSV / Excel       Excel report      PDF report
```

## 2. Application layer — `app.py`

The Streamlit application is responsible for:

- Accepting CSV and Excel uploads.
- Displaying the Overview, Data Profiling, Column Statistics, Data Cleaning, and Cleaning Report screens.
- Collecting user-selected cleaning options.
- Calling the reusable profiling and cleaning functions.
- Keeping the active dataset and cleaning outputs in Streamlit session state.
- Preparing and exposing downloads for cleaned data and cleaning reports.

The current UI uses cached dataset loading/analysis to avoid repeating expensive parsing and profiling work on every interaction. Cleaning outputs and prepared exports are held in session state for the active uploaded dataset.

## 3. Core package — `datalens/`

### `profiling.py`

Provides dataset and data-type inspection functions:

- `profile_dataset(df)` — dataset-level metrics such as row count, column count, missing values, and duplicate rows.
- `inspect_data_types(df)` — column data types and non-null/missing counts.

### `validation.py`

Validates inputs and cleaning configuration before processing, including the dataframe, missing-value strategy, selected columns, and requested conversion types.

### `cleaning.py`

Contains reusable cleaning operations, including duplicate removal, missing-value handling, and supported type conversions. Nullable integer and string types are used where appropriate. Mean imputation on integer-like columns must support fractional results rather than forcing them into an integer dtype.

### `pipeline.py`

Coordinates validation and cleaning operations. It works on a copy of the input dataframe, applies configured conversions and cleaning steps, and returns the cleaned dataframe with a run report.

## 4. Typical processing flow

1. User uploads a CSV or Excel file.
2. The app reads the file into a pandas DataFrame.
3. Profiling functions calculate dataset and column information.
4. The user selects cleaning options in the Data Cleaning screen.
5. The UI validates/normalizes relevant settings and invokes `clean_dataset`.
6. The cleaning pipeline validates the request and applies the selected operations.
7. The app stores the cleaned DataFrame and report in session state.
8. The user previews results and downloads the cleaned dataset.
9. The Cleaning Report screen presents summary and column-level outcomes and provides report exports.

## 5. State and caching

The app uses two complementary mechanisms:

- **Caching** for repeatable, potentially expensive operations such as reading and analysing the same uploaded file.
- **Session state** for user work in progress, including the active file identity, cleaned dataframe, cleaning report, and prepared Excel export.

A newly uploaded dataset invalidates cleaning outputs and prepared exports associated with the previous dataset. Inspecting another sample column should not itself trigger a new cleaning run.

## 6. Export formats

| Output | Format | Purpose |
|---|---|---|
| Cleaned dataset | CSV | Portable tabular data |
| Cleaned dataset | XLSX | Spreadsheet-friendly cleaned data |
| Cleaning report | XLSX | Summary and column-outcome worksheets |
| Cleaning report | PDF | Shareable report document |

## 7. Design principles

- Keep core data operations reusable outside Streamlit.
- Validate user inputs before processing.
- Avoid mutating the source dataframe during cleaning.
- Preserve cleaning outputs across ordinary UI interactions.
- Make export readiness visible to the user.
- Keep profiling, cleaning, reporting, and presentation responsibilities distinct.
