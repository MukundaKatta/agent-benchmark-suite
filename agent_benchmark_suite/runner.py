"""Run an agent function against a list of tasks and collect results."""
from __future__ import annotations

import time
from typing import Callable, Iterable

from .scorecard import Scorecard
from .suite import STANDARD_SUITE
from .tasks import Category, CategoryStats, Task, TaskResult

# An agent is anything callable from prompt -> response string.
AgentFn = Callable[[str], str]


def run_suite(
    agent: AgentFn,
    tasks: Iterable[Task] | None = None,
    *,
    agent_name: str = "agent",
) -> Scorecard:
    """Run `agent` against every task in `tasks` and return a scorecard.

    If `tasks` is None, the bundled `STANDARD_SUITE` is used. The function
    never raises on an agent exception: failures are recorded as a score
    of 0.0 with the exception message in `error`.
    """
    task_list = list(tasks) if tasks is not None else list(STANDARD_SUITE)
    if not task_list:
        raise ValueError("run_suite requires at least one task")

    results: list[TaskResult] = []
    for task in task_list:
        results.append(_run_one(agent, task))

    category_stats = _aggregate_by_category(results, task_list)
    overall_score = sum(r.score for r in results) / len(results)
    total_passed = sum(1 for r in results if r.passed)
    avg_latency = sum(r.latency_ms for r in results) / len(results)

    return Scorecard(
        agent_name=agent_name,
        overall_score=overall_score,
        total_tasks=len(results),
        total_passed=total_passed,
        avg_latency_ms=avg_latency,
        categories=category_stats,
        results=results,
    )


def _run_one(agent: AgentFn, task: Task) -> TaskResult:
    start = time.perf_counter()
    try:
        response = agent(task.prompt)
        if not isinstance(response, str):
            response = str(response)
    except Exception as exc:  # noqa: BLE001 - report all agent failures
        latency_ms = (time.perf_counter() - start) * 1000
        return TaskResult(
            task_id=task.id,
            category=task.category,
            score=0.0,
            latency_ms=latency_ms,
            response="",
            error=f"{type(exc).__name__}: {exc}",
        )

    latency_ms = (time.perf_counter() - start) * 1000
    try:
        raw = task.scorer(response)
    except Exception as exc:  # noqa: BLE001 - bad custom scorer should not crash the run
        return TaskResult(
            task_id=task.id,
            category=task.category,
            score=0.0,
            latency_ms=latency_ms,
            response=response,
            error=f"scorer error: {type(exc).__name__}: {exc}",
        )

    score = max(0.0, min(1.0, float(raw)))
    return TaskResult(
        task_id=task.id,
        category=task.category,
        score=score,
        latency_ms=latency_ms,
        response=response,
    )


def _aggregate_by_category(
    results: list[TaskResult], tasks: list[Task]
) -> list[CategoryStats]:
    # Preserve a stable ordering: the order categories first appear in the task list.
    seen: list[Category] = []
    for task in tasks:
        if task.category not in seen:
            seen.append(task.category)

    stats: list[CategoryStats] = []
    for cat in seen:
        in_cat = [r for r in results if r.category == cat]
        if not in_cat:
            continue
        score = sum(r.score for r in in_cat) / len(in_cat)
        passed = sum(1 for r in in_cat if r.passed)
        avg_latency = sum(r.latency_ms for r in in_cat) / len(in_cat)
        stats.append(
            CategoryStats(
                category=cat,
                score=score,
                passed=passed,
                total=len(in_cat),
                avg_latency_ms=avg_latency,
                results=in_cat,
            )
        )
    return stats
