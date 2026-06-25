# backend/app/schemas/query.py

from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    connection_id: uuid.UUID
    natural_language: str = Field(..., min_length=3, max_length=1000)
    execute: bool = False


class ConfidenceBreakdown(BaseModel):
    llm_self_reported: float
    schema_grounding: float
    complexity_score: float


class ConfidenceResult(BaseModel):
    score: float
    level: str
    auto_execute: bool
    breakdown: ConfidenceBreakdown


class QueryResponse(BaseModel):
    query_id: uuid.UUID
    natural_language: str
    generated_sql: str
    explanation: str
    confidence: ConfidenceResult
    assumptions: list[str]
    ambiguous: bool
    clarifying_question: str | None
    execution_result: dict | None = None


class QueryHistoryResponse(BaseModel):
    id: uuid.UUID
    nl_query: str
    generated_sql: str
    confidence_score: float
    explanation: str | None
    was_executed: bool
    result_row_count: int | None
    created_at: datetime

    model_config = {"from_attributes": True}