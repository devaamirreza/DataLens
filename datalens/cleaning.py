import pandas as pd


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicate rows without modifying the original DataFrame.
    """

    cleaned_df = df.drop_duplicates()

    return cleaned_df


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = "drop"
) -> pd.DataFrame:
    """
    Handle missing values using drop, mean or median strategies.
    """

    # Preserve the original dataset
    cleaned_df = df.copy()

    if strategy == "drop":

        # Remove rows containing missing values
        cleaned_df = cleaned_df.dropna()

    elif strategy == "mean":

        # Identify numerical columns
        numerical_columns = cleaned_df.select_dtypes(
            include="number"
        ).columns

        # Replace missing numerical values with column means
        cleaned_df[numerical_columns] = cleaned_df[
            numerical_columns
        ].fillna(
            cleaned_df[numerical_columns].mean()
        )

    elif strategy == "median":

        # Identify numerical columns
        numerical_columns = cleaned_df.select_dtypes(
            include="number"
        ).columns

        # Replace missing numerical values with column medians
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


def convert_data_types(
    df: pd.DataFrame,
    conversions: dict
) -> pd.DataFrame:
    """
    Convert specified DataFrame columns into requested data types.

    Parameters:
        df: Original DataFrame.
        conversions: Dictionary containing column names and target types.

    Example:
        {"Age": "int", "Salary": "float", "Joining_Date": "datetime"}

    Returns:
        pd.DataFrame: DataFrame with converted column types.
    """

    # Create a copy to preserve the original dataset
    cleaned_df = df.copy()

    for column, target_type in conversions.items():

        # Check whether the requested column exists
        if column not in cleaned_df.columns:
            raise ValueError(f"Column '{column}' does not exist.")

        # Convert column based on requested data type
        if target_type == "int":

            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="raise"
            ).astype("Int64")

        elif target_type == "float":

            cleaned_df[column] = pd.to_numeric(
                cleaned_df[column],
                errors="raise"
            )

        elif target_type == "str":

            cleaned_df[column] = cleaned_df[column].astype("string")

        elif target_type == "datetime":

            cleaned_df[column] = pd.to_datetime(
                cleaned_df[column],
                errors="raise"
            )

        else:
            raise ValueError(
                f"Unsupported data type: {target_type}"
            )

    return cleaned_df