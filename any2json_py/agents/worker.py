from __future__ import annotations
import asyncio
from pydantic import BaseModel
import instructor
from litellm import completion
from any2json_py.config import get_settings
from any2json_py.utils.cost_tracker import CostTracker

_SYSTEM_PROMPT = (
    "You are a precise data extraction assistant. "
    "Extract only information explicitly present in the provided content. "
    "Never infer or hallucinate. Use null for any field not found in the content."
)


async def run_worker(
    content: str | list,
    model: type[BaseModel],
    tracker: CostTracker,
    llm_model: str | None = None,
) -> BaseModel:
    """Single unit of LLM execution. Accepts text (str) or image (list of vision message parts)."""
    settings = get_settings()
    llm_model = llm_model or settings.models.worker
    client = instructor.from_litellm(completion)

    if isinstance(content, str):
        user_content = f"Extract data from the following content:\n\n{content}"
    else:
        user_content = content  # vision message list

    response, comp = await asyncio.to_thread(
        client.chat.completions.create_with_completion,
        model=llm_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_model=model,
        temperature=0,
    )
    tracker.add(llm_model, comp.usage.prompt_tokens, comp.usage.completion_tokens)
    return response
