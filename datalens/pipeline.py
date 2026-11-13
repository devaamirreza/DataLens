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


def clean_dataset(
    df: pd.DataFrame,
    remove_duplicate_rows: bool = True,
    missing_strategy: str = "drop",
    conversions: dict | None = None
) -> tuple[pd.DataFrame, dict]:
    """
    Execute the complete DataLens cleaning pipeline.
    """

    # STEP 1: Validate input dataset
    validate_dataframe(df)

    # STEP 2: Validate cleaning strategy
    validate_missing_strategy(missing_strategy)

    # STEP 3: Validate conversion requests
    if conversions is not None:

        validate_columns(df, conversions)

        validate_conversion_types(conversions)

    # Preserve original dataset
    cleaned_df = df.copy()

    # Initialize cleaning report
    report = {
        "original_rows": len(cleaned_df),
        "original_columns": len(cleaned_df.columns),
        "duplicates_removed": 0,
        "missing_values_handled": 0,
        "final_rows": 0,
        "final_columns": 0
    }

    # STEP 4: Convert data types
    if conversions:

        cleaned_df = convert_data_types(
            cleaned_df,
            conversions
        )

    # STEP 5: Remove duplicates
    if remove_duplicate_rows:

        duplicates_before = int(cleaned_df.duplicated().sum())

        cleaned_df = remove_duplicates(cleaned_df)

        report["duplicates_removed"] = duplicates_before

    # STEP 6: Handle missing values
    missing_before = int(cleaned_df.isnull().sum().sum())

    cleaned_df = handle_missing_values(
        cleaned_df,
        strategy=missing_strategy
    )

    missing_after = int(cleaned_df.isnull().sum().sum())

    report["missing_values_handled"] = (
        missing_before - missing_after
    )

    # STEP 7: Capture final statistics
    report["final_rows"] = len(cleaned_df)
    report["final_columns"] = len(cleaned_df.columns)

    return cleaned_df, report