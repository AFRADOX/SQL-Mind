# backend/app/schemas/schema.py

from __future__ import annotations
from pydantic import BaseModel


class ColumnMeta(BaseModel):
    name: str
    type: str
    nullable: bool
    is_primary_key: bool


class ForeignKeyMeta(BaseModel):
    column: str
    references_table: str
    references_column: str


class TableMeta(BaseModel):
    name: str
    columns: list[ColumnMeta]
    foreign_keys: list[ForeignKeyMeta]
    sample_values: dict[str, list[str]] = {}


class DatabaseSchema(BaseModel):
    tables: list[TableMeta]
    total_tables: int