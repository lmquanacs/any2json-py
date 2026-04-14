from __future__ import annotations
import json
from pydantic import BaseModel
import instructor
from litellm import completion
from any2json_py.config import get_settings
from any2json_py.utils.cost_tracker import CostTracker

_SYSTEM_PROMPT = (
    "You are a data merging coordinator. You receive multiple partial JSON extractions from document chunks. "
    "Merge them into a single coherent result. "
    "NEVER infer, hallucinate, or fill in missing data. "
    "If a field is null in all chunks, it must remain null in the final output."
)


def run_coordinator(partials: list[BaseModel], model: type[BaseModel], tracker: CostTracker) -> BaseModel:
    settings = get_settings()
    llm_model = settings.models.coordinator
    client = instructor.from_litellm(completion)
    partial_jsons = json.dumps([p.model_dump() for p in partials], indent=2)
    response, comp = client.chat.completions.create_with_completion(
        model=llm_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": f"Merge these partial extractions:\n\n{partial_jsons}"},
        ],
        response_model=model,
        temperature=0,
    )
    tracker.add(llm_model, comp.usage.prompt_tokens, comp.usage.completion_tokens)
    return response
