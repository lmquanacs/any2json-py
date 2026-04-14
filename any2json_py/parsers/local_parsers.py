from __future__ import annotations
import csv
import json
from pathlib import Path
from pydantic import BaseModel
import yaml
import xmltodict
from any2json_py.parsers.base import BaseParser
from any2json_py.utils.cost_tracker import CostTracker


class LocalParser(BaseParser):
    def parse(self, path: Path, model: type[BaseModel], tracker: CostTracker) -> BaseModel:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            data = _parse_csv(path)
        elif suffix in (".yaml", ".yml"):
            data = _parse_yaml(path)
        elif suffix == ".xml":
            data = _parse_xml(path)
        else:
            raise ValueError(f"LocalParser cannot handle {suffix}")
        # Flatten single-row CSV or map top-level keys to model fields
        if isinstance(data, list) and len(data) == 1:
            data = data[0]
        if isinstance(data, list):
            data = {"items": json.dumps(data)}
        # xmltodict wraps content in a root key — unwrap single-key dicts
        if isinstance(data, dict) and len(data) == 1:
            inner = next(iter(data.values()))
            if isinstance(inner, dict):
                data = inner
        return model.model_validate({k: str(v) for k, v in data.items()})


def _parse_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _parse_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_xml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return xmltodict.parse(f.read())
