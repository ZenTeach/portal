from datetime import timedelta

from flask import Blueprint, current_app, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                current_user, get_jti, get_jwt, jwt_required)
from server import bcrypt, jwt, redis_store
from server.api import logger
from server.lib.utils.jwt_fixes import set_access_cookies, set_refresh_cookies
from server.models import Student, StudentSchema
from server.tasks import send_student_confirmation_instructions

student_auth_blueprint = Blueprint("student_auth", __name__)

dumper = StudentSchema()
ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)


@jwt.user_lookup_loader
def lookup_user(args, kwargs) -> Student:
    return Student.query.get(kwargs["sub"]["id"])


@jwt.user_identity_loader
def load_user(*args, **kwargs) -> Student:
    return Student.query.get(args[0])


class StudentRegistration(MethodView):
    def post(self):
        data = request.get_json()
        if Student.query.filter_by(email=data["email"]).first():
            return make_response(jsonify({
                "message": "Student {} already exists".format(data["email"])
            }), 400)

        password_hash = bcrypt.generate_password_hash(
            data["password"]).decode("utf-8")
        new_student = Student(
            firstname=data["firstname"],
            lastname=data["lastname"],
            email=data["email"],
            password=password_hash
        )
        try:
            new_student.save()
            access_token = create_access_token(new_student.id, fresh=True)
            refresh_token = create_refresh_token(new_student.id)
            response = jsonify(
                {"message": "Student {} was created".format(
                    new_student.full_name)}
            )
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            access_jti = get_jti(access_token)
            refresh_jti = get_jti(refresh_token)
            redis_store.set(access_jti, "true", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "true", REFRESH_EXPIRES * 1.2)
            return make_response(response, 200)
        except Exception as e:
            current_app.logger.error(e)
            return make_response(
                jsonify({"message": "Something went wrong"}),
                500)


class StudentLogin(MethodView):
    def post(self):
        data = request.get_json()
        current_user = Student.query.filter_by(email=data["email"]).first()
        if not current_user:
            return make_response(
                jsonify({
                    "message": "User {} doesn't exist".format(data["email"])
                }), 404)

        if bcrypt.check_password_hash(current_user.password, data["password"]):
            access_token = create_access_token(current_user.id, fresh=True)
            refresh_token = create_refresh_token(current_user.id)
            response = jsonify(
                {"message": "Logged in as {}".format(current_user.email)}
            )
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, "true", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "true", REFRESH_EXPIRES * 1.2)

            return make_response(response, 200)
        else:
            return make_response({"message": "Wrong credentials"}, 400)


class StudentLogout(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        jti = get_jwt()["jti"]
        redis_store.set(jti, "false", ACCESS_EXPIRES * 1.2)
        return jsonify({"msg": "Access token revoked"}), 200


class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt()
        current_identity = current_user
        current_user = Student.query.filter_by(email=current_identity.email).first()
        access_token = create_access_token(current_user.id, fresh=True)
        access_jti = get_jti(access_token)
        redis_store.set(access_jti, "true", ACCESS_EXPIRES * 1.2)

        response = jsonify({"refresh": True})
        set_access_cookies(response, access_token)
        return make_response(response, 200)


class CurrentUser(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        # Fetches and returns the current logged in user
        try:
            identity = current_user
            return make_response(identity, 200)
        except Exception as e:
            logger.error(
                "Got an error fetching current user", e)
            return make_response("User not logged in", 400)


class StudentAuthRefreshRevoke(MethodView):
    @jwt_required(refresh=True)
    def delete(self):
        jti = get_jwt()["jti"]
        redis_store.set(jti, "true", REFRESH_EXPIRES * 1.2)
        return jsonify({"msg": "Refresh token revoked"}), 200


class ConfirmAccount(MethodView):
    def post(self):
        post_data = request.get_json()
        confirmation_token = post_data["token"]
        student = Student.query.filter_by(confirmation_token=confirmation_token).first()

        if not student:
            return make_response(jsonify({
                'message': "Encountered an error confirming account. Make sure the email is correct."  # noqa
            }), 404)

        if confirmation_token is None or not student.valid_confirmation_token(confirmation_token):
            return make_response(jsonify({
                'message': "Encountered an error. Invalid token."
            }), 404)

        if not student.confirm_user():
            return make_response(jsonify({
                'message': "Account already confirmed."
            }), 400)

        return make_response(jsonify({
            "status": "Success",
            "message": "Account successfully confirmed."
        }), 200)


class SendStudentConfirmation(MethodView):
    @jwt_required(fresh=True)
    def get(self, student_id):
        student = Student.query.filter_by(id=student_id).first()

        if not student:
            return make_response(jsonify({
                'message': "Student not found."
            }), 404)

        try:
            send_student_confirmation_instructions.apply_async(args=[student.id])
        except Exception:
            return make_response(jsonify({
                'message': "Server got an error sending confirmation email."
            }), 500)
        else:
            return make_response(jsonify({
                "status": "Success",
                "message": "Confirmation email is on it's way!"
            }), 200)


student_auth_blueprint.add_url_rule(
    "/student/registration", view_func=StudentRegistration.as_view('registration_api'))
student_auth_blueprint.add_url_rule("/student/login", view_func=StudentLogin.as_view('login_api'))
student_auth_blueprint.add_url_rule(
    "/student/logout", view_func=StudentLogout.as_view('logout_api'))
student_auth_blueprint.add_url_rule(
    "/student/token/refresh", view_func=TokenRefresh.as_view('refresh_api'))
student_auth_blueprint.add_url_rule(
    "/student/current", view_func=CurrentUser.as_view('current_api'))
student_auth_blueprint.add_url_rule(
    "/student/confirm", view_func=ConfirmAccount.as_view('confirm_api'))
student_auth_blueprint.add_url_rule("/student/<int:student_id>/send_confirmation",
                                    view_func=SendStudentConfirmation.as_view('send_confirmation_api'))  # noqa
student_auth_blueprint.add_url_rule(
    "/student/auth/refresh_revoke", view_func=StudentAuthRefreshRevoke.as_view('refresh_revoke_api'))  # noqa
