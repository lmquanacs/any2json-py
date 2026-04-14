from __future__ import annotations
import asyncio
from pathlib import Path
from pydantic import BaseModel
from any2json_py.config import get_settings
from any2json_py.utils.cost_tracker import CostTracker
from any2json_py.utils.file_helpers import validate_file
from any2json_py.utils.chunker import chunk_text, count_tokens
from any2json_py.utils.logger import info
from any2json_py.parsers.ai_parsers import AIParser, _extract_text, _is_image
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

    if _is_image(path):
        info(f"Vision extraction via {settings.models.image}")
        if dry_run:
            return {"dry_run": True, "chunks": 1, "estimated_prompt_tokens": "N/A (image)", "estimated_cost_usd": "N/A"}
        return AIParser().parse(path, model, tracker)

    text = _extract_text(path)
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
        info(f"Single-pass text extraction")
        return AIParser().parse(path, model, tracker)

    info(f"Multi-agent flow: chunking into ~{settings.chunk_size_tokens}-token pieces")
    chunks = chunk_text(text)
    partials = asyncio.run(_run_workers(chunks, model, tracker))
    return run_coordinator(partials, model, tracker)


async def _run_workers(chunks: list[str], model: type[BaseModel], tracker: CostTracker) -> list[BaseModel]:
    tasks = [run_worker(chunk, model, tracker) for chunk in chunks]
    return await asyncio.gather(*tasks)
