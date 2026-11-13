# DataLens — User Guide

## 1. Launch DataLens

Activate the project's virtual environment and run:

```cmd
streamlit run app.py
```

Upload a CSV or Excel (`.xlsx`) file using the uploader at the top of the app. The uploaded dataset is the active dataset for the application screens.

## 2. Overview

Use Overview for a quick view of the uploaded dataset and its general quality indicators. Start here to understand the scale and basic condition of the data before cleaning.

## 3. Data Profiling

Open **Data Profiling** to review dataset-level information, including:

- Total rows and columns.
- Missing-value counts.
- Duplicate-row count.
- Column data types and completeness.
- Visual summaries of missing data / data quality.

Use this screen to identify potential cleaning work before changing the dataset.

## 4. Column Statistics

Open **Column Statistics** and choose a column from the selector.

The screen provides column-specific information such as:

- Data type.
- Non-null and missing counts.
- Missing percentage and unique-value count.
- Type-appropriate descriptive statistics and visual distributions.
- Sample values.

For numeric columns, available statistics include measures such as mean, median, standard deviation, minimum, maximum, quartiles, and skewness. Categorical and date columns show relevant frequency or date-range information.

Changing the selected sample column is for inspection only; it should not replace the uploaded dataset or run cleaning.

## 5. Data Cleaning

Open **Data Cleaning** to configure the cleaning operation.

### Remove duplicates

Enable the duplicate-removal option to remove duplicate rows during the cleaning run.

### Handle missing values

Choose the missing-value strategy exposed by the app. The available strategies include:

- **Drop** — remove rows containing missing values according to the pipeline's configured behavior.
- **Mean** — fill eligible numeric missing values using the column mean.
- **Median** — fill eligible numeric missing values using the column median.

Mean and median are numeric imputation strategies; do not assume they fill missing text values.

### Convert column types

Enable type conversion and select one or more columns. Configure the target type for each selected column.

Supported conversions include integer, float, string, and datetime. For integer conversion, select the rounding behavior:

- Round
- Floor
- Ceil

For datetime conversion, select the format:

- Auto Detect
- `DD-MM-YYYY`
- `MM-DD-YYYY`
- `YYYY-MM-DD`

Use the format that matches the source data. For example, `28-07-2019` is compatible with `DD-MM-YYYY`, not `MM-DD-YYYY`.

Review the displayed configuration and preview before running the cleaning operation.

### Run cleaning

Click **Run Data Cleaning**. When the operation succeeds, review the cleaned dataset preview and the run summary.

The cleaning run report includes measures such as original/final rows, duplicates removed, and missing values handled.

### Download cleaned data

- CSV becomes available as a ready-to-download export after the cleaning result is produced.
- Excel may first need to be prepared. Click **Prepare Excel** and wait for preparation to complete. The button changes to a green ready-to-download state when the workbook is ready.

The prepared exports should remain available while navigating within the same active session and dataset.

## 6. Cleaning Report

Open **Cleaning Report** after a successful cleaning run.

Review the run-level summary and column-level outcomes, including original/final data types, missing-value counts, and final unique-value counts.

Export the report as:
- Excel workbook, with Cleaning Summary and Column Outcomes worksheets.
- PDF report.

If no cleaning run exists for the active dataset, run cleaning first.

## 7. Recommended workflow

1. Upload the source dataset.
2. Review Overview.
3. Inspect Data Profiling.
4. Investigate important columns in Column Statistics.
5. Configure and run cleaning.
6. Review the cleaned preview.
7. Download CSV and/or Excel.
8. Review and export the Cleaning Report.

## 8. Troubleshooting

**Excel export is unavailable or fails**
- Confirm `openpyxl` is installed in the active environment:
  `python -m pip install openpyxl`
- If preparing Excel, wait for the preparation step to finish.
- Review any error shown by the app.

**PDF report export fails**
- Confirm ReportLab is installed:
  `python -m pip install reportlab`

**Date conversion fails**
- Check the actual source date format.
- Select the matching format explicitly.
- Look for inconsistent values or invalid dates in the source column.

**The app is slow**
- The initial upload and profiling can take longer for large files.
- Subsequent interactions should benefit from cached loading/analysis.
- Performance depends on dataset size, file format, available memory, and the operations selected.

**Cleaning results disappear after a new upload**
- A new dataset is expected to reset cleaning outputs and exports so results from one dataset are not mistakenly applied to another.
