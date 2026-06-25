# backend/app/api/v1/routes/query.py

from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import QueryService

router = APIRouter()


@router.post("/", response_model=QueryResponse)
async def generate_query(
    request: QueryRequest,
    req: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = QueryService(db)
    redis = getattr(req.app.state, "redis", None)
    return await service.process_query(
        request, current_user.id, redis
    )