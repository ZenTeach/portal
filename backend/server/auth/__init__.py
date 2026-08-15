"""FastAPI authentication: JWT token engine, cookie helpers, and dependencies.

Replicates flask-jwt-extended's wire format and the legacy ``jwt_fixes``
cookie contract so the FastAPI app and the Flask compat path can share the
same tokens. Consolidates the two duplicate ``user_identity_loader`` /
``user_lookup_loader`` registrations (teacher + student) into a single
resolver that stores an explicit ``user_type`` claim in the token.
"""

from server.auth.cookies import (
    ACCESS_COOKIE_NAME,
    ACCESS_CSRF_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    REFRESH_CSRF_COOKIE_NAME,
    set_access_cookies,
    set_refresh_cookies,
)
from server.auth.deps import (
    get_current_user,
    get_jwt,
    jwt_required,
    with_required_roles,
)
from server.auth.tokens import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    STUDENT,
    TEACHER,
    USER_TYPE_CLAIM,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_csrf_token,
    get_jti,
    load_user,
)

__all__ = [
    "ACCESS_COOKIE_NAME",
    "ACCESS_CSRF_COOKIE_NAME",
    "ACCESS_TOKEN_TYPE",
    "REFRESH_COOKIE_NAME",
    "REFRESH_CSRF_COOKIE_NAME",
    "REFRESH_TOKEN_TYPE",
    "STUDENT",
    "TEACHER",
    "USER_TYPE_CLAIM",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "get_csrf_token",
    "get_current_user",
    "get_jti",
    "get_jwt",
    "jwt_required",
    "load_user",
    "set_access_cookies",
    "set_refresh_cookies",
    "with_required_roles",
]
