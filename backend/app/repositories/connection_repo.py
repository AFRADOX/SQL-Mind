# backend/app/repositories/connection_repo.py

from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.connection import DatabaseConnection


class ConnectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_user(
        self, user_id: uuid.UUID
    ) -> list[DatabaseConnection]:
        result = await self.db.execute(
            select(DatabaseConnection)
            .where(DatabaseConnection.user_id == user_id)
            .order_by(DatabaseConnection.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(
        self, conn_id: uuid.UUID, user_id: uuid.UUID
    ) -> DatabaseConnection | None:
        result = await self.db.execute(
            select(DatabaseConnection).where(
                DatabaseConnection.id == conn_id,
                DatabaseConnection.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: uuid.UUID,
        name: str,
        host: str,
        port: int,
        database_name: str,
        username: str,
        encrypted_password: str,
    ) -> DatabaseConnection:
        conn = DatabaseConnection(
            user_id=user_id,
            name=name,
            host=host,
            port=port,
            database_name=database_name,
            username=username,
            encrypted_password=encrypted_password,
        )
        self.db.add(conn)
        await self.db.flush()
        return conn

    async def delete(self, conn: DatabaseConnection) -> None:
        await self.db.delete(conn)
        await self.db.flush()