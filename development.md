# Development

## Test

Do the following tests:

- Make sure tests works in Visual Studio Code
- Run `bandit -r src/rssfixer` to check for security related bugs.
- Check code test coverage: `coverage run -m pytest` and look at the report via `coverage report -m`
- Generate badge for coverage: `coverage-badge -f -q -o resources/coverage.svg`

## Build

Update version number in _pyproject.toml_ before building with:

```bash
python3 -m build
```

## Upload to pypi.org

```bash
python3 -m twine upload dist/* --repository rssfixer
```
