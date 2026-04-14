import tempfile, os, csv
import pytest
from pydantic import BaseModel
from typing import Optional
from any2json_py.parsers.local_parsers import LocalParser
from any2json_py.utils.cost_tracker import CostTracker


class PersonModel(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None


def test_csv_parser():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "age"])
        writer.writeheader()
        writer.writerow({"name": "Alice", "age": "30"})
        path = f.name
    try:
        from pathlib import Path
        result = LocalParser().parse(Path(path), PersonModel, CostTracker())
        assert result.name == "Alice"
        assert result.age == "30"
    finally:
        os.unlink(path)


def test_yaml_parser():
    import yaml
    from pathlib import Path
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"name": "Bob", "age": "25"}, f)
        path = f.name
    try:
        result = LocalParser().parse(Path(path), PersonModel, CostTracker())
        assert result.name == "Bob"
    finally:
        os.unlink(path)


def test_xml_parser():
    from pathlib import Path
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write("<root><name>Carol</name><age>40</age></root>")
        path = f.name
    try:
        result = LocalParser().parse(Path(path), PersonModel, CostTracker())
        assert result.name == "Carol"
    finally:
        os.unlink(path)
