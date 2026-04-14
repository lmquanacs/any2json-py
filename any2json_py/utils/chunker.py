from __future__ import annotations
import tiktoken
from any2json_py.config import get_settings


def _encoder():
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(_encoder().encode(text))


def chunk_text(text: str) -> list[str]:
    settings = get_settings()
    enc = _encoder()
    tokens = enc.encode(text)
    size = settings.chunk_size_tokens
    overlap = settings.chunk_overlap_tokens
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + size, len(tokens))
        chunks.append(enc.decode(tokens[start:end]))
        if end == len(tokens):
            break
        start += size - overlap
    return chunks
