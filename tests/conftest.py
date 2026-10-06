"""Generic pytest configuration for CLI dataset injection."""

from pathlib import Path
import pytest


def pytest_addoption(parser):
    """Register generic dataset CLI flags."""
    parser.addoption(
        "--custom-dataset",
        action="append",
        default=None,
        help="Path to a custom JSON file or directory containing JSON files",
    )



def _get_dataset_paths(config) -> list[Path]:
    """Extract and sanitise dataset file paths from config."""
    raw_options = config.getoption("--custom-dataset")
    if not raw_options:
        return []

    candidate_paths = []
    for item in raw_options:
        trimmed = item.strip("[] ")
        for sub_path in trimmed.split(","):
            sanitised = sub_path.strip()
            if not sanitised:
                continue

            candidate_paths.append(Path(sanitised))

    dataset_paths = []
    for path in candidate_paths:
        if path.is_dir():
            # Use path.rglob("*.json") if you want to include subdirectories
            dataset_paths.extend(sorted(p for p in path.glob("*.json") if p.is_file()))
        elif path.is_file():
            dataset_paths.append(path)

    return dataset_paths


def pytest_generate_tests(metafunc):
    """Parametrise cli_dataset_path across test runs if requested by fixture signature."""
    paths = _get_dataset_paths(metafunc.config)
    if "cli_dataset_path" in metafunc.fixturenames:
        if paths:
            metafunc.parametrize("cli_dataset_path", paths, ids=[p.name for p in paths])
        else:
            metafunc.parametrize("cli_dataset_path", [None], ids=["default"])