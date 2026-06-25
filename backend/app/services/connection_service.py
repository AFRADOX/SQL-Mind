# backend/app/services/connection_service.py

from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException
from app.core.security import decrypt, encrypt
from app.repositories.connection_repo import ConnectionRepository
from app.schemas.connection import ConnectionCreateRequest, ConnectionTestResponse


class ConnectionService:
    def __init__(self, db: AsyncSession):
        self.repo = ConnectionRepository(db)

    async def list_connections(self, user_id: uuid.UUID):
        return await self.repo.get_all_by_user(user_id)

    async def create_connection(
        self, user_id: uuid.UUID, data: ConnectionCreateRequest
    ):
        encrypted = encrypt(data.password)
        return await self.repo.create(
            user_id=user_id,
            name=data.name,
            host=data.host,
            port=data.port,
            database_name=data.database_name,
            username=data.username,
            encrypted_password=encrypted,
        )

    async def delete_connection(
        self, conn_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        conn = await self.repo.get_by_id(conn_id, user_id)
        if not conn:
            raise NotFoundException("Connection not found.")
        await self.repo.delete(conn)

    async def test_connection(
        self, conn_id: uuid.UUID, user_id: uuid.UUID
    ) -> ConnectionTestResponse:
        conn = await self.repo.get_by_id(conn_id, user_id)
        if not conn:
            raise NotFoundException("Connection not found.")
        plain_password = decrypt(conn.encrypted_password)
        dsn = (
            f"postgresql+asyncpg://{conn.username}:{plain_password}"
            f"@{conn.host}:{conn.port}/{conn.database_name}"
        )
        try:
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import create_async_engine
            test_engine = create_async_engine(dsn, connect_args={"timeout": 5})
            async with test_engine.connect() as c:
                await c.execute(text("SELECT 1"))
            await test_engine.dispose()
            return ConnectionTestResponse(
                success=True, message="Connection successful."
            )
        except Exception as e:
            return ConnectionTestResponse(success=False, message=str(e))

    async def get_connection_with_password(
        self, conn_id: uuid.UUID, user_id: uuid.UUID
    ):
        conn = await self.repo.get_by_id(conn_id, user_id)
        if not conn:
            raise NotFoundException("Connection not found.")
        plain_password = decrypt(conn.encrypted_password)
        return conn, plain_password