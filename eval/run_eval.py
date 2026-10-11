"""Runs every question in questions.jsonl through nl_to_sql + the validator, compares the
result set against the ground-truth expected_sql, and writes an accuracy report."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.llm import nl_to_sql
from app.sql_validator import validate_and_cap, SQLValidationError
from app.db import run_query

QUESTIONS_PATH = Path(__file__).parent / "questions.jsonl"
REPORT_PATH = Path(__file__).parent / "report.md"


def normalize(rows: list[dict]) -> set:
    return {tuple(sorted(r.items())) for r in rows}


def main():
    questions = [json.loads(line) for line in QUESTIONS_PATH.read_text().splitlines() if line.strip()]
    results = []
    for q in questions:
        expected_rows = run_query(q["expected_sql"])
        try:
            raw_sql = nl_to_sql(q["question"])
            safe_sql = validate_and_cap(raw_sql)
            actual_rows = run_query(safe_sql)
            match = normalize(actual_rows) == normalize(expected_rows)
            error = None
        except SQLValidationError as e:
            match, actual_rows, error = False, [], str(e)
        results.append({"id": q["id"], "question": q["question"], "match": match, "error": error})

    total = len(results)
    correct = sum(1 for r in results if r["match"])
    accuracy = correct / total if total else 0.0

    lines = [
        "# Text-to-SQL Eval Report", "",
        f"**Accuracy: {correct}/{total} = {accuracy:.1%}**", "",
        "| id | question | match | error |", "|---|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['id']} | {r['question']} | {'✅' if r['match'] else '❌'} | {r['error'] or ''} |")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Accuracy: {correct}/{total} = {accuracy:.1%}")
    print(f"Report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
