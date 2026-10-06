# Code Style Guide


## 1. Tooling & Enforcement

We rely on automated tooling to enforce code formatting, linting, and static type checks.
All code must pass these checks before being merged.

- Linter & Formatter: Ruff
- Static Type Checker: Mypy

Run these tools locally from the project root:

```bash

# Format source code
ruff format .

# Check lint rules and apply automatic fixes
ruff check --fix .

# Perform static type checking
mypy .
```


## 2. Formatting & Syntax Rules

### Base Standard:

- PEP 8 compliance: Enforced via Ruff.

- Language: Preference for British English in variable names, comments, and documentation.

- Line Length: Maximum 88 characters (matching Black style defaults).

- Quotes: Double quotes ("...") for strings unless single quotes avoid escaping.


### Comments

Use comments where suitable to break up complex logic.

- Single-line comments: Start with a capital letter and a single space after the hash (e.g., # Calculate offset).

- Multi-line comments: Start each line with a capital letter, end full sentences with a full stop, and use a single space after each hash.


### Whitespace & Blank Lines

Use whitespace and blank lines to break up code blocks to improve readability.

- Imports:
    - Explicit absolute imports grouped into three blocks separated by a single blank line.
	    - Standard library modules
        - Third-party dependencies
        - Local library imports
	- Use two blank lines after the import block before code or top-level initialisations.

- Docstrings:
    - No blank lines immediately after opening or before closing docstring quotes.
	- Use a single blank line between a function/class docstring and the starting code block.

- Control Flow & Variables:
    - Use a single blank line to separate logical code sections, variable assignments, or if/else control flow blocks where it improves readability.

- Functions & Classes:
    - Use two blank lines before and after top-level function and class definitions.
	- Use one blank line between methods within a class.


Example:
```python
"""Example module demonstrating Ruff-compliant formatting and layout rules."""

import os
from typing import Optional

import numpy as np

from my_library.core import ProcessingClient


# Global constants and variable initialisations
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3


def process_payload(raw_data: dict[str, float]) -> Optional[dict[str, float]]:
    """Process incoming data payload and apply scaling.

    Parameters
    ----------
    raw_data :
        Dictionary of raw scores.

    Returns
    -------
    dict of {str : float} or None
        Processed dictionary or None if empty.
    """
    # Check for empty input
    if not raw_data:
        return None

    # Apply scaling transformation to all elements.
    # Scores are doubled before returning to caller.
    scaled_data = {k: v * 2.0 for k, v in raw_data.items()}

    return scaled_data


class DataTransformer:
    """Class demonstrating single blank line spacing between internal methods."""

    def __init__(self, scale_factor: float) -> None:
        self.scale_factor = scale_factor

    def transform(self, value: float) -> float:
        return value * self.scale_factor
```


## 3. Type Annotations (Mypy)

Public APIs:
    - All public classes, methods, and functions must have complete type annotations for parameters and return values.

Explicit Types:
    - Avoid `Any`
	- Prefer specific types, generics, or `Optional[...]` where values can be `None`.

Example:
```python
# Good
def calculate_metrics(values: list[float], scale: float = 1.0) -> list[float]:
    return [v * scale for v in values]

# Bad
def calculate_metrics(values, scale=1.0):
    return [v * scale for v in values]
```


## 4. Docstring Standard (NumPy Style)

Use the NumPy Docstring Standard for all public modules, functions, classes, and methods.

Header Underlines: Section headers (Parameters, Returns, Raises, Examples) must be underlined with hyphens (----------).

Type Omission: Do not repeat parameter types in the docstring text if they are already declared via Python type hints.

Example:
```python
def transform_data(payload: dict[str, float], threshold: float = 0.0) -> dict[str, float]:
    """Filter and normalise payload scores above a threshold.

    Parameters
    ----------
    payload :
        Dictionary mapping item names to numerical scores.
    threshold :
        Minimum score required to retain an item. Defaults to 0.0.

    Returns
    -------
    dict of {str : float}
        Filtered and normalised scores.

    Raises
    ------
    ValueError
        If threshold is negative.
    """
    if threshold < 0.0:
        raise ValueError("Threshold cannot be negative.")

    return {k: v for k, v in payload.items() if v >= threshold}
```


## 5. Naming Conventions

| Entity | Style | Example |
| :--- | :--- | :--- |
| **Modules / Files** | `snake_case` | `data_loader.py` |
| **Functions / Methods** | `snake_case` | `process_record()` |
| **Variables** | `snake_case` | `batch_size` |
| **Classes / Exceptions** | `PascalCase` | `MatrixTransformer`, `ParseError` |
| **Constants** | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES` |
| **Internal Helpers** | `_leading_underscore` | `_validate_buffer()` |


## 6. Error Handling

Prefer raising and catching specific errors (such as built-in exception types or custom domain errors) rather than using generic Exception or bare except: clauses.

Example
```python
# Good
try:
    value = float(raw_input)
except ValueError as err:
    raise ValueError(f"Invalid numerical input: {raw_input}") from err

# Bad
try:
    value = float(raw_input)
except:
    print("An error occurred")
```


## 7. Testing

All code contributions must be accompanied by unit tests written using Pytest.

### General Guidelines

Framework:
    - Use `pytest` for running and writing tests.

Coverage:
    - Aim for high unit test coverage across all public functions, classes, and CLI entry points.

Naming Conventions:
    - Test files must be named `test_<module_name>.py`.
    - Test functions must start with `test_` (e.g., `test_json_to_pandas_df_valid()`).
	
Test Isolation:
    - Tests must be deterministic and isolated; avoid relying on persistent external state or real external files unless using fixtures.

Fixtures & Parameterisation:
    - Use `@pytest.fixture` for reusable setup objects and `@pytest.mark.parametrize` to test multiple input/output permutations cleanly.

Example:
```python
"""Module docstring describing test scope."""

import pytest

from my_library.module import target_function


@pytest.fixture
def resource_fixture():
    # Setup
    resource = {"key": "value"}
    yield resource
    # Teardown (if needed)


def test_happy_path(resource_fixture):
    """Verify standard operational success."""
    result = target_function(resource_fixture)
    assert result is True


def test_error_handling():
    """Verify explicit error handling behavior."""
    with pytest.raises(ValueError):
        target_function(invalid_input=True)


@pytest.mark.parametrize("input_val, expected", [(1, 2), (3, 6)])
def test_parameterised_inputs(input_val, expected):
    """Verify function output across multiple input permutations."""
    assert target_function(input_val) == expected
```

### Testing Code with Logging

Avoid Persistent Logs:
    - Unit tests must not write permanent files to disk or pollute the standard `logs/` directory.
 
Use `caplog` for Assertions:
    - Use `pytest`'s built-in `caplog` fixture to inspect logged messages and levels without reading log files.
