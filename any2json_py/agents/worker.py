from __future__ import annotations
import asyncio
from pydantic import BaseModel
import instructor
from litellm import completion
from any2json_py.config import get_settings
from any2json_py.utils.cost_tracker import CostTracker

_SYSTEM_PROMPT = (
    "You are a data extraction worker. Extract only information explicitly present in the provided chunk. "
    "Never infer or hallucinate. Use null for any field not found in this chunk."
)


async def run_worker(chunk: str, model: type[BaseModel], tracker: CostTracker) -> BaseModel:
    settings = get_settings()
    client = instructor.from_litellm(completion)
    response, comp = await asyncio.to_thread(
        client.chat.completions.create_with_completion,
        model=settings.worker_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract data from this document chunk:\n\n{chunk}"},
        ],
        response_model=model,
        temperature=0,
    )
    tracker.add(settings.worker_model, comp.usage.prompt_tokens, comp.usage.completion_tokens)
    return response
