"""Tests for AgentBenchmarkSuite."""
from src.core import AgentBenchmarkSuite
def test_init(): assert AgentBenchmarkSuite().get_stats()["ops"] == 0
def test_op(): c = AgentBenchmarkSuite(); c.process(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = AgentBenchmarkSuite(); [c.process() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = AgentBenchmarkSuite(); c.process(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = AgentBenchmarkSuite(); r = c.process(); assert r["service"] == "agent-benchmark-suite"
