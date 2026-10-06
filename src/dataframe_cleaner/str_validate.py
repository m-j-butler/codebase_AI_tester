"""Utilities for cleaning and standardizing string columns in pandas DataFrames.

This module provides helpers for trimming whitespace, replacing missing-like
values, removing unwanted characters, and standardizing text case.
"""

import numpy as np
import pandas as pd


def str_validate(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    strip_whitespace: bool = True,
    text_case: str | None = None,
    na_values: list[str] | None = None,
    missing_strategy: str = "keep",
    fill_value: str = "Missing",
    regex_clean: str | None = None,
) -> pd.DataFrame:

    """Clean and standardise string columns in a pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to clean.
    columns : list[str] | None, default None
        Specific columns to clean. If None, all object/string columns are used.
    strip_whitespace : bool, default True
        Remove leading and trailing whitespace from string values.
    text_case : {'lower', 'upper', 'title', 'capitalize', None}, default None
        Transform the text case after cleaning.
    na_values : list[str] | None, default None
        Additional values to treat as missing, such as ['N/A', 'null', 'none'].
    missing_strategy : {'keep', 'fill', 'drop'}, default 'keep'
        How to handle missing values after cleaning.
    fill_value : str, default 'Missing'
        Replacement value used when missing_strategy='fill'.
    regex_clean : str | None, default None
        Regex pattern for removing unwanted characters from strings.

    Returns
    -------
    pd.DataFrame
        A cleaned copy of the input DataFrame.
    """


    valid_cases = {"lower", "upper", "title", "capitalize", None}
    valid_missing_strategies = {"keep", "fill", "drop"}

    if text_case not in valid_cases:
        raise ValueError(
            "text_case must be one of {'lower', 'upper', 'title', 'capitalize', None}."
        )

    if missing_strategy not in valid_missing_strategies:
        raise ValueError(
            "missing_strategy must be one of {'keep', 'fill', 'drop'}."
        )

    # Identify target string columns if not explicitly provided
    if columns is None:
        columns = df.select_dtypes(
            include=["object", "string"]
        ).columns.tolist()

    if not columns:
        return df.copy()

    missing_columns = [col for col in columns if col not in df.columns]
    if missing_columns:
        raise ValueError(
            "The following columns were not found in the DataFrame: "
            + ", ".join(map(str, missing_columns))
        )

    non_string_columns = []
    for col in columns:
        series = df[col]
        if not (
            pd.api.types.is_string_dtype(series.dtype)
            or pd.api.types.is_object_dtype(series.dtype)
        ):
            non_string_columns.append(col)
            continue

        non_null_values = series.dropna()
        if len(non_null_values) > 0 and not non_null_values.map(lambda x: isinstance(x, str)).all():
            non_string_columns.append(col)

    if non_string_columns:
        raise TypeError(
            "The following columns are not valid string columns and may contain mixed or non-string values: "
            + ", ".join(map(str, non_string_columns))
        )

    cleaned_df = df.copy()

    # Default common bad string representations if not specified
    if na_values is None:
        na_values = ["", " ", "NA", "N/A", "n/a", "null", "NULL", "none", "None"]

    for col in columns:
        # Convert column to pandas StringDtype to safely perform string vectorised operations
        series = cleaned_df[col].astype("string")

        # Trim whitespace
        if strip_whitespace:
            series = series.str.strip()

        # Handle specific missing string values
        if na_values:
            series = series.replace(na_values, np.nan)

        # Regex character removal
        if regex_clean:
            series = series.str.replace(regex_clean, "", regex=True)

        # Case standardization
        if text_case == "lower":
            series = series.str.lower()
        elif text_case == "upper":
            series = series.str.upper()
        elif text_case == "title":
            series = series.str.title()
        elif text_case == "capitalize":
            series = series.str.capitalize()

        cleaned_df[col] = series

    # Apply missing value strategy across selected target columns
    if missing_strategy == "drop":
        cleaned_df = cleaned_df.dropna(subset=columns)
    elif missing_strategy == "fill":
        cleaned_df[columns] = cleaned_df[columns].fillna(fill_value)

    return cleaned_df