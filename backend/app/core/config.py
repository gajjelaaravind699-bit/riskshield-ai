"""
Application configuration management with strict production validation using Pydantic Settings.
"""

import json
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import computed_field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Project Information
    PROJECT_NAME: str = "RiskShield AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = True

    # Security & Secrets
    SECRET_KEY: str = "dev-secret-key-riskshield-ai-development-only-change-in-production"
    AUTH_ENABLED: bool = True
    API_KEY_HEADER_NAME: str = "X-API-Key"
    
    # API Keys Configuration: JSON string or dict of {"key": {"role": "...", "identity": "...", "scopes": [...]}}
    # In development/test, provides default keys if none specified in env
    API_KEYS: Union[str, Dict[str, Dict[str, Any]]] = {
        "rs_analyst_key_dev": {
            "identity": "lead-analyst",
            "role": "analyst",
            "scopes": ["read", "write", "analyst"],
        },
        "rs_ingest_key_dev": {
            "identity": "payment-ingestion-worker",
            "role": "ingest",
            "scopes": ["write", "ingest"],
        },
        "rs_admin_key_dev": {
            "identity": "system-admin",
            "role": "admin",
            "scopes": ["read", "write", "admin", "analyst", "ingest"],
        },
    }

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    ENABLE_SECURITY_HEADERS: bool = True

    # Rate Limiting & Request Protection
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 120
    MAX_REQUEST_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # Logging & Observability
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    # PostgreSQL Database Settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "riskshield_db"
    POSTGRES_USER: str = "riskshield_user"
    POSTGRES_PASSWORD: str = "riskshield_password"
    DATABASE_URL: Optional[str] = None

    # Database Reliability & Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_POOL_PRE_PING: bool = True

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def assemble_allowed_hosts(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """
        Enforce strict production security requirements.
        Fails safely if secrets or passwords are default or insecure in production mode.
        """
        if self.ENVIRONMENT == "production":
            # 1. Reject default or weak SECRET_KEY
            if not self.SECRET_KEY or "dev-" in self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "Production configuration error: SECRET_KEY must be a cryptographically strong secret with at least 32 characters."
                )

            # 2. Reject default PostgreSQL password
            if self.POSTGRES_PASSWORD in ["riskshield_password", "password", "123456", "admin"]:
                raise ValueError(
                    "Production configuration error: POSTGRES_PASSWORD cannot use default or weak password in production."
                )

            # 3. Reject default debug mode in production
            if self.DEBUG:
                self.DEBUG = False

            # 4. Reject default API keys in production
            if isinstance(self.API_KEYS, dict) and "rs_analyst_key_dev" in self.API_KEYS:
                raise ValueError(
                    "Production configuration error: Development API keys cannot be used in production. Configure API_KEYS explicitly via environment."
                )

        return self

    @property
    def parsed_api_keys(self) -> Dict[str, Dict[str, Any]]:
        """
        Parse and normalize API_KEYS dictionary from dict or JSON string.
        """
        if isinstance(self.API_KEYS, dict):
            return self.API_KEYS
        if isinstance(self.API_KEYS, str):
            try:
                parsed = json.loads(self.API_KEYS)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                # Comma separated list of keys -> default to analyst role
                return {
                    k.strip(): {"role": "analyst", "identity": f"client-{i+1}", "scopes": ["read", "write"]}
                    for i, k in enumerate(self.API_KEYS.split(","))
                    if k.strip()
                }
        return {}

    @computed_field
    @property
    def async_database_uri(self) -> str:
        """
        Build async SQLAlchemy PostgreSQL connection URI.
        """
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def sync_database_uri(self) -> str:
        """
        Build synchronous SQLAlchemy PostgreSQL connection URI for migrations/sync drivers.
        """
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
                return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
            if self.DATABASE_URL.startswith("sqlite+aiosqlite://"):
                return self.DATABASE_URL.replace("sqlite+aiosqlite://", "sqlite://", 1)
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()
