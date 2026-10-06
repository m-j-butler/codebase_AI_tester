# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project documentation and setup notes in the README.
- JSON-to-DataFrame conversion utilities for loading structured data into pandas DataFrames.
- String cleaning and validation utilities for DataFrame columns.
- Logging helpers for operational tracking and error reporting.
- CLI workflow for processing JSON input files and saving cleaned CSV output.
- Pytest fixtures and CLI support for injecting custom datasets during testing.
- Mock dataset files under `data/` for local testing and demonstration.

### Changed
- Refined project structure and documentation to reflect the current module layout.
- Improved testability by separating validation, cleaning, and dataset-injection concerns.

### Fixed
- Improved input validation and error handling for malformed JSON, empty payloads, and unsupported types.
- Ensured logging configuration creates the required directories for log output.

## [0.1.0] - 2026-09-17

### Added
- Initial project scaffold and package configuration.
- DataFrame cleaning utilities for JSON ingestion and string-value validation.
- Core test suite covering validation and cleaning behaviours.
- Basic CLI entry point for dataset processing.
