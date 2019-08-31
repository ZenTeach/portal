from sqlalchemy import exc
from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required

import json
from server.models import SchoolClass as SchoolClassModel
from server import db

school_class_blueprint = Blueprint('school_class', __name__)
api = Api(school_class_blueprint)

class SchoolClass(Resource):
    @jwt_required
    def get(self, school_class_id):
        error_response = {
            'message': "Class room doesn't exist"
        }
        try:
            class_room = SchoolClassModel.query.filter_by(id=int(school_class_id)).first()
            if not class_room:
                return error_response, 404
            else:
                response_object = {
                    'status': 'success',
                    data: class_room.to_json()
                }
            return response_object, 200
        except ValueError:
            return error_response, 404

class SchoolClassList(Resource):
    def get(self):
        response_object = {
            'status': 'success',
            'data': {
                'school_classes': [classroom.to_json() for classroom in SchoolClassModel.query.all()]
            }
        }
        return response_object, 200

    def post(self):
        post_data = request.get_json()
        error_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return error_object, 400
        name = post_data.get('name')
        subject = post_data.get('subject')
        start_date = post_data.get('start_date')
        try:
            school_class = SchoolClassModel.query.filter_by(subject=subject).first()
            if not school_class:
                db.session.add(SchoolClassModel(name=name,subject=subject,start_date=start_date))
                db.session.commit()
                response_object = {
                    'status' : 'success',
                    'message': f'{name} was added!'
                }
                return response_object, 201
            else:
                error_object['message'] = 'Sorry. That school class already exists.'
                return error_object, 400
        except exc.IntegrityError:
            db.session.rollback()
            return error_object, 500

class SchoolClassPing(Resource):
    def get(self):
        return {
            'status': 'success',
            'message': 'Pinged school class'
        }

api.add_resource(SchoolClassPing, '/school_class/ping')
api.add_resource(SchoolClass, '/school_class/<school_class_id>')
api.add_resource(SchoolClassList, '/school_class')
