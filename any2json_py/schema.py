from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, create_model

_NULL_INSTRUCTION = "If this information is not explicitly found in the document, return null."


def build_model(query: dict[str, str], exact_quotes: bool = False) -> type[BaseModel]:
    """Build a Pydantic model from a {field: description} query dict."""
    fields: dict[str, Any] = {}
    for field_name, description in query.items():
        full_desc = f"{description}. {_NULL_INSTRUCTION}"
        if exact_quotes:
            value_field = (Optional[str], _field(None, full_desc))
            quote_field = (Optional[str], _field(None, f"Exact quote from source text supporting the value of '{field_name}'."))
            fields[field_name] = value_field
            fields[f"{field_name}__quote"] = quote_field
        else:
            fields[field_name] = (Optional[str], _field(None, full_desc))
    return create_model("ExtractionResult", **fields)


def _field(default: Any, description: str):
    from pydantic import Field
    return Field(default, description=description)
