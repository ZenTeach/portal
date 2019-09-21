from flask import Blueprint, jsonify, request, make_response, current_app
import logging
from flask_restful import Resource, Api
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies, get_jwt_identity, get_raw_jwt)
from server.models import Teacher
from server import db, bcrypt, jwt

teacher_auth_blueprint = Blueprint('teacher_auth', __name__)
api = Api(teacher_auth_blueprint)

logger = logging.getLogger('resources.api')
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s: %(levelname)s %(message)s')

@jwt.user_identity_loader
def load_user(identity):
    return { 'identity': identity.to_json() }

class TeacherRegistration(Resource):
    def post(self):
        data = request.get_json()
        if Teacher.query.filter_by(email = data['email']).first():
            return {'message': 'Teacher {} already exists'. format(data['email'])}

        password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_teacher = Teacher(
            firstname = data['firstname'],
            lastname = data['lastname'],
            email = data['email'],
            password = password_hash,
            date_of_birth = data['date_of_birth']
        )
        try:
            new_teacher.save()
            access_token = create_access_token(identity = new_teacher)
            refresh_token = create_refresh_token(identity = new_teacher)
            response = jsonify({
                    'message': 'Teacher {} was created'.format( new_teacher.full_name() )
                })
            # import pdb
            # pdb.set_trace()
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return  make_response(response, 200)
        except Exception as e:
            current_app.logger.error(e)
            return make_response(jsonify({'message': 'Something went wrong'}), 500)

class TeacherLogin(Resource):
    def post(self):
        data = request.get_json()
        print("Got a request with this payload: ", data)
        current_user = Teacher.query.filter_by(email=data['email']).first()
        if not current_user:
            return make_response(jsonify({'message': 'User {} doesn\'t exist'.format(data['email'])}), 404)
        
        if bcrypt.check_password_hash(current_user.password, data['password']):
            access_token = create_access_token(identity = current_user)
            refresh_token = create_refresh_token(identity = current_user)
            response =  jsonify({
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

api.add_resource(TeacherRegistration, '/teacher/registration')
api.add_resource(TeacherLogin, '/teacher/login')
api.add_resource(TeacherLogout, '/teacher/logout')
api.add_resource(TokenRefresh, '/teacher/token/refresh')
api.add_resource(AllTeachers, '/teachers')
api.add_resource(CurrentUser, '/teacher/current')