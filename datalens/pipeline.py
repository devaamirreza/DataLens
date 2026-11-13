import pandas as pd

from datalens.cleaning import (
    remove_duplicates,
    handle_missing_values,
    convert_data_types
)

from datalens.validation import (
    validate_dataframe,
    validate_missing_strategy,
    validate_columns,
    validate_conversion_types
)


# --------------------------------------------------
# COMPLETE DATA CLEANING PIPELINE
# --------------------------------------------------

def clean_dataset(
    df: pd.DataFrame,
    remove_duplicate_rows: bool = True,
    missing_strategy: str = "drop",
    conversions: dict | None = None,
    datetime_formats: dict | None = None
) -> tuple[pd.DataFrame, dict]:
    """
    Execute the complete DataLens cleaning pipeline.

    Parameters:
        df:
            Original DataFrame.

        remove_duplicate_rows:
            Whether duplicate rows should be removed.

        missing_strategy:
            drop, mean or median.

        conversions:
            Optional dictionary specifying column conversions.

        datetime_formats:
            Optional dictionary specifying datetime formats.

    Returns:
        cleaned_df:
            Processed DataFrame.

        report:
            Cleaning summary.
    """

    # --------------------------------------------------
    # STEP 1: VALIDATE INPUT DATASET
    # --------------------------------------------------

    validate_dataframe(df)

    # --------------------------------------------------
    # STEP 2: VALIDATE CLEANING STRATEGY
    # --------------------------------------------------

    validate_missing_strategy(missing_strategy)

    # --------------------------------------------------
    # STEP 3: VALIDATE CONVERSION REQUESTS
    # --------------------------------------------------

    if conversions is not None:

        validate_columns(df, conversions)

        validate_conversion_types(conversions)

    # Validate datetime format configuration.
    if datetime_formats is not None:

        # Date formats can only be supplied for columns
        # included in the conversion request.
        if conversions is None:

            raise ValueError(
                "Datetime formats require conversion requests."
            )

        supported_formats = {
            "DD-MM-YYYY",
            "MM-DD-YYYY",
            "YYYY-MM-DD",
            "auto"
        }

        for column, date_format in datetime_formats.items():

            # Ensure the column is included in conversions.
            if column not in conversions:

                raise ValueError(
                    f"Datetime format provided for '{column}', "
                    "but no conversion was requested for this column."
                )

            # Ensure the column is being converted to datetime.
            if conversions[column] != "datetime":

                raise ValueError(
                    f"Datetime format can only be configured "
                    f"for datetime columns. '{column}' is "
                    f"configured as {conversions[column]}."
                )

            # Validate the selected format.
            if date_format not in supported_formats:

                raise ValueError(
                    f"Unsupported datetime format: {date_format}. "
                    "Choose DD-MM-YYYY, MM-DD-YYYY, "
                    "YYYY-MM-DD or auto."
                )

    # --------------------------------------------------
    # STEP 4: PRESERVE ORIGINAL DATASET
    # --------------------------------------------------

    cleaned_df = df.copy()

    # --------------------------------------------------
    # STEP 5: INITIALIZE CLEANING REPORT
    # --------------------------------------------------

    report = {
        "original_rows": len(cleaned_df),
        "original_columns": len(cleaned_df.columns),
        "duplicates_removed": 0,
        "missing_values_handled": 0,
        "final_rows": 0,
        "final_columns": 0
    }

    # --------------------------------------------------
    # STEP 6: CONVERT DATA TYPES
    # --------------------------------------------------

    if conversions:

        cleaned_df = convert_data_types(
            cleaned_df,
            conversions,
            datetime_formats=datetime_formats
        )

    # --------------------------------------------------
    # STEP 7: REMOVE DUPLICATES
    # --------------------------------------------------

    if remove_duplicate_rows:

        duplicates_before = int(
            cleaned_df.duplicated().sum()
        )

        cleaned_df = remove_duplicates(cleaned_df)

        report["duplicates_removed"] = duplicates_before

    # --------------------------------------------------
    # STEP 8: HANDLE MISSING VALUES
    # --------------------------------------------------

    missing_before = int(
        cleaned_df.isnull().sum().sum()
    )

    cleaned_df = handle_missing_values(
        cleaned_df,
        strategy=missing_strategy
    )

    missing_after = int(
        cleaned_df.isnull().sum().sum()
    )

    report["missing_values_handled"] = (
        missing_before - missing_after
    )

    # --------------------------------------------------
    # STEP 9: CAPTURE FINAL STATISTICS
    # --------------------------------------------------

    report["final_rows"] = len(cleaned_df)

    report["final_columns"] = len(cleaned_df.columns)

    # --------------------------------------------------
    # STEP 10: RETURN RESULTS
    # --------------------------------------------------

    return cleaned_df, report