# Lessons Learned

## 1. Schema design is the hardest part

The LLM is only as good as the field descriptions. Vague descriptions like `"The title"` return null. Explicit ones like `"The full job title including seniority level"` work reliably.

This is the #1 thing users will struggle with. Field descriptions should answer: *"If I were reading this document, what exact text would I look for?"*

## 2. All formats are just text

The initial instinct to have "local parsers" for CSV/YAML/XML was wrong. Once you accept that everything is just text going into an LLM, the architecture becomes much simpler.

Binary formats (PDF, DOCX) are the only special case — they need a conversion step first. Everything else is a plain text read.

## 3. Provider abstraction pays off immediately

Switching from `google-generativeai` to LiteLLM took one afternoon but unlocked every provider. The `config.yml` approach means you can swap `gpt-4o-mini` for `claude-3-haiku` with one line change.

Should have started here from day one.

## 4. Per-task model config matters

Using the same model for everything is wasteful:

- Vision needs a strong model (`gpt-4o`)
- Workers can be cheap (`gpt-4o-mini`)
- Coordinator needs to be reliable (`gpt-4o`)

Separating them in `config.yml` gives real cost control without touching code.

## 5. Hallucination mitigation needs to be structural

`temperature=0` and null instructions in the schema are not enough on their own. The `--exact-quotes` pattern is the only way to actually audit what the LLM extracted vs. invented.

For production use this should probably be on by default.

## 6. Cost tracking is a first-class feature

Not an afterthought. The `provider/model` prefix stripping bug (`openai/gpt-4o-mini` → `gpt-4o-mini`) showed that if cost tracking is wrong, users lose trust in the tool entirely.

Cost visibility is what makes the tool safe to use at scale.

## 7. Test with real documents early

The Bunnings invoice and the AI Engineer job posting revealed things unit tests never would:

- `line_items` needed to be an array, not a flat string
- The `title` field returned null due to a vague description
- Vision API works but costs ~14k tokens per image

Real documents expose edge cases that synthetic test data never will.

## 8. The multi-agent flow is the biggest unknown

Workers and coordinator are architecturally sound but have not been tested on a real large document. The chunking, parallel execution, and merge logic all need a real stress test with a 100+ page document.

This is the highest risk area before production use.
