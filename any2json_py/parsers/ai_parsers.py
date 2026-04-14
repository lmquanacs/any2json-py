from __future__ import annotations
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="instructor")
from pathlib import Path
from pydantic import BaseModel
import instructor
from litellm import completion
from any2json_py.config import get_settings
from any2json_py.parsers.base import BaseParser
from any2json_py.utils.cost_tracker import CostTracker
from any2json_py.utils.logger import info

_SYSTEM_PROMPT = (
    "You are a precise data extraction assistant. "
    "Extract only information explicitly present in the document. "
    "Never infer or hallucinate values. Use null for missing fields."
)


def _extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        import fitz
        doc = fitz.open(str(path))
        return "\n".join(page.get_text() for page in doc)
    if suffix == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(str(path)).paragraphs)
    if suffix == ".csv":
        return path.read_text(encoding="utf-8")
    if suffix in (".yaml", ".yml"):
        return path.read_text(encoding="utf-8")
    if suffix == ".xml":
        return path.read_text(encoding="utf-8")
    raise ValueError(f"AIParser cannot extract text from {suffix}")


def _is_image(path: Path) -> bool:
    return path.suffix.lower() in (".png", ".jpg", ".jpeg")


def _image_message(path: Path) -> list:
    import base64
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return [
        {"type": "text", "text": "Extract data from the following image:"},
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
    ]


class AIParser(BaseParser):
    def parse(self, path: Path, model: type[BaseModel], tracker: CostTracker) -> BaseModel:
        settings = get_settings()
        client = instructor.from_litellm(completion)
        info(f"Single-pass AI extraction via {settings.worker_model}")
        if _is_image(path):
            user_content = _image_message(path)
        else:
            text = _extract_text(path)
            user_content = f"Extract data from the following document:\n\n{text}"
        response, comp = client.chat.completions.create_with_completion(
            model=settings.worker_model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            response_model=model,
            temperature=0,
        )
        tracker.add(settings.worker_model, comp.usage.prompt_tokens, comp.usage.completion_tokens)
        return response
