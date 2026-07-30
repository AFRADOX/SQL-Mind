# backend/app/services/execution_service.py

from __future__ import annotations
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import get_settings
from app.core.db_utils import build_dsn
from app.core.exceptions import BadRequestException
from app.services.connection_service import ConnectionService
from app.services.validation_service import ValidationService

settings = get_settings()


class ExecutionService:
    def __init__(self, db: AsyncSession):
        self.conn_service = ConnectionService(db)
        self.validator = ValidationService()

    async def execute(
        self,
        sql: str,
        connection_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> dict:
        conn, password = await self.conn_service.get_connection_with_password(
            connection_id, user_id
        )

        safe_sql = self.validator.validate(sql, conn.db_type)
        dsn = build_dsn(
            conn.db_type, conn.username, password,
            conn.host, conn.port, conn.database_name
        )

        if "limit" not in safe_sql.lower():
            safe_sql = f"{safe_sql} LIMIT {settings.max_rows_returned}"

        try:
            timeout_key = "connect_timeout" if conn.db_type == "mysql" else "timeout"
            engine = create_async_engine(dsn, connect_args={timeout_key: 5})
            async with engine.connect() as target_conn:
                if conn.db_type == "mysql":
                    await target_conn.execute(
                        text(
                            f"SET SESSION MAX_EXECUTION_TIME = "
                            f"{settings.query_timeout_seconds * 1000}"
                        )
                    )
                else:
                    await target_conn.execute(
                        text(
                            f"SET statement_timeout = "
                            f"'{settings.query_timeout_seconds}000'"
                        )
                    )
                result = await target_conn.execute(text(safe_sql))
                columns = list(result.keys())
                rows = [
                    dict(zip(columns, row))
                    for row in result.fetchall()
                ]
            await engine.dispose()

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "sql_executed": safe_sql,
            }
        except Exception as e:
            error_msg = str(e)
            if "statement_timeout" in error_msg:
                raise BadRequestException(
                    f"Query timed out after {settings.query_timeout_seconds}s."
                )
            raise BadRequestException(f"Query execution failed: {error_msg}")