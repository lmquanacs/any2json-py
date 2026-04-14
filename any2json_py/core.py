from __future__ import annotations
import asyncio
from pathlib import Path
from pydantic import BaseModel
from any2json_py.config import get_settings
from any2json_py.utils.cost_tracker import CostTracker
from any2json_py.utils.file_helpers import validate_file
from any2json_py.utils.chunker import chunk_text, count_tokens
from any2json_py.utils.logger import info
from any2json_py.parsers.content import extract_text, extract_image, is_image
from any2json_py.agents.worker import run_worker
from any2json_py.agents.coordinator import run_coordinator


def extract(
    path: Path,
    model: type[BaseModel],
    tracker: CostTracker,
    dry_run: bool = False,
) -> BaseModel | dict:
    validate_file(path)
    settings = get_settings()

    # Image — single worker with vision content
    if is_image(path):
        info(f"Vision extraction via {settings.models.image}")
        if dry_run:
            return {"dry_run": True, "chunks": 1, "estimated_prompt_tokens": "N/A (image)", "estimated_cost_usd": "N/A"}
        content = extract_image(path)
        return asyncio.run(run_worker(content, model, tracker, llm_model=settings.models.image))

    # Text-based — extract content then route by token count
    text = extract_text(path)
    token_count = count_tokens(text)
    info(f"Document tokens: {token_count:,}")

    if dry_run:
        chunks = chunk_text(text)
        estimated_prompt = token_count + len(chunks) * 500
        return {
            "dry_run": True,
            "chunks": len(chunks),
            "estimated_prompt_tokens": estimated_prompt,
            "estimated_cost_usd": round(estimated_prompt / 1_000_000 * 0.075, 6),
        }

    if token_count <= settings.context_threshold_tokens:
        # Single worker — full document fits in context
        info(f"Single worker via {settings.models.text}")
        return asyncio.run(run_worker(text, model, tracker, llm_model=settings.models.text))

    # Multi-agent — chunk and run workers in parallel, then coordinate
    info(f"Multi-agent flow via {settings.models.worker} workers + {settings.models.coordinator} coordinator")
    chunks = chunk_text(text)
    info(f"Split into {len(chunks)} chunks")
    partials = asyncio.run(_run_workers(chunks, model, tracker))
    return run_coordinator(partials, model, tracker)


async def _run_workers(chunks: list[str], model: type[BaseModel], tracker: CostTracker) -> list[BaseModel]:
    tasks = [run_worker(chunk, model, tracker) for chunk in chunks]
    return await asyncio.gather(*tasks)
