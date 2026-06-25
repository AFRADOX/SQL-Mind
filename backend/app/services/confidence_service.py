# backend/app/services/confidence_service.py

from __future__ import annotations
import sqlglot
from sqlglot import exp
from app.schemas.schema import DatabaseSchema


class ConfidenceService:
    def score(
        self,
        llm_confidence: int,
        generated_sql: str,
        schema: DatabaseSchema,
    ) -> dict:
        grounding = self._grounding_score(generated_sql, schema)
        complexity = self._complexity_score(generated_sql)
        llm_norm = llm_confidence / 100.0

        composite = (
            0.30 * llm_norm +
            0.40 * grounding +
            0.30 * complexity
        )
        composite_pct = round(composite * 100, 2)

        if composite_pct >= 80:
            level = "HIGH"
            auto_execute = True
        elif composite_pct >= 55:
            level = "MEDIUM"
            auto_execute = False
        else:
            level = "LOW"
            auto_execute = False

        return {
            "score": composite_pct,
            "level": level,
            "auto_execute": auto_execute,
            "breakdown": {
                "llm_self_reported": llm_confidence,
                "schema_grounding": round(grounding * 100, 2),
                "complexity_score": round(complexity * 100, 2),
            },
        }

    def _grounding_score(self, sql: str, schema: DatabaseSchema) -> float:
        known_tables = {t.name.lower() for t in schema.tables}
        known_columns = {
            c.name.lower()
            for t in schema.tables
            for c in t.columns
        }
        try:
            statements = sqlglot.parse(sql, dialect="postgres")
            if not statements:
                return 0.0

            referenced_tables = {
                t.name.lower()
                for t in statements[0].find_all(exp.Table)
                if t.name
            }
            referenced_columns = {
                c.name.lower()
                for c in statements[0].find_all(exp.Column)
                if c.name and c.name != "*"
            }

            if not referenced_tables:
                return 0.5

            table_score = len(
                referenced_tables & known_tables
            ) / max(len(referenced_tables), 1)

            col_score = (
                len(referenced_columns & known_columns)
                / max(len(referenced_columns), 1)
                if referenced_columns else 1.0
            )
            return (table_score + col_score) / 2

        except Exception:
            return 0.5

    def _complexity_score(self, sql: str) -> float:
        sql_upper = sql.upper()
        score = 1.0
        score -= sql_upper.count("JOIN") * 0.05
        score -= (sql_upper.count("SELECT") - 1) * 0.10
        score -= sql_upper.count("UNION") * 0.10
        return max(0.0, min(1.0, score))