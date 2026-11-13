import pandas as pd

from datalens.profiling import profile_dataset, inspect_data_types


def test_profile_dataset():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Sana", "Aamir"],
        "Age": [32, 28, None, 32],
        "City": ["Araria", "Delhi", "Patna", "Araria"]
    })

    result = profile_dataset(df)

    assert result["total_rows"] == 4
    assert result["total_columns"] == 3
    assert result["missing_values"]["Age"] == 1
    assert result["duplicate_rows"] == 1


def test_inspect_data_types():

    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul"],
        "Age": [32, 28]
    })

    result = inspect_data_types(df)

    assert len(result) == 2
    assert list(result["Column"]) == ["Name", "Age"]
    assert result["Non_Null_Count"].tolist() == [2, 2]