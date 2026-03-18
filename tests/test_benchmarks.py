"""Tests for agent-benchmark-suite core logic."""
import pytest


def test_import():
    from src import benchmarks
    assert hasattr(benchmarks, "__doc__")

def test_classes_exist():
    import src.benchmarks as m
    classes = [n for n in dir(m) if isinstance(getattr(m, n), type) and not n.startswith("_")]
    assert len(classes) >= 1, f"Expected classes in benchmarks, found: {classes}"
