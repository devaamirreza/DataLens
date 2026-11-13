import pandas as pd


# --------------------------------------------------
# 1. REMOVE DUPLICATES
# --------------------------------------------------

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows without modifying the original DataFrame.
    """

    cleaned_df = df.drop_duplicates()

    return cleaned_df


# --------------------------------------------------
# 2. HANDLE MISSING VALUES
# --------------------------------------------------

def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop"
) -> pd.DataFrame:
    """
    Handle missing values using drop, mean or median strategies.
    """

    # Preserve the original dataset.
    cleaned_df = df.copy()

    if strategy == "drop":

        # Remove rows containing missing values.
        cleaned_df = cleaned_df.dropna()

    elif strategy == "mean":

        # Identify numerical columns.
        numerical_columns = cleaned_df.select_dtypes(
            include="number"
        ).columns

        # Replace missing numerical values with column means.
        cleaned_df[numerical_columns] = cleaned_df[
            numerical_columns
        ].fillna(
            cleaned_df[numerical_columns].mean()
        )

    elif strategy == "median":

        # Identify numerical columns.
        numerical_columns = cleaned_df.select_dtypes(
            include="number"
        ).columns

        # Replace missing numerical values with column medians.
        cleaned_df[numerical_columns] = cleaned_df[
            numerical_columns
        ].fillna(
            cleaned_df[numerical_columns].median()
        )

    else:

        raise ValueError(
            f"Unsupported strategy: {strategy}. "
            "Choose drop, mean or median."
        )

    return cleaned_df


# --------------------------------------------------
# 3. DATETIME CONVERSION HELPER
# --------------------------------------------------

def convert_datetime(
    series: pd.Series,
    column: str,
    date_format: str = "auto"
) -> pd.Series:
    """
    Convert a Series into datetime using a selected date format.

    Supported formats:
        DD-MM-YYYY
        MM-DD-YYYY
        YYYY-MM-DD
        auto

    Auto mode uses mixed-format parsing with dayfirst=True.
    """

    # Map user-friendly format names to Pandas formats.
    format_mapping = {
        "DD-MM-YYYY": "%d-%m-%Y",
        "MM-DD-YYYY": "%m-%d-%Y",
        "YYYY-MM-DD": "%Y-%m-%d"
    }

    try:

        if date_format == "auto":

            # Infer individual date formats.
            # dayfirst=True prioritizes day-month-year interpretation
            # when the date is ambiguous.
            converted_series = pd.to_datetime(
                series,
                format="mixed",
                dayfirst=True,
                errors="raise"
            )

        elif date_format in format_mapping:

            # Apply the explicitly selected date format.
            converted_series = pd.to_datetime(
                series,
                format=format_mapping[date_format],
                errors="raise"
            )

        else:

            raise ValueError(
                f"Unsupported date format: {date_format}. "
                "Choose DD-MM-YYYY, MM-DD-YYYY, "
                "YYYY-MM-DD or auto."
            )

        return converted_series

    except (ValueError, TypeError) as error:

        raise ValueError(
            f"Datetime conversion failed for column '{column}'. "
            f"Selected format: {date_format}. "
            f"Please verify the date values. Details: {error}"
        ) from error


# --------------------------------------------------
# 4. DATA TYPE CONVERSION
# --------------------------------------------------

def convert_data_types(
    df: pd.DataFrame,
    conversions: dict,
    datetime_formats: dict | None = None
) -> pd.DataFrame:
    """
    Convert specified DataFrame columns into requested data types.

    Parameters:
        df:
            Original DataFrame.

        conversions:
            Dictionary containing column names and target types.

            Example:
                {
                    "Age": "int",
                    "Salary": "float",
                    "Joining_Date": "datetime"
                }

        datetime_formats:
            Optional dictionary containing date formats
            for datetime columns.

            Example:
                {
                    "Joining_Date": "DD-MM-YYYY"
                }

            Supported:
                DD-MM-YYYY
                MM-DD-YYYY
                YYYY-MM-DD
                auto

    Returns:
        pd.DataFrame: DataFrame with converted column types.
    """

    # Create a copy to preserve the original dataset.
    cleaned_df = df.copy()

    # Use an empty dictionary if no formats were provided.
    datetime_formats = datetime_formats or {}

    for column, target_type in conversions.items():

        # Check whether the requested column exists.
        if column not in cleaned_df.columns:

            raise ValueError(
                f"Column '{column}' does not exist."
            )

        # --------------------------------------------------
        # INTEGER CONVERSION
        # --------------------------------------------------

        if target_type == "int":

            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="raise"
            ).astype("Int64")

        # --------------------------------------------------
        # FLOAT CONVERSION
        # --------------------------------------------------

        elif target_type == "float":

            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="raise"
            )

        # --------------------------------------------------
        # STRING CONVERSION
        # --------------------------------------------------

        elif target_type == "str":

            cleaned_df[column] = cleaned_df[
                column
            ].astype("string")

        # --------------------------------------------------
        # DATETIME CONVERSION
        # --------------------------------------------------

        elif target_type == "datetime":

            # Get the selected format for this column.
            # Default to automatic detection.
            date_format = datetime_formats.get(
                column,
                "auto"
            )

            cleaned_df[column] = convert_datetime(
                series=cleaned_df[column],
                column=column,
                date_format=date_format
            )

        # --------------------------------------------------
        # UNSUPPORTED CONVERSION
        # --------------------------------------------------

        else:

            raise ValueError(
                f"Unsupported data type: {target_type}"
            )

    return cleaned_df