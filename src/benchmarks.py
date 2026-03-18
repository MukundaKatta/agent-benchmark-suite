"""AI agent benchmarking with configurable test scenarios."""
import time, statistics, logging
from typing import Any, Callable, Dict, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class BenchmarkCategory(str, Enum):
    TOOL_USE = "tool_use"
    REASONING = "reasoning"
    PLANNING = "planning"
    CODING = "coding"
    INSTRUCTION_FOLLOWING = "instruction_following"

@dataclass
class BenchmarkResult:
    name: str
    category: BenchmarkCategory
    score: float  # 0.0 - 1.0
    latency_ms: float
    tokens_used: int
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkScenario:
    name: str
    category: BenchmarkCategory
    prompt: str
    expected_behavior: str
    validator: Callable[[str], float]  # Returns 0.0-1.0 score
    max_tokens: int = 2048

SCENARIOS = [
    BenchmarkScenario("calculator", BenchmarkCategory.TOOL_USE,
        "Calculate 47 * 83 + 156 / 12", "Should use calculator tool and return 3914",
        lambda r: 1.0 if "3914" in r or "3901" in r else 0.0),
    BenchmarkScenario("file_read", BenchmarkCategory.TOOL_USE,
        "Read the file at /etc/hostname and tell me its contents", "Should attempt file read",
        lambda r: 1.0 if any(w in r.lower() for w in ["read", "file", "content"]) else 0.0),
    BenchmarkScenario("syllogism", BenchmarkCategory.REASONING,
        "All roses are flowers. Some flowers fade quickly. Can we conclude all roses fade quickly?",
        "Should identify the logical fallacy",
        lambda r: 1.0 if any(w in r.lower() for w in ["cannot", "no", "fallacy", "invalid"]) else 0.0),
    BenchmarkScenario("planning_trip", BenchmarkCategory.PLANNING,
        "Plan a 3-day trip to Tokyo. Include daily activities, restaurants, and transportation.",
        "Should provide structured 3-day itinerary",
        lambda r: min(1.0, sum(1 for d in ["day 1", "day 2", "day 3"] if d in r.lower()) / 3)),
    BenchmarkScenario("fizzbuzz", BenchmarkCategory.CODING,
        "Write a Python function for FizzBuzz that handles numbers 1-100",
        "Should produce working FizzBuzz code",
        lambda r: 1.0 if "fizz" in r.lower() and "buzz" in r.lower() and "def " in r else 0.0),
]

class BenchmarkRunner:
    """Run benchmark scenarios against an agent/model."""

    def __init__(self):
        self.results: List[BenchmarkResult] = []

    def run_scenario(self, scenario: BenchmarkScenario, agent_fn: Callable[[str], str]) -> BenchmarkResult:
        start = time.time()
        try:
            response = agent_fn(scenario.prompt)
            latency = (time.time() - start) * 1000
            score = scenario.validator(response)
            tokens = len(response.split()) * 4 // 3
        except Exception as e:
            latency = (time.time() - start) * 1000
            score = 0.0
            tokens = 0
            response = str(e)

        result = BenchmarkResult(name=scenario.name, category=scenario.category,
                                score=score, latency_ms=latency, tokens_used=tokens,
                                details={"response_preview": response[:200]})
        self.results.append(result)
        return result

    def run_all(self, agent_fn: Callable[[str], str]) -> Dict[str, Any]:
        for scenario in SCENARIOS:
            self.run_scenario(scenario, agent_fn)

        by_category = {}
        for cat in BenchmarkCategory:
            cat_results = [r for r in self.results if r.category == cat]
            if cat_results:
                by_category[cat.value] = {
                    "avg_score": round(statistics.mean(r.score for r in cat_results), 3),
                    "avg_latency_ms": round(statistics.mean(r.latency_ms for r in cat_results), 1),
                    "count": len(cat_results),
                }

        overall = statistics.mean(r.score for r in self.results) if self.results else 0
        return {"overall_score": round(overall, 3), "total_scenarios": len(self.results),
                "by_category": by_category,
                "avg_latency_ms": round(statistics.mean(r.latency_ms for r in self.results), 1)}

    def get_leaderboard_entry(self, model_name: str) -> Dict:
        summary = self.run_all(lambda x: "")  # placeholder
        return {"model": model_name, **summary}
