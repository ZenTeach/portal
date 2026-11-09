"""FastAPI dependencies for JWT authentication and role guards.

Replicates the behaviour of flask-jwt-extended's ``@jwt_required`` /
``verify_jwt_in_request`` and the legacy ``with_required_roles`` decorator,
reading the token from cookies (``JWT_TOKEN_LOCATION = ["cookies"]``) and
enforcing the double-submit CSRF check.

The request-scoped database session is bound by the app's session middleware
before these dependencies run, so ``load_user`` can issue ``Model.query.get``.
"""

from typing import Callable, Optional, Sequence

import jwt as pyjwt
from fastapi import HTTPException, Request

from server.auth.cookies import ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME
from server.auth.tokens import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    decode_token,
    load_user,
)
from server.config.settings import get_settings

# Methods on which flask-jwt-extended enforced the double-submit CSRF check
# (JWT_CSRF_METHODS default). Safe methods (GET/HEAD/OPTIONS) are exempt.
_CSRF_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def _session_expired() -> HTTPException:
    return HTTPException(
        status_code=401, detail={"status": "error", "message": "Session expired"}
    )


def _token_is_revoked(jti: str) -> bool:
    """Return True if the jti is revoked.

    Mirrors the legacy ``token_in_blocklist_loader``. It is effectively an
    allowlist: a missing key means revoked, ``"true"`` means active, any other
    value means revoked. The legacy loader compared bytes to the ``"true"``
    string, which made revocation a no-op; this module normalizes the value so
    the intended behaviour actually works for both FlaskRedis (bytes) and the
    FastAPI plain client (str, ``decode_responses=True``).
    """
    import server

    store = getattr(server, "redis_store", None)
    if store is None:
        return True
    entry = store.get(jti)
    if entry is None:
        return True
    if isinstance(entry, bytes):
        entry = entry.decode("utf-8")
    return entry != "true"


def _verify_token(
    request: Request,
    *,
    fresh: bool = False,
    refresh: bool = False,
    optional: bool = False,
):
    settings = get_settings()
    cookie_name = REFRESH_COOKIE_NAME if refresh else ACCESS_COOKIE_NAME
    expected_type = REFRESH_TOKEN_TYPE if refresh else ACCESS_TOKEN_TYPE
    token = request.cookies.get(cookie_name)

    if token is None:
        if optional:
            return None
        raise _session_expired()

    try:
        payload = decode_token(token)
    except pyjwt.ExpiredSignatureError:
        raise _session_expired()
    except pyjwt.InvalidTokenError:
        raise _session_expired()

    if payload.get("type") != expected_type:
        raise _session_expired()

    if fresh and not payload.get("fresh", False):
        raise HTTPException(
            status_code=401, detail={"status": "error", "message": "Fresh token required"}
        )

    token_type = payload.get("type")
    if token_type in settings.jwt_blacklist_token_checks and _token_is_revoked(
        payload.get("jti")
    ):
        raise _session_expired()

    # Double-submit CSRF: header value must equal the token's csrf claim.
    # Only enforced on the unsafe methods, mirroring flask-jwt-extended's
    # JWT_CSRF_METHODS gating (safe methods like GET are exempt).
    if settings.jwt_cookie_csrf_protect and request.method in _CSRF_METHODS:
        header_name = (
            settings.jwt_refresh_csrf_header_name
            if token_type == REFRESH_TOKEN_TYPE
            else settings.jwt_access_csrf_header_name
        )
        if request.headers.get(header_name) != payload.get("csrf"):
            raise HTTPException(
                status_code=401,
                detail={"status": "error", "message": "Missing CSRF token"},
            )

    user = load_user(payload)
    if user is None:
        raise _session_expired()

    request.state.current_user = user
    request.state.jwt_payload = payload
    return user


def jwt_required(
    fresh: bool = False, refresh: bool = False, optional: bool = False
) -> Callable:
    """Dependency factory mirroring ``@jwt_required(...)``."""

    def dependency(request: Request):
        return _verify_token(
            request, fresh=fresh, refresh=refresh, optional=optional
        )

    return dependency


def get_current_user(request: Request):
    """Return the user resolved by a ``jwt_required`` dependency."""
    return getattr(request.state, "current_user", None)


def get_jwt(request: Request) -> dict:
    """Return the decoded JWT payload for the current request."""
    return getattr(request.state, "jwt_payload", None)


def with_required_roles(roles: Sequence[str]) -> Callable:
    """Dependency factory mirroring the legacy ``with_required_roles`` decorator.

    Requires a fresh access token and that the user's role is in ``roles``.
    """

    def dependency(request: Request) -> object:
        user = _verify_token(request, fresh=True)
        if user is None or getattr(user, "role", None) not in roles:
            raise HTTPException(status_code=403, detail={"msg": "Unauthorized user."})
        return user

    return dependency
