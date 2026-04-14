# any2json-py Flow Diagram

```mermaid
flowchart TD
    A([User: file + schema]) --> B[cli.py\nbuild_model + CostTracker]
    B --> C[core.py\nvalidate_file]
    C --> D{File type?}

    D -->|image\n.png .jpg| E[ai_parsers.py\nvision base64]
    D -->|text-based\n.csv .yaml .xml .pdf .txt .docx| F[ai_parsers.py\nextract as plain text]

    F --> G[chunker.py\ncount_tokens]
    G --> H{tokens >\nthreshold?}
    H -->|No\nsingle-pass| E
    H -->|Yes\nmulti-agent| I[chunker.py\nsplit into chunks]

    I --> J[worker.py × N\nparallel asyncio]
    J -->|partial JSONs| K[coordinator.py\nmerge + validate]

    E --> L[cost_tracker.py\nrecord usage]
    K --> L

    L --> M([JSON output\n+ usage metadata])
```

## Key Decision Points

| Condition | Path |
|---|---|
| `.png` / `.jpg` | Vision API, base64 encoded |
| any text-based format ≤ threshold | Single-pass AI extraction |
| any text-based format > threshold | Multi-agent: workers → coordinator |

## Token Threshold

Default: `CONTEXT_THRESHOLD_TOKENS=100000`. Override in `.env` to force multi-agent flow for testing.
