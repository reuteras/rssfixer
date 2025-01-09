# Development

## Setup

Install needed dependencies (only macOS example with brew).

```bash
brew install poetry pre-commit
poetry install --with dev
pre-commit install
pre-commit
```

## Test

Run the following tests and validations and make sure that they all pass before committing. The tests are also run by GitHub Actions and with `pre-commit` before committing.

```bash
black .
ruff .
bandit -r src/rssfixer
coverage run -m pytest
coverage report -m
```

## Build

Update the version number with the help of poetry.

```bash
poetry version patch          # or minor or major
```

```bash
poetry build
```

## Upload to pypi.org

```bash
poetry publish
```

## Update

```bash
poetry update
poetry update --with dev
```
