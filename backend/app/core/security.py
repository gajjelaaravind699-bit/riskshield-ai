"""
Authentication and Authorization foundation using API Key and Role-Based Access Control (RBAC).
"""

import secrets
from typing import Callable, Dict, List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from app.core.config import settings

api_key_header = APIKeyHeader(
    name=settings.API_KEY_HEADER_NAME,
    auto_error=False,
    description="API Key for RiskShield AI Sentinel API",
)


class AuthContext(BaseModel):
    """
    Principal identity and role context for authenticated API requests.
    """
    identity: str = Field(..., description="Unique client or service identifier")
    role: str = Field("analyst", description="Role: admin, analyst, ingest, or readonly")
    scopes: List[str] = Field(default_factory=list, description="Assigned authorization scopes")
    authenticated: bool = Field(True, description="Whether authentication was verified")


def verify_api_key(api_key: Optional[str]) -> AuthContext:
    """
    Validate provided API key against configured key registry using constant-time comparison.
    """
    if not settings.AUTH_ENABLED:
        # Development / Test override mode when auth is explicitly disabled in config
        return AuthContext(
            identity="dev-environment-user",
            role="admin",
            scopes=["read", "write", "admin", "ingest", "analyst"],
            authenticated=True,
        )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid API key via X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # settings.parsed_api_keys is a dict: {key_value: {"role": "...", "identity": "...", "scopes": [...]}}
    configured_keys = settings.parsed_api_keys

    for key_secret, key_info in configured_keys.items():
        if secrets.compare_digest(api_key, key_secret):
            return AuthContext(
                identity=key_info.get("identity", "api-client"),
                role=key_info.get("role", "analyst"),
                scopes=key_info.get("scopes", ["read", "write"]),
                authenticated=True,
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or revoked API key.",
        headers={"WWW-Authenticate": "ApiKey"},
    )


async def get_current_auth(
    api_key: Optional[str] = Security(api_key_header),
) -> AuthContext:
    """
    FastAPI dependency for authenticating requests.
    """
    return verify_api_key(api_key)


def require_role(allowed_roles: List[str]) -> Callable[[AuthContext], AuthContext]:
    """
    Dependency factory to enforce role-based access control.
    """
    async def role_checker(
        auth: AuthContext = Depends(get_current_auth),
    ) -> AuthContext:
        # 'admin' role has universal access
        if auth.role == "admin" or auth.role in allowed_roles:
            return auth

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access forbidden: requires one of the following roles: {', '.join(allowed_roles)} (current role: '{auth.role}')",
        )

    return role_checker


# Role shortcut dependencies
require_admin = require_role(["admin"])
require_analyst = require_role(["analyst", "admin"])
require_ingest = require_role(["ingest", "admin", "analyst"])
