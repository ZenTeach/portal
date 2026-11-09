"""PyJWT token engine replicating flask-jwt-extended's on-the-wire format.

flask-jwt-extended (4.4.4) emits HS512 tokens whose payload is::

    {
        "fresh": bool,
        "iat": int,
        "jti": str(uuid4),
        "type": "access" | "refresh",
        "sub": <identity>,
        "nbf": int,
        "csrf": str(uuid4),
        "exp": int,
    }

The legacy app registered two conflicting ``user_identity_loader`` /
``user_lookup_loader`` pairs (one in each auth module). Because the Teacher
loader was registered last it won globally, so ``sub`` was always a dict
(``Teacher.to_dict()``) -- even for student tokens -- and the resolver did
``kwargs['sub']['id']``. That is the "TwoDuplicateLoader" bug this module
consolidates away: ``sub`` now carries the integer primary key and an
explicit ``user_type`` claim selects the model.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple

import jwt as pyjwt

from server.config.settings import get_settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

#: Extra claim identifying the model an identity belongs to. Stored in the
#: payload (not the JOSE header) so the legacy app never has to care about it.
USER_TYPE_CLAIM = "user_type"

TEACHER = "teacher"
STUDENT = "student"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _resolve_identity(identity: Any, user_type: Optional[str]) -> Tuple[Any, str]:
    """Normalize an identity to ``(primary_key, user_type)``.

    Accepts either a model instance (type inferred) or a bare primary key
    (requires an explicit ``user_type``). Defaults to teacher to preserve the
    historical global-loader behaviour when no type can be determined.
    """
    from server.models import Student, Teacher

    if user_type is None:
        if isinstance(identity, Teacher):
            user_type = TEACHER
        elif isinstance(identity, Student):
            user_type = STUDENT
        else:
            user_type = TEACHER

    identity_id = getattr(identity, "id", identity)
    return identity_id, user_type


def _expires(settings, token_type: str) -> timedelta:
    if token_type == REFRESH_TOKEN_TYPE:
        return settings.jwt_refresh_token_expires
    return settings.jwt_access_token_expires


def _encode(
    identity: Any, token_type: str, fresh: bool, user_type: Optional[str]
) -> str:
    settings = get_settings()
    identity_id, user_type = _resolve_identity(identity, user_type)
    now = _now()
    payload = {
        "fresh": fresh,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "type": token_type,
        settings.jwt_identity_claim: identity_id,
        "nbf": now,
        "csrf": str(uuid.uuid4()),
        "exp": now + _expires(settings, token_type),
    }
    if user_type:
        payload[USER_TYPE_CLAIM] = user_type
    return pyjwt.encode(
        payload, settings.effective_jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_access_token(
    identity: Any, fresh: bool = True, user_type: Optional[str] = None
) -> str:
    """Create a fresh access token (HS512, flask-jwt-extended wire format)."""
    return _encode(identity, ACCESS_TOKEN_TYPE, fresh, user_type)


def create_refresh_token(identity: Any, user_type: Optional[str] = None) -> str:
    """Create a non-fresh refresh token."""
    return _encode(identity, REFRESH_TOKEN_TYPE, False, user_type)


def decode_token(token: str, verify: bool = True) -> dict:
    """Decode (and by default verify) a token, returning its payload."""
    settings = get_settings()
    options = None
    if not verify:
        options = {
            "verify_signature": False,
            "verify_exp": False,
            "verify_nbf": False,
            "verify_iat": False,
        }
    return pyjwt.decode(
        token,
        settings.effective_jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options=options,
    )


def get_jti(token: str) -> str:
    """Return the ``jti`` claim of a (verified) token."""
    return decode_token(token)["jti"]


def get_csrf_token(token: str) -> str:
    """Return the ``csrf`` claim of a (verified) token."""
    return decode_token(token)["csrf"]


def load_user(payload: dict):
    """Resolve the authenticated model from a decoded token payload.

    Consolidates the legacy ``user_lookup_loader`` / ``user_identity_loader``
    pairs. Handles both the new compact ``sub`` (int id) and the legacy dict
    shape produced by the old serializing loader.
    """
    from server.models import Student, Teacher

    sub = payload.get(get_settings().jwt_identity_claim)
    if isinstance(sub, dict):
        identity_id = sub.get("id")
    else:
        identity_id = sub

    if identity_id is None:
        return None
    try:
        identity_id = int(identity_id)
    except (TypeError, ValueError):
        return None

    model = Student if payload.get(USER_TYPE_CLAIM) == STUDENT else Teacher
    return model.query.get(identity_id)
