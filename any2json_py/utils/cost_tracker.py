from __future__ import annotations
from dataclasses import dataclass, field

# Cost per 1M tokens (USD)
_COST_PER_1M = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}


@dataclass
class UsageRecord:
    model: str
    prompt_tokens: int
    completion_tokens: int

    @property
    def cost_usd(self) -> float:
        # Strip LiteLLM provider prefix e.g. "openai/gpt-4o-mini" -> "gpt-4o-mini"
        key = self.model.split("/")[-1]
        rates = _COST_PER_1M.get(key, {"input": 0.0, "output": 0.0})
        return (self.prompt_tokens * rates["input"] + self.completion_tokens * rates["output"]) / 1_000_000


@dataclass
class CostTracker:
    records: list[UsageRecord] = field(default_factory=list)

    def add(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        self.records.append(UsageRecord(model, prompt_tokens, completion_tokens))

    @property
    def total_prompt_tokens(self) -> int:
        return sum(r.prompt_tokens for r in self.records)

    @property
    def total_completion_tokens(self) -> int:
        return sum(r.completion_tokens for r in self.records)

    @property
    def total_cost_usd(self) -> float:
        return sum(r.cost_usd for r in self.records)

    def summary(self) -> dict:
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "estimated_cost_usd": round(self.total_cost_usd, 6),
        }
