# backend/app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.connections import router as connections_router
from app.api.v1.routes.query import router as query_router
from app.api.v1.routes.history import router as history_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)
api_router.include_router(
    connections_router,
    prefix="/connections",
    tags=["Connections"]
)
api_router.include_router(
    query_router,
    prefix="/query",
    tags=["Query"]
)
api_router.include_router(
    history_router,
    prefix="/history",
    tags=["History"]
)