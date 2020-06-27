from flask import Blueprint, jsonify, request, make_response, current_app, url_for, redirect
from flask_restful import Resource, Api
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, set_access_cookies,
                                set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_raw_jwt, get_jti, get_csrf_token)
from server.models import Teacher, TeacherSchema
from server import db, bcrypt, jwt, redis_store
from pathlib import Path
import pickle
from datetime import timedelta
import requests
import os.path as path
import os
import json

teacher_auth_blueprint = Blueprint('teacher_auth', __name__)
api = Api(teacher_auth_blueprint)
dumper = TeacherSchema()
ACCESS_EXPIRES = timedelta(days=1)
REFRESH_EXPIRES = timedelta(days=30)

@jwt.user_identity_loader
def load_user(identity):
    return {'identity': dumper.dump(identity)}

class TeacherRegistration(Resource):
    def post(self):
        data = request.get_json()
        if Teacher.query.filter_by(email=data['email']).first():
            return {'message': 'Teacher {} already exists'. format(data['email'])}

        password_hash = bcrypt.generate_password_hash(
            data['password']).decode('utf-8')
        new_teacher = Teacher(
            firstname=data['firstname'],
            lastname=data['lastname'],
            email=data['email'],
            password=password_hash,
            date_of_birth=data['date_of_birth'],
            role=data['role']
        )
        try:
            new_teacher.save()
            access_token = create_access_token(identity=new_teacher)
            refresh_token = create_refresh_token(identity=new_teacher)
            response = jsonify({
                'message': 'Teacher {} was created'.format(new_teacher.full_name())
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)

            return make_response(response, 200)
        except Exception as e:
            current_app.logger.error(e)
            return make_response(jsonify({'message': 'Something went wrong'}), 500)


class TeacherLogin(Resource):
    def post(self):
        data = request.get_json()
        current_user = Teacher.query.filter_by(email=data['email']).first()
        if not current_user:
            return make_response(jsonify({'message': 'User {} doesn\'t exist'.format(data['email'])}), 404)

        if bcrypt.check_password_hash(current_user.password, data['password']):
            access_token = create_access_token(identity=current_user)
            refresh_token = create_refresh_token(identity=current_user)
            response_data = jsonify({
                'message': 'Logged in as {}'.format(current_user.email)
            })
            set_access_cookies(response_data, access_token)
            set_refresh_cookies(response_data, refresh_token)
            access_jti = get_jti(encoded_token=access_token)
            refresh_jti = get_jti(encoded_token=refresh_token)
            redis_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
            redis_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)


            response = make_response(response_data, 200)
            return response

        else:
            return make_response({'message': 'Wrong credentials'}, 400)


class TeacherLogout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        redis_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)
        return make_response(jsonify({"msg": "Access token revoked"}), 200)



class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        access_jti = get_jti(encoded_token=access_token)
        redis_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)

        response = jsonify({
            'refresh': True
        })
        set_access_cookies(response, access_token)
        return make_response(response, 200)


class AllTeachers(Resource):
    def get(self):
        return {'message': 'List of Teachers'}

    def delete(self):
        return {'message': 'Delete all Teachers'}


class CurrentUser(Resource):
    @jwt_required
    def get(self):
        teacher = get_jwt_identity()['identity']
        t = Teacher.query.filter_by(email=teacher["email"]).first()
        try:
            identity = jsonify({
                'user': dumper.dump(t)
            })
            return make_response(identity, 200)
        except Exception as e:
            from server.api import api_logger
            api_logger.debug(e)
            return make_response("User not logged in", 400)

@api.resource('/student/auth/refresh_revoke')
class StudentAuthRefreshRevoke(Resource):
    @jwt_refresh_token_required
    def delete():
        jti = get_raw_jwt()['jti']
        redis_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
        return jsonify({"msg": "Refresh token revoked"}), 200

class GAuth(Resource):
    @jwt_required
    def post(self):
        teacher = get_jwt_identity()['identity']
        t = Teacher.query.filter_by(email=teacher["email"]).first()

        request_data = request.get_json()
        try:
            auth_key = "gauth-code_{}".format(t.uuid)
            m = redis_store.set(auth_key, request_data['authCode'])

            return make_response(jsonify({
                "message": "Successfully generated Google form",
                "status": "Success"}), 200)

        except Exception as e:
            return make_response(jsonify({
                "message": "Encountered error",
                "status": "Failed"}), 400)


api.add_resource(TeacherRegistration, '/teacher/registration')
api.add_resource(TeacherLogin, '/teacher/login')
api.add_resource(TeacherLogout, '/teacher/logout')
api.add_resource(TokenRefresh, '/teacher/token/refresh')
api.add_resource(AllTeachers, '/teachers')
api.add_resource(CurrentUser, '/teacher/current')
api.add_resource(GAuth, '/teacher/auth/google')
