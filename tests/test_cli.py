from typer.testing import CliRunner
from unittest.mock import patch, MagicMock
from any2json_py.cli import app
import json, tempfile, os

runner = CliRunner()


def _schema_file(tmp_path, query: dict) -> str:
    p = os.path.join(tmp_path, "schema.json")
    with open(p, "w") as f:
        json.dump(query, f)
    return p


def test_missing_schema():
    with tempfile.TemporaryDirectory() as tmp:
        dummy = os.path.join(tmp, "file.csv")
        open(dummy, "w").close()
        result = runner.invoke(app, [dummy])
        assert result.exit_code == 1


def test_dry_run(tmp_path):
    schema = _schema_file(str(tmp_path), {"name": "Person name"})
    dummy = tmp_path / "doc.txt"
    dummy.write_text("John Doe is the CEO.")
    with patch("any2json_py.cli.extract") as mock_extract:
        mock_extract.return_value = {"dry_run": True, "chunks": 1, "estimated_prompt_tokens": 100, "estimated_cost_usd": 0.0}
        result = runner.invoke(app, [str(dummy), "--schema", schema, "--dry-run"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["dry_run"] is True
