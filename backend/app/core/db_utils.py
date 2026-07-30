from __future__ import annotations


def build_dsn(db_type: str, username: str, password: str, host: str, port: int, database_name: str) -> str:
    """Build an async SQLAlchemy connection string for the given database type."""
    if db_type == "mysql":
        return f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database_name}"
    # default / postgres
    return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database_name}"