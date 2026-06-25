# backend/app/schemas/connection.py

from __future__ import annotations
import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ConnectionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    host: str = Field(..., min_length=1)
    port: int = Field(default=5432, ge=1, le=65535)
    database_name: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    host: str
    port: int
    database_name: str
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str