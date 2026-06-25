# backend/app/api/v1/routes/connections.py

from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.connection import (
    ConnectionCreateRequest,
    ConnectionResponse,
    ConnectionTestResponse,
)
from app.services.connection_service import ConnectionService

router = APIRouter()


@router.get("/", response_model=list[ConnectionResponse])
async def list_connections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConnectionService(db)
    return await service.list_connections(current_user.id)


@router.post(
    "/",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_connection(
    data: ConnectionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConnectionService(db)
    return await service.create_connection(current_user.id, data)


@router.delete("/{conn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    conn_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConnectionService(db)
    await service.delete_connection(conn_id, current_user.id)


@router.post("/{conn_id}/test", response_model=ConnectionTestResponse)
async def test_connection(
    conn_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConnectionService(db)
    return await service.test_connection(conn_id, current_user.id)