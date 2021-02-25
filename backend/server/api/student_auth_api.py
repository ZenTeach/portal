from datetime import timedelta

from flask import (Blueprint, abort, current_app, jsonify, make_response,
                   request)
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jti, get_jwt_claims, get_jwt_identity,
                                get_raw_jwt, jwt_refresh_token_required,
                                jwt_required, set_access_cookies,
                                set_refresh_cookies)
from flask_restful import Api, Resource
from server import bcrypt, jwt, redis_store
from server.api import logger, report_5xx_error
from server.models import Student, StudentSchema
from server.tasks import send_student_confirmation_instructions

student_auth_blueprint = Blueprint("student_auth", __name__)
api = Api(student_auth_blueprint)
dumper = StudentSchema()
ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)


@jwt.user_identity_loader
def load_user(identity):
    return {"identity": dumper.dump(identity)}


class StudentRegistration(Resource):
    def post(self):
        data = request.get_json()
        if Student.query.filter_by(email=data["email"]).first():
            return {
                "message": "Student {} already exists".format(data["email"])
            }

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
            access_token = create_access_token(identity=new_student)
            refresh_token = create_refresh_token(identity=new_student)
            response = jsonify(
                {"message": "Student {} was created".format(
                    new_student.full_name)}
            )
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "false", REFRESH_EXPIRES * 1.2)

            return make_response(response, 200)
        except Exception as e:
            current_app.logger.error(e)
            report_5xx_error(e)
            return make_response(
                jsonify({"message": "Something went wrong"}),
                500)


class StudentLogin(Resource):
    def post(self):
        data = request.get_json()
        current_user = Student.query.filter_by(email=data["email"]).first()
        if not current_user:
            return make_response(
                jsonify({
                    "message": "User {} doesn't exist".format(data["email"])
                }), 404)

        if bcrypt.check_password_hash(current_user.password, data["password"]):
            access_token = create_access_token(identity=current_user)
            refresh_token = create_refresh_token(identity=current_user)
            response = jsonify(
                {"message": "Logged in as {}".format(current_user.email)}
            )
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, "false", REFRESH_EXPIRES * 1.2)

            return make_response(response, 200)
        else:
            return make_response({"message": "Wrong credentials"}, 400)


class StudentLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()["jti"]
        redis_store.set(jti, "true", ACCESS_EXPIRES * 1.2)
        return jsonify({"msg": "Access token revoked"}), 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_claims()
        current_identity = get_jwt_identity()["identity"]
        current_user = Student.query.filter_by(email=current_identity["email"]).first()
        access_token = create_access_token(identity=current_user)
        access_jti = get_jti(encoded_token=access_token)
        redis_store.set(access_jti, "false", ACCESS_EXPIRES * 1.2)

        response = jsonify({"refresh": True})
        set_access_cookies(response, access_token)
        return make_response(response, 200)


class CurrentUser(Resource):
    @jwt_required
    def get(self):
        # Fetches and returns the current logged in user
        try:
            identity = jsonify({"user": get_jwt_identity()})
            return make_response(identity, 200)
        except Exception as e:
            logger.error(
                "Got an error fetching current user", e)
            return make_response("User not logged in", 400)


@api.resource("/student/auth/refresh_revoke")
class StudentAuthRefreshRevoke(Resource):
    @jwt_refresh_token_required
    def delete(self):
        jti = get_raw_jwt()["jti"]
        redis_store.set(jti, "true", REFRESH_EXPIRES * 1.2)
        return jsonify({"msg": "Refresh token revoked"}), 200


class ConfirmAccount(Resource):
    def post(self):
        post_data = request.get_json()
        confirmation_token = post_data["token"]
        student = Student.query.filter_by(confirmation_token=confirmation_token).first()

        if not student:
            abort(404, "Encountered an error confirming account. Make sure the email is correct.")

        if confirmation_token is None or not student.valid_confirmation_token(confirmation_token):
            abort(404, "Encountered an error. Invalid token.")

        if not student.confirm_user():
            abort(400, "Account already confirmed.")

        return make_response(jsonify({
            "status": "Success",
            "message": "Account successfully confirmed."
        }), 200)


class SendStudentConfirmation(Resource):
    @jwt_required
    def get(self, student_id):
        student = Student.query.filter_by(id=student_id).first()

        if not student:
            abort(404, "Student not found.")

        try:
            send_student_confirmation_instructions.apply_async(args=[student.id])
        except Exception as e:
            report_5xx_error(e)
            abort(500, "Server got an error sending confirmation email.")
        else:
            return make_response(jsonify({
                "status": "Success",
                "message": "Confirmation email is on it's way!"
            }), 200)


api.add_resource(StudentRegistration, "/student/registration")
api.add_resource(StudentLogin, "/student/login")
api.add_resource(StudentLogout, "/student/logout")
api.add_resource(TokenRefresh, "/student/token/refresh")
api.add_resource(CurrentUser, "/student/current")
api.add_resource(ConfirmAccount, "/student/confirm")
api.add_resource(SendStudentConfirmation, "/student/<int:student_id>/send_confirmation")
