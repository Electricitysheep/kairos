# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Docker hardening: the image now binds Streamlit to `0.0.0.0` (dashboard is
  actually reachable), runs as a non-root user, installs non-editable, and is
  slimmer via a `.dockerignore`. README documents `docker build` / `docker run`.
- `.github/dependabot.yml` — weekly pip + github-actions dependency updates.
- `.gitattributes` normalizing line endings to LF across the repo.
- Notifications module: a `Notifier` interface with `ConsoleNotifier`,
  `WebhookNotifier` (Slack / Discord / Telegram / custom), and `MultiNotifier`
  fan-out, plus a `TradeAlert` payload — deliver trading signals anywhere.
- `kairos analyze --webhook <url>` pushes the decision through the notifications
  module (Slack / Discord / Telegram / custom endpoint).
- Data caching layer: an in-memory `TTLCache` plus a `CachedDataProvider`
  wrapper that memoizes `fetch_price_data` / `fetch_market_data` for a TTL —
  implements the previously-declared-but-unused `cache_ttl_seconds` setting.
- Top-level lazy exports: `from kairos import Orchestrator, Strategy, Signal, StrategyContext`
  now work without importing pandas/agents up front (keeps `import kairos` fast).
- `py.typed` marker so downstream users get Kairos' type hints.
- PyPI packaging metadata: trove classifiers, keywords, and project URLs
  (Homepage, Repository, Documentation, Changelog, Bug Tracker).
- `CHANGELOG.md`, `CONTRIBUTING.md`, issue/PR templates, and an MIT `LICENSE` file.

### Removed
- Unused `ta` extra that referenced an undeclared `pandas-ta` dependency
  (indicators are computed by the built-in `kairos.indicators.ta` module).
- Dead `OPENAI_API_KEY` collection in config and the unused `use_finbert` flag /
  "Supports FinBERT" claim in `SentimentAgent` — neither was ever wired up.

### Changed
- Real test coverage: the CLI commands, the HTML report generator, the Yahoo
  Finance and FRED providers, and `__main__` are now unit-tested and removed
  from the coverage `omit` — only the Streamlit dashboard UI stays excluded.
  `cli/app.py` went from ~25% to 80%; the 85% gate is now genuine rather than
  inflated by exclusions.
- Bumped pre-commit hooks (ruff v0.8.6, pre-commit-hooks v5.0.0) so local hooks
  understand the `[tool.ruff.lint]` config.
- Documentation now describes Kairos accurately as a **transparent, rule-based**
  quant agent framework: the 5 agents are deterministic (no LLM), and the
  decision trace records each agent's explicit rule-based rationale.
- `resolve_journal_path()` now honors `KairosConfig.journal_path` instead of
  always returning `~/.kairos/journal.json`.
- Vectorized the buy-and-hold benchmark computation in the walk-forward engine
  (replaces a per-bar Python loop with a single pandas operation).
- Bumped ruff line-length to 120 and applied `ruff format` across the codebase.

### Fixed
- Demo sentiment is now reproducible across processes (was seeded from Python's
  per-process-salted builtin `hash()`, contradicting the reproducibility goal).
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
