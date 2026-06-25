# backend/app/repositories/history_repo.py

from __future__ import annotations
import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.query_history import QueryHistory


class HistoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: uuid.UUID,
        connection_id: uuid.UUID,
        nl_query: str,
        generated_sql: str,
        confidence_score: float,
        explanation: str | None,
        was_executed: bool,
        result_row_count: int | None,
        error_message: str | None,
    ) -> QueryHistory:
        entry = QueryHistory(
            user_id=user_id,
            connection_id=connection_id,
            nl_query=nl_query,
            generated_sql=generated_sql,
            confidence_score=Decimal(str(round(confidence_score, 2))),
            explanation=explanation,
            was_executed=was_executed,
            result_row_count=result_row_count,
            error_message=error_message,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[QueryHistory]:
        result = await self.db.execute(
            select(QueryHistory)
            .where(QueryHistory.user_id == user_id)
            .order_by(QueryHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_by_id(
        self,
        entry_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> QueryHistory | None:
        result = await self.db.execute(
            select(QueryHistory).where(
                QueryHistory.id == entry_id,
                QueryHistory.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()