"""FastAPI port of ``server/api/teacher_auth_api.py``.

Mirrors the legacy teacher auth endpoints under ``/api/v1`` exactly:

* registration (invite-gated), login, logout, token refresh, current user,
  google auth handshake, account confirmation, password reset, invite and
  confirmation-email dispatch.

JWT handling is delegated to :mod:`server.auth` (``jwt_required`` dependency +
  ``set_access_cookies`` / ``set_refresh_cookies``), which replicates the
  flask-jwt-extended wire format and CSRF contract. Marshmallow schemas are
  reused for now; conversion to Pydantic is tracked separately.
"""

from datetime import timedelta
from secrets import token_hex
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import JSONResponse

from server.auth import jwt_required, set_access_cookies, set_refresh_cookies
from server.auth.deps import get_jwt
from server.auth.tokens import create_access_token, create_refresh_token, get_jti
from server.models import Invitations, Teacher, TeacherSchema
from server.routers.helpers import log_activity, logger, redis_store
from server.security import bcrypt
from server.tasks import (
    send_account_recovery_instructions,
    send_confirmation_instructions,
    send_user_invite,
)

teacher_auth_router = APIRouter(tags=["teacher-auth"])

ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)


def _json(content: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=content, status_code=status_code)


def _error(message: str, status_code: int) -> JSONResponse:
    return _json({"message": message}, status_code)


@teacher_auth_router.post("/teacher/registration")
def teacher_registration(payload: Dict[str, Any] = Body(...)):
    email = payload["email"]
    invitation_code = payload["invitation_code"]

    if not Invitations.validate_email_invitation_token(email, invitation_code):
        return _error("Registrations are only through valid invites.", 400)

    Invitations.use_token(email, invitation_code)

    if Teacher.query.filter_by(email=email).first():
        return _error("Teacher {} already exists".format(email), 400)

    new_teacher = Teacher(
        firstname=payload["firstname"],
        lastname=payload["lastname"],
        email=email,
        password=payload["password"],
        date_of_birth=payload["date_of_birth"],
        role=payload["role"],
    )
    try:
        new_teacher.save()
        access_token = create_access_token(new_teacher.id, fresh=True)
        refresh_token = create_refresh_token(new_teacher.id)
        response = _json(
            {"message": "Teacher {} was created".format(new_teacher.full_name())}
        )

        redis_store().set(get_jti(access_token), "true", ex=ACCESS_EXPIRES * 1.2)
        redis_store().set(get_jti(refresh_token), "true", ex=REFRESH_EXPIRES * 1.2)

        send_confirmation_instructions.delay(new_teacher.id)
        Invitations.associate_invitee(new_teacher, invitation_code)

        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return _error("Something went wrong", 500)


@teacher_auth_router.post("/teacher/login")
def teacher_login(request: Request, payload: Dict[str, Any] = Body(...)):
    email = payload["email"]
    current_user = Teacher.query.filter_by(email=email).first()
    if not current_user:
        return _error("User {} doesn't exist".format(email), 404)

    if current_user.check_password(payload["password"]):
        access_token = create_access_token(current_user.id, fresh=True)
        refresh_token = create_refresh_token(current_user.id)
        response = _json({"message": "Logged in as {}".format(current_user.email)})
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        redis_store().set(get_jti(access_token), "true", ex=ACCESS_EXPIRES * 1.2)
        redis_store().set(get_jti(refresh_token), "true", ex=REFRESH_EXPIRES * 1.2)

        log_activity(
            current_user,
            "create",
            "login",
            current_user.id,
            {"useragent_data": request.headers.get("User-Agent")},
            "Logged in as {}".format(current_user.email),
        )
        return response

    return _error("Wrong credentials", 400)


@teacher_auth_router.delete("/teacher/logout")
def teacher_logout(
    request: Request, _: object = Depends(jwt_required(fresh=True))
):
    jti = get_jwt(request)["jti"]
    redis_store().set(jti, "false", ex=ACCESS_EXPIRES * 1.2)
    return _json({"msg": "Access token revoked"}, 204)


@teacher_auth_router.post("/teacher/token/refresh")
def teacher_token_refresh(
    request: Request, current_user: Teacher = Depends(jwt_required(refresh=True))
):
    teacher = Teacher.query.filter_by(email=current_user.email).first()
    access_token = create_access_token(teacher.id, fresh=True)

    redis_store().set(get_jti(access_token), "true", ex=ACCESS_EXPIRES * 1.2)

    response = _json({"refresh": True})
    set_access_cookies(response, access_token)
    return response


@teacher_auth_router.get("/teachers")
def all_teachers():
    return {"message": "List of Teachers"}


@teacher_auth_router.delete("/teachers")
def delete_all_teachers():
    return {"message": "Delete all Teachers"}


@teacher_auth_router.get("/teacher/current")
def current_teacher(
    request: Request, teacher: Teacher = Depends(jwt_required(fresh=True))
):
    try:
        t = Teacher.query.filter_by(email=teacher.email).first()
        return _json({"user": TeacherSchema.dump_one(t)})
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        logger.debug(teacher)
        return _json("User not logged in", 400)


@teacher_auth_router.post("/teacher/auth/google")
def teacher_gauth(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    teacher: Teacher = Depends(jwt_required(fresh=True)),
):
    t = Teacher.query.filter_by(email=teacher.email).first()
    try:
        auth_key = "gauth-code_{}".format(t.uuid)
        redis_store().set(auth_key, payload["authCode"])
        return _json(
            {"message": "Successfully generated Google form", "status": "Success"}
        )
    except Exception:  # noqa: BLE001
        return _json({"message": "Encountered error", "status": "Failed"}, 400)


@teacher_auth_router.post("/teacher/confirm")
def teacher_confirm(payload: Dict[str, Any] = Body(...)):
    confirmation_token = payload["token"]
    teacher = Teacher.query.filter_by(confirmation_token=confirmation_token).first()

    if not teacher:
        return _error(
            "Encountered an error confirming account. Make sure the email is correct.",
            404,
        )

    if confirmation_token is None or not teacher.valid_confirmation_token(
        confirmation_token
    ):
        return _error("Encountered an error. Invalid token.", 404)

    if not teacher.confirm_user():
        return _error("Account already confirmed.", 400)

    return _json(
        {"status": "Success", "message": "Account successfully confirmed."}
    )


@teacher_auth_router.get("/teacher/reset-password")
def teacher_reset_password(email: str = Query(...)):
    send_account_recovery_instructions.delay(email)
    return _json(
        {
            "status": "Success",
            "message": "Recovery successful. If the account exists, "
            "you will get a recovery instruction.",
        }
    )


@teacher_auth_router.post("/teacher/reset-password")
def teacher_reset_password_post(payload: Dict[str, Any] = Body(...)):
    token = payload["token"]
    email = payload["email"]
    password = bcrypt.generate_password_hash(payload["password"]).decode("utf-8")

    teacher = Teacher.query.filter_by(email=email).first()

    if not teacher:
        return _error(
            "Encountered an recovering account. Make sure the email is correct.", 404
        )

    if token is None or not teacher.valid_recovery_token(token):
        return _error("Encountered an error. Invalid token.", 404)

    if not teacher.reset_account(token, password):
        return _error("Account token not recognized.", 400)

    return _json(
        {
            "status": "Success",
            "message": "Account successfully recovered. Please login with your "
            "new credentials.",
        }
    )


@teacher_auth_router.post("/teacher/invite")
def teacher_invite(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    teacher: Teacher = Depends(jwt_required(fresh=True)),
):
    t = Teacher.query.filter_by(email=teacher.email).first()
    email = payload["email"]
    try:
        invite = Invitations(email, token_hex(8), t.id)
        invite.save(refresh=True)
        log_activity(
            t,
            "create",
            "user_invite",
            invite.id,
            {},
            "Invited user with email {}".format(invite.email),
        )
        send_user_invite.delay(email)
        return _json({"status": "success", "message": "Invite Sent!"})
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return _json({"status": "error", "message": "Encountered an error."})


@teacher_auth_router.post("/teacher/send_confirmation")
def teacher_send_confirmation(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    email = payload["email"]
    if email is None:
        return _error("Email is required to perform this action.", 400)

    teacher = Teacher.query.filter_by(email=email).first()
    if teacher is None:
        return _error("Email doesn't exist.", 404)

    try:
        send_confirmation_instructions.apply_async(args=[teacher.id])
        return _json(
            {
                "status": "success",
                "message": "Confirmation instruction Sent! Check your mailbox.",
            }
        )
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return _error(
            "Couldn't send confirmation instruction. Please wait while we resolve "
            "the issue.",
            500,
        )
