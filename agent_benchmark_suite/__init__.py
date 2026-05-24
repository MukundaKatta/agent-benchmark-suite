"""agent-benchmark-suite: a small fixed benchmark set for AI agents.

Run any agent (a function from prompt -> string) against the bundled
20-task suite and get a comparable scorecard.

Public surface:

    from agent_benchmark_suite import (
        Task,
        Category,
        TaskResult,
        Scorecard,
        run_suite,
        STANDARD_SUITE,
        exact_match,
        contains,
        contains_all,
        regex_match,
        json_key_equals,
    )
"""
from .scorers import (
    Scorer,
    exact_match,
    contains,
    contains_all,
    regex_match,
    json_key_equals,
)
from .tasks import Category, Task, TaskResult
from .suite import STANDARD_SUITE, tasks_for_category
from .runner import run_suite
from .scorecard import Scorecard, render_scorecard

__version__ = "0.2.0"

__all__ = [
    "Category",
    "Task",
    "TaskResult",
    "Scorecard",
    "Scorer",
    "STANDARD_SUITE",
    "tasks_for_category",
    "run_suite",
    "render_scorecard",
    "exact_match",
    "contains",
    "contains_all",
    "regex_match",
    "json_key_equals",
    "__version__",
]
