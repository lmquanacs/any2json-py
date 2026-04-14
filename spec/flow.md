# any2json-py Flow Diagram

```mermaid
flowchart TD
    A([User: file + schema]) --> B[cli.py\nbuild_model + CostTracker]
    B --> C[core.py\nvalidate_file]
    C --> D{File type?}

    D -->|image\n.png .jpg| E[parsers/content.py\nbase64 encode]
    D -->|text-based\n.csv .yaml .xml .pdf .txt .docx| F[parsers/content.py\nextract as plain text]

    F --> G[chunker.py\ncount_tokens]
    G --> H{tokens >\nthreshold?}

    H -->|No\n1 chunk| I[worker.py × 1]
    H -->|Yes\nN chunks| J[chunker.py\nsplit into chunks]
    E --> I

    J --> K[worker.py × N\nparallel asyncio]
    K -->|partial JSONs| L[coordinator.py\nmerge + validate]

    I --> M[cost_tracker.py\nrecord usage]
    L --> M

    M --> N([JSON output\n+ usage metadata])
```

## Key Decision Points

| Condition | Agent flow |
|---|---|
| image | 1 worker (vision message) |
| text-based ≤ threshold | 1 worker (full content) |
| text-based > threshold | N workers in parallel → coordinator |

The worker is the single unit of LLM execution in all cases. The coordinator is only invoked when there are multiple workers.

## Token Threshold

Default: `context_threshold_tokens: 100000` in `config.yml`. Lower it to force multi-agent flow for testing.
