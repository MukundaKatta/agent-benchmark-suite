"""Tests for the suite runner."""
import pytest

from agent_benchmark_suite import run_suite
from agent_benchmark_suite.scorers import contains, exact_match
from agent_benchmark_suite.suite import STANDARD_SUITE
from agent_benchmark_suite.tasks import Category, Task


def _always(response: str):
    def fn(_prompt: str) -> str:
        return response

    return fn


def test_run_suite_with_empty_task_list_raises():
    with pytest.raises(ValueError):
        run_suite(_always("x"), tasks=[])


def test_run_suite_defaults_to_standard_suite():
    scorecard = run_suite(_always(""))
    assert scorecard.total_tasks == len(STANDARD_SUITE)


def test_failing_agent_scores_zero_and_passes_count_is_zero():
    scorecard = run_suite(_always("definitely not the answer"))
    assert scorecard.total_passed == 0
    assert scorecard.overall_score == 0.0


def test_perfect_agent_on_single_task():
    task = Task(
        id="math.one",
        category=Category.MATH,
        prompt="say two",
        scorer=exact_match("two"),
    )
    scorecard = run_suite(_always("two"), tasks=[task])
    assert scorecard.total_passed == 1
    assert scorecard.overall_score == 1.0
    assert scorecard.pass_rate == 1.0


def test_runner_records_agent_exception_as_zero_score():
    def boom(_prompt: str) -> str:
        raise RuntimeError("agent went boom")

    task = Task(
        id="reasoning.one",
        category=Category.REASONING,
        prompt="anything",
        scorer=contains("x"),
    )
    scorecard = run_suite(boom, tasks=[task])
    assert scorecard.results[0].score == 0.0
    assert "RuntimeError" in scorecard.results[0].error


def test_runner_records_scorer_exception_as_zero_score():
    def bad_scorer(_response: str) -> float:
        raise ValueError("scorer is broken")

    task = Task(
        id="reasoning.bad",
        category=Category.REASONING,
        prompt="anything",
        scorer=bad_scorer,
    )
    scorecard = run_suite(_always("hi"), tasks=[task])
    assert scorecard.results[0].score == 0.0
    assert "scorer error" in scorecard.results[0].error


def test_runner_coerces_non_string_agent_output():
    """An agent that accidentally returns a number should not crash the run."""

    def numeric(_prompt: str) -> str:  # type: ignore[return-value]
        return 42  # type: ignore[return-value]

    task = Task(
        id="reasoning.numeric",
        category=Category.REASONING,
        prompt="x",
        scorer=contains("42"),
    )
    scorecard = run_suite(numeric, tasks=[task])
    assert scorecard.results[0].score == 1.0


def test_runner_clips_scores_above_one_and_below_zero():
    def too_high(_response: str) -> float:
        return 17.0

    def too_low(_response: str) -> float:
        return -3.0

    tasks = [
        Task(id="a", category=Category.MATH, prompt="x", scorer=too_high),
        Task(id="b", category=Category.MATH, prompt="x", scorer=too_low),
    ]
    scorecard = run_suite(_always(""), tasks=tasks)
    assert scorecard.results[0].score == 1.0
    assert scorecard.results[1].score == 0.0


def test_runner_aggregates_per_category():
    tasks = [
        Task(id="m.1", category=Category.MATH, prompt="x", scorer=exact_match("yes")),
        Task(id="m.2", category=Category.MATH, prompt="x", scorer=exact_match("no")),
        Task(id="r.1", category=Category.REASONING, prompt="x", scorer=exact_match("yes")),
    ]
    scorecard = run_suite(_always("yes"), tasks=tasks)
    by_cat = {c.category: c for c in scorecard.categories}
    assert by_cat[Category.MATH].score == 0.5
    assert by_cat[Category.MATH].passed == 1
    assert by_cat[Category.REASONING].score == 1.0
    assert by_cat[Category.REASONING].passed == 1


def test_scorecard_pass_rate_is_zero_when_no_tasks():
    """The pass_rate property should not divide by zero on an empty result.

    The runner refuses to build a scorecard with zero tasks, so this is
    a direct check on the dataclass invariant.
    """
    from agent_benchmark_suite.scorecard import Scorecard

    empty = Scorecard(
        agent_name="x",
        overall_score=0.0,
        total_tasks=0,
        total_passed=0,
        avg_latency_ms=0.0,
    )
    assert empty.pass_rate == 0.0
