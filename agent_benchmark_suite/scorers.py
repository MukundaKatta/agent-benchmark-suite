"""Standard scorers for agent responses.

A scorer is any callable that takes a response string and returns a
float between 0.0 and 1.0. The helpers in this module build scorers
from common matching strategies. Custom callables work too, as long
as they return a number in [0.0, 1.0].
"""
from __future__ import annotations

import json
import re
from typing import Callable

# A scorer takes the agent's raw response and returns a score in [0, 1].
Scorer = Callable[[str], float]


def _clip(value: float) -> float:
    """Clamp a score into the valid [0.0, 1.0] window."""
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return float(value)


def exact_match(expected: str, *, case_sensitive: bool = False, strip: bool = True) -> Scorer:
    """Return a scorer that gives 1.0 only when the response equals `expected`."""
    target = expected if case_sensitive else expected.lower()
    if strip:
        target = target.strip()

    def score(response: str) -> float:
        value = response if case_sensitive else response.lower()
        if strip:
            value = value.strip()
        return 1.0 if value == target else 0.0

    return score


def contains(needle: str, *, case_sensitive: bool = False) -> Scorer:
    """Return a scorer that gives 1.0 when `needle` appears in the response."""
    target = needle if case_sensitive else needle.lower()

    def score(response: str) -> float:
        value = response if case_sensitive else response.lower()
        return 1.0 if target in value else 0.0

    return score


def contains_all(needles: list[str], *, case_sensitive: bool = False) -> Scorer:
    """Return a scorer that grants partial credit for each needle present.

    Score is `hits / len(needles)`. Useful for tasks where the answer is
    a small set of required tokens, like "list the three primary colors".
    """
    if not needles:
        raise ValueError("contains_all requires at least one needle")
    targets = [n if case_sensitive else n.lower() for n in needles]

    def score(response: str) -> float:
        value = response if case_sensitive else response.lower()
        hits = sum(1 for t in targets if t in value)
        return _clip(hits / len(targets))

    return score


def regex_match(pattern: str, *, flags: int = re.IGNORECASE) -> Scorer:
    """Return a scorer that gives 1.0 if the regex finds a match."""
    compiled = re.compile(pattern, flags)

    def score(response: str) -> float:
        return 1.0 if compiled.search(response) else 0.0

    return score


def json_key_equals(key: str, expected_value: object) -> Scorer:
    """Return a scorer that parses the response as JSON and checks one key.

    The scorer tolerates extra prose around the JSON by extracting the
    first balanced object it finds. Returns 0.0 on parse failure or
    missing key.
    """

    def score(response: str) -> float:
        payload = _extract_first_json_object(response)
        if payload is None:
            return 0.0
        try:
            obj = json.loads(payload)
        except (json.JSONDecodeError, ValueError):
            return 0.0
        if not isinstance(obj, dict):
            return 0.0
        if key not in obj:
            return 0.0
        return 1.0 if obj[key] == expected_value else 0.0

    return score


def _extract_first_json_object(text: str) -> str | None:
    """Find the first {...} block with balanced braces, ignoring string contents."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None
