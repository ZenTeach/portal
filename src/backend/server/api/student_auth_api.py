from flask import Blueprint, jsonify, request, make_response, current_app
from flask_restful import Resource, Api
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, set_access_cookies,
                                set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_raw_jwt, get_jwt_claims)
from server.models import Student
from server import db, bcrypt, jwt

student_auth_blueprint = Blueprint('student_auth', __name__)
api = Api(student_auth_blueprint)


@jwt.user_identity_loader
def load_user(identity):
    return {'identity': identity.to_json()}


class StudentRegistration(Resource):
    def post(self):
        data = request.get_json()
        if Student.query.filter_by(email=data['email']).first():
            return {'message': 'Student {} already exists'. format(data['email'])}

        password_hash = bcrypt.generate_password_hash(
            data['password']).decode('utf-8')
        new_student = Student(
            firstname=data['firstname'],
            lastname=data['lastname'],
            email=data['email'],
            password=password_hash,
            date_of_birth=data['date_of_birth'],
            classes=data['classes'],
            quiz_grades=data['quiz_grades']
        )
        try:
            new_student.save()
            access_token = create_access_token(identity=new_student)
            refresh_token = create_refresh_token(identity=new_student)
            response = jsonify({
                'message': 'Student {} was created'.format(new_student.full_name())
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return make_response(response, 200)
        except Exception as e:
            current_app.logger.error(e)
            return make_response(jsonify({'message': 'Something went wrong'}), 500)


class StudentLogin(Resource):
    def post(self):
        data = request.get_json()
        print("Got a request with this payload: ", data)
        current_user = Student.query.filter_by(email=data['email']).first()
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


class StudentLogout(Resource):
    @jwt_required
    def post(self):
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        return make_response(resp, 200)


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_claims()
        access_token = create_access_token(identity=current_user)

        response = jsonify({
            'refresh': True
        })
        set_access_cookies(resp, access_token)
        return make_response(response, 200)


class AllStudents(Resource):
    def get(self):
        return {'message': 'List of Teachers'}

    def delete(self):
        return {'message': 'Delete all Teachers'}


class CurrentUser(Resource):
    @jwt_required
    def get(self):
        # Fetches and returns the current logged in user
        try:
            identity = jsonify({
                'user': get_jwt_identity()
            })
            return make_response(identity, 200)
        except:
            return make_response("User not logged in", 400)


api.add_resource(StudentRegistration, '/student/registration')
api.add_resource(StudentLogin, '/student/login')
api.add_resource(StudentLogout, '/student/logout')
api.add_resource(TokenRefresh, '/student/token/refresh')
api.add_resource(AllStudents, '/students')
api.add_resource(CurrentUser, '/student/current')
