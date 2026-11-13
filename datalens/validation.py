import pandas as pd


def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate the input DataFrame.

    Checks:
        - Input must be a Pandas DataFrame.
        - Dataset must contain at least one column.
        - Dataset must not be empty.
    """

    # Check whether input is a DataFrame
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a Pandas DataFrame.")

    # Check whether dataset contains columns
    if len(df.columns) == 0:
        raise ValueError("Dataset must contain at least one column.")

    # Check whether dataset contains any rows
    if df.empty:
        raise ValueError("Dataset is empty. Please upload valid data.")


def validate_missing_strategy(strategy: str) -> None:
    """
    Validate the missing-value handling strategy.

    Supported strategies:
        - drop
        - mean
        - median
    """

    allowed_strategies = ["drop", "mean", "median"]

    if strategy not in allowed_strategies:
        raise ValueError(
            f"Invalid strategy '{strategy}'. "
            f"Supported strategies: {allowed_strategies}"
        )


def validate_columns(
    df: pd.DataFrame,
    conversions: dict
) -> None:
    """
    Validate whether requested conversion columns exist.
    """

    for column in conversions:

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' does not exist in the dataset."
            )


def validate_conversion_types(conversions: dict) -> None:
    """
    Validate requested target data types.

    Supported types:
        - int
        - float
        - str
        - datetime
    """

    allowed_types = ["int", "float", "str", "datetime"]

    for column, target_type in conversions.items():

        if target_type not in allowed_types:
            raise ValueError(
                f"Unsupported conversion type '{target_type}' "
                f"for column '{column}'."
            )