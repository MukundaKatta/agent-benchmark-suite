"""Command-line entrypoint for agent-benchmark-suite.

Usage:

    agent-benchmark-suite run --agent fake_agent --output report.json
    agent-benchmark-suite list
    agent-benchmark-suite info

The --agent flag accepts either a built-in name (currently `fake_agent`,
which always answers "n/a") or a dotted path of the form
`my_module:my_callable` resolvable on sys.path.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Callable

from . import __version__
from .runner import AgentFn, run_suite
from .scorecard import render_scorecard
from .suite import STANDARD_SUITE
from .tasks import Category


def fake_agent(_prompt: str) -> str:
    """Built-in placeholder agent: always replies 'n/a'.

    Useful for smoke-testing the runner and seeing what a 0% scorecard
    looks like before plugging in a real agent.
    """
    return "n/a"


_BUILT_IN_AGENTS: dict[str, AgentFn] = {"fake_agent": fake_agent}


def resolve_agent(spec: str) -> AgentFn:
    """Resolve an agent spec into a callable.

    Built-in names short-circuit. Otherwise the spec must be of the form
    `module.path:callable_name`.
    """
    if spec in _BUILT_IN_AGENTS:
        return _BUILT_IN_AGENTS[spec]
    if ":" not in spec:
        raise ValueError(
            f"unknown agent {spec!r}. Use a built-in ({', '.join(_BUILT_IN_AGENTS)}) "
            f"or a dotted path like 'mymod:myfn'."
        )
    module_path, attr = spec.split(":", 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError as exc:
        raise ValueError(f"could not import {module_path!r}: {exc}") from exc
    if not hasattr(module, attr):
        raise ValueError(f"module {module_path!r} has no attribute {attr!r}")
    obj = getattr(module, attr)
    if not callable(obj):
        raise ValueError(f"{spec!r} is not callable")
    return obj  # type: ignore[return-value]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-benchmark-suite",
        description="Standard 20-task benchmark suite for AI agents.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_p = subparsers.add_parser("run", help="run the suite against an agent")
    run_p.add_argument(
        "--agent",
        required=True,
        help="agent spec: a built-in name or 'module:callable'",
    )
    run_p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="write the JSON report to this path (default: stdout only)",
    )
    run_p.add_argument(
        "--category",
        choices=[c.value for c in Category],
        default=None,
        help="restrict the run to a single category",
    )
    run_p.add_argument(
        "--quiet",
        action="store_true",
        help="suppress the ASCII scorecard on stdout",
    )

    subparsers.add_parser("list", help="print the bundled task ids")
    subparsers.add_parser("info", help="print package info")
    return parser


def cmd_run(args: argparse.Namespace) -> int:
    try:
        agent: Callable[[str], str] = resolve_agent(args.agent)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    tasks = STANDARD_SUITE
    if args.category:
        tasks = [t for t in STANDARD_SUITE if t.category.value == args.category]

    scorecard = run_suite(agent, tasks, agent_name=args.agent)

    if not args.quiet:
        print(render_scorecard(scorecard))

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(scorecard.to_dict(), indent=2))
        print(f"wrote report to {args.output}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    by_cat: dict[str, list[str]] = {}
    for t in STANDARD_SUITE:
        by_cat.setdefault(t.category.value, []).append(t.id)
    for cat, ids in by_cat.items():
        print(f"{cat}:")
        for task_id in ids:
            print(f"  {task_id}")
    return 0


def cmd_info(_args: argparse.Namespace) -> int:
    print(f"agent-benchmark-suite v{__version__}")
    print(f"bundled tasks: {len(STANDARD_SUITE)}")
    print(f"categories:    {', '.join(c.value for c in Category)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "list":
        return cmd_list(args)
    if args.command == "info":
        return cmd_info(args)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
