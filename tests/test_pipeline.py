import pandas as pd
import pytest

from pandas.testing import assert_frame_equal

from datalens.pipeline import clean_dataset


# Test 1: Complete cleaning pipeline
def test_complete_cleaning_pipeline():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Sana", "Aamir"],
        "Age": ["32", "28", None, "32"],
        "Salary": ["50000", "60000", "45000", "50000"]
    })

    conversions = {
        "Age": "int",
        "Salary": "float"
    }

    cleaned_df, report = clean_dataset(
        df,
        remove_duplicate_rows=True,
        missing_strategy="mean",
        conversions=conversions
    )

    assert len(cleaned_df) == 3
    assert cleaned_df["Age"].isnull().sum() == 0
    assert cleaned_df.loc[2, "Age"] == 30

    assert report["duplicates_removed"] == 1
    assert report["missing_values_handled"] == 1


# Test 2: Original dataset preservation
def test_pipeline_preserves_original_data():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Aamir"],
        "Age": ["32", "28", "32"]
    })

    original_df = df.copy()

    clean_dataset(
        df,
        conversions={"Age": "int"}
    )

    assert_frame_equal(df, original_df)


# Test 3: Invalid DataFrame
def test_pipeline_rejects_invalid_dataframe():

    with pytest.raises(TypeError):
        clean_dataset(["Aamir", "Rahul"])


# Test 4: Invalid missing-value strategy
def test_pipeline_rejects_invalid_strategy():

    df = pd.DataFrame({
        "Name": ["Aamir"],
        "Age": [32]
    })

    with pytest.raises(ValueError):
        clean_dataset(df, missing_strategy="mode")


# Test 5: Invalid conversion column
def test_pipeline_rejects_invalid_column():

    df = pd.DataFrame({
        "Name": ["Aamir"],
        "Age": [32]
    })

    with pytest.raises(ValueError):
        clean_dataset(
            df,
            conversions={"Salary": "float"}
        )


# Test 6: Invalid conversion data
def test_pipeline_rejects_invalid_conversion():

    df = pd.DataFrame({
        "Age": ["unknown"]
    })

    with pytest.raises(ValueError):
        clean_dataset(
            df,
            conversions={"Age": "int"}
        )