# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

rssfixer is a Python command-line tool that generates RSS/Atom feeds for WordPress blogs and other sites that don't provide their own feeds. It uses BeautifulSoup for HTML parsing and feedgen for RSS/Atom generation.

## Development Commands

### Setup and Installation
```bash
# Create virtual environment and install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Code Quality and Testing
```bash
# Format and lint with Ruff (includes security checks)
uv run ruff format .
uv run ruff check .

# Auto-fix issues where possible
uv run ruff check --fix .

# Run tests with coverage
uv run coverage run -m pytest
uv run coverage report -m

# Run all pre-commit hooks
uv run pre-commit run --all-files
```

### Running the Tool
```bash
# Run via uv
uv run rssfixer --help

# Run tests
uv run pytest src/tests/
```

### Building and Publishing
```bash
# Build package
uv build

# Publish to PyPI
uv publish
```

## Code Architecture

### Core Structure
- `src/rssfixer/rss.py` - Main module containing all RSS generation logic, argument parsing, and web scraping functionality
- `src/rssfixer/__init__.py` - Entry point that imports and calls main()
- `src/tests/` - Comprehensive test suite with pytest

### Key Components
- **Argument Parsing**: Custom argparse actions (`CheckHtmlAction`, `CheckJsonAction`, `CheckReleaseAction`) to validate command-line options
- **Web Scraping**: Four main parsing modes:
  - `--list` - Simple ul-list parsing (default)
  - `--json` - JSON structure parsing
  - `--html` - General HTML element parsing
  - `--release` - Release page parsing for version tracking
- **Feed Generation**: Uses feedgen library to create RSS/Atom feeds

### Configuration Files
- `pyproject.toml` - Project configuration, dependencies, and tool settings (Ruff)
- `.pre-commit-config.yaml` - Pre-commit hooks for code quality
- `development.md` - Detailed development workflow

### Code Quality Standards
- Line length: 120 characters (Ruff configuration)
- Python 3.11+ required
- Ruff handles all linting, formatting, and security checks (includes bandit rules)
- Pre-commit hooks enforce formatting and quality standards

## Testing

Tests are located in `src/tests/` and use pytest. Run with coverage reporting to maintain code quality standards.
