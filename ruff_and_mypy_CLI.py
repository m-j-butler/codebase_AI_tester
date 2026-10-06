#!/usr/bin/env python3
"""Run code quality checks using mypy and ruff.

This script executes static type checking (mypy) and linting/formatting checks
(ruff) on specified files or directories, printing coloured results to stdout and
optionally logging plain text results to a file with a timestamped filename.
"""

import argparse
from datetime import datetime
import os
from pathlib import Path
import re
import subprocess
import sys

# Define the log directory and timestamped output file
LOG_DIR = Path("tests/logs")
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = LOG_DIR / f"{timestamp}_ruff_mypy.txt"

# Regex pattern to strip ANSI colour codes for plain-text log files
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

# ANSI colour constants
GREEN = "\033[32m"
RED = "\033[31m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


def enable_ansi_colours() -> None:
    """Enable ANSI escape sequence processing on Windows Command Prompt."""
    if sys.platform == "win32":
        os.system("")


def colour(text: str, code: str) -> str:
    """Wrap text in an ANSI colour code and append a reset sequence."""
    return f"{code}{text}{RESET}"


def run_ruff_format_summary(targets: list[str]) -> str:
    """Run ruff format --diff on targets and calculate added/deleted line counts per file."""
    cmd = [sys.executable, "-m", "ruff", "format", "--diff", *targets]
    result = subprocess.run(cmd, capture_output=True, text=True)

    files: dict[str, dict[str, int]] = {}
    current_file = None

    for line in result.stdout.splitlines():
        if line.startswith("+++ "):
            parts = line.split()
            current_file = parts[1] if len(parts) > 1 else line[4:]
            files[current_file] = {"+": 0, "-": 0}
        elif current_file and line.startswith("+") and not line.startswith("+++"):
            files[current_file]["+"] += 1
        elif current_file and line.startswith("-") and not line.startswith("---"):
            files[current_file]["-"] += 1

    if not files:
        return "No formatting changes required.\n"

    output_lines = []
    for path, counts in files.items():
        added = colour(f"+{counts['+']}", GREEN)
        removed = colour(f"-{counts['-']}", RED)
        output_lines.append(f"{added:>15} {removed:<15} {path}")

    return "\n".join(output_lines) + "\n"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run mypy static type checking and ruff linting/formatting checks."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["src", "tests"],
        help="Specific files or directories to check (default: src tests)",
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        help=f"Save output to a timestamped file in {LOG_DIR}",
    )
    return parser.parse_args()


def main() -> None:
    enable_ansi_colours()
    args = parse_args()

    targets: list[str] = args.paths
    save_log: bool = args.log
    output_buffer: list[str] = []

    def log(text: str) -> None:
        """Print text directly to stdout and record it in the output buffer."""
        print(text, end="")
        output_buffer.append(text)

    def header(title: str) -> None:
        """A cyan-highlighted section header."""
        return f"\n\n{colour(f'===== {title} =====', CYAN)}\n\n"

    def run_check(cmd: list[str], env: dict[str, str] | None = None) -> None:
        """Run a subprocess check and log stdout/stderr or a default fallback."""
        res = subprocess.run(cmd, capture_output=True, text=True, env=env)
        out = res.stdout + res.stderr
        log(out if out.strip() else "No issues found.\n")

    # Create environment dict forcing colour emission in captured pipes
    mypy_env = {**os.environ, "MYPY_FORCE_COLOR": "1", "FORCE_COLOR": "1"}

    print(header("STARTING TEST SUITE"))
    log(f"Targets: {', '.join(targets)}\n")

    # 1. Run Mypy Type Checks
    log(header(f"MYPY: {', '.join(targets)}"))
    run_check(
        [sys.executable, "-m", "mypy", "--color-output", *targets],
        env=mypy_env,
    )

    # 2. Run Ruff Linter Summary
    log(header("RUFF: SUMMARY - LINTER"))
    run_check(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            *targets,
            "--statistics",
            "--color",
            "always",
        ]
    )

    # 3. Run Ruff Formatting Summary
    log(header("RUFF: SUMMARY - FORMATTING"))
    log(run_ruff_format_summary(targets))

    # Save plain-text output to log file if requested
    if save_log:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        clean_output = ANSI_ESCAPE.sub("", "".join(output_buffer))
        LOG_FILE.write_text(clean_output, encoding="utf-8")

        print(header("SAVING LOGS"))
        print(f"Output successfully saved to {LOG_FILE}\n")

    print(header("FINISHED TEST SUITE"))


if __name__ == "__main__":
    main()