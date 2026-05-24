"""Scorecard: the full result of a suite run, plus an ASCII renderer."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .tasks import CategoryStats, TaskResult


@dataclass
class Scorecard:
    """The output of `run_suite`.

    Holds the overall score, per-category stats, and the underlying
    per-task results. Can be serialized via `to_dict` (the CLI uses this
    to write the JSON report) or printed via `render_scorecard`.
    """

    agent_name: str
    overall_score: float
    total_tasks: int
    total_passed: int
    avg_latency_ms: float
    categories: list[CategoryStats] = field(default_factory=list)
    results: list[TaskResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.total_passed / self.total_tasks

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly representation suitable for writing to disk."""
        return {
            "agent": self.agent_name,
            "overall_score": round(self.overall_score, 3),
            "pass_rate": round(self.pass_rate, 3),
            "total_tasks": self.total_tasks,
            "total_passed": self.total_passed,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "categories": [
                {
                    "category": c.category.value,
                    "score": round(c.score, 3),
                    "pass_rate": round(c.pass_rate, 3),
                    "passed": c.passed,
                    "total": c.total,
                    "avg_latency_ms": round(c.avg_latency_ms, 2),
                }
                for c in self.categories
            ],
            "results": [
                {
                    "task_id": r.task_id,
                    "category": r.category.value,
                    "score": round(r.score, 3),
                    "passed": r.passed,
                    "latency_ms": round(r.latency_ms, 2),
                    "response_preview": _preview(r.response),
                    "error": r.error,
                }
                for r in self.results
            ],
        }


def render_scorecard(scorecard: Scorecard) -> str:
    """Render a scorecard as a fixed-width ASCII report."""
    lines: list[str] = []
    header = f"agent-benchmark-suite scorecard for {scorecard.agent_name}"
    rule = "=" * len(header)
    lines.append(rule)
    lines.append(header)
    lines.append(rule)
    lines.append("")
    lines.append(
        f"overall score:   {scorecard.overall_score * 100:5.1f}% "
        f"({scorecard.total_passed}/{scorecard.total_tasks} tasks passed)"
    )
    lines.append(f"avg latency:     {scorecard.avg_latency_ms:5.1f} ms")
    lines.append("")
    lines.append("by category")
    lines.append("-" * 60)
    lines.append(f"  {'category':<14} {'score':>7}  {'pass rate':>10}  {'avg ms':>8}")
    for cat in scorecard.categories:
        lines.append(
            f"  {cat.category.value:<14} {cat.score * 100:6.1f}% "
            f"  {cat.passed:>3}/{cat.total:<3}    "
            f"  {cat.avg_latency_ms:6.1f}"
        )
    lines.append("")
    lines.append("per task")
    lines.append("-" * 60)
    for r in scorecard.results:
        mark = "[ok]" if r.passed else "[  ]"
        score = f"{r.score * 100:5.1f}%"
        lines.append(
            f"  {mark} {r.task_id:<28} {score}   {r.latency_ms:6.1f} ms"
            + (f"   ! {r.error}" if r.error else "")
        )
    lines.append("")
    return "\n".join(lines)


def _preview(text: str, *, limit: int = 160) -> str:
    flat = " ".join(text.split())
    if len(flat) <= limit:
        return flat
    return flat[: limit - 3] + "..."
