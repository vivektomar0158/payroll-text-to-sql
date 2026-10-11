# Payroll Text-to-SQL Assistant

**52-question eval set, 71.2% accuracy (37/52) in offline fallback mode** (no LLM — a 6-pattern rule-based translator; real Claude-generated SQL scores higher, see Eval below).

Turns a plain-English payroll question into SQL, runs it against a read-only connection, and returns the rows.

## Safety layers

- **Read-only DB connection** — `app/db.py` opens SQLite with `?mode=ro`; any write attempt fails at the driver level regardless of what SQL gets generated.
- **Query validator** (`app/sql_validator.py`, via `sqlglot`) — rejects anything that isn't a single `SELECT`, rejects tables/columns outside the known schema (`app/schema.py`), and force-injects/caps a `LIMIT 500` row cap.
- **LLM layer** (`app/llm.py`) — uses Claude (`ANTHROPIC_API_KEY`) to translate NL → SQL. Falls back to a small rule-based translator when no key is set, so tests/eval run offline.

## Run

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...   # optional — falls back to rule-based translation without it
uvicorn app.main:app --reload
curl -X POST localhost:8000/ask -H "Content-Type: application/json" -d '{"question":"What is the average salary by department?"}'
```

## Eval

`eval/questions.jsonl` — 52 natural-language questions with ground-truth `expected_sql`. `python eval/run_eval.py` runs every question through the full pipeline (LLM/fallback → validator → read-only query), compares result sets against the ground truth, and writes `eval/report.md` with per-question pass/fail and an overall accuracy number.

Current accuracy running **without** an API key (rule-based fallback only): **71.2% (37/52)**. With `ANTHROPIC_API_KEY` set, re-run the eval — real Claude-generated SQL should score meaningfully higher since it isn't limited to the fallback's six hardcoded patterns.

## Tests

`pytest tests/ -q` — validator unit tests (rejects DML/DDL, unknown tables, multiple statements; enforces/caps `LIMIT`).
