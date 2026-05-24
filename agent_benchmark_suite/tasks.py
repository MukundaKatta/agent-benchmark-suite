"""Task and TaskResult: the atomic unit of a benchmark suite."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .scorers import Scorer


class Category(str, Enum):
    """The four canonical task families in the standard suite."""

    MATH = "math"
    CODE = "code"
    REASONING = "reasoning"
    TOOL_USE = "tool_use"


@dataclass(frozen=True)
class Task:
    """A single benchmark task.

    A task is a prompt plus a scorer. The scorer decides whether the
    agent's response is right or wrong, optionally with partial credit.
    Tasks are immutable so they can be shared across runs without
    accidental mutation by an agent.
    """

    id: str
    category: Category
    prompt: str
    scorer: Scorer
    description: str = ""
    timeout_s: float = 30.0


@dataclass
class TaskResult:
    """The outcome of running one task against one agent."""

    task_id: str
    category: Category
    score: float
    latency_ms: float
    response: str
    error: str = ""

    @property
    def passed(self) -> bool:
        """A task is considered passed when the score is at the perfect mark."""
        return self.score >= 1.0


@dataclass
class CategoryStats:
    """Aggregate stats for one category in a single run."""

    category: Category
    score: float
    passed: int
    total: int
    avg_latency_ms: float
    results: list[TaskResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total


def to_jsonable(value: Any) -> Any:
    """Recursively convert dataclasses/enums into JSON-safe shapes."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    if hasattr(value, "__dataclass_fields__"):
        from dataclasses import asdict

        return to_jsonable(asdict(value))
    return value
