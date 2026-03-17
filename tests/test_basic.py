"""Tests for agent-benchmark-suite."""
import pytest
from src import __version__

def test_version():
    assert __version__ == "0.1.0"

def test_import():
    import src
    assert hasattr(src, "__version__")
