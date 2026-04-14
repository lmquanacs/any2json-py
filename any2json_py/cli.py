from __future__ import annotations
import json
from pathlib import Path
from typing import Optional
import typer
from any2json_py.core import extract
from any2json_py.schema import build_model
from any2json_py.utils.cost_tracker import CostTracker
from any2json_py.utils.logger import info, error, success
from any2json_py.exceptions import Any2JsonError

app = typer.Typer(help="Convert any file to structured JSON.")


@app.command()
def main(
    file: Path = typer.Argument(..., help="Input file to extract data from"),
    schema: Optional[Path] = typer.Option(None, "--schema", help="JSON file with {field: description} query"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Estimate cost without running extraction"),
    exact_quotes: bool = typer.Option(False, "--exact-quotes", help="Require source quotes for each extracted value"),
    verbose: bool = typer.Option(False, "--verbose", help="Print usage metadata to stderr"),
) -> None:
    query: dict[str, str] = {}
    if schema:
        query = json.loads(schema.read_text(encoding="utf-8"))

    if not query:
        error("Provide a --schema file with {field: description} pairs.")
        raise typer.Exit(1)

    model = build_model(query, exact_quotes=exact_quotes)
    tracker = CostTracker()

    try:
        result = extract(file, model, tracker, dry_run=dry_run)
    except Any2JsonError as e:
        error(str(e))
        raise typer.Exit(1)

    if isinstance(result, dict):
        typer.echo(json.dumps(result, indent=2))
    else:
        output = {"data": result.model_dump(), "usage": tracker.summary()}
        typer.echo(json.dumps(output, indent=2))

    if verbose:
        info(f"Usage: {tracker.summary()}")
        success("Done.")
