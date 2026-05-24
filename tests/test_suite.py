"""Tests for the bundled standard suite shape and contents."""
from collections import Counter

from agent_benchmark_suite import STANDARD_SUITE, tasks_for_category
from agent_benchmark_suite.tasks import Category


def test_suite_has_twenty_tasks():
    assert len(STANDARD_SUITE) == 20


def test_suite_has_five_tasks_per_category():
    counts = Counter(t.category for t in STANDARD_SUITE)
    for cat in Category:
        assert counts[cat] == 5, f"{cat} has {counts[cat]} tasks"


def test_every_task_id_is_unique():
    ids = [t.id for t in STANDARD_SUITE]
    assert len(set(ids)) == len(ids)


def test_every_task_id_starts_with_its_category():
    for task in STANDARD_SUITE:
        assert task.id.startswith(task.category.value + ".")


def test_every_task_has_nonempty_prompt():
    for task in STANDARD_SUITE:
        assert task.prompt.strip(), f"empty prompt for {task.id}"


def test_every_task_scorer_is_callable():
    for task in STANDARD_SUITE:
        assert callable(task.scorer), f"non-callable scorer for {task.id}"


def test_tasks_for_category_filters_correctly():
    math_tasks = tasks_for_category(Category.MATH)
    assert len(math_tasks) == 5
    assert all(t.category == Category.MATH for t in math_tasks)


def test_each_task_has_known_good_answer():
    """An 'oracle' agent that returns the canonical answer scores 1.0 on its own task.

    This is the contract that makes the suite testable: every task has
    at least one response string the scorer accepts. If a future edit
    breaks this, that task is silently unscorable.
    """
    oracle = {
        "math.basic_arith": "3901",
        "math.percent": "45",
        "math.word_problem": "13:00",
        "math.fraction": "7/8",
        "math.compound_interest": "1210",
        "code.fizzbuzz": "def fizzbuzz(n): return 'FizzBuzz' if n % 15 == 0 else 'Fizz' if n % 3 == 0 else 'Buzz' if n % 5 == 0 else str(n)",
        "code.reverse_string": "s[::-1]",
        "code.sum_evens": "def sum_evens(nums): return sum(x for x in nums if x % 2 == 0)",
        "code.is_palindrome": "def is_palindrome(s): t = ''.join(c.lower() for c in s if c.isalnum()); return t == t[::-1]",
        "code.json_parse": "data = json.loads(s)",
        "reasoning.syllogism": "no",
        "reasoning.sibling_age": "1",
        "reasoning.causation": "no",
        "reasoning.deduction": "carol",
        "reasoning.sequence": "42",
        "tool_use.search": '{"tool": "web_search", "args": {"query": "2024 super bowl winner"}}',
        "tool_use.calculator": '{"tool": "calculator", "args": {"expression": "17 * 23"}}',
        "tool_use.file_read": '{"tool": "read_file", "args": {"path": "/etc/hostname"}}',
        "tool_use.no_tool_needed": "none",
        "tool_use.json_strict": '{"city": "Tokyo", "country": "Japan"}',
    }
    for task in STANDARD_SUITE:
        assert task.id in oracle, f"missing oracle answer for {task.id}"
        score = task.scorer(oracle[task.id])
        assert score == 1.0, f"oracle answer for {task.id} scored {score}"


def test_each_task_rejects_a_blank_response():
    """A scorer that returns 1.0 for the empty string is too lenient to be useful."""
    for task in STANDARD_SUITE:
        assert task.scorer("") < 1.0, f"{task.id} accepts blank response"
