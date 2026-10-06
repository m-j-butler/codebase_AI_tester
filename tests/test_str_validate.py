"""Tests for dataframe string-cleaning behavior in str_validate.

These tests verify whitespace stripping, casing transforms, regex cleanup,
missing-value handling, and selective processing of string columns.
"""

import numpy as np
import pandas as pd
import pytest

from dataframe_cleaner.str_validate import str_validate


@pytest.fixture
def sample_df():
    """Provides a sample DataFrame containing raw, messy string data."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "name": ["  Alice ", "BOB", "n/a", "Charlie!", "none"],
            "city": ["LONDON", "Manchester ", "", " Bristol ", "LEEDS"],
            "age": [25, 30, 35, 40, 45],
        }
    )


def test_default_cleaning(sample_df):
    """Tests that default cleaning strips whitespace and identifies default NA values."""
    result = str_validate(sample_df)

    # Ensures non-string column 'age' remains unchanged
    assert result["age"].tolist() == [25, 30, 35, 40, 45]

    # Checks whitespace stripping
    assert result["name"].iloc[0] == "Alice"
    assert result["city"].iloc[1] == "Manchester"

    # Checks default missing value handling (na_values converted to NA/NaN, strategy='keep')
    assert pd.isna(result["name"].iloc[2])  # 'n/a'
    assert pd.isna(result["name"].iloc[4])  # 'none'
    assert pd.isna(result["city"].iloc[2])  # ''


def test_specific_columns_only(sample_df):
    """Tests targeting only a single specified string column."""
    result = str_validate(sample_df, columns=["name"])

    # 'name' column should be cleaned
    assert result["name"].iloc[0] == "Alice"

    # 'city' column should remain untouched (leading/trailing spaces preserved)
    assert result["city"].iloc[1] == "Manchester "


def test_case_transformations(sample_df):
    """Tests lower, upper, and title casing options."""
    res_lower = str_validate(sample_df, text_case="lower")
    assert res_lower["name"].iloc[1] == "bob"

    res_upper = str_validate(sample_df, text_case="upper")
    assert res_upper["name"].iloc[0] == "ALICE"

    res_title = str_validate(sample_df, text_case="title")
    assert res_title["city"].iloc[0] == "London"


def test_invalid_text_case_raises_error(sample_df):
    """Rejects unsupported text transformations."""
    with pytest.raises(ValueError, match="text_case"):
        str_validate(sample_df, text_case="camel")


def test_invalid_missing_strategy_raises_error(sample_df):
    """Rejects unsupported missing-value strategies."""
    with pytest.raises(ValueError, match="missing_strategy"):
        str_validate(sample_df, missing_strategy="invalid")


def test_missing_columns_raise_error(sample_df):
    """Fails when a requested column does not exist."""
    with pytest.raises(ValueError, match="not found"):
        str_validate(sample_df, columns=["name", "missing_col"])


def test_non_string_column_raises_error(sample_df):
    """Rejects columns that are not string-like."""
    with pytest.raises(TypeError, match="not valid string columns"):
        str_validate(sample_df, columns=["age"])


def test_regex_cleaning(sample_df):
    """Tests removing non-alphabetic characters using regex."""
    result = str_validate(sample_df, regex_clean=r"[^a-zA-Z\s]")

    # Exclamation mark in 'Charlie!' should be removed
    assert result["name"].iloc[3] == "Charlie"


def test_missing_strategy_fill(sample_df):
    """Tests filling missing/bad values with a default fill value."""
    result = str_validate(
        sample_df,
        missing_strategy="fill",
        fill_value="Unknown",
    )

    assert result["name"].iloc[2] == "Unknown"
    assert result["name"].iloc[4] == "Unknown"
    assert result["city"].iloc[2] == "Unknown"


def test_missing_strategy_drop(sample_df):
    """Tests dropping rows containing missing/bad values."""
    result = str_validate(sample_df, missing_strategy="drop")

    # Rows index 2 and 4 have missing values in target string columns
    assert len(result) == 3
    assert result["id"].tolist() == [1, 2, 4]


def test_custom_na_values(sample_df):
    """Tests overriding or adding custom missing value representations."""
    # Treat 'BOB' as a bad/missing entry
    result = str_validate(
        sample_df,
        na_values=["BOB"],
        missing_strategy="fill",
        fill_value="REDACTED",
    )

    assert result["name"].iloc[1] == "REDACTED"
    # 'n/a' should remain as a string because default na_values were overridden
    assert result["name"].iloc[2] == "n/a"




# --- Piping in a custom dataset ---

from dataframe_cleaner.json_to_pandas_df import json_to_pandas_df


@pytest.fixture
def custom_dataframe(cli_dataset_path) -> pd.DataFrame | None:
    """Loads custom dataset from generic CLI path if provided; returns None otherwise."""
    if cli_dataset_path is None:
        return None
    return json_to_pandas_df(cli_dataset_path)


def _string_columns(df: pd.DataFrame) -> list[str]:
    """Return columns where all non-null values are actual strings."""
    string_cols = []
    for col in df.select_dtypes(include=["object", "string"]).columns:
        non_nulls = df[col].dropna()
        if not non_nulls.empty and all(isinstance(val, str) for val in non_nulls):
            string_cols.append(col)
    return string_cols


def test_custom_dataset_fixture(custom_dataframe):
    """Loads and cleans a custom mock dataset when passed via the pytest CLI."""
    if custom_dataframe is None:
        pytest.skip("No custom dataset provided. Run with --custom-dataset=path/to/file.json")

    if custom_dataframe.empty:
        pytest.xfail("Query: Provided custom dataset is empty.")
        
    string_columns = _string_columns(custom_dataframe)
    assert string_columns, "Expected at least one string-like column in the custom dataset"

    result = str_validate(
        custom_dataframe,
        columns=string_columns,
        missing_strategy="fill",
        fill_value="Missing",
        text_case="title",
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(custom_dataframe)
    assert set(string_columns).issubset(result.columns)


def test_custom_dataset_empty_subset_is_handled(custom_dataframe):
    """An empty slice of a custom dataset should still be accepted by the cleaner."""
    if custom_dataframe is None:
        pytest.skip("No custom dataset provided. Run with --custom-dataset=path/to/file.json")

    string_columns = _string_columns(custom_dataframe)
    if not string_columns:
        pytest.skip("Custom dataset has no string-like columns to validate.")

    empty_df = custom_dataframe[string_columns].iloc[0:0].copy()
    result = str_validate(empty_df, columns=string_columns, missing_strategy="fill", fill_value="Missing")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert set(string_columns).issubset(result.columns)


def test_custom_dataset_all_missing_string_column_is_handled(custom_dataframe):
    """A custom dataset with a fully missing string column should still be processed safely."""
    if custom_dataframe is None:
        pytest.skip("No custom dataset provided. Run with --custom-dataset=path/to/file.json")

    string_columns = _string_columns(custom_dataframe)
    if not string_columns:
        pytest.skip("Custom dataset has no string-like columns to validate.")

    column = string_columns[0]
    all_missing = pd.DataFrame({column: [None, None, None]})
    result = str_validate(all_missing, columns=[column], missing_strategy="fill", fill_value="Missing")

    assert result[column].tolist() == ["Missing", "Missing", "Missing"]