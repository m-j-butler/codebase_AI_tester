"""Utilities for cleaning a pandas DataFrame.

"""

import numpy as np
import pandas as pd


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    """Cleans DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to clean.

    Returns
    -------
    pd.DataFrame
        A cleaned copy of the input DataFrame.
    """

    cleaned_df = df.copy()

    return cleaned_df