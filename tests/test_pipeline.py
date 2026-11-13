import pandas as pd
import pytest

from pandas.testing import assert_frame_equal

from datalens.pipeline import clean_dataset


# --------------------------------------------------
# TEST 1: COMPLETE CLEANING PIPELINE
# --------------------------------------------------

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

    assert report["original_rows"] == 4

    assert report["final_rows"] == 3


# --------------------------------------------------
# TEST 2: ORIGINAL DATASET PRESERVATION
# --------------------------------------------------

def test_pipeline_preserves_original_data():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Aamir"],
        "Age": ["32", "28", "32"]
    })

    original_df = df.copy()

    clean_dataset(
        df,
        conversions={
            "Age": "int"
        }
    )

    assert_frame_equal(df, original_df)


# --------------------------------------------------
# TEST 3: INVALID DATAFRAME
# --------------------------------------------------

def test_pipeline_rejects_invalid_dataframe():

    with pytest.raises(TypeError):

        clean_dataset([
            "Aamir",
            "Rahul"
        ])


# --------------------------------------------------
# TEST 4: INVALID MISSING-VALUE STRATEGY
# --------------------------------------------------

def test_pipeline_rejects_invalid_strategy():

    df = pd.DataFrame({
        "Name": ["Aamir"],
        "Age": [32]
    })

    with pytest.raises(ValueError):

        clean_dataset(
            df,
            missing_strategy="mode"
        )


# --------------------------------------------------
# TEST 5: INVALID CONVERSION COLUMN
# --------------------------------------------------

def test_pipeline_rejects_invalid_column():

    df = pd.DataFrame({
        "Name": ["Aamir"],
        "Age": [32]
    })

    with pytest.raises(ValueError):

        clean_dataset(
            df,
            conversions={
                "Salary": "float"
            }
        )


# --------------------------------------------------
# TEST 6: INVALID CONVERSION DATA
# --------------------------------------------------

def test_pipeline_rejects_invalid_conversion():

    df = pd.DataFrame({
        "Age": ["unknown"]
    })

    with pytest.raises(ValueError):

        clean_dataset(
            df,
            conversions={
                "Age": "int"
            }
        )


# --------------------------------------------------
# TEST 7: PIPELINE WITHOUT DUPLICATE REMOVAL
# --------------------------------------------------

def test_pipeline_without_duplicate_removal():

    df = pd.DataFrame({
        "Name": ["Aamir", "Aamir", "Rahul"],
        "Age": [30, 30, 28]
    })

    cleaned_df, report = clean_dataset(
        df,
        remove_duplicate_rows=False,
        missing_strategy="drop"
    )

    # All original rows should remain.
    assert len(cleaned_df) == 3

    # No duplicates should have been removed.
    assert report["duplicates_removed"] == 0

    # Validate final statistics.
    assert report["original_rows"] == 3

    assert report["final_rows"] == 3

    assert report["final_columns"] == 2