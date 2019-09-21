import json

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource
from server import db
from server.decorators import with_required_roles
from server.models import SchoolClass as SchoolClassModel
from sqlalchemy import exc

school_class_blueprint = Blueprint('school_class', __name__)
api = Api(school_class_blueprint)


class SchoolClass(Resource):
    @jwt_required
    def get(self, school_class_id):
        error_response = jsonify({
            'message': "Class room doesn't exist"
        })
        try:
            class_room = SchoolClassModel.query.filter_by(
                id=int(school_class_id)).first()
            if not class_room:
                return error_response, 404
            else:
                response_object = jsonify({
                    'status': 'success',
                    'data': class_room.to_json()
                })
            return make_response(response_object, 200)
        except ValueError:
            return make_response(error_response, 404)


class SchoolClassList(Resource):
    def get(self):
        response_object = jsonify({
            'status': 'success',
            'data': {
                'school_classes': [classroom.to_json() for classroom in SchoolClassModel.query.all()]
            }
        })
        return make_response(response_object, 200)

    @with_required_roles(["Teacher", "Admin"])
    def post(self):
        post_data = request.get_json()
        error_object = jsonify({
            'status': 'fail',
            'message': 'Invalid payload.'
        })
        if not post_data:
            return make_response(error_object, 400)
        name = post_data.get('name')
        subject = post_data.get('subject')
        start_date = post_data.get('start_date')
        student_id = post_data.get('student_id')
        teacher_id = post_data.get('teacher_id')
        try:
            school_class = SchoolClassModel.query.filter_by(name=name).first()
            if not school_class:
                db.session.add(SchoolClassModel(name=name, subject=subject,
                                                start_date=start_date, student_id=student_id, teacher_id=teacher_id))
                db.session.commit()
                response_object = jsonify({
                    'status': 'success',
                    'message': '{} was added!'.format(name)
                })
                return make_response(response_object, 201)
            else:
                error_object['message'] = 'Sorry. That school class already exists.'
                return make_response(error_object, 400)
        except exc.IntegrityError:
            db.session.rollback()
            return make_response(error_object, 500)


class SchoolClassPing(Resource):
    def get(self):
        return make_response(jsonify({
            'status': 'success',
            'message': 'Pinged school class'
        }))


api.add_resource(SchoolClassPing, '/school_class/ping')
api.add_resource(SchoolClass, '/school_class/<school_class_id>')
api.add_resource(SchoolClassList, '/school_class')
