from __future__ import annotations
import base64
from pathlib import Path


def extract_text(path: Path) -> str:
    """Extract raw text content from any supported file format."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        import fitz
        doc = fitz.open(str(path))
        return "\n".join(page.get_text() for page in doc)
    if suffix == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(str(path)).paragraphs)
    # txt, csv, yaml, yml, xml — read as plain text
    return path.read_text(encoding="utf-8")


def extract_image(path: Path) -> list:
    """Encode image as base64 vision message content."""
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return [
        {"type": "text", "text": "Extract data from the following image:"},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ]


def is_image(path: Path) -> bool:
    return path.suffix.lower() in (".png", ".jpg", ".jpeg")
