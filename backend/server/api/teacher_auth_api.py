from datetime import timedelta
from secrets import token_hex

from flask import Blueprint, abort, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import current_user as jwt_user
from flask_jwt_extended import get_jti, get_jwt, jwt_required
from server import bcrypt, jwt, redis_store
from server.api import logger
from server.lib.utils.jwt_fixes import set_access_cookies, set_refresh_cookies
from server.models import Invitations, Teacher, TeacherSchema
from server.tasks import (send_account_recovery_instructions,
                          send_confirmation_instructions, send_user_invite)
from webargs import fields
from webargs.flaskparser import use_kwargs

teacher_auth_blueprint = Blueprint("teacher_auth", __name__)

dumper = TeacherSchema()
ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)


@jwt.user_identity_loader
def load_user(*args, **kwargs) -> Teacher:
    return Teacher.query.get(args[0])


class TeacherRegistration(MethodView):
    def validate_invite(self, email, invite_code):
        return Invitations.validate_email_invitation_token(email, invite_code)

    def deactivate_token(self, email, invite_code):
        Invitations.use_token(email, invite_code)

    def post(self):
        data = request.get_json()

        if not self.validate_invite(data["email"], data["invitation_code"]):
            abort(400, "Registrations are only through valid invites.")

        self.deactivate_token(data["email"], data["invitation_code"])

        if Teacher.query.filter_by(email=data["email"]).first():
            return {
                "message": "Teacher {} already exists".format(data["email"])
            }

        new_teacher = Teacher(
            firstname=data["firstname"],
            lastname=data["lastname"],
            email=data["email"],
            password=data["password"],
            date_of_birth=data["date_of_birth"],
            role=data["role"],
        )
        try:
            new_teacher.save()
            access_token = create_access_token(new_teacher.id, fresh=True)
            refresh_token = create_refresh_token(new_teacher.id)
            response = jsonify({
                'message': 'Teacher {} was created'.format(new_teacher.full_name())
            })

            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, "true", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "true", REFRESH_EXPIRES * 1.2)

            send_confirmation_instructions.delay(new_teacher.id)

            response = make_response(response, 200)

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response
        except Exception as e:
            logger.error(e)
            return make_response(
                jsonify({
                    "message": "Something went wrong"
                }),
                500)


class TeacherLogin(MethodView):
    def post(self):
        data = request.get_json()
        email = data["email"]
        current_user = Teacher.query.filter_by(email=email).first()
        if not current_user:
            return make_response(
                jsonify({
                    "message": "User {} doesn't exist".format(email)
                }),
                404)

        if current_user.check_password(data["password"]):
            access_token = create_access_token(current_user.id, fresh=True)
            refresh_token = create_refresh_token(current_user.id)
            response_data = jsonify({
                'message': 'Logged in as {}'.format(current_user.email)
            })
            set_access_cookies(response_data, access_token)
            set_refresh_cookies(response_data, refresh_token)
            access_jti = get_jti(access_token)
            refresh_jti = get_jti(refresh_token)
            redis_store.set(access_jti, "true", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "true", REFRESH_EXPIRES * 1.2)

            response = make_response(response_data, 200)
            return response

        else:
            return make_response({"message": "Wrong credentials"}, 400)


class TeacherLogout(MethodView):
    @jwt_required(fresh=True)
    def delete(self):
        jti = get_jwt()["jti"]
        redis_store.set(jti, "false", ACCESS_EXPIRES * 1.2)
        return make_response(jsonify({"msg": "Access token revoked"}), 204)


class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_identity = jwt_user
        current_user = Teacher.query.filter_by(email=current_identity.email).first()
        access_token = create_access_token(current_user.id, fresh=True)

        access_jti = get_jti(access_token)
        redis_store.set(access_jti, "true", ACCESS_EXPIRES * 1.2)

        response = jsonify({"refresh": True})
        set_access_cookies(response, access_token)
        return make_response(response, 200)


class AllTeachers(MethodView):
    def get(self):
        return {"message": "List of Teachers"}

    def delete(self):
        return {"message": "Delete all Teachers"}


class CurrentUser(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        teacher = jwt_user
        try:
            t = Teacher.query.filter_by(email=teacher.email).first()
            identity = jsonify({"user": dumper.dump(t)})
            return make_response(identity, 200)
        except Exception as e:
            from server.api import logger

            logger.debug(e)
            logger.debug(teacher)
            return make_response("User not logged in", 400)


class GAuth(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        teacher = jwt_user
        t = Teacher.query.filter_by(email=teacher.email).first()

        request_data = request.get_json()
        try:
            auth_key = "gauth-code_{}".format(t.uuid)
            m = redis_store.set(auth_key, request_data["authCode"])  # noqa

            return make_response(
                jsonify(
                    {
                        "message": "Successfully generated Google form",
                        "status": "Success",
                    }
                ),
                200,
            )

        except Exception as e:  # noqa
            return make_response(
                jsonify({"message": "Encountered error",
                         "status": "Failed"}), 400
            )


class ConfirmAccount(MethodView):
    def post(self):
        post_data = request.get_json()
        confirmation_token = post_data["token"]
        teacher = Teacher.query.filter_by(confirmation_token=confirmation_token).first()

        if not teacher:
            abort(404, "Encountered an error confirming account. Make sure the email is correct.")

        if confirmation_token is None or not teacher.valid_confirmation_token(confirmation_token):
            abort(404, "Encountered an error. Invalid token.")

        if not teacher.confirm_user():
            abort(400, "Account already confirmed.")

        return make_response(jsonify({
            "status": "Success",
            "message": "Account successfully confirmed."
        }), 200)


reset_account_args = {
    'email': fields.Email(required=True)
}


class ResetAccount(MethodView):
    @use_kwargs(reset_account_args, location='query')
    def get(self, email):
        send_account_recovery_instructions.delay(email)
        return make_response(jsonify({
            "status": "Success",
            "message": "Recovery successful. If the account\
                        exists, you will get a recovery instruction."
        }), 200)

    def post(self):
        post_data = request.get_json()
        token = post_data["token"]
        email = post_data["email"]
        password = bcrypt.generate_password_hash(
            post_data["password"]).decode("utf-8")

        teacher = Teacher.query.filter_by(email=email).first()

        if not teacher:
            abort(404, "Encountered an recovering account. Make sure the email is correct.")

        if token is None or not teacher.valid_recovery_token(token):
            abort(404, "Encountered an error. Invalid token.")

        if not teacher.reset_account(token, password):
            abort(400, "Account token not recognized.")

        return make_response(jsonify({
            "status": "Success",
            "message": "Account successfully recovered. Please login with your new credentials."
        }), 200)


class InviteTeacher(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        teacher = jwt_user
        t = Teacher.query.filter_by(email=teacher.email).first()

        post_data = request.get_json()
        email = post_data["email"]
        try:
            Invitations(email, token_hex(8), t.id).save()
            send_user_invite.delay(email)

            return make_response(jsonify({
                'status': 'success',
                'message': 'Invite Sent!'
            }))
        except Exception as e:
            logger.error(e)
            return make_response(jsonify({
                'status': 'error',
                'message': 'Encountered an error.'
            }))


class SendConfirmation(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        post_data = request.get_json()
        email = post_data["email"]
        if email is None:
            abort(400, "Email is required to perform this action.")

        teacher = Teacher.query.filter_by(email=email).first()

        if teacher is None:
            abort(404, "Email doesn't exist.")

        try:
            send_confirmation_instructions.apply_async(args=[teacher.id])
            return make_response(jsonify({
                'status': 'success',
                'message': 'Confirmation instruction Sent! Check your mailbox.'
            }), 200)
        except Exception as e:
            logger.error(e)
            return make_response(jsonify({
                'status': 'error',
                'message': 'Couldn\'t send confirmation instruction. Please wait while we resolve the issue.'  # noqa
            }), 500)


teacher_auth_blueprint.add_url_rule(
    "/teacher/registration", view_func=TeacherRegistration.as_view('registration_api'))
teacher_auth_blueprint.add_url_rule("/teacher/login", view_func=TeacherLogin.as_view('login_api'))
teacher_auth_blueprint.add_url_rule(
    "/teacher/logout", view_func=TeacherLogout.as_view('logout_api'))
teacher_auth_blueprint.add_url_rule(
    "/teacher/token/refresh", view_func=TokenRefresh.as_view('refresh_api'))
teacher_auth_blueprint.add_url_rule("/teachers", view_func=AllTeachers.as_view('all_teachers_api'))
teacher_auth_blueprint.add_url_rule(
    "/teacher/current", view_func=CurrentUser.as_view('current_api'))
teacher_auth_blueprint.add_url_rule("/teacher/auth/google", view_func=GAuth.as_view('gauth_api'))
teacher_auth_blueprint.add_url_rule(
    "/teacher/confirm", view_func=ConfirmAccount.as_view('confirm_api'))
teacher_auth_blueprint.add_url_rule("/teacher/reset-password",
                                    view_func=ResetAccount.as_view('reset_password_api'))
teacher_auth_blueprint.add_url_rule(
    "/teacher/invite", view_func=InviteTeacher.as_view('invite_api'))
teacher_auth_blueprint.add_url_rule(
    "/teacher/send_confirmation", view_func=SendConfirmation.as_view('send_confirmation_api'))
