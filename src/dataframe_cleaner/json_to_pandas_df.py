"""Convert JSON data into a pandas DataFrame."""

import json
from pathlib import Path
from typing import Union
import pandas as pd


class JSONValidationError(ValueError):
    """Raised when JSON cannot be converted into a DataFrame."""


def json_to_pandas_df(json_input: Union[str, Path, dict, list, tuple]) -> pd.DataFrame:
    """Convert JSON input from a file, raw string, or Python object into a DataFrame."""

    # Step 1: Parse input structure
    if isinstance(json_input, (str, Path)):
        if isinstance(json_input, Path):
            if not json_input.is_file():
                raise FileNotFoundError(f"JSON file not found: {json_input}")
            try:
                data = json.loads(json_input.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise JSONValidationError(f"File contains invalid JSON: {exc}") from exc
        else:
            if not json_input.strip():
                raise JSONValidationError("JSON string is empty.")
            try:
                data = json.loads(json_input)
            except json.JSONDecodeError as exc:
                raise JSONValidationError(f"Invalid JSON string: {exc}") from exc

    elif isinstance(json_input, (dict, list, tuple)):
        data = json_input
    else:
        raise JSONValidationError(f"Unsupported input type: {type(json_input).__name__}")

    # Step 2: Validate payload existence
    if data is None:
        raise JSONValidationError("JSON payload is empty or null.")

    # Step 3: Handle empty data structure gracefully
    if not data:
        return pd.DataFrame()

    # Step 4: Convert JSON structure into a pandas DataFrame
    try:
        if isinstance(data, dict):
            try:
                df = pd.DataFrame(data)
            except ValueError:
                df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)
    except Exception as exc:
        raise JSONValidationError(f"Failed to convert JSON structure to DataFrame: {exc}") from exc

    return df