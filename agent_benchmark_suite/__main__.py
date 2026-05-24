"""Allow running the suite as `python -m agent_benchmark_suite`."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
