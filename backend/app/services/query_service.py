# backend/app/services/query_service.py

from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.history_repo import HistoryRepository
from app.schemas.query import QueryRequest, QueryResponse
from app.services.confidence_service import ConfidenceService
from app.services.execution_service import ExecutionService
from app.services.llm_service import LLMService
from app.services.schema_service import SchemaService
from app.services.validation_service import ValidationService


class QueryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.schema_service = SchemaService(db)
        self.llm_service = LLMService()
        self.validator = ValidationService()
        self.confidence_service = ConfidenceService()
        self.execution_service = ExecutionService(db)
        self.history_repo = HistoryRepository(db)

    async def process_query(
        self,
        request: QueryRequest,
        user_id: uuid.UUID,
        redis=None,
    ) -> QueryResponse:

        # 1. Get schema
        schema = await self.schema_service.get_schema(
            request.connection_id, user_id, redis
        )

        # 2. Call LLM
        llm_result = await self.llm_service.generate_sql(
            request.natural_language, schema
        )

        generated_sql = llm_result.get("sql", "")
        llm_confidence = llm_result.get("confidence", 50)
        explanation = llm_result.get("explanation", "")
        assumptions = llm_result.get("assumptions", [])
        ambiguous = llm_result.get("ambiguous", False)
        clarifying_question = llm_result.get("clarifying_question")

        # 3. Validate
        try:
            safe_sql = self.validator.validate(generated_sql)
            validation_passed = True
        except Exception as e:
            safe_sql = generated_sql
            validation_passed = False
            explanation = f"Validation failed: {e}"

        # 4. Score
        confidence = self.confidence_service.score(
            llm_confidence, safe_sql, schema
        )

        # 5. Execute if requested
        execution_result = None
        was_executed = False
        result_row_count = None
        error_message = None

        should_execute = (
            request.execute
            and validation_passed
            and confidence["level"] != "LOW"
        )

        if should_execute:
            try:
                execution_result = await self.execution_service.execute(
                    safe_sql, request.connection_id, user_id
                )
                was_executed = True
                result_row_count = execution_result.get("row_count")
            except Exception as e:
                error_message = str(e)

        # 6. Save history
        history_entry = await self.history_repo.create(
            user_id=user_id,
            connection_id=request.connection_id,
            nl_query=request.natural_language,
            generated_sql=safe_sql,
            confidence_score=confidence["score"],
            explanation=explanation,
            was_executed=was_executed,
            result_row_count=result_row_count,
            error_message=error_message,
        )

        return QueryResponse(
            query_id=history_entry.id,
            natural_language=request.natural_language,
            generated_sql=safe_sql,
            explanation=explanation,
            confidence=confidence,
            assumptions=assumptions,
            ambiguous=ambiguous,
            clarifying_question=clarifying_question,
            execution_result=execution_result,
        )