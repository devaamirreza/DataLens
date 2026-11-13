import pandas as pd
import pytest

from datalens.cleaning import convert_data_types


# Test 1: String to integer conversion
def test_convert_string_to_integer():

    df = pd.DataFrame({
        "Age": ["32", "28", "35"]
    })

    result = convert_data_types(df, {"Age": "int"})

    assert str(result["Age"].dtype) == "Int64"
    assert result["Age"].tolist() == [32, 28, 35]


# Test 2: String to float conversion
def test_convert_string_to_float():

    df = pd.DataFrame({
        "Salary": ["50000.50", "60000.75"]
    })

    result = convert_data_types(df, {"Salary": "float"})

    assert result["Salary"].dtype == "float64"
    assert result["Salary"].tolist() == [50000.50, 60000.75]


# Test 3: String to datetime conversion
def test_convert_string_to_datetime():

    df = pd.DataFrame({
        "Joining_Date": ["2024-01-15", "2024-02-10"]
    })

    result = convert_data_types(
        df,
        {"Joining_Date": "datetime"}
    )

    assert pd.api.types.is_datetime64_any_dtype(
        result["Joining_Date"]
    )


# Test 4: Invalid column
def test_invalid_column_conversion():

    df = pd.DataFrame({
        "Age": ["32", "28"]
    })

    with pytest.raises(ValueError):
        convert_data_types(df, {"Salary": "float"})


# Test 5: Invalid conversion type
def test_invalid_conversion_type():

    df = pd.DataFrame({
        "Age": ["32", "28"]
    })

    with pytest.raises(ValueError):
        convert_data_types(df, {"Age": "boolean"})


# Test 6: Invalid data conversion
def test_invalid_data_conversion():

    df = pd.DataFrame({
        "Age": ["32", "unknown"]
    })

    with pytest.raises(ValueError):
        convert_data_types(df, {"Age": "int"})


# Test 7: Original DataFrame preservation
def test_original_dataframe_unchanged():

    df = pd.DataFrame({
        "Age": ["32", "28"]
    })

    original_df = df.copy()

    convert_data_types(df, {"Age": "int"})

    pd.testing.assert_frame_equal(df, original_df)

# Test 8: Convert integer column to string
def test_convert_column_to_string():

    # Create a DataFrame with integer values.
    df = pd.DataFrame({
        "Age": [32, 28, 35]
    })

    # Convert the Age column from integer to string.
    result = convert_data_types(df, {"Age": "str"})

    # Verify that the column data type is string.
    assert str(result["Age"].dtype) == "string"

    # Verify that the values are correctly converted into strings.
    assert result["Age"].tolist() == ["32", "28", "35"]