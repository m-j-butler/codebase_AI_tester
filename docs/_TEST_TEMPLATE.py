"""[Module Name] Test Suite.

Quick-reference template for test layout, fixtures, parametrised tests,
edge cases, and running checks against external datasets via CLI.

Usage:
    pytest tests/test_example.py
    pytest tests/test_example.py --dataset=path/to/data.csv
"""

from pathlib import Path
import pytest

# TODO: Import target module/function
# from your_package.module import target_function


# ==============================================================================
# 1. FIXTURES (Reusable Mock Data & CLI Datasets)
# ==============================================================================

@pytest.fixture
def sample_data() -> dict[str, str]:
    """Provides reusable mock data for standard unit tests."""
    return {"name": "  Alice  ", "city": "London"}


@pytest.fixture
def external_dataset(request: pytest.FixtureRequest) -> Path | None:
    """Retrieves an external dataset path if passed via CLI (`--dataset=<path>`)."""
    cli_path = request.config.getoption("--dataset", default=None)
    return Path(cli_path) if cli_path else None


# ==============================================================================
# 2. CORE BEHAVIOUR (Standard Assertions)
# ==============================================================================

def test_basic_behaviour(sample_data: dict[str, str]) -> None:
    """Verify standard functionality under default conditions."""
    result = sample_data["name"].strip()
    assert result == "Alice"


# ==============================================================================
# 3. PARAMETRISED TESTS (Testing Multiple Inputs)
# ==============================================================================

@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("  hello  ", "hello"),
        ("WORLD", "WORLD"),
    ],
)
def test_input_variations(input_val: str, expected: str) -> None:
    """Test multiple input/output pairs cleanly."""
    assert input_val.strip() == expected


# ==============================================================================
# 4. EXCEPTION & ERROR HANDLING
# ==============================================================================

def test_invalid_inputs_raise_errors() -> None:
    """Verify that invalid arguments raise expected exceptions."""
    with pytest.raises(TypeError, match="string required"):
        raise TypeError("string required")


# ==============================================================================
# 5. EDGE CASES & CONDITIONAL SKIPPING
# ==============================================================================

def test_empty_or_edge_case_inputs() -> None:
    """Verify graceful handling of edge cases (e.g., empty strings or nulls)."""
    assert "".strip() == ""


def test_conditional_feature_skip(sample_data: dict[str, str]) -> None:
    """Demonstrates dynamic test skipping when optional prerequisites are missing."""
    if "status" not in sample_data:
        pytest.skip("Required key 'status' missing from fixture.")

    assert sample_data["status"] == "active"


# ==============================================================================
# 6. EXTERNAL DATASET TESTING (CLI Option Handling)
# ==============================================================================

def test_external_dataset_pipeline(external_dataset: Path | None) -> None:
    """Runs validation against a custom dataset file supplied at runtime."""
    if external_dataset is None:
        pytest.skip("No dataset provided. Pass '--dataset=path/to/file' to run.")

    if not external_dataset.exists():
        pytest.fail(f"Dataset path does not exist: {external_dataset}")

    # TODO: Load dataset and run assertions
    # df = pd.read_csv(external_dataset)
    # assert not df.empty
    assert external_dataset.is_file()