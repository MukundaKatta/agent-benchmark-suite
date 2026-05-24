# agent-benchmark-suite

A fixed 20-task benchmark suite for AI agents. Run any agent against
the same canonical tasks and get a comparable scorecard.

Landing page: [MukundaKatta.github.io/agent-benchmark-suite](https://MukundaKatta.github.io/agent-benchmark-suite)

- 20 bundled tasks across 4 categories: math, code, reasoning, tool_use
- Standard scorers: exact match, contains, contains-all, regex, JSON-key
- One CLI command, one JSON report, one ASCII scorecard
- Zero runtime dependencies
- MIT licensed

## Why a fixed suite

Most "eval frameworks" hand you primitives and ask you to bring your
own tasks. That makes scores incomparable across agents and across
projects. This package goes the other way: a small, fixed set of tasks
so two agents run against the same questions and produce numbers you
can put side by side.

If you want a generic runner with bring-your-own-tasks, use
[agent-eval-arena](https://github.com/MukundaKatta/agent-eval-arena).

## Install

```bash
pip install -e ".[dev]"
```

## Quick start

The fastest way to see the output is the built-in `fake_agent` that
always answers `n/a`. It will fail every task. That is the point.

```bash
agent-benchmark-suite run --agent fake_agent --output report.json
```

Sample scorecard:

```
============================================================
agent-benchmark-suite scorecard for fake_agent
============================================================

overall score:     0.0% (0/20 tasks passed)
avg latency:       0.0 ms

by category
------------------------------------------------------------
  category         score   pass rate   avg ms
  math               0.0%     0/5         0.0
  code               0.0%     0/5         0.0
  reasoning          0.0%     0/5         0.0
  tool_use           0.0%     0/5         0.0

per task
------------------------------------------------------------
  [  ] math.basic_arith                0.0%      0.0 ms
  [  ] math.percent                    0.0%      0.0 ms
  ...
```

## Using it from Python

```python
from agent_benchmark_suite import run_suite, render_scorecard

def my_agent(prompt: str) -> str:
    # Call your LLM or agent here and return the response string.
    return "..."

scorecard = run_suite(my_agent, agent_name="my-agent")
print(render_scorecard(scorecard))

# JSON-friendly form for storage:
import json
print(json.dumps(scorecard.to_dict(), indent=2))
```

## Plugging in a real agent

The CLI accepts any callable exposed as `module:name`:

```bash
agent-benchmark-suite run --agent myproject.agents:claude_agent --output out.json
```

`myproject/agents.py` just needs:

```python
def claude_agent(prompt: str) -> str:
    return call_claude(prompt)
```

## Running one category at a time

```bash
agent-benchmark-suite run --agent fake_agent --category math
```

Valid values: `math`, `code`, `reasoning`, `tool_use`.

## The scorers

| Helper | Score = 1.0 when |
|---|---|
| `exact_match(expected)` | response equals `expected` (case-insensitive, stripped by default) |
| `contains(needle)` | `needle` appears anywhere in the response |
| `contains_all(needles)` | partial credit, one point per needle, divided by count |
| `regex_match(pattern)` | `re.search` matches |
| `json_key_equals(key, value)` | the first balanced `{...}` parses and `key == value` |

A scorer is any callable returning a float in `[0.0, 1.0]`. You can
write your own and pass it into a custom `Task`.

## Tests

```bash
pytest
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT
