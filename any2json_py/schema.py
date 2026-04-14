from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field, create_model

_NULL_INSTRUCTION = "If this information is not explicitly found in the document, return null."


def build_model(query: dict[str, Any], exact_quotes: bool = False) -> type[BaseModel]:
    """Build a Pydantic model from a query dict.

    Simple field:   {"invoice_number": "The invoice number"}
    Array field:    {"line_items": {"description": "...", "type": "array", "fields": {...}}}
    """
    fields: dict[str, Any] = {}
    for field_name, definition in query.items():
        if isinstance(definition, dict) and definition.get("type") == "array":
            item_model = _build_item_model(field_name, definition["fields"])
            desc = definition.get("description", f"List of {field_name}.")
            fields[field_name] = (Optional[list[item_model]], Field(None, description=f"{desc} {_NULL_INSTRUCTION}"))
        else:
            description = definition if isinstance(definition, str) else definition.get("description", field_name)
            full_desc = f"{description}. {_NULL_INSTRUCTION}"
            if exact_quotes:
                fields[field_name] = (Optional[str], Field(None, description=full_desc))
                fields[f"{field_name}__quote"] = (Optional[str], Field(None, description=f"Exact quote from source text supporting '{field_name}'."))
            else:
                fields[field_name] = (Optional[str], Field(None, description=full_desc))
    return create_model("ExtractionResult", **fields)


def _build_item_model(parent_name: str, fields: dict[str, str]) -> type[BaseModel]:
    item_fields = {
        k: (Optional[str], Field(None, description=f"{v}. {_NULL_INSTRUCTION}"))
        for k, v in fields.items()
    }
    return create_model(f"{parent_name.title()}Item", **item_fields)
