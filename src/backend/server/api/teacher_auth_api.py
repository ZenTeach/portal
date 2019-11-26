from flask import Blueprint, jsonify, request, make_response, current_app
from flask_restful import Resource, Api
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, set_access_cookies,
                                set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_raw_jwt)
from server.models import Teacher, TeacherSchema
from server import db, bcrypt, jwt
from pathlib import Path
import pickle
import requests
import os.path as path
import os
import json

teacher_auth_blueprint = Blueprint('teacher_auth', __name__)
api = Api(teacher_auth_blueprint)
dumper = TeacherSchema()


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
            response = jsonify({
                'message': 'Logged in as {}'.format(current_user.email)
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return make_response(response, 200)
        else:
            return make_response({'message': 'Wrong credentials'}, 400)


class TeacherLogout(Resource):
    @jwt_required
    def post(self):
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        return make_response(resp, 200)


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)

        response = jsonify({
            'refresh': True
        })
        set_access_cookies(resp, access_token)
        return response, 200


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


class GAuth(Resource):
    def post(self):
        credentials_dir = path.join(os.getcwd(), "server", "lib/interfaces/client_id.json")
        print(credentials_dir)
        creds = None
        with open(credentials_dir, 'rb') as f:
            # creds = pickle.load(f)
            creds = json.load(f)
        request_data = request.get_json()
        print(creds)
        try:
            data = {
                'client_id': creds['web']['client_id'],
                'client_secret': creds['web']['client_secret'],
                'redirect_uri': 'postmessage',
                'grant_type': 'authorization_code',
                'code': request_data['authCode']
            }
            response = requests.post(creds['web']['token_uri'], data=data)
            response_data = response.json()
            print("GAuth response", response_data)
            keys = {
                'access_token':response_data['access_token'],
                'id_token': response_data['id_token']
            }
            output = path.join(os.getcwd(), "server", "lib/interfaces/token.pickle")
            with open(output, 'wb') as token:
                pickle.dump(keys, token)
        except Exception as e:
            pass


api.add_resource(TeacherRegistration, '/teacher/registration')
api.add_resource(TeacherLogin, '/teacher/login')
api.add_resource(TeacherLogout, '/teacher/logout')
api.add_resource(TokenRefresh, '/teacher/token/refresh')
api.add_resource(AllTeachers, '/teachers')
api.add_resource(CurrentUser, '/teacher/current')
api.add_resource(GAuth, '/teacher/auth/google')
