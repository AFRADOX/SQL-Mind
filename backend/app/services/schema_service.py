# backend/app/services/schema_service.py

from __future__ import annotations
import json
import uuid
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import get_settings
from app.core.exceptions import BadRequestException
from app.schemas.schema import ColumnMeta, DatabaseSchema, ForeignKeyMeta, TableMeta
from app.services.connection_service import ConnectionService

settings = get_settings()


class SchemaService:
    def __init__(self, db: AsyncSession):
        self.conn_service = ConnectionService(db)

    async def get_schema(
        self,
        connection_id: uuid.UUID,
        user_id: uuid.UUID,
        redis=None,
    ) -> DatabaseSchema:
        cache_key = f"schema:{user_id}:{connection_id}"
        if redis:
            cached = await redis.get(cache_key)
            if cached:
                return DatabaseSchema(**json.loads(cached))

        conn, password = await self.conn_service.get_connection_with_password(
            connection_id, user_id
        )
        dsn = (
            f"postgresql+asyncpg://{conn.username}:{password}"
            f"@{conn.host}:{conn.port}/{conn.database_name}"
        )
        try:
            engine = create_async_engine(dsn, connect_args={"timeout": 10})
            schema = await self._introspect(engine)
            await engine.dispose()
        except Exception as e:
            raise BadRequestException(f"Schema introspection failed: {e}")

        if redis:
            await redis.setex(
                cache_key,
                settings.schema_cache_ttl,
                json.dumps(schema.model_dump()),
            )
        return schema

    async def _introspect(self, engine) -> DatabaseSchema:
        tables = []
        async with engine.connect() as conn:
            table_names = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_table_names()
            )
            for table_name in table_names:
                def _get_table_info(sync_conn, tname=table_name):
                    insp = inspect(sync_conn)
                    return (
                        insp.get_columns(tname),
                        insp.get_foreign_keys(tname),
                        insp.get_pk_constraint(tname),
                    )

                raw_cols, raw_fks, pk_constraint = await conn.run_sync(
                    _get_table_info
                )
                pk_cols = pk_constraint.get("constrained_columns", [])

                columns = [
                    ColumnMeta(
                        name=col["name"],
                        type=str(col["type"]),
                        nullable=col.get("nullable", True),
                        is_primary_key=col["name"] in pk_cols,
                    )
                    for col in raw_cols
                ]

                fks = [
                    ForeignKeyMeta(
                        column=local_col,
                        references_table=fk["referred_table"],
                        references_column=fk["referred_columns"][i],
                    )
                    for fk in raw_fks
                    for i, local_col in enumerate(fk["constrained_columns"])
                ]

                sample_values = {}
                for col in columns:
                    if any(
                        t in col.type.upper()
                        for t in ["VARCHAR", "TEXT", "CHAR"]
                    ):
                        try:
                            result = await conn.execute(
                                text(
                                    f'SELECT DISTINCT "{col.name}" FROM '
                                    f'"{table_name}" WHERE "{col.name}" '
                                    f'IS NOT NULL LIMIT 5'
                                )
                            )
                            vals = [str(row[0]) for row in result.fetchall()]
                            if vals:
                                sample_values[col.name] = vals
                        except Exception:
                            pass

                tables.append(TableMeta(
                    name=table_name,
                    columns=columns,
                    foreign_keys=fks,
                    sample_values=sample_values,
                ))

        return DatabaseSchema(tables=tables, total_tables=len(tables))

    @staticmethod
    def schema_to_prompt_string(schema: DatabaseSchema) -> str:
        lines = []
        for table in schema.tables:
            lines.append(f"Table: {table.name}")
            for col in table.columns:
                pk = " PK" if col.is_primary_key else ""
                null = " NOT NULL" if not col.nullable else ""
                samples = ""
                if col.name in table.sample_values:
                    vals = ", ".join(
                        f"'{v}'" for v in table.sample_values[col.name]
                    )
                    samples = f" [sample: {vals}]"
                lines.append(f"  - {col.name} ({col.type}{pk}{null}{samples})")
            for fk in table.foreign_keys:
                lines.append(
                    f"  FK: {fk.column} → "
                    f"{fk.references_table}.{fk.references_column}"
                )
            lines.append("")
        return "\n".join(lines)