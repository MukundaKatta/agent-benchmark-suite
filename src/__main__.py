"""CLI for agent-benchmark-suite."""
import sys, json, argparse
from .core import AgentBenchmarkSuite

def main():
    parser = argparse.ArgumentParser(description="Comprehensive benchmarking suite for evaluating AI agent capabilities")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = AgentBenchmarkSuite()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"agent-benchmark-suite v0.1.0 — Comprehensive benchmarking suite for evaluating AI agent capabilities")

if __name__ == "__main__":
    main()
