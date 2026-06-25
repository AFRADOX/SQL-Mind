# backend/app/models/connection.py

from __future__ import annotations
import uuid
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class DatabaseConnection(Base, TimestampMixin):
    __tablename__ = "db_connections"

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
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    host: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5432,
    )
    database_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    encrypted_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="connections",
    )
    query_history: Mapped[list["QueryHistory"]] = relationship(
        "QueryHistory",
        back_populates="connection",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<DatabaseConnection id={self.id} name={self.name}>"