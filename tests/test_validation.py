import pandas as pd
import pytest

from datalens.validation import (
    validate_dataframe,
    validate_missing_strategy,
    validate_columns,
    validate_conversion_types
)


# Test 1: Valid DataFrame
def test_valid_dataframe():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul"],
        "Age": [32, 28]
    })

    validate_dataframe(df)


# Test 2: Invalid DataFrame type
def test_invalid_dataframe_type():

    with pytest.raises(TypeError):
        validate_dataframe(["Aamir", "Rahul"])


# Test 3: Empty DataFrame
def test_empty_dataframe():

    with pytest.raises(ValueError):
        validate_dataframe(pd.DataFrame())


# Test 4: Valid missing-value strategy
@pytest.mark.parametrize(
    "strategy",
    ["drop", "mean", "median"]
)
def test_valid_missing_strategy(strategy):

    validate_missing_strategy(strategy)


# Test 5: Invalid missing-value strategy
def test_invalid_missing_strategy():

    with pytest.raises(ValueError):
        validate_missing_strategy("mode")


# Test 6: Valid conversion columns
def test_valid_columns():

    df = pd.DataFrame({
        "Name": ["Aamir"],
        "Age": [32]
    })

    validate_columns(df, {"Age": "int"})


# Test 7: Invalid conversion column
def test_invalid_column():

    df = pd.DataFrame({
        "Name": ["Aamir"],
        "Age": [32]
    })

    with pytest.raises(ValueError):
        validate_columns(df, {"Salary": "float"})


# Test 8: Valid conversion types
@pytest.mark.parametrize(
    "target_type",
    ["int", "float", "str", "datetime"]
)
def test_valid_conversion_type(target_type):

    validate_conversion_types({"Age": target_type})


# Test 9: Invalid conversion type
def test_invalid_conversion_type():

    with pytest.raises(ValueError):
        validate_conversion_types({"Age": "boolean"})


# Test 10: Reject a DataFrame without columns
def test_dataframe_without_columns():

    # Create a DataFrame containing 3 rows but no columns.
    df = pd.DataFrame(index=[0, 1, 2])

    # Verify that validation raises a ValueError
    # when the DataFrame has no columns.
    with pytest.raises(
        ValueError,
        match="Dataset must contain at least one column."
    ):
        validate_dataframe(df)

# Test 11: Reject a DataFrame with columns but no rows
def test_dataframe_without_rows():

    # Create a DataFrame with columns but no records.
    df = pd.DataFrame(columns=["Name", "Age"])

    # Verify that validation raises a ValueError
    # when the DataFrame contains no rows.
    with pytest.raises(
        ValueError,
        match="Dataset is empty. Please upload valid data."
    ):
        validate_dataframe(df)