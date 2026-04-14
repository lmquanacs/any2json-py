# Project Specification: any2json-py

## 1. Overview

any2json-py is a universal data extraction tool (CLI and Python Library) designed to convert any file format into a structured JSON object. It bridges the gap between structured files (CSV, XML, YAML) and unstructured/visual files (PDFs, Images, Word Documents) by utilizing standard local parsers for the former and Multimodal Large Language Models (LLMs) for the latter.

**Unique Selling Proposition (USP):** The user can pass a "Contextual Query" (mapping field names to explicit descriptions) or a strict JSON schema. Furthermore, it employs a **Multi-Agent Architecture** to safely chunk and process massive files that exceed standard LLM context windows, guided by a central Coordinator model.

## 2. Core Features

* **Format Agnostic:** Handles .csv, .yaml, .xml, .pdf, .png, .jpg, .docx, .txt. All formats are routed through the AI pipeline — structured files (.csv, .yaml, .xml) are serialized as plain text and passed to the LLM for schema-aware extraction.
* **Contextual Schema Enforcement:** Uses Pydantic to guarantee the output matches the user's requested schema, utilizing descriptions to guide the LLM's extraction logic. Field descriptions must be explicit and unambiguous to avoid null returns — e.g. prefer `"The full job title including seniority level"` over `"The title"`.
* **Smart Routing:** Automatically detects the file type and routes accordingly: images use the vision API, all other formats are extracted as text and routed based on token count (single-pass vs. multi-agent).
* **File Size & Context Management:** Enforces configurable file size limits and intelligently chunks large documents.
* **Multi-Agent Orchestration:** For large files, dispatches document chunks to parallel "Worker" agents, whose outputs are merged and validated by a "Coordinator" agent.
* **Configurable Models:** Every agent's underlying model (Coordinator vs. Worker) can be configured independently for cost/performance optimization.
* **Cost & Token Tracking:** Aggregates prompt and completion tokens across all agents, calculating estimated API costs. Model names use LiteLLM format (`provider/model`) — the cost table strips the provider prefix for lookup.
* **Dry-Run Mode:** Allows users to estimate token usage and costs *before* executing live API calls on massive documents.
* **Dual Interface:** Can be run via the command line or imported as a standard Python module.

## 3. Project Directory Structure

The project follows standard modern Python packaging guidelines (using pyproject.toml).

```text
any2json-py/
├── .env                      # Local environment variables (API keys, never committed)
├── .env.example              # Example environment variables (API keys)
├── .gitignore                # Git ignore rules
├── venv/                     # Python virtual environment (never committed)
├── README.md                 # Project documentation
├── pyproject.toml            # Dependencies and package metadata
├── any2json_py/              # Main application package
│   ├── __init__.py           # Exposes main library functions
│   ├── cli.py                # CLI interface commands (Typer/Click)
│   ├── core.py               # The Orchestrator: routes files to parsers
│   ├── config.py             # Configuration management (Model selection, limits)
│   ├── exceptions.py         # Custom error handling
│   ├── schema.py             # Dynamic Pydantic schema generation logic
│   ├── agents/               # Multi-Agent Orchestration
│   │   ├── __init__.py
│   │   ├── coordinator.py    # Merges worker outputs and enforces final schema
│   │   └── worker.py         # Extracts data from specific document chunks
│   ├── parsers/              # Sub-package for all parsing strategies
│   │   ├── __init__.py
│   │   ├── base.py           # Abstract Base Class for parsers
│   │   ├── local_parsers.py  # CSV, YAML, XML logic
│   │   └── ai_parsers.py    # Instructor + LLM logic for unstructured files
│   └── utils/
│       ├── file_helpers.py   # File type detection, MIME types, Size limits
│       ├── chunker.py        # Semantic text/PDF chunking logic
│       ├── cost_tracker.py   # Token counting and cost estimation logic
│       └── logger.py         # Standardized console logging
└── tests/                    # Pytest directory
    ├── test_cli.py
    ├── test_agents.py
    └── test_parsers.py
```

## 4. Architecture & Data Flow

1. **Input & Validation Stage:** User provides a file and schema. file_helpers.py checks the file size against the configured limit.
2. **Dry-Run Check:** If --dry-run is enabled, cost_tracker.py uses tiktoken to estimate the number of chunks and total prompt tokens, printing an estimated cost report and exiting early.
3. **Dynamic Modeling:** The schema.py module converts the user's query into a strict Pydantic model.
4. **Router & Chunker (core.py):**
   * *If structured (e.g., CSV):* Routes directly to local_parsers.py.
   * *If unstructured (e.g., PDF/Text) and SMALL:* Routes to a standard single-pass ai_parsers.py.
   * *If unstructured and LARGE (Exceeds Context Threshold):* Triggers the **Multi-Agent Flow**.
5. **Multi-Agent Flow (Large Files):**
   * **Chunking:** chunker.py splits the document into overlapping semantic chunks.
   * **Workers:** The worker.py agent processes each chunk. As each worker finishes, it reports its token usage to the cost_tracker.py singleton.
   * **Coordinator:** The coordinator.py agent receives partial JSONs, merges them, and logs its own token usage to the tracker.
6. **Output Stage:** The parser returns the validated Pydantic model *along with* the aggregated usage metadata, which cli.py dumps to standard output.

## 5. Hallucination Mitigation Strategy (CRITICAL)

To ensure the tool is safe for enterprise use, the AI parsing pipeline must implement a defense-in-depth approach against LLM hallucinations:

1. **Zero Temperature:** All ai_parsers.py and agent API calls will hardcode temperature=0 (or the lowest supported by the model) to enforce deterministic, non-creative extraction.
2. **Strict Null Allowances:** The dynamic schema generator (schema.py) will automatically append instructions to the LLM indicating: *"If this information is not explicitly found in the document, return null."*
3. **The 'Exact Quote' Pattern (Optional Flag):** For high-stakes data, users can enable an --exact-quotes flag. The dynamically generated Pydantic schema will force the LLM to output both the value AND an exact_quote from the source text verifying the value.
4. **Coordinator Verification:** The coordinator.py agent's system prompt strictly prohibits inferring missing data when merging worker JSONs.

## 6. Technology Stack

* **Language:** Python 3.10+
* **CLI Framework:** Typer or Click.
* **Data Validation:** Pydantic (V2).
* **AI Orchestration:** Instructor (guarantees JSON compliance) + LiteLLM (unified interface over OpenAI, Gemini, Anthropic, and 100+ providers). Model names follow LiteLLM format: `openai/gpt-4o`, `gemini/gemini-1.5-pro`, `anthropic/claude-3-5-sonnet`, etc.
* **Concurrency:** Native Python asyncio (for parallel Worker agent execution).
* **Text Processing:** tiktoken (for accurate token counting, chunking, and cost estimation).
* **Local Parsing:** PyYAML, xmltodict, standard csv library — used only to read raw file content as text before passing to the LLM. No direct key mapping.
* **Testing:** pytest and pytest-mock (for safe agent simulation).

## 6a. LiteLLM Integration

LiteLLM is the LLM abstraction layer. It provides a single OpenAI-compatible interface across all providers, so swapping models requires only a config change — no code changes.

**Model name format:** `provider/model-name`

| Provider | Example model string |
|---|---|
| OpenAI | `openai/gpt-4o`, `openai/gpt-4o-mini` |
| Anthropic | `anthropic/claude-3-5-sonnet-20241022` |
| Google Gemini | `gemini/gemini-1.5-pro`, `gemini/gemini-1.5-flash` |
| AWS Bedrock | `bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0` |
| Azure OpenAI | `azure/my-deployment-name` |

**Required env vars per provider:**

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
GEMINI_API_KEY=...

# AWS Bedrock (uses boto3 credentials)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION_NAME=us-east-1

# Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://my-resource.openai.azure.com
AZURE_API_VERSION=2024-02-01
```

**Switching models:** Update `COORDINATOR_MODEL` and `WORKER_MODEL` in `.env` — no code changes required.

```bash
# Use a cheaper worker, more capable coordinator
WORKER_MODEL=openai/gpt-4o-mini
COORDINATOR_MODEL=openai/gpt-4o

# Or switch entirely to Anthropic
WORKER_MODEL=anthropic/claude-3-haiku-20240307
COORDINATOR_MODEL=anthropic/claude-3-5-sonnet-20241022
```

**Cost tracking:** The `cost_tracker.py` table maps bare model names (e.g. `gpt-4o-mini`) to per-token rates. The `provider/` prefix is stripped automatically before lookup.

## 7. Interface Design

### Command Line Interface (CLI)

**Example 1: The Dry Run (Cost Estimation)**

Check how much a large job will cost before running it.

```bash
any2json-py massive_report.pdf --schema report_schema.json --dry-run
```

**Example 2: Safe Execution with Usage Reporting**

```bash
any2json-py massive_report.pdf --schema report_schema.json --exact-quotes --verbose > output.json
```

## 8. Local Development Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment variables
cp .env.example .env
# Edit .env and fill in your API keys
```

The `.env` file holds secrets (e.g. `OPENAI_API_KEY`, `GEMINI_API_KEY`) and must never be committed. It is loaded at runtime via `python-dotenv` in config.py.

## 9. Development Phases (Roadmap)

* **Phase 1: Foundation (MVP)**
  * Setup pyproject.toml and CLI scaffolding.
  * Implement local parsers and basic file routing.
* **Phase 2: AI Integration & Anti-Hallucination**
  * Integrate instructor with LiteLLM.
  * Build schema.py with Zero Temp and Strict Nulls built-in.
  * Implement Exact Quote functionality.
* **Phase 3: File Management & Chunking**
  * Implement file size validation (file_helpers.py).
  * Implement chunker.py and cost_tracker.py for token estimation.
* **Phase 4: Multi-Agent Orchestration**
  * Build asynchronous worker.py logic.
  * Build coordinator.py logic.
  * Write mock pytest suites simulating large file chunking.
