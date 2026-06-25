# backend/app/services/validation_service.py

from __future__ import annotations
import sqlglot
from sqlglot import exp
from app.core.exceptions import UnsafeSQLException

BLOCKED_TYPES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Create,
    exp.AlterTable,
    exp.Command,
)


class ValidationService:
    SYSTEM_SCHEMAS = {"pg_catalog", "information_schema"}

    def validate(self, sql: str) -> str:
        sql = sql.strip().rstrip(";")

        try:
            statements = sqlglot.parse(sql, dialect="postgres")
        except Exception as e:
            raise UnsafeSQLException(f"SQL parsing failed: {e}")

        if not statements or len(statements) != 1:
            raise UnsafeSQLException("Exactly one SQL statement is required.")

        statement = statements[0]

        if not isinstance(statement, exp.Select):
            raise UnsafeSQLException(
                f"Only SELECT statements are allowed. "
                f"Got: {type(statement).__name__}"
            )

        for node in statement.walk():
            if isinstance(node, BLOCKED_TYPES):
                raise UnsafeSQLException(
                    f"Blocked SQL operation: {type(node).__name__}"
                )

        for table in statement.find_all(exp.Table):
            db = table.args.get("db") or {}
            schema_name = str(db).lower() if db else ""
            if schema_name in self.SYSTEM_SCHEMAS:
                raise UnsafeSQLException(
                    f"Access to system schema '{schema_name}' is not allowed."
                )

        return sql