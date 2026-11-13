import pandas as pd
import pytest


# Fixture 1: Provide a sample DataFrame for testing
@pytest.fixture
def sample_dataframe():

    # Create a reusable DataFrame containing duplicate and missing values.
    df = pd.DataFrame({
        "Name": ["Aamir", "Rahul", "Sana", "Aamir"],
        "Age": [32, 28, None, 32],
        "City": ["Araria", "Delhi", "Patna", "Araria"]
    })

    return df