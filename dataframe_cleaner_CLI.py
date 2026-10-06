"""
Main application CLI for the Data Cleaner library.
"""

import argparse
from pathlib import Path
from src.dataframe_cleaner import json_to_pandas_df
from src.dataframe_cleaner.clean_dataframe import clean_dataframe
from src.utils.logger import setup_logger, log_operation


def parse_args():
    parser = argparse.ArgumentParser(
        description="Load and clean JSON datasets."
    )
    
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the input JSON file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/output.csv",
        help="Path where the cleaned CSV should be saved.",
    )
    
    # CLI flags for logging control
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--silent", action="store_true", help="Suppress console log output."
    )
    group.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose debug logs."
    )

    return parser.parse_args()


def main():
    args = parse_args()
    logger = setup_logger(silent=args.silent, verbose=args.verbose)
    
    input_path = Path(args.input)
    output_path = Path(args.output)

    # Step 1: Load JSON to DataFrame
    try:
        logger.info(f"Processing input file: {input_path}")
        df = json_to_pandas_df(input_path)
        log_operation("Load JSON File", success=True, details=f"Loaded {len(df)} rows")
    except Exception as e:
        log_operation("Load JSON File", success=False, details=str(e))
        return  # Exit early if loading fails

    # Step 2: Clean the Dataset
    try:
        cleaned_df = clean_dataframe(df)
        log_operation("Clean Dataset", success=True, details=f"Retained {len(cleaned_df)} rows")
    except Exception as e:
        log_operation("Clean Dataset", success=False, details=str(e))
        return

    # Step 3: Save the Output
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned_df.to_csv(output_path, index=False)
        log_operation("Save Output CSV", success=True, details=f"Saved to {output_path}")
    except Exception as e:
        log_operation("Save Output CSV", success=False, details=str(e))


if __name__ == "__main__":
    main()