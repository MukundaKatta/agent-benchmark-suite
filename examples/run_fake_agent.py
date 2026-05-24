"""Run the bundled suite against the built-in fake agent.

The fake agent always replies "n/a", which scores 0/20. The point of
this example is to show the end-to-end shape of a run without needing
an API key. Replace `fake_agent` with your own callable to score a
real agent.

    python examples/run_fake_agent.py
"""
from agent_benchmark_suite import render_scorecard, run_suite
from agent_benchmark_suite.cli import fake_agent


def main() -> None:
    scorecard = run_suite(fake_agent, agent_name="fake_agent")
    print(render_scorecard(scorecard))


if __name__ == "__main__":
    main()
