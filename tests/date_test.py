import pandas as pd
import pytest

from datalens.cleaning import convert_datetime
from datalens.pipeline import clean_dataset


# --------------------------------------------------
# TEST 1: DD-MM-YYYY FORMAT
# --------------------------------------------------

def test_convert_datetime_dd_mm_yyyy():

    series = pd.Series([
        "28-07-2019",
        "15-08-2020"
    ])

    result = convert_datetime(
        series=series,
        column="Join_Date",
        date_format="DD-MM-YYYY"
    )

    assert pd.api.types.is_datetime64_any_dtype(result)

    assert result.iloc[0] == pd.Timestamp("2019-07-28")

    assert result.iloc[1] == pd.Timestamp("2020-08-15")


# --------------------------------------------------
# TEST 2: MM-DD-YYYY FORMAT
# --------------------------------------------------

def test_convert_datetime_mm_dd_yyyy():

    series = pd.Series([
        "07-28-2019",
        "08-15-2020"
    ])

    result = convert_datetime(
        series=series,
        column="Join_Date",
        date_format="MM-DD-YYYY"
    )

    assert pd.api.types.is_datetime64_any_dtype(result)

    assert result.iloc[0] == pd.Timestamp("2019-07-28")

    assert result.iloc[1] == pd.Timestamp("2020-08-15")


# --------------------------------------------------
# TEST 3: YYYY-MM-DD FORMAT
# --------------------------------------------------

def test_convert_datetime_yyyy_mm_dd():

    series = pd.Series([
        "2019-07-28",
        "2020-08-15"
    ])

    result = convert_datetime(
        series=series,
        column="Join_Date",
        date_format="YYYY-MM-DD"
    )

    assert pd.api.types.is_datetime64_any_dtype(result)

    assert result.iloc[0] == pd.Timestamp("2019-07-28")

    assert result.iloc[1] == pd.Timestamp("2020-08-15")


# --------------------------------------------------
# TEST 4: AUTOMATIC DATE FORMAT DETECTION
# --------------------------------------------------

def test_convert_datetime_auto():

    series = pd.Series([
        "28-07-2019",
        "15-08-2020"
    ])

    result = convert_datetime(
        series=series,
        column="Join_Date",
        date_format="auto"
    )

    assert pd.api.types.is_datetime64_any_dtype(result)

    assert result.iloc[0] == pd.Timestamp("2019-07-28")

    assert result.iloc[1] == pd.Timestamp("2020-08-15")


# --------------------------------------------------
# TEST 5: INVALID DATE VALUES
# --------------------------------------------------

def test_convert_datetime_invalid_values():

    series = pd.Series([
        "28-07-2019",
        "invalid-date"
    ])

    with pytest.raises(
        ValueError,
        match="Datetime conversion failed"
    ):

        convert_datetime(
            series=series,
            column="Join_Date",
            date_format="DD-MM-YYYY"
        )


# --------------------------------------------------
# TEST 6: UNSUPPORTED DATETIME FORMAT
# --------------------------------------------------

def test_convert_datetime_with_unsupported_format():

    series = pd.Series([
        "28-07-2019"
    ])

    with pytest.raises(
        ValueError,
        match="Datetime conversion failed"
    ):

        convert_datetime(
            series=series,
            column="Join_Date",
            date_format="DD/MM/YYYY"
        )


# --------------------------------------------------
# TEST 7: ORIGINAL DATAFRAME PRESERVATION
# --------------------------------------------------

def test_datetime_conversion_preserves_original_dataframe():

    df = pd.DataFrame({
        "Join_Date": [
            "28-07-2019",
            "15-08-2020"
        ]
    })

    original_df = df.copy()

    cleaned_df, report = clean_dataset(
        df,
        remove_duplicate_rows=False,
        missing_strategy="drop",
        conversions={
            "Join_Date": "datetime"
        },
        datetime_formats={
            "Join_Date": "DD-MM-YYYY"
        }
    )

    # Original DataFrame should remain unchanged.
    pd.testing.assert_frame_equal(df, original_df)

    # Cleaned DataFrame should contain datetime values.
    assert pd.api.types.is_datetime64_any_dtype(
        cleaned_df["Join_Date"]
    )

    assert report["final_rows"] == 2


# --------------------------------------------------
# TEST 8: MISSING DATETIME VALUES
# --------------------------------------------------

def test_datetime_conversion_with_missing_values():

    df = pd.DataFrame({
        "Join_Date": [
            "28-07-2019",
            None,
            "15-08-2020"
        ]
    })

    cleaned_df, report = clean_dataset(
        df,
        remove_duplicate_rows=False,
        missing_strategy="mean",
        conversions={
            "Join_Date": "datetime"
        },
        datetime_formats={
            "Join_Date": "DD-MM-YYYY"
        }
    )

    # Datetime column should retain its missing value.
    assert cleaned_df["Join_Date"].isnull().sum() == 1

    assert report["final_rows"] == 3


# --------------------------------------------------
# TEST 9: DATETIME FORMATS WITHOUT CONVERSIONS
# --------------------------------------------------

def test_datetime_formats_without_conversions():

    df = pd.DataFrame({
        "Join_Date": [
            "28-07-2019"
        ]
    })

    with pytest.raises(
        ValueError,
        match="Datetime formats require conversion requests"
    ):

        clean_dataset(
            df,
            datetime_formats={
                "Join_Date": "DD-MM-YYYY"
            }
        )


# --------------------------------------------------
# TEST 10: FORMAT FOR A COLUMN NOT IN CONVERSIONS
# --------------------------------------------------

def test_datetime_format_for_unconverted_column():

    df = pd.DataFrame({
        "Join_Date": [
            "28-07-2019"
        ],
        "Age": [
            30
        ]
    })

    with pytest.raises(
        ValueError,
        match="no conversion was requested"
    ):

        clean_dataset(
            df,
            conversions={
                "Age": "int"
            },
            datetime_formats={
                "Join_Date": "DD-MM-YYYY"
            }
        )


# --------------------------------------------------
# TEST 11: FORMAT FOR A NON-DATETIME COLUMN
# --------------------------------------------------

def test_datetime_format_for_non_datetime_column():

    df = pd.DataFrame({
        "Join_Date": [
            "28-07-2019"
        ]
    })

    with pytest.raises(
        ValueError,
        match="Datetime format can only be configured"
    ):

        clean_dataset(
            df,
            conversions={
                "Join_Date": "str"
            },
            datetime_formats={
                "Join_Date": "DD-MM-YYYY"
            }
        )

# --------------------------------------------------
# TEST 12: PIPELINE REJECTS UNSUPPORTED DATETIME FORMAT
# --------------------------------------------------

def test_pipeline_rejects_unsupported_datetime_format():

    df = pd.DataFrame({
        "Join_Date": [
            "28-07-2019",
            "15-08-2020"
        ]
    })

    with pytest.raises(
        ValueError,
        match="Unsupported datetime format"
    ):

        clean_dataset(
            df,
            conversions={
                "Join_Date": "datetime"
            },
            datetime_formats={
                "Join_Date": "DD/MM/YYYY"
            }
        )