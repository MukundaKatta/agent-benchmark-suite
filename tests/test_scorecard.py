"""Tests for the scorecard renderer and JSON export."""
import json

from agent_benchmark_suite import render_scorecard, run_suite
from agent_benchmark_suite.scorers import contains
from agent_benchmark_suite.tasks import Category, Task


def _agent(_prompt: str) -> str:
    return "hello"


def _two_task_suite():
    return [
        Task(id="math.a", category=Category.MATH, prompt="x", scorer=contains("hello")),
        Task(id="reasoning.b", category=Category.REASONING, prompt="x", scorer=contains("world")),
    ]


def test_render_scorecard_includes_agent_name_and_summary():
    scorecard = run_suite(_agent, tasks=_two_task_suite(), agent_name="my-agent")
    text = render_scorecard(scorecard)
    assert "my-agent" in text
    assert "overall score" in text
    assert "by category" in text


def test_render_scorecard_marks_passed_and_failed_tasks():
    scorecard = run_suite(_agent, tasks=_two_task_suite())
    text = render_scorecard(scorecard)
    # math.a should pass because the response contains "hello"
    # reasoning.b should fail because the response does not contain "world"
    assert "[ok] math.a" in text
    assert "[  ] reasoning.b" in text


def test_to_dict_round_trips_through_json():
    scorecard = run_suite(_agent, tasks=_two_task_suite(), agent_name="json-agent")
    payload = scorecard.to_dict()
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert decoded["agent"] == "json-agent"
    assert decoded["total_tasks"] == 2
    assert decoded["total_passed"] == 1
    assert len(decoded["results"]) == 2
    assert decoded["results"][0]["task_id"] == "math.a"


def test_to_dict_rounds_scores():
    scorecard = run_suite(_agent, tasks=_two_task_suite())
    payload = scorecard.to_dict()
    for entry in payload["results"]:
        # rounded to 3 decimals
        assert round(entry["score"], 3) == entry["score"]


def test_response_preview_collapses_whitespace_and_truncates():
    def chatty(_prompt: str) -> str:
        return ("answer  \n  contains   hello   " + "x" * 500).strip()

    scorecard = run_suite(chatty, tasks=_two_task_suite())
    payload = scorecard.to_dict()
    preview = payload["results"][0]["response_preview"]
    # No runs of more than one space in the preview.
    assert "  " not in preview
    # Limit enforced.
    assert len(preview) <= 160
