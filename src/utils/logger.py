"""
Logging module for application log configuration, file output, and error tracking.

This module initialises and manages a centralised application logger 
("agent_testbase"). It automatically creates designated log directories and routes
log events to dual log files and configurable console streams.

Features:
    - Dual File Logging: Writes all messages (INFO+) to `logs/info.log` and error-only 
      messages (ERROR+) to `logs/errors/error.log`.
    - CLI Verbosity Control: Supports silent output (-s) or detailed debug logging (-v).
    - Standardised Reporting: Provides the `log_operation()` helper for consistent 
      PASS/FAIL operation tracking.

Usage in Python Code:
    >>> from src.utils.logger import setup_logger, log_operation, logger
    >>> 
    >>> # Initialise logger at CLI entry point
    >>> setup_logger(silent=False, verbose=True)
    >>> 
    >>> # Standard logging
    >>> logger.info("Application started.")
    >>> 
    >>> # Record structured operation status
    >>> log_operation("Data Cleaning", success=True, details="Loaded 30 rows")

Command Line Execution Examples:
    Run main script with default logging (Console: INFO, Files: info.log & error.log):
        $ python <FUNCTION_FILE.py>

    Run with verbose console output (Console: DEBUG):
        $ python <FUNCTION_FILE.py> --verbose

    Run in silent mode (Console: Off, Files: Active):
        $ python <FUNCTION_FILE.py> --silent

    Run with custom input path and verbose logging:
        $ python <FUNCTION_FILE.py> -v --input data/mock_dataset.json
"""

from pathlib import Path
import logging
from typing import Optional

# Define log directories relative to project root
LOG_DIR = Path("logs")
ERROR_LOG_DIR = LOG_DIR / "errors"

# Global logger instance
logger = logging.getLogger("agent_testbase")


def setup_logger(silent: bool = False, verbose: bool = False) -> logging.Logger:
    """Configures file and console logging based on CLI flags.

    Args:
        silent: If True, suppresses all console output.
        verbose: If True, sets console log level to DEBUG (shows extra detail).

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Ensure log directories exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ERROR_LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if function is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter definitions
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d - %(message)s"
    )
    console_format = logging.Formatter("[%(levelname)s] %(message)s")

    # 1. Info Log Handler (Logs EVERYTHING: INFO, WARNING, ERROR)
    info_handler = logging.FileHandler(LOG_DIR / "info.log", encoding="utf-8")
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_format)
    logger.addHandler(info_handler)

    # 2. Error Log Handler (Logs ONLY ERROR and CRITICAL in error folder)
    error_handler = logging.FileHandler(
        ERROR_LOG_DIR / "error.log", encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    logger.addHandler(error_handler)

    # 3. Console Handler (Controlled by CLI flags)
    if not silent:
        console_handler = logging.StreamHandler()
        console_level = logging.DEBUG if verbose else logging.INFO
        console_handler.setLevel(console_level)
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

    return logger


def log_operation(
    operation_name: str, success: bool, details: Optional[str] = None
) -> None:
    """Helper to log operations with an explicit PASS or FAIL status."""
    status = "PASS" if success else "FAIL"
    msg = f"Operation '{operation_name}' -> Status: {status}"
    if details:
        msg += f" | Details: {details}"

    if success:
        logger.info(msg)
    else:
        logger.error(msg)