"""FastAPI port of ``server/api/student_auth_api.py``.

Mirrors the legacy student auth endpoints under ``/api/v1`` exactly. JWT
handling is delegated to :mod:`server.auth`. The legacy student refresh was
broken (it treated the JWT payload as a ``Student``); this port resolves the
authenticated student through the ``jwt_required`` dependency instead.
"""

from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse

from server.auth import jwt_required, set_access_cookies, set_refresh_cookies
from server.auth.deps import get_current_user, get_jwt
from server.auth.tokens import STUDENT, create_access_token, create_refresh_token, get_jti
from server.models import Student
from server.routers.helpers import logger, redis_store
from server.security import bcrypt
from server.tasks import send_student_confirmation_instructions

student_auth_router = APIRouter(tags=["student-auth"])

ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)


def _json(content: Any, status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=content, status_code=status_code)


def _error(message: str, status_code: int) -> JSONResponse:
    return _json({"message": message}, status_code)


@student_auth_router.post("/student/registration")
def student_registration(payload: Dict[str, Any] = Body(...)):
    if Student.query.filter_by(email=payload["email"]).first():
        return _error(
            "Student {} already exists".format(payload["email"]), 400
        )

    # Legacy pre-hashes here and passes the digest through to ``Student``,
    # which hashes again. Kept verbatim for parity with the Flask behaviour.
    password_hash = bcrypt.generate_password_hash(payload["password"]).decode(
        "utf-8"
    )
    new_student = Student(
        firstname=payload["firstname"],
        lastname=payload["lastname"],
        email=payload["email"],
        password=password_hash,
    )
    try:
        new_student.save()
        access_token = create_access_token(new_student.id, fresh=True, user_type=STUDENT)
        refresh_token = create_refresh_token(new_student.id, user_type=STUDENT)
        response = _json(
            {"message": "Student {} was created".format(new_student.full_name())}
        )
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)

        redis_store().set(get_jti(access_token), "true", ex=ACCESS_EXPIRES * 1.2)
        redis_store().set(get_jti(refresh_token), "true", ex=REFRESH_EXPIRES * 1.2)
        return response
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return _error("Something went wrong", 500)


@student_auth_router.post("/student/login")
def student_login(payload: Dict[str, Any] = Body(...)):
    current_user = Student.query.filter_by(email=payload["email"]).first()
    if not current_user:
        return _error(
            "User {} doesn't exist".format(payload["email"]), 404
        )

    if bcrypt.check_password_hash(current_user.password, payload["password"]):
        access_token = create_access_token(
            current_user.id, fresh=True, user_type=STUDENT
        )
        refresh_token = create_refresh_token(current_user.id, user_type=STUDENT)
        response = _json({"message": "Logged in as {}".format(current_user.email)})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        redis_store().set(get_jti(access_token), "true", ex=ACCESS_EXPIRES * 1.2)
        redis_store().set(get_jti(refresh_token), "true", ex=REFRESH_EXPIRES * 1.2)
        return response

    return _error("Wrong credentials", 400)


@student_auth_router.post("/student/logout")
def student_logout(request: Request, _: object = Depends(jwt_required(fresh=True))):
    jti = get_jwt(request)["jti"]
    redis_store().set(jti, "false", ex=ACCESS_EXPIRES * 1.2)
    return _json({"msg": "Access token revoked"})


@student_auth_router.post("/student/token/refresh")
def student_token_refresh(
    request: Request, current_user: Student = Depends(jwt_required(refresh=True))
):
    student = Student.query.filter_by(email=current_user.email).first()
    access_token = create_access_token(student.id, fresh=True, user_type=STUDENT)
    redis_store().set(get_jti(access_token), "true", ex=ACCESS_EXPIRES * 1.2)

    response = _json({"refresh": True})
    set_access_cookies(response, access_token)
    return response


@student_auth_router.put("/student/current")
def student_current_put(
    request: Request,
    email: Optional[str] = Body(None),
    data: Dict[str, Any] = Body({}),
):
    student = get_current_user(request)
    if student is None:
        student = Student.query.filter_by(email=email).first()
        if student is None:
            return _error("Student not found", 404)

    try:
        student.update_and_save(**data)
        return _json({"message": "Successfully updated student."})
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return _error(
            "Encountered an exception when updating student {}".format(
                student.email
            ),
            500,
        )


@student_auth_router.get("/student/current")
def student_current(
    request: Request, student: Student = Depends(jwt_required(fresh=True))
):
    try:
        return _json(student.to_dict())
    except Exception as e:  # noqa: BLE001
        logger.error("Got an error fetching current user", e)
        return _error("User not logged in", 400)


@student_auth_router.delete("/student/auth/refresh_revoke")
def student_refresh_revoke(
    request: Request, _: object = Depends(jwt_required(refresh=True))
):
    jti = get_jwt(request)["jti"]
    redis_store().set(jti, "true", ex=REFRESH_EXPIRES * 1.2)
    return _json({"msg": "Refresh token revoked"})


@student_auth_router.post("/student/confirm")
def student_confirm(payload: Dict[str, Any] = Body(...)):
    confirmation_token = payload["token"]
    student = Student.query.filter_by(confirmation_token=confirmation_token).first()

    if not student:
        return _error(
            "Encountered an error confirming account. Make sure the email is correct.",
            404,
        )

    if confirmation_token is None or not student.valid_confirmation_token(
        confirmation_token
    ):
        return _error("Encountered an error. Invalid token.", 404)

    if not student.confirm_user():
        return _error("Account already confirmed.", 400)

    return _json(
        {"status": "Success", "message": "Account successfully confirmed."}
    )


@student_auth_router.get("/student/{student_id}/send_confirmation")
def student_send_confirmation(
    request: Request,
    student_id: int,
    _: object = Depends(jwt_required(fresh=True)),
):
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return _error("Student not found.", 404)

    try:
        send_student_confirmation_instructions.apply_async(args=[student.id])
        return _json(
            {
                "status": "Success",
                "message": "Confirmation email is on it's way!",
            }
        )
    except Exception:  # noqa: BLE001
        return _error(
            "Server got an error sending confirmation email.", 500
        )
