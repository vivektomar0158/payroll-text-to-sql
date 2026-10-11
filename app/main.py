from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.llm import nl_to_sql
from app.sql_validator import validate_and_cap, SQLValidationError
from app.db import run_query

app = FastAPI(title="Payroll Text-to-SQL Assistant")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: str
    sql: str
    rows: list[dict]
    row_count: int


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    raw_sql = nl_to_sql(req.question)
    try:
        safe_sql = validate_and_cap(raw_sql)
    except SQLValidationError as e:
        raise HTTPException(status_code=400, detail=f"Generated SQL rejected: {e}")
    rows = run_query(safe_sql)
    return AskResponse(question=req.question, sql=safe_sql, rows=rows, row_count=len(rows))


@app.get("/health")
async def health():
    return {"status": "ok"}
