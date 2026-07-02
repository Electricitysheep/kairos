# Contributing to Kairos

Thanks for your interest in improving Kairos! Contributions of all sizes are welcome.

## Development setup

Kairos uses [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/Electricitysheep/kairos.git
cd kairos
poetry install
poetry run pytest        # run the test suite
```

Optionally enable the pre-commit hooks:

```bash
poetry run pre-commit install
```

## Before you open a PR

Run the same checks CI runs:

```bash
poetry run ruff check src/            # lint
poetry run mypy src/ --ignore-missing-imports   # type check
poetry run pytest tests/ --cov=kairos --cov-fail-under=80   # tests + coverage
```

- Keep coverage at or above **80%** — add tests for new code.
- Match the existing style (ruff-formatted, 100-char lines, type hints).
- Write a clear, imperative commit message (e.g. `feat: add VWAP strategy`).

## Good first contributions

- **Add a strategy** — subclass `Strategy` in `src/kairos/strategies/`, register it, add a test.
- **Add a data provider** — implement the provider interface in `src/kairos/data/providers/`.
- **Improve docs** — examples, docstrings, or the README.

## Reporting bugs

Open an issue with a minimal reproduction, the command you ran, and the full output. The more precise, the faster it gets fixed.

## Code of conduct

Be respectful and constructive. We're all here to build something useful.
