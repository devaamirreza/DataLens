import pandas as pd
import pytest

from pandas.testing import assert_frame_equal

from datalens.cleaning import (
    remove_duplicates,
    handle_missing_values
)


# Test 1: Duplicate removal
def test_remove_duplicates():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Aamir"],
        "Age": [32, 28, 32]
    })

    cleaned_df = remove_duplicates(df)

    assert len(cleaned_df) == 2
    assert cleaned_df.duplicated().sum() == 0


# Test 2: Original DataFrame preservation
def test_original_dataframe_unchanged():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Aamir"],
        "Age": [32, 28, 32]
    })

    original_df = df.copy()

    remove_duplicates(df)

    assert_frame_equal(df, original_df)


# Test 3: Drop missing values
def test_handle_missing_values_drop():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Sana"],
        "Age": [32, 28, None]
    })

    cleaned_df = handle_missing_values(df, strategy="drop")

    assert len(cleaned_df) == 2
    assert cleaned_df.isnull().sum().sum() == 0


# Test 4: Mean imputation
def test_handle_missing_values_mean():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Sana"],
        "Age": [32, 28, None]
    })

    cleaned_df = handle_missing_values(df, strategy="mean")

    assert cleaned_df["Age"].isnull().sum() == 0
    assert cleaned_df.loc[2, "Age"] == 30


# Test 5: Median imputation
def test_handle_missing_values_median():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Sana", "Zara"],
        "Age": [28, 32, 35, None]
    })

    cleaned_df = handle_missing_values(df, strategy="median")

    assert cleaned_df["Age"].isnull().sum() == 0
    assert cleaned_df.loc[3, "Age"] == 32


# Test 6: Unsupported strategy
def test_invalid_missing_strategy():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul"],
        "Age": [32, 28]
    })

    with pytest.raises(ValueError):
        handle_missing_values(df, strategy="mode")