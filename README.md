# any2json-py

Convert any file format into structured JSON using local parsers and LLMs.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Usage

```bash
# Dry run (cost estimate)
any2json-py massive_report.pdf --schema schema.json --dry-run

# Full extraction
any2json-py report.pdf --schema schema.json --exact-quotes --verbose > output.json
```

## Supported Formats

Local parsers: `.csv`, `.yaml`, `.xml`
AI parsers: `.pdf`, `.png`, `.jpg`, `.docx`, `.txt`
