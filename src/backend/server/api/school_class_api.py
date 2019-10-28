import json

from flask import Blueprint, jsonify, make_response, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Api, Resource
from server import db
from server.decorators import with_required_roles
from server.models import SchoolClassSchema, SchoolClass as SchoolClassModel
from sqlalchemy import exc

school_class_blueprint = Blueprint('school_class', __name__)
api = Api(school_class_blueprint)
schema_dumper = SchoolClassSchema()


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
                return make_response(error_response, 404)
            else:
                response_object = jsonify({
                    'status': 'success',
                    'data': schema_dumper.dump(class_room)
                })
            return make_response(response_object, 200)
        except ValueError:
            return make_response(error_response, 404)


class SchoolClassList(Resource):
    @jwt_required
    @with_required_roles(['Admin'])
    def get(self):
        response_object = jsonify({
            'status': 'success',
            'data': {
                'school_classes': [classroom.to_json() for classroom in SchoolClassModel.query.all()]
            }
        })
        return make_response(response_object, 200)

    @jwt_required
    @with_required_roles(["Teacher", "Admin"])
    def post(self):
        post_data = request.get_json()
        error_object = jsonify({
            'status': 'fail',
            'message': 'Invalid payload.'
        })
        teacher = get_jwt_identity()['identity']
        if not post_data:
            return make_response(error_object, 400)
        name = post_data.get('name')
        subject = post_data.get('subject')
        start_date = post_data.get('start_date')
        student_id = post_data.get('student_id')
        teacher_id = teacher["id"]
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
        except exc.IntegrityError as err:
            db.session.rollback()
            return make_response(error_object, 500)


class SchoolClassOwned(Resource):
    @jwt_required
    @with_required_roles(['Admin'])
    def get(self, teacher_id):
        error_message = jsonify({
            'message': "Class room doesn't exist"
        })
        try:
            class_rooms = SchoolClassModel.query.filter_by(
                teacher_id=int(teacher_id)).all()
            if not class_rooms:
                return make_response(error_response, 404)
            else:

                response_object = jsonify({
                    'status': 'success',
                    'data': [schema_dumper.dump(classroom) for classroom in class_rooms]
                    # 'data': schema_dumper.dump(class_rooms)
                })
                return make_response(response_object, 200)
        except ValueError:
            return make_response(error_message, 400)


class TeacherOwnedClass(Resource):
    @jwt_required
    def get(self):
        error_object = {
            'message': ''
        }
        try:
            teacher = get_jwt_identity()['identity']
            class_rooms = SchoolClassModel.query.filter_by(
                teacher_id=int(teacher['id']))

            if not class_rooms:
                error_object['message'] = 'No class rooms found'
                return make_response(jsonify(error_object), 200)
            else:
                response_object = jsonify({
                    'status': 'success',
                    # 'data': [classroom.to_json() for classroom in class_rooms]
                    'data': [schema_dumper.dump(classroom) for classroom in class_rooms]
                })
                return make_response(response_object, 200)
        except Exception as e:
            from server.api import api_logger
            api_logger.debug(e)
            error_object['message'] = 'Error processing request'
            return make_response(jsonify(error_object), 500)


class SchoolClassPing(Resource):
    def get(self):
        return make_response(jsonify({
            'status': 'success',
            'message': 'Pinged school class'
        }))


api.add_resource(SchoolClassPing, '/school_class/ping')
api.add_resource(SchoolClass, '/school_class/<school_class_id>')
api.add_resource(SchoolClassOwned, '/school_class/owned/<teacher_id>')
api.add_resource(TeacherOwnedClass, '/school_class/owned')
api.add_resource(SchoolClassList, '/school_class')
