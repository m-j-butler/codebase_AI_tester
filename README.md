# DataFrame Cleaner

## Overview

DataFrame Cleaner is a modular Python toolkit for loading, validating, and preparing pandas DataFrames for analysis and downstream processing. It is designed to grow into a broader library of dataframe cleaning operations, with a focus on reusable, composable utilities for data quality and preparation.

The project currently includes:

- a JSON ingestion and validation layer for converting structured input into pandas DataFrames
- dataframe cleaning utilities for standardising text fields and handling missing values
- a logging module for tracking successful and failed operations
- a command-line entry point for processing JSON datasets
- automated tests covering core validation and cleaning behaviour



## Features

- Convert JSON strings, file paths, dictionaries, and list-like structures into pandas DataFrames
- Validate malformed, empty, or unsupported input data with clear exceptions
- Standardise text content in selected DataFrame columns without affecting non-string columns
- Replace common missing-value markers such as `"N/A"`, `"n/a"`, `"none"`, and empty strings
- Support optional row removal or value filling during cleaning operations
- Run data-processing workflows from the command line with structured logging



## Functions

The core functions are located in `./src/dataframe_cleaner`.

### `json_to_pandas_df`

Converts JSON input from a string, file path, dictionary, or list-like structure into a pandas DataFrame. It validates the payload, rejects unsupported or empty inputs, and raises explicit errors for malformed JSON or invalid structures.

### `str_validate`

Cleans and standardises string-based columns in a DataFrame. It supports trimming whitespace, case transformation, custom missing-value handling, regex-based cleanup, and optional row dropping or replacement strategies for null-like values.



## Utilities

Support utilities are located in `./src/utils`.

### `setup_logger` and `log_operation`

These helpers configure application logging and record operational events in the project log files. They help track successful processing steps and failure conditions during data loading, cleaning, and export workflows.



## Project Structure

```text
.
├── data/
├── docs/
│   ├── STYLE_GUIDE.md
│   └── _TEST_TEMPLATE.py
├── logs/
│   ├── errors/
│   │   └── error.log
│   └── info.log
├── src/
│   ├── dataframe_cleaner/
│   │   ├── __init__.py
│   │   ├── py.typed
│   │   ├── clean_dataframe.py
│   │   ├── json_to_pandas_df.py
│   │   └── str_validate.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── tests/
│   ├── test_data/
│   │   ├── for_statistics/
│   │   │   ├── boolean.json
│   │   │   ├── clean_data.json
│   │   │   ├── clean_data_2.json
│   │   │   ├── edge_case_no_numeric_columns.json
│   │   │   ├── float_precision.json
│   │   │   └── multimodal_data.json
│   │   ├── generic/
│   │   │   ├── clean_dataset.json
│   │   │   ├── empty_dataset.json
│   │   │   ├── mock_dataset.json
│   │   │   └── mock_dataset_2.json
│   │   └── creating_json_from_df.py
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_json_validator.py
│   └── test_str_validate.py
├── CHANGELOG.md
├── dataframe_cleaner_CLI.py         # CLI script for processing JSON input files
├── pyproject.toml                   # Project metadata and pytest config
├── README.md
├── requirements.txt                 # Python dependencies
└── ruff_and_mypy_CLI.py

```



## Requirements

- Python 3.11+
- pandas
- pytest (for development/testing)



## Installation

Clone the repository and create a virtual environment:

```bash
cd codebase_AI_test
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows PowerShell
pip install -r requirements.txt
```

If you are working with the package metadata directly, you can also install it in editable mode:

```bash
pip install -e .
```



## Usage

### Python API

```python
from src.dataframe_cleaner.json_to_pandas_df import json_to_pandas_df
from src.dataframe_cleaner.str_validate import str_validate

raw_json = '[{"name": " Alice ", "city": "LONDON"}, {"name": "BOB", "city": "Paris"}]'
df = json_to_pandas_df(raw_json)
cleaned_df = str_validate(df, columns=["name", "city"], text_case="title")
print(cleaned_df)
```



### Command-line workflow

The project includes a CLI script that loads a dataset in JSON format, cleans the data, and saves it as a CSV output:

```bash
python dataframe_cleaner_CLI.py --input tests/test_data/generic/mock_dataset.json --output data/output.csv
```

Optional logging flags:

```bash
python dataframe_cleaner_CLI.py --input tests/test_data/generic/mock_dataset.json --output data/output.csv -v
python dataframe_cleaner_CLI.py --input tests/test_data/generic/mock_dataset.json --output data/output.csv -s
```

- `-v` / `--verbose`: enables debug-level console output
- `-s` / `--silent`: suppresses console logging



## Logging

The logger is configured in `./src/utils/logger.py` and creates logs in the project root under the `logs` directory.

- General activity log: `./logs/info.log`
- Error log: `./logs/errors/error.log`

The logger writes:

- informational messages for successful operations
- error messages for failed operations
- console output based on the chosen verbosity flags

This makes it easy to diagnose JSON loading, cleaning, and export issues without needing to modify the application code.



## Testing

### Writing unit tests

A template is located at docs/_TEST_TEMPLATE.py

### Running unit tests

Run the full test suite from the project root:

```bash
pytest
```

Run a specific test file:

```bash
pytest tests/test_json_validator.py
pytest tests/test_str_validate.py
```

Run with coverage if desired:

```bash
pytest --cov=src
```



### Custom dataset injection during tests

The project includes a pytest option for passing a custom JSON dataset into tests via the CLI. This is configured in `tests/conftest.py` and allows you to run tests against your own sample data without changing the test code.

The repository includes mock datasets in `tests/test_data`, which can be used as a quick dataset for local testing. This can be amended as the scope of the module grows.


```bash
pytest --custom-dataset tests/test_data/generic/mock_dataset.json
```

The dataset may be a JSON array of records or a single JSON object. When supplied, the fixture loads it into a pandas DataFrame and exposes it to test functions via the `custom_dataframe` fixture.



## Code Quality & Linting

We use a helper script (`ruff_and_mypy_CLI.py`) to run static type checking with **Mypy** alongside linting and formatting diff summaries with **Ruff**.

### Quick Start

Run checks on the default directories (`src/` and `tests/`):

```bash
python ruff_and_mypy_CLI.py
```

### Options & Features
Check Specific Files or Folders: Pass one or more paths as positional arguments.

```bash
python ruff_and_mypy_CLI.py src/my_module.py tests/test_my_module.py
```

Log Output to File: Use the -l or --log flag to save a plain-text, uncoloured copy of the terminal output to tests/logs/<YYYY-MM-DD_HH-MM-SS>_ruff_mypy.txt.

```bash
python ruff_and_mypy_CLI.py --log
```

View help:

```bash
python ruff_and_mypy_CLI.py --help
```

## Notes

The project is designed as a lightweight data-cleaning toolkit and is suitable for small to medium JSON-based data preparation tasks. The codebase is intentionally modular so that validation, cleaning, and logging can be reused independently.
