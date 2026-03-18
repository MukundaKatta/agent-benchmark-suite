"""LLM client abstraction with multi-provider support."""
import time, logging, hashlib
from typing import Any, AsyncGenerator, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

class Provider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"

@dataclass
class Message:
    role: str  # system, user, assistant, tool
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None

@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    finish_reason: str = "stop"
    tool_calls: List[Dict] = field(default_factory=list)

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]

MODEL_PRICING = {
    "claude-haiku-4-5": (0.25, 1.25),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-4-6": (15.0, 75.0),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.0),
}

class LLMClient:
    """Unified LLM client supporting multiple providers."""

    def __init__(self, provider: Provider = Provider.ANTHROPIC, model: Optional[str] = None,
                 api_key: Optional[str] = None, max_retries: int = 3):
        self.provider = provider
        self.model = model or self._default_model(provider)
        self.api_key = api_key
        self.max_retries = max_retries
        self._usage: List[Dict] = []
        self._cache: Dict[str, str] = {}
        logger.info(f"LLMClient initialized: {provider.value}/{self.model}")

    @staticmethod
    def _default_model(provider: Provider) -> str:
        defaults = {Provider.ANTHROPIC: "claude-sonnet-4-6",
                   Provider.OPENAI: "gpt-4o", Provider.OLLAMA: "llama3.2"}
        return defaults.get(provider, "claude-sonnet-4-6")

    def _estimate_tokens(self, text: str) -> int:
        return len(text.split()) * 4 // 3

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = MODEL_PRICING.get(self.model, (1.0, 3.0))
        return (input_tokens / 1000 * pricing[0] + output_tokens / 1000 * pricing[1]) / 1000

    def chat(self, messages: List[Message], tools: Optional[List[ToolDefinition]] = None,
             temperature: float = 0.7, max_tokens: int = 4096) -> LLMResponse:
        start = time.time()
        
        # Build cache key
        cache_key = hashlib.md5(str([(m.role, m.content[:100]) for m in messages]).encode()).hexdigest()
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            return LLMResponse(content=cached, model=self.model, provider=self.provider.value,
                             input_tokens=0, output_tokens=0, latency_ms=0, cost_usd=0,
                             finish_reason="cached")

        # Estimate tokens
        input_text = " ".join(m.content for m in messages)
        input_tokens = self._estimate_tokens(input_text)
        
        # This would call the actual API — placeholder for structure
        response_content = f"[{self.model} response to: {messages[-1].content[:50]}...]"
        output_tokens = self._estimate_tokens(response_content)

        latency = (time.time() - start) * 1000
        cost = self._calculate_cost(input_tokens, output_tokens)

        self._usage.append({"model": self.model, "input_tokens": input_tokens,
                           "output_tokens": output_tokens, "cost": cost, "timestamp": time.time()})
        self._cache[cache_key] = response_content

        return LLMResponse(content=response_content, model=self.model, provider=self.provider.value,
                         input_tokens=input_tokens, output_tokens=output_tokens,
                         latency_ms=round(latency, 2), cost_usd=round(cost, 6))

    @property
    def total_cost(self) -> float:
        return sum(u["cost"] for u in self._usage)

    @property
    def total_tokens(self) -> int:
        return sum(u["input_tokens"] + u["output_tokens"] for u in self._usage)

    def get_usage(self) -> Dict:
        return {"total_calls": len(self._usage), "total_cost_usd": round(self.total_cost, 4),
                "total_tokens": self.total_tokens, "cache_size": len(self._cache),
                "model": self.model, "provider": self.provider.value}
