import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a basic profile of a Pandas DataFrame.

    Returns:
        dict: Dataset dimensions, missing values and duplicate count.
    """

    profile = {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }

    return profile


def inspect_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Inspect the data types and completeness of each column.

    Returns:
        pd.DataFrame: Column-level data type information.
    """

    # Create a summary containing information about each column
    inspection = pd.DataFrame({
        "Column": df.columns,
        "Data_Type": df.dtypes.astype(str).values,
        "Non_Null_Count": df.count().values,
        "Missing_Count": df.isnull().sum().values
    })

    # Return the inspection report
    return inspection