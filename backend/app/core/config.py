# # backend/app/core/config.py

# from __future__ import annotations
# from functools import lru_cache
# from typing import Literal
# from pydantic import Field, computed_field, model_validator
# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8",
#         case_sensitive=False,
#         extra="ignore",
#     )

#     # App
#     app_name: str = "Text-to-SQL"
#     app_env: Literal["development", "production"] = "development"
#     debug: bool = True
#     api_v1_prefix: str = "/api/v1"

#     # Security
#     secret_key: str = Field(..., min_length=32)
#     jwt_algorithm: str = "HS256"
#     access_token_expire_minutes: int = 30
#     refresh_token_expire_days: int = 7
#     encryption_key: str = Field(..., min_length=44)

#     # Database
#     postgres_user: str = "postgres"
#     postgres_password: str = "NOICE"
#     postgres_db: str = "texttosql_db"
#     postgres_host: str = "localhost"
#     postgres_port: int = 5432
#     database_url: str | None = None
#     database_url_sync: str | None = None

#     # Redis
#     redis_url: str = "redis://redis:6379/0"
#     schema_cache_ttl: int = 3600
#     result_cache_ttl: int = 300

#     # LLM
#     # llm_provider: Literal["openai", "gemini"] = "gemini"
#     llm_provider: Literal["openai", "gemini", "groq"] = "groq"
#     openai_api_key: str | None = None
#     openai_model: str = "gpt-4o"
#     gemini_api_key: str | None = None
#     gemini_model: str = "gemini-1.5-flash"
#     llm_temperature: float = 0.1
#     llm_max_tokens: int = 2048
#     llm_timeout_seconds: int = 30
#     groq_api_key: str | None = None
# groq_model: str = "llama-3.3-70b-versatile"

#     # Safety
#     max_rows_returned: int = 500
#     query_timeout_seconds: int = 10

#     # CORS
#     allowed_origins: str = "http://localhost:3000,http://localhost:5173"

#     @computed_field
#     @property
#     def async_database_url(self) -> str:
#         if self.database_url:
#             return self.database_url
#         return (
#             f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
#             f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
#         )

#     @computed_field
#     @property
#     def sync_database_url(self) -> str:
#         if self.database_url_sync:
#             return self.database_url_sync
#         return (
#             f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
#             f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
#         )

#     @computed_field
#     @property
#     def cors_origins(self) -> list[str]:
#         return [o.strip() for o in self.allowed_origins.split(",")]

#     @model_validator(mode="after")
#     def validate_llm_keys(self) -> "Settings":
#         if self.llm_provider == "openai" and not self.openai_api_key:
#             raise ValueError("OPENAI_API_KEY is missing.")
#         if self.llm_provider == "gemini" and not self.gemini_api_key:
#             raise ValueError("GEMINI_API_KEY is missing.")
#         return self


# @lru_cache()
# def get_settings() -> Settings:
#     return Settings()

# backend/app/core/config.py

from __future__ import annotations
from functools import lru_cache
from typing import Literal
from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Text-to-SQL"
    app_env: Literal["development", "production"] = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    encryption_key: str = Field(..., min_length=44)

    # Database
    postgres_user: str = "postgres"
    postgres_password: str = "NOICE"
    postgres_db: str = "texttosql_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str | None = None
    database_url_sync: str | None = None

    # Redis
    redis_url: str = "redis://redis:6379/0"
    schema_cache_ttl: int = 3600
    result_cache_ttl: int = 300

    # LLM
    llm_provider: Literal["openai", "gemini", "groq"] = "groq"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    groq_api_key: str | None = None
    groq_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 2048
    llm_timeout_seconds: int = 30

    # Safety
    max_rows_returned: int = 500
    query_timeout_seconds: int = 10

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    @computed_field
    @property
    def async_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def sync_database_url(self) -> str:
        if self.database_url_sync:
            return self.database_url_sync
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    @model_validator(mode="after")
    def validate_llm_keys(self) -> "Settings":
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing.")
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is missing.")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing.")
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()