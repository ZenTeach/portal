from datetime import timedelta

from flask import (Blueprint, abort, current_app, jsonify, make_response,
                   request)
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jti, get_jwt_identity, get_raw_jwt,
                                jwt_refresh_token_required, jwt_required,
                                set_access_cookies, set_refresh_cookies)
from flask_restful import Api, Resource
from server import bcrypt, jwt, redis_store
from server.models import Teacher, TeacherSchema
from server.tasks import confirm_and_send_instruction

teacher_auth_blueprint = Blueprint("teacher_auth", __name__)
api = Api(teacher_auth_blueprint)
dumper = TeacherSchema()
ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)


@jwt.user_identity_loader
def load_user(identity):
    return {"identity": dumper.dump(identity)}


class TeacherRegistration(Resource):
    def post(self):
        data = request.get_json()
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
            access_token = create_access_token(identity=new_teacher)
            refresh_token = create_refresh_token(identity=new_teacher)
            response = jsonify({
                'message': 'Teacher {} was created'.format(new_teacher.full_name())
            })

            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "false", REFRESH_EXPIRES * 1.2)

            confirm_and_send_instruction.delay(new_teacher.id)

            return make_response(response, 200)
        except Exception as e:
            current_app.logger.error(e)
            return make_response(
                jsonify({
                    "message": "Something went wrong"
                }),
                500)


class TeacherLogin(Resource):
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
            access_token = create_access_token(identity=current_user)
            refresh_token = create_refresh_token(identity=current_user)
            response_data = jsonify({
                'message': 'Logged in as {}'.format(current_user.email)
            })
            set_access_cookies(response_data, access_token)
            set_refresh_cookies(response_data, refresh_token)
            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "false", REFRESH_EXPIRES * 1.2)

            response = make_response(response_data, 200)
            return response

        else:
            return make_response({"message": "Wrong credentials"}, 400)


class TeacherLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        redis_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
        return make_response(jsonify({"msg": "Access token revoked"}), 200)


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        access_jti = get_jti(encoded_token=access_token)
        redis_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)

        response = jsonify({"refresh": True})
        set_access_cookies(response, access_token)
        return make_response(response, 200)


class AllTeachers(Resource):
    def get(self):
        return {"message": "List of Teachers"}

    def delete(self):
        return {"message": "Delete all Teachers"}


class CurrentUser(Resource):
    @jwt_required
    def get(self):
        teacher = get_jwt_identity()["identity"]
        t = Teacher.query.filter_by(email=teacher["email"]).first()
        try:
            identity = jsonify({"user": dumper.dump(t)})
            return make_response(identity, 200)
        except Exception as e:
            from server.api import api_logger

            api_logger.debug(e)
            return make_response("User not logged in", 400)


@api.resource("/student/auth/refresh_revoke")
class StudentAuthRefreshRevoke(Resource):
    @jwt_refresh_token_required
    def delete(self):
        jti = get_raw_jwt()["jti"]
        redis_store.set(jti, "true", REFRESH_EXPIRES * 1.2)
        return jsonify({"msg": "Refresh token revoked"}), 200


class GAuth(Resource):
    @jwt_required
    def post(self):
        teacher = get_jwt_identity()["identity"]
        t = Teacher.query.filter_by(email=teacher["email"]).first()

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


class ConfirmAccount(Resource):
    def post(self):
        print("Inside ConfirmAccount")
        post_data = request.get_json()
        teacher_email = post_data["email"]
        confirmation_token = post_data["token"]
        teacher = Teacher.query.filter_by(email=teacher_email).first()

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


class ResetAccount(Resource):
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
            abort(400, "Account already confirmed.")

        return make_response(jsonify({
            "status": "Success",
            "message": "Account successfully recovered."
        }), 200)


api.add_resource(TeacherRegistration, "/teacher/registration")
api.add_resource(TeacherLogin, "/teacher/login")
api.add_resource(TeacherLogout, "/teacher/logout")
api.add_resource(TokenRefresh, "/teacher/token/refresh")
api.add_resource(AllTeachers, "/teachers")
api.add_resource(CurrentUser, "/teacher/current")
api.add_resource(GAuth, "/teacher/auth/google")
api.add_resource(ConfirmAccount, "/teacher/confirm")
api.add_resource(ResetAccount, "/teacher/reset-password")
