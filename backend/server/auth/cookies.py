"""Starlette cookie helpers replicating the legacy ``jwt_fixes`` contract.

The client (Vue/Vuetify SPA) reads ``csrf_access_token`` / ``csrf_refresh_token``
cookies and echoes them as ``X-CSRF-ACCESS-TOKEN`` / ``X-CSRF-REFRESH-TOKEN``
headers (double-submit CSRF). Cookie names, paths, and the CSRF-cookie gating
(``JWT_COOKIE_CSRF_PROTECT`` AND ``JWT_CSRF_IN_COOKIES``) all mirror
flask-jwt-extended's defaults plus the app's overrides.
"""

from typing import Optional

from server.auth.tokens import get_csrf_token
from server.config.settings import get_settings

ACCESS_COOKIE_NAME = "access_token_cookie"
REFRESH_COOKIE_NAME = "refresh_token_cookie"
ACCESS_CSRF_COOKIE_NAME = "csrf_access_token"
REFRESH_CSRF_COOKIE_NAME = "csrf_refresh_token"


def _resolve_samesite(settings) -> Optional[str]:
    """Map the app's ``JWT_COOKIE_SAMESITE`` string to a Starlette value.

    Starlette only accepts ``lax`` / ``strict`` / ``none``. The legacy config
    uses the string ``"None"`` to mean "unset"; modern browsers reject
    ``SameSite=None`` on non-secure cookies, so downgrade to ``lax`` in that
    case.
    """
    raw = (settings.jwt_cookie_samesite or "").strip().lower()
    if raw in ("lax", "strict"):
        return raw
    if raw == "none" and settings.jwt_cookie_secure:
        return "none"
    return "lax"


def _set_csrf_cookie(response, key: str, token: str, settings, max_age: int) -> None:
    response.set_cookie(
        key=key,
        value=get_csrf_token(token),
        max_age=max_age,
        path="/",
        domain=settings.jwt_cookie_domain,
        secure=settings.jwt_cookie_secure,
        httponly=False,
        samesite=_resolve_samesite(settings),
    )


def set_access_cookies(response, token: str) -> None:
    """Set the access token (and its CSRF cookie) on a Starlette response."""
    settings = get_settings()
    max_age = int(settings.jwt_access_token_expires.total_seconds())
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=token,
        max_age=max_age,
        path=settings.jwt_access_cookie_path,
        domain=settings.jwt_cookie_domain,
        secure=settings.jwt_cookie_secure,
        httponly=True,
        samesite=_resolve_samesite(settings),
    )
    if settings.jwt_cookie_csrf_protect and settings.jwt_csrf_in_cookies:
        _set_csrf_cookie(response, ACCESS_CSRF_COOKIE_NAME, token, settings, max_age)


def set_refresh_cookies(response, token: str) -> None:
    """Set the refresh token (and its CSRF cookie) on a Starlette response."""
    settings = get_settings()
    max_age = int(settings.jwt_refresh_token_expires.total_seconds())
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=max_age,
        path=settings.jwt_refresh_cookie_path,
        domain=settings.jwt_cookie_domain,
        secure=settings.jwt_cookie_secure,
        httponly=True,
        samesite=_resolve_samesite(settings),
    )
    if settings.jwt_cookie_csrf_protect and settings.jwt_csrf_in_cookies:
        _set_csrf_cookie(response, REFRESH_CSRF_COOKIE_NAME, token, settings, max_age)
