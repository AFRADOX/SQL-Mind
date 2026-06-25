# backend/app/models/query_history.py

from __future__ import annotations
import uuid
from decimal import Decimal
from sqlalchemy import Boolean, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class QueryHistory(Base, TimestampMixin):
    __tablename__ = "query_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("db_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    nl_query: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    generated_sql: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=0,
    )
    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    was_executed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    result_row_count: Mapped[int | None] = mapped_column(
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="query_history",
    )
    connection: Mapped["DatabaseConnection"] = relationship(
        "DatabaseConnection",
        back_populates="query_history",
    )

    def __repr__(self) -> str:
        return f"<QueryHistory id={self.id} score={self.confidence_score}>"