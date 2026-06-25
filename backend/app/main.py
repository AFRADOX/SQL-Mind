from __future__ import annotations
import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api.v1.router import api_router
from app.core.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up %s", settings.app_name)

    from app.db.session import engine

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connected.")
    except Exception as e:
        logger.critical("Cannot connect to PostgreSQL: %s", e)
        raise

    # Redis is optional
    try:
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await redis_client.ping()
        app.state.redis = redis_client
        logger.info("Redis connected.")
    except Exception:
        logger.warning("Redis unavailable — caching disabled.")
        app.state.redis = None

    from app.db.session import engine as db_engine
    app.state.db_engine = db_engine
    logger.info("Startup complete. Docs at http://localhost:8000/docs")

    yield

    from app.db.session import engine as shutdown_engine
    await shutdown_engine.dispose()
    logger.info("Database pool closed.")

    if app.state.redis:
        await app.state.redis.aclose()
        logger.info("Redis closed.")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description="Text-to-SQL SaaS API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    return app


app = create_application()


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


@app.get("/health", tags=["Health"])
async def health_check(request: Request) -> JSONResponse:
    health = {}
    overall_ok = True

    try:
        from sqlalchemy import text as sa_text
        from sqlalchemy.ext.asyncio import AsyncEngine
        engine = request.app.state.db_engine
        async with engine.connect() as conn:
            await conn.execute(sa_text("SELECT 1"))
        health["postgres"] = "ok"
    except Exception as e:
        health["postgres"] = f"error: {e}"
        overall_ok = False

    try:
        redis = request.app.state.redis
        if redis:
            await redis.ping()
            health["redis"] = "ok"
        else:
            health["redis"] = "disabled"
    except Exception as e:
        health["redis"] = f"error: {e}"

    return JSONResponse(
        status_code=status.HTTP_200_OK if overall_ok
        else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if overall_ok else "degraded",
            "app": settings.app_name,
            "services": health,
        },
    )