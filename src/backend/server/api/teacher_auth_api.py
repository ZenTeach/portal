from flask import Blueprint, jsonify
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_raw_jwt)

from server.models import Teacher
from server import db, bcrypt

teacher_auth_blueprint = Blueprint('teacher_auth', __name__)
api = Api(teacher_auth_blueprint)

parser = reqparse.RequestParser()
parser.add_argument('email', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)
parser.add_argument('firstname', required=True)
parser.add_argument('lastname', required=True)
parser.add_argument('date_of_birth', required=True)

class TeacherRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        if Teacher.query.filter_by(email = data['email']).first():
            return {'message': 'Teacher {} already exists'. format(data['email'])}

        password_hash = bcrypt.generate_password_hash(data['password'])
        new_teacher = Teacher(
            firstname = data['firstname'],
            lastname = data['lastname'],
            email = data['email'],
            password = password_hash,
            date_of_birth = data['date_of_birth']
        )
        try:
            db.session.add(new_teacher)
            db.session.commit()
            access_token = create_access_token(identity = data['email'])
            refresh_token = create_refresh_token(identity = data['email'])
            return {
                'message': 'Teacher {} was created'.format( new_teacher.full_name ),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'message': 'Something went wrong'}, 500


class TeacherLogin(Resource):
    def post(self):
        data = parser.parse_args()
        current_user = Teacher.query.filter_by(data['email'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if bcrypt.check_password_hash(current_user.password, data['password']):
            access_token = create_access_token(identity = data['email'])
            refresh_token = create_refresh_token(identity = data['email'])
            response =  jsonify({
                'message': 'Logged in as {}'.format(current_user.email)
            })
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return resp, 200
        else:
            return {'message': 'Wrong credentials'}
      
      
class TeacherLogout(Resource):
    @jwt_required
    def post(self):
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        return resp, 200    
      
class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)

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
      

api.add_resource(TeacherRegistration, '/teacher/registration')
api.add_resource(TeacherLogin, '/teacher/login')
api.add_resource(TeacherLogout, '/teacher/logout')
api.add_resource(TokenRefresh, '/teacher/token/refresh')
api.add_resource(AllTeachers, '/teachers')