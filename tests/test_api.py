"""Tests for agent-benchmark-suite API."""
import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["service"] == "agent-benchmark-suite"

def test_process():
    r = client.post("/process", json={"input": "test data for processing"})
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["result"]["processed"] is True
    assert data["result"]["word_count"] == 4
    assert data["processing_time_ms"] >= 0

def test_process_with_options():
    r = client.post("/process", json={"input": "test", "options": {"verbose": True, "format": "json"}})
    assert r.status_code == 200
    assert "verbose" in r.json()["result"]["options_applied"]

def test_process_empty():
    r = client.post("/process", json={"input": ""})
    assert r.status_code == 200
    assert r.json()["result"]["word_count"] == 0

def test_batch():
    r = client.post("/batch", json={"items": [
        {"input": "first item"},
        {"input": "second item"},
        {"input": "third item"},
    ]})
    assert r.status_code == 200
    assert r.json()["total"] == 3

def test_history():
    client.post("/process", json={"input": "track this"})
    r = client.get("/history")
    assert r.status_code == 200
    assert len(r.json()) > 0

def test_status():
    r = client.get("/status")
    assert r.status_code == 200
    assert r.json()["ready"] is True
    assert r.json()["version"] == "0.1.0"
