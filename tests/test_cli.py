"""Tests for the CLI entrypoint."""
import json
import sys
import types

import pytest

from agent_benchmark_suite import cli
from agent_benchmark_suite.cli import fake_agent, main, resolve_agent


def test_fake_agent_returns_na():
    assert fake_agent("anything") == "n/a"


def test_resolve_agent_handles_built_in_name():
    fn = resolve_agent("fake_agent")
    assert fn("ignored") == "n/a"


def test_resolve_agent_rejects_unknown_bare_name():
    with pytest.raises(ValueError):
        resolve_agent("nope")


def test_resolve_agent_handles_dotted_path(monkeypatch):
    module = types.ModuleType("agent_benchmark_suite._test_agent")

    def my_agent(prompt: str) -> str:
        return f"echo: {prompt}"

    module.my_agent = my_agent
    monkeypatch.setitem(sys.modules, "agent_benchmark_suite._test_agent", module)

    fn = resolve_agent("agent_benchmark_suite._test_agent:my_agent")
    assert fn("hello") == "echo: hello"


def test_resolve_agent_rejects_missing_attribute(monkeypatch):
    module = types.ModuleType("agent_benchmark_suite._test_agent2")
    monkeypatch.setitem(sys.modules, "agent_benchmark_suite._test_agent2", module)
    with pytest.raises(ValueError):
        resolve_agent("agent_benchmark_suite._test_agent2:missing")


def test_resolve_agent_rejects_non_callable(monkeypatch):
    module = types.ModuleType("agent_benchmark_suite._test_agent3")
    module.constant = 42
    monkeypatch.setitem(sys.modules, "agent_benchmark_suite._test_agent3", module)
    with pytest.raises(ValueError):
        resolve_agent("agent_benchmark_suite._test_agent3:constant")


def test_cli_run_writes_json_report(tmp_path, capsys):
    report = tmp_path / "report.json"
    exit_code = main(["run", "--agent", "fake_agent", "--output", str(report), "--quiet"])
    assert exit_code == 0
    payload = json.loads(report.read_text())
    assert payload["agent"] == "fake_agent"
    assert payload["total_tasks"] == 20
    assert payload["total_passed"] == 0


def test_cli_run_restricts_to_category(tmp_path):
    report = tmp_path / "math.json"
    exit_code = main(
        [
            "run",
            "--agent",
            "fake_agent",
            "--output",
            str(report),
            "--category",
            "math",
            "--quiet",
        ]
    )
    assert exit_code == 0
    payload = json.loads(report.read_text())
    assert payload["total_tasks"] == 5
    for entry in payload["results"]:
        assert entry["category"] == "math"


def test_cli_list_prints_every_task_id(capsys):
    exit_code = main(["list"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "math.basic_arith" in out
    assert "tool_use.json_strict" in out


def test_cli_info_prints_version_and_task_count(capsys):
    exit_code = main(["info"])
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "bundled tasks: 20" in out


def test_cli_run_rejects_unknown_agent_spec(capsys):
    exit_code = main(["run", "--agent", "no_such_agent", "--quiet"])
    assert exit_code == 2
    err = capsys.readouterr().err
    assert "unknown agent" in err
