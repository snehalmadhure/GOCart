"""Supabase JWT verification for protected API routes."""

from __future__ import annotations

import os
import logging

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def _decode_access_token(token: str) -> dict[str, object]:
    """Verify both legacy HMAC and current Supabase asymmetric JWTs."""

    algorithm = jwt.get_unverified_header(token).get("alg")
    if algorithm == "HS256":
        secret = os.getenv("SUPABASE_JWT_SECRET")
        if not secret:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured")
        return jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")

    supabase_url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
    if not supabase_url:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured")
    issuer = f"{supabase_url.rstrip('/')}/auth/v1"
    jwks = jwt.PyJWKClient(f"{issuer}/.well-known/jwks.json", cache_keys=True)
    signing_key = jwks.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["ES256", "RS256"],
        audience="authenticated",
        issuer=issuer,
    )


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    """Return the authenticated Supabase user id from a valid bearer token."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        claims = _decode_access_token(credentials.credentials)
    except jwt.PyJWTError as error:
        logger.warning("Rejected Supabase access token: %s", error)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token") from error
    user_id = claims.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token has no user identity")
    return user_id
