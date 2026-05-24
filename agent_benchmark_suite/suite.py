"""The bundled standard suite: 20 fixed tasks across 4 categories.

Five tasks each for math, code, reasoning, and tool_use. The set is
small on purpose. A standard suite has value because everyone runs the
same tasks with the same scorers, not because the suite is huge.

To extend or replace tasks for a custom run, build your own list of
`Task` instances and hand it to `run_suite`.
"""
from __future__ import annotations

from .scorers import contains, contains_all, exact_match, json_key_equals, regex_match
from .tasks import Category, Task

# ---- Math: arithmetic where the right answer is a specific number string. ----

MATH_TASKS: list[Task] = [
    Task(
        id="math.basic_arith",
        category=Category.MATH,
        prompt="What is 47 * 83? Reply with only the number.",
        scorer=contains("3901"),
        description="Two-digit multiplication.",
    ),
    Task(
        id="math.percent",
        category=Category.MATH,
        prompt="What is 18% of 250? Reply with only the number.",
        scorer=contains("45"),
        description="Percentage of a round number.",
    ),
    Task(
        id="math.word_problem",
        category=Category.MATH,
        prompt=(
            "A train leaves at 9:00 going 60 mph. A second train leaves at 10:00 "
            "from the same place going the same direction at 80 mph. At what time "
            "does the second train catch up? Reply with the time in HH:MM 24-hour."
        ),
        scorer=contains("13:00"),
        description="Catch-up word problem; answer is 13:00.",
    ),
    Task(
        id="math.fraction",
        category=Category.MATH,
        prompt="What is 3/4 + 1/8 as a single reduced fraction? Reply with only the fraction.",
        scorer=contains("7/8"),
        description="Add unlike fractions and reduce.",
    ),
    Task(
        id="math.compound_interest",
        category=Category.MATH,
        prompt=(
            "If $1000 grows at 10% per year compounded annually for 2 years, "
            "what is the final amount in dollars, rounded to the nearest dollar? "
            "Reply with only the number."
        ),
        scorer=contains("1210"),
        description="Two-year compound interest at 10%.",
    ),
]

# ---- Code: shape-of-answer checks for short programs. ----

CODE_TASKS: list[Task] = [
    Task(
        id="code.fizzbuzz",
        category=Category.CODE,
        prompt=(
            "Write a Python function called fizzbuzz(n) that returns 'Fizz' "
            "for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for "
            "both, and str(n) otherwise. Reply with only the code."
        ),
        scorer=contains_all(["def fizzbuzz", "fizz", "buzz", "%", "3", "5"]),
        description="Classic FizzBuzz; checks function name and arithmetic shape.",
    ),
    Task(
        id="code.reverse_string",
        category=Category.CODE,
        prompt=(
            "Write a Python one-liner that reverses the string s. "
            "Reply with only the expression, no 'print', no assignment."
        ),
        scorer=regex_match(r"s\s*\[\s*::\s*-\s*1\s*\]"),
        description="Slice-based reverse: s[::-1].",
    ),
    Task(
        id="code.sum_evens",
        category=Category.CODE,
        prompt=(
            "Write a Python function called sum_evens(nums) that returns the "
            "sum of even numbers in the iterable nums. Reply with only the code."
        ),
        scorer=contains_all(["def sum_evens", "sum(", "%", "2"]),
        description="Sum even numbers; checks function name and the mod-2 filter.",
    ),
    Task(
        id="code.is_palindrome",
        category=Category.CODE,
        prompt=(
            "Write a Python function called is_palindrome(s) that returns True "
            "if s reads the same forwards and backwards, case-insensitive, "
            "ignoring non-alphanumeric. Reply with only the code."
        ),
        scorer=contains_all(["def is_palindrome", "lower", "[::-1]"]),
        description="Palindrome with case-folding; checks shape, not output.",
    ),
    Task(
        id="code.json_parse",
        category=Category.CODE,
        prompt=(
            "Write a Python one-liner that parses a JSON string `s` into a dict "
            "called `data`. Reply with only the line."
        ),
        scorer=regex_match(r"data\s*=\s*json\.loads\(\s*s\s*\)"),
        description="json.loads one-liner with a specific variable name.",
    ),
]

# ---- Reasoning: short-answer logic and inference. ----

REASONING_TASKS: list[Task] = [
    Task(
        id="reasoning.syllogism",
        category=Category.REASONING,
        prompt=(
            "All roses are flowers. Some flowers fade quickly. Does it "
            "follow that some roses fade quickly? Reply with only 'yes' or 'no'."
        ),
        scorer=exact_match("no"),
        description="Existential fallacy; correct answer is 'no'.",
    ),
    Task(
        id="reasoning.sibling_age",
        category=Category.REASONING,
        prompt=(
            "Sally has 3 brothers. Each of her brothers has 2 sisters. How "
            "many sisters does Sally have? Reply with only the number."
        ),
        scorer=contains("1"),
        description="The trick is that Sally herself is one of the sisters.",
    ),
    Task(
        id="reasoning.causation",
        category=Category.REASONING,
        prompt=(
            "Ice cream sales and drowning deaths both rise in summer. Does "
            "ice cream cause drowning? Reply with only 'yes' or 'no'."
        ),
        scorer=exact_match("no"),
        description="Confounding variable; the answer is 'no'.",
    ),
    Task(
        id="reasoning.deduction",
        category=Category.REASONING,
        prompt=(
            "Alice, Bob, and Carol stand in a line. Alice is not first. "
            "Carol is not last. Bob is not next to Alice. Who is first? "
            "Reply with only the name."
        ),
        scorer=exact_match("carol"),
        description="Small constraint puzzle; only Carol can be first.",
    ),
    Task(
        id="reasoning.sequence",
        category=Category.REASONING,
        prompt=(
            "What is the next number in the sequence 2, 6, 12, 20, 30, ...? "
            "Reply with only the number."
        ),
        scorer=contains("42"),
        description="n*(n+1) for n in 1..5, next term is 42.",
    ),
]

# ---- Tool-use: structured tool-call output, judged by JSON shape. ----

TOOL_USE_TASKS: list[Task] = [
    Task(
        id="tool_use.search",
        category=Category.TOOL_USE,
        prompt=(
            'You can call the tool web_search(query: str). To use it, '
            'reply with a single JSON object on one line of the form '
            '{"tool": "web_search", "args": {"query": "<text>"}} and nothing else. '
            "The user asks: who won the 2024 super bowl?"
        ),
        scorer=json_key_equals("tool", "web_search"),
        description="Pick the search tool; checks the JSON 'tool' field.",
    ),
    Task(
        id="tool_use.calculator",
        category=Category.TOOL_USE,
        prompt=(
            'You can call calculator(expression: str). Reply with a single JSON object '
            'of the form {"tool": "calculator", "args": {"expression": "<expr>"}} and '
            "nothing else. The user asks: what is 17 * 23?"
        ),
        scorer=json_key_equals("tool", "calculator"),
        description="Pick the calculator tool over freeform reasoning.",
    ),
    Task(
        id="tool_use.file_read",
        category=Category.TOOL_USE,
        prompt=(
            'You can call read_file(path: str). Reply with a single JSON object '
            'of the form {"tool": "read_file", "args": {"path": "<path>"}} and '
            'nothing else. The user asks: read /etc/hostname.'
        ),
        scorer=json_key_equals("tool", "read_file"),
        description="Pick the file-read tool; checks the JSON 'tool' field.",
    ),
    Task(
        id="tool_use.no_tool_needed",
        category=Category.TOOL_USE,
        prompt=(
            'You can call web_search(query: str) and calculator(expression: str). '
            "If no tool is needed, reply with the word 'none' and nothing else. "
            "The user asks: what is your name?"
        ),
        scorer=exact_match("none"),
        description="Self-knowledge question; the agent should decline to call a tool.",
    ),
    Task(
        id="tool_use.json_strict",
        category=Category.TOOL_USE,
        prompt=(
            'Reply with a JSON object that has exactly two keys: "city" set to '
            '"Tokyo" and "country" set to "Japan". Reply with only the JSON.'
        ),
        scorer=json_key_equals("country", "Japan"),
        description="Structured-output discipline; reply must be valid JSON.",
    ),
]

STANDARD_SUITE: list[Task] = MATH_TASKS + CODE_TASKS + REASONING_TASKS + TOOL_USE_TASKS


def tasks_for_category(category: Category) -> list[Task]:
    """Return the bundled tasks for a single category."""
    return [t for t in STANDARD_SUITE if t.category == category]
