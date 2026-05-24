# Changelog

## v0.2.0 - 2026-05-24

The 0.1 release shipped a scaffold with seven stubbed `Component`
modules and an empty `AgentBenchmarkSuite.process()` that returned its
own service name. There were no benchmarks. This release deletes that
scaffold and ships the actual fixed benchmark set.

### Added

- 20 bundled tasks across 4 categories (5 each):
  math, code, reasoning, tool_use.
- Standard scorers: `exact_match`, `contains`, `contains_all`,
  `regex_match`, `json_key_equals`.
- `run_suite(agent, tasks=None)` returns a typed `Scorecard` with per-task
  results, per-category aggregates, latency, and pass/fail counts.
- ASCII scorecard renderer via `render_scorecard(scorecard)`.
- CLI: `agent-benchmark-suite run --agent <name> --output report.json`,
  plus `list` and `info` subcommands and a `--category` filter.
- `--agent` resolves both built-in names (`fake_agent`) and arbitrary
  dotted paths (`module.path:callable`).
- 41 tests covering scorers, the suite shape, the runner, the
  scorecard, and the CLI.

### Changed

- License changed from proprietary to MIT.
- Package is now installable via standard `setuptools.build_meta`
  (0.1 referenced a non-existent build backend).
- No runtime dependencies. Removed `fastapi`, `uvicorn`, `anthropic`,
  `openai`, `pydantic`.

### Removed

- `src/core.py` `AgentBenchmarkSuite` god-class and its seven stubbed
  operations.
- `src/api.py` FastAPI surface (the runner does not need an HTTP
  server, and an HTTP API for a CLI-shaped tool is overhead).
- Empty `src/benchmarks/{coding,planning,reasoning,tool_use}.py`
  templates.
- `src/llm.py`, `src/leaderboard.py`, `src/metrics.py`,
  `src/reporter.py`, `src/runner.py`, `src/utils.py`, `src/health.py`.
- `Dockerfile`, `docker-compose.yml`, `config.example.yaml`,
  `.env.example`, `CONTRIBUTING.md` (none were wired to anything real).
- Tests that asserted hardcoded constants like
  `result["service"] == "agent-benchmark-suite"`.

## v0.1.0 - 2026-03-18

- Initial scaffold with stub modules and a placeholder FastAPI surface.
- No real benchmarks; tests asserted hardcoded constants.
