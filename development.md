# Development

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
python3 -m twine upload dist/* --repository rssfixer
```
