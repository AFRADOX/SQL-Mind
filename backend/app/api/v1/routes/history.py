# backend/app/api/v1/routes/history.py

from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.query import QueryHistoryResponse
from app.repositories.history_repo import HistoryRepository

router = APIRouter()


@router.get("/", response_model=list[QueryHistoryResponse])
async def get_history(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = HistoryRepository(db)
    return await repo.get_by_user(current_user.id, limit, offset)