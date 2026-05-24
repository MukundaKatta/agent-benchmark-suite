"""Run the bundled suite against a hand-rolled keyword agent.

This 'agent' is a small dictionary lookup that happens to know the
canonical answer for some of the tasks. It will score above zero but
nowhere near a real model. The example exists to show how a custom
callable plugs into `run_suite`.

    python examples/run_keyword_agent.py
"""
from agent_benchmark_suite import render_scorecard, run_suite

# A trivial 'rule-based agent' that scans the prompt for keywords and
# returns a fixed string. Not a real agent, just a demo.
_LOOKUP = {
    "47 * 83": "3901",
    "18% of 250": "45",
    "3/4 + 1/8": "7/8",
    "compound": "1210",
    "fizzbuzz": "def fizzbuzz(n):\n    return 'Fizz' if n % 3 == 0 else 'Buzz' if n % 5 == 0 else str(n)",
    "reverses the string": "s[::-1]",
    "no tool is needed": "none",
    "Tokyo": '{"city": "Tokyo", "country": "Japan"}',
}


def keyword_agent(prompt: str) -> str:
    for needle, answer in _LOOKUP.items():
        if needle in prompt:
            return answer
    return "I don't know."


def main() -> None:
    scorecard = run_suite(keyword_agent, agent_name="keyword_agent")
    print(render_scorecard(scorecard))


if __name__ == "__main__":
    main()
