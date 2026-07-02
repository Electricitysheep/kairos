# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Top-level lazy exports: `from kairos import Orchestrator, Strategy, Signal, StrategyContext`
  now work without importing pandas/agents up front (keeps `import kairos` fast).
- `py.typed` marker so downstream users get Kairos' type hints.
- `CHANGELOG.md`, `CONTRIBUTING.md`, issue/PR templates, and an MIT `LICENSE` file.

### Changed
- `resolve_journal_path()` now honors `KairosConfig.journal_path` instead of
  always returning `~/.kairos/journal.json`.
- Vectorized the buy-and-hold benchmark computation in the walk-forward engine
  (replaces a per-bar Python loop with a single pandas operation).
- Bumped ruff line-length to 120 and applied `ruff format` across the codebase.

### Fixed
- CI now runs on the `master` branch (previously only `main`, so it never ran).
- Resolved all ruff lint and mypy type errors; renamed `StrategyRegistry.list()`
  to `names()` to stop shadowing the builtin `list`.
- CLI help tests are now resilient to Rich ANSI color codes.

## [0.1.0]

### Added
- Initial release: 5-agent pipeline (Research, Quant, Risk, Sentiment, Executor),
  Walk-Forward backtesting, Bootstrap statistics, strategy plugin system,
  6 built-in strategies, 6 data sources, Alpaca paper/live trading, HTML reports,
  and a Streamlit dashboard.
