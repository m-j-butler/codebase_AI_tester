"""Tests for JSON-to-DataFrame conversion and input validation."""

import json
from pathlib import Path
import pandas as pd
import pytest

from dataframe_cleaner.json_to_pandas_df import JSONValidationError, json_to_pandas_df


# --- Local Dataset Resolver Fixture ---

@pytest.fixture
def active_df(cli_dataset_path) -> pd.DataFrame:
    """Uses piped CLI dataset if provided; otherwise falls back to local module sample data."""
    if cli_dataset_path is not None:
        df = json_to_pandas_df(cli_dataset_path)
        if df.empty:
            pytest.skip("Piped CLI dataset is empty.")
        return df
    
    # Local fallback sample records for this specific test file
    return pd.DataFrame([{"id": 101, "name": "Alice"}, {"id": 102, "name": "Bob"}])


# --- Core Functionality Tests ---

def test_valid_dataframe_creation(active_df):
    """Runs against piped CLI dataset or local sample fallback."""
    assert isinstance(active_df, pd.DataFrame)
    if active_df.empty:
        pytest.xfail("Query: Provided active dataset is empty.")
    
    assert not active_df.empty


def test_valid_list_of_dicts():
    data = [{"id": 101, "name": "Alice"}, {"id": 102, "name": "Bob"}]
    df = json_to_pandas_df(data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2


def test_valid_scalar_dict():
    data = {"customer_id": "C101", "score": 98.5}
    df = json_to_pandas_df(data)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert list(df.columns) == ["customer_id", "score"]


# --- Edge Case & Exception Tests ---

def test_empty_json_payload_returns_empty_dataframe():
    df = json_to_pandas_df([])
    assert isinstance(df, pd.DataFrame)
    assert df.empty


def test_missing_file_path_raises_error(tmp_path):
    missing_file = tmp_path / "non_existent_data.json"
    with pytest.raises(FileNotFoundError, match="JSON file not found"):
        json_to_pandas_df(missing_file)


def test_empty_json_string_raises_error():
    with pytest.raises(JSONValidationError, match="JSON string is empty"):
        json_to_pandas_df("    ")


def test_malformed_json_file_raises_error(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{invalid_json: true", encoding="utf-8")

    with pytest.raises(JSONValidationError, match="File contains invalid JSON"):
        json_to_pandas_df(bad_file)


def test_unsupported_input_type_raises_error():
    with pytest.raises(JSONValidationError, match="Unsupported input type"):
        json_to_pandas_df(12345)