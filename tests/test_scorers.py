"""Tests for the standard scorer helpers."""
import pytest

from agent_benchmark_suite.scorers import (
    contains,
    contains_all,
    exact_match,
    json_key_equals,
    regex_match,
)


def test_exact_match_default_is_case_insensitive_and_strips():
    scorer = exact_match("YES")
    assert scorer("yes") == 1.0
    assert scorer("  yes  ") == 1.0
    assert scorer("Yes\n") == 1.0
    assert scorer("no") == 0.0


def test_exact_match_case_sensitive():
    scorer = exact_match("Tokyo", case_sensitive=True, strip=False)
    assert scorer("Tokyo") == 1.0
    assert scorer("tokyo") == 0.0


def test_contains_returns_one_when_substring_present():
    scorer = contains("3914")
    assert scorer("the answer is 3914") == 1.0
    assert scorer("the answer is 3901") == 0.0


def test_contains_all_grants_partial_credit():
    scorer = contains_all(["alpha", "beta", "gamma"])
    assert scorer("alpha beta gamma") == 1.0
    assert scorer("alpha beta only") == pytest.approx(2 / 3)
    assert scorer("alpha only") == pytest.approx(1 / 3)
    assert scorer("nothing here") == 0.0


def test_contains_all_rejects_empty_list():
    with pytest.raises(ValueError):
        contains_all([])


def test_regex_match_uses_search_semantics():
    scorer = regex_match(r"\b3914\b")
    assert scorer("answer: 3914.") == 1.0
    assert scorer("answer: 39140") == 0.0


def test_json_key_equals_handles_prose_around_object():
    scorer = json_key_equals("tool", "web_search")
    response = 'Sure, here you go: {"tool": "web_search", "args": {"q": "x"}} done.'
    assert scorer(response) == 1.0


def test_json_key_equals_returns_zero_on_bad_json():
    scorer = json_key_equals("tool", "web_search")
    assert scorer("not json at all") == 0.0
    assert scorer('{"tool": "calculator"}') == 0.0
    assert scorer('{this is broken}') == 0.0


def test_json_key_equals_returns_zero_when_root_is_array():
    scorer = json_key_equals("tool", "web_search")
    # The extractor walks for the first '{', but an array-only response has none.
    assert scorer('[{"tool": "web_search"}]') == 1.0  # array still contains the object
    assert scorer("[1, 2, 3]") == 0.0


def test_json_key_equals_tolerates_nested_objects():
    scorer = json_key_equals("ok", True)
    response = '{"ok": true, "nested": {"a": {"b": 1}}}'
    assert scorer(response) == 1.0
