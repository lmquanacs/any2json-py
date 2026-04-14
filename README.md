# any2json-py

Convert any file format into structured JSON using LLMs. Supports text, PDF, DOCX, images, CSV, YAML, and XML — all routed through an AI extraction pipeline with multi-agent support for large documents.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and add your API key
```

## Configuration

Models are configured in `config.yml`:

```yaml
models:
  text: openai/gpt-4o-mini      # single-pass text extraction
  image: openai/gpt-4o          # vision extraction
  worker: openai/gpt-4o-mini    # chunk extraction (multi-agent)
  coordinator: openai/gpt-4o    # merge worker outputs (multi-agent)

limits:
  max_file_size_mb: 50
  context_threshold_tokens: 100000
  chunk_size_tokens: 8000
  chunk_overlap_tokens: 200
```

Model names follow [LiteLLM format](https://docs.litellm.ai/docs/providers): `provider/model-name`. Swap any model without code changes.

## Usage

### CLI

```bash
# Text / PDF / DOCX
any2json-py report.pdf --schema schema.json

# Image
any2json-py photo.png --schema schema.json

# Dry run — estimate cost before running
any2json-py massive_report.pdf --schema schema.json --dry-run

# With exact quotes for high-stakes extraction
any2json-py report.pdf --schema schema.json --exact-quotes --verbose > output.json
```

### Schema format

A schema is a JSON file mapping field names to descriptions:

```json
{
  "job": "The job title or position name",
  "company": "The name of the hiring company",
  "summary": "A concise summary of the document"
}
```

Field descriptions guide the LLM — be explicit to avoid null returns.

### Python library

```python
from pathlib import Path
from any2json_py import extract, build_model, CostTracker

model = build_model({
    "job": "The job title",
    "company": "The hiring company"
})

tracker = CostTracker()
result = extract(Path("report.pdf"), model, tracker)

print(result.model_dump())
print(tracker.summary())
```

## Supported Formats

| Format | Extensions |
|---|---|
| Text | `.txt`, `.csv`, `.yaml`, `.xml` |
| Documents | `.pdf`, `.docx` |
| Images | `.png`, `.jpg`, `.jpeg` |

All formats are routed through the AI pipeline. Binary formats (PDF, DOCX) are converted to text first via local parsers, then passed to the LLM for schema extraction.

## Supported Providers

Any provider supported by LiteLLM works out of the box — set the model in `config.yml` and add the corresponding API key to `.env`:

| Provider | Example model | Env var |
|---|---|---|
| OpenAI | `openai/gpt-4o` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| Google Gemini | `gemini/gemini-1.5-pro` | `GEMINI_API_KEY` |
| AWS Bedrock | `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0` | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` |
| Azure OpenAI | `azure/my-deployment` | `AZURE_API_KEY` + `AZURE_API_BASE` |
