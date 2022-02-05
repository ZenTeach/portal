from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import current_user, jwt_required
from marshmallow import ValidationError
from server import db
from server.api import log_activity, logger
from server.decorators import with_required_roles
from server.lib import format_validation_for_api
from server.models import (KnowledgeItem, Questions, QuestionsSchema, Subject,
                           Topic)
from server.models.question_choice import QuestionChoice
from server.models.questions import \
    AdminFormValidator as QuestionSchemaValidator
from sqlalchemy import exc
from webargs import fields
from webargs.flaskparser import use_kwargs

question_blueprint = Blueprint("question", __name__)
dumper = QuestionsSchema()

question_args = {
    'subject': fields.Str(required=True)
}


class QuestionList(MethodView):
    @jwt_required(fresh=True)
    @use_kwargs(question_args, location='query')
    def get(self, **kwargs):
        subject = kwargs.get('subject')

        question_list = None
        if subject == "":
            question_list = []
        else:
            subject_ = Subject.query.filter(Subject.name.op('~*')(subject)).first()
            if subject_ is None:
                return make_response(jsonify({
                    'questions': [],
                    'message': f"{subject} subject not found"
                }), 400)
            question_list = Questions.query.filter_by(subject_id=subject_.id).all()

        return make_response(
            {"questions": [dumper.dump(question)
                           for question in question_list]}, 200
        )

    @jwt_required(fresh=True)
    def post(self):
        data = request.get_json()
        error_object = jsonify(
            {"status": "fail", "message": "Invalid payload."})

        if not data:
            return make_response(error_object, 400)

        try:
            question_entry = Questions.query.filter_by(
                subject_id=data.get('subject_id'),
                tag=data.get('tag'),
                question=data.get('question')
            ).first()
            if not question_entry:
                Questions.create_from_admin_form(data)

                response_object = jsonify(
                    {"status": "success", "message": "Question was added!"}
                )
                return make_response(response_object, 201)
            else:
                return make_response(jsonify({
                    "status": "fail",
                    "message": "Question already exists."
                }), 400)
        except ValidationError as e:
            logger.error(e)
            return make_response(error_object, 400)
        except Exception as e:
            db.session.rollback()
            logger.error(e)
            return make_response(error_object, 500)


class Question(MethodView):

    @jwt_required(fresh=True)
    def get(self, question_id):
        question = Questions.query.filter_by(id=question_id).first()
        return make_response({"question": dumper.dump(question)}, 200)

    @jwt_required(fresh=True)
    def delete(self, question_id):
        try:
            question = Questions.query.filter_by(id=question_id).first()
            if not question:
                return make_response(
                    jsonify({
                        "message": "Question not found"
                    }),
                    400)
            db.session.delete(question)
            return make_response(
                jsonify({
                    "message": "Deleted question {}".format(question.id)
                }), 204)
        except exc.IntegrityError as e:
            logger.error(e)
            db.session.rollback()
            return make_response(
                jsonify({
                    "message": "Error while deleteing \
                        question id: {}".format(question_id)
                }),
                500)

    @jwt_required(fresh=True)
    @with_required_roles(["Admin"])
    def put(self):
        pass


class TeacherOwnedQuestions(MethodView):

    @jwt_required(fresh=True)
    def get(self):
        teacher = current_user
        questions = teacher.questions

        return make_response(
            jsonify({
                "questions": [dumper.dump(question) for question in questions]
            }), 200)

    @jwt_required(fresh=True)
    def post(self):
        teacher = current_user
        data = request.get_json()
        data.update({
            'user_created': True
        })

        validation_errors = QuestionSchemaValidator().validate(data=data)
        if validation_errors is not None and len(validation_errors) != 0:
            errors = format_validation_for_api(validation_errors)
            return make_response(jsonify(errors), 422)

        if teacher.id != data.get('teacher_id', None):
            return make_response(jsonify({
                'message': 'Teacher is not recognized'
            }), 422)

        if 'subject' in data:
            subject_id = Subject.query.filter_by(name=data.pop('subject')).first().id
            data.update(subject_id=subject_id)
        if 'knowledge_item' in data:
            knowledge_item = KnowledgeItem.query.filter_by(
                value=data.pop('knowledge_item')).first()
            data.update({'knowledge_item': knowledge_item})

        if 'topic' in data:
            topic = Topic.query.filter_by(value=data.pop('topic')).first()
            data.update({'topic': topic})

        choices = data.pop('choices')
        for choice in choices:
            choice.update({
                'user_created': True,
                'teacher_id': teacher.id
            })
        data.update({
            'choices': choices
        })
        question = Questions(**data)
        try:
            question.save()
            log_activity(
                current_user,
                'create',
                'question',
                question.id,
                f'{current_user.full_name()} created question {question.id}'
            )
            return make_response(jsonify({
                'message': 'Question successfully added'
            }), 201)
        except Exception as e:
            logger.exception(e)
            return make_response(jsonify({
                'message': "Run into an error creating question. We will take a look in a bit!"
            }), 500)


class TeacherOwnedQuestion(MethodView):
    @jwt_required(fresh=True)
    def delete(self, question_id):
        teacher = current_user

        question: Questions = Questions.query.filter_by(id=question_id).first()

        if question is None:
            return make_response(jsonify({
                'message': "Question doesn't exist."
            }), 404)

        if question.teacher_id != teacher.id:
            return make_response(jsonify({
                'message': "The selected question doesn't belong to the teacher"
            }), 422)

        try:
            question_id = question.id
            question.delete()
            log_activity(
                current_user,
                'delete',
                'question',
                question.id,
                f'{current_user.full_name()} deleted question {question_id}'
            )
            return make_response(jsonify({
                'message': "Question deleted successfully!"
            }), 204)
        except Exception as e:
            logger.exception(e)
            return make_response(jsonify({
                'message': "We ran into a problem deleting the question."
            }), 500)

    @jwt_required(fresh=True)
    def patch(self, question_id):
        data = request.get_json()
        teacher = current_user

        success_message = {
            'message': "Question was updated successfully."
        }
        status_code = 200
        question: Questions = Questions.query.filter_by(id=question_id).first()
        if question is None:
            return make_response(jsonify({
                'message': "Question doesn't exist."
            }), 404)

        if data is None:
            return make_response(jsonify({
                'message': "Cannot update question with empty values."
            }), 400)

        try:
            if 'subject' in data:
                subject_id = Subject.query.filter_by(name=data.pop('subject')).first().id
                data.update(subject_id=subject_id)

            if 'knowledge_item' in data:
                knowledge_item = KnowledgeItem.query\
                    .filter_by(value=data.pop('knowledge_item'))\
                    .first()
                data.update({
                    'knowledge_item': knowledge_item,
                    'knowledge_item_id': knowledge_item.id
                })

            if 'topic' in data:
                topic = Topic.query.filter_by(value=data.pop('topic')).first()
                data.update({
                    'topic': topic,
                    'topic_id': topic.id
                })
            if question.teacher_id != teacher.id:
                question = Questions.empty_instance()
                data.update({
                    'user_created': True
                })
                success_message['message'] = "Question successfully added."
                status_code = 201

            if 'choices' in data:
                choices = data.pop('choices')
                choice_objects = []
                correct_choice_uuid = [choice['uuid']
                                       for choice in choices
                                       if choice['is_correct_choice']][0]

                for choice_data in choices:
                    c = QuestionChoice.query.\
                        filter_by(uuid=choice_data.pop('uuid')).\
                        first()
                    choice = None
                    is_cloned_choice_correct = False
                    if c is not None:
                        # We clone the choices when it's created freshly by a user
                        if not c.user_created:
                            choice = QuestionChoice.clone(c,
                                                          autosave=True,
                                                          **{
                                                              'user_created': True,
                                                              'teacher_id': teacher.id
                                                          })
                            if str(c.uuid) == correct_choice_uuid:
                                is_cloned_choice_correct = True
                        else:
                            choice = c
                            choice.update_from_dict(choice_data)
                            choice.save()

                        choice_objects.append(choice)
                        if str(choice.uuid) == correct_choice_uuid or is_cloned_choice_correct:
                            data.update({
                                'correct_choice_id': choice.id
                            })
                    else:
                        new_choice = QuestionChoice(
                            **choice_data,
                            user_created=True,
                            teacher_id=teacher.id)
                        new_choice.save()
                        choice_objects.append(new_choice)
                        if choice_data.get('is_correct_choice'):
                            data.update({
                                'correct_choice_id': new_choice.id
                            })

                data.update({
                    'choices': choice_objects
                })
            question.update_from_dict(data)
            question.save()
            log_activity(
                current_user,
                'update',
                'question',
                question.id,
                f'{current_user.full_name()} updated question {question.id}'
            )

            return make_response(jsonify(success_message), status_code)
        except Exception as e:
            logger.exception(e)
            return make_response(jsonify({
                'message': "We ran into a problem updating the question."
            }), 500)


class QuestionSearch(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        query_params = request.get_json()
        try:
            subject_ = Subject.query.filter(Subject.name == query_params['subject']).first()
            if subject_ is None:
                return make_response(jsonify({
                    'message': 'Subject not found'
                }), 404)

            if query_params['query'] == '':
                return make_response(jsonify({
                    'message': 'Query cannot be empty'
                }), 400)
            if query_params['query'] == '*':
                result_set = Questions.query.filter_by(subject_id=subject_.id)
            else:
                result_set = Questions.query.search(
                    query_params["query"]).filter_by(subject_id=subject_.id)

            if len(query_params["topic"]) != 0:
                result_set = result_set.join(Topic)\
                    .filter(Topic.value.in_(query_params["topic"]))

            if len(query_params["knowledge_item"]) != 0:
                result_set = result_set.join(KnowledgeItem)\
                    .filter(KnowledgeItem.value.in_(query_params["knowledge_item"]))

            result_set = result_set.all()

            logger.debug(f"Result set length: {len(result_set)}")
            if len(result_set) != 0:
                response = {"data": [dumper.dump(
                    result) for result in result_set]}
                return make_response(jsonify(response), 200)
            else:
                response = {"message": "No result found"}
                return make_response(jsonify(response), 200)
        except Exception as e:
            logger.error(e)
            error_object = {"message": "Error processing request"}
            return make_response(jsonify(error_object), 500)


class QuestionFromKIsAndTopics(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        json_payload = request.get_json()
        topics = json_payload.get("topics", [])
        kis = json_payload.get("kis", [])
        query = Questions.query

        if len(topics) == 0 and len(kis) == 0:
            return make_response(jsonify({
                'message': 'Topic and Knowledge Items not set'
            }), 400)

        if len(topics) != 0:
            query = query.join(Topic).filter(Topic.value.in_(topics))
        if len(kis) != 0:
            selected_kis_id = [k.id for k in KnowledgeItem.query.filter(
                KnowledgeItem.value.in_(kis)).all()]
            query = query.filter(Questions.knowledge_item_id.in_(selected_kis_id))
        questions = query.all()

        response = {"data": [dumper.dump(
                    question) for question in questions]}

        return make_response(response, 200)


class QuestionKIFilter(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        """
            POST /api/v1/question/filter/ki
            payload:
                {
                    topics_selected: [topic_1, topic_2]
                }
        """
        data = request.get_json()
        topics_selected = data.get("topics_selected")

        if topics_selected is None:
            return make_response("Please select topics first.", 400)

        if len(topics_selected) == 0:
            return make_response("", 404)
        try:
            filtered_kis = KnowledgeItem.query.join(Topic)\
                .filter(Topic.value.in_(topics_selected)).all()
            for_response = [(ki.topic.value, ki.value) for ki in filtered_kis]

            return make_response(jsonify(for_response), 200)
        except Exception as e:
            logger.error(e)
            return make_response(jsonify({
                "message": "Error filtering Knowledge Items"
            }), 500)


class QuestionTopicFilter(MethodView):
    @jwt_required(fresh=True)
    def get(self, subject: str):
        try:
            subject_ = Subject.query.filter(Subject.name.op('~*')(subject)).first()
            if subject_ is None:
                return make_response(jsonify({}), 400)
            topics = Topic.query.filter(Topic.subject_id == subject_.id)\
                .filter(Topic.value.isnot(None))\
                .filter(Topic.value != '').distinct(Topic.value).all()

            response = [topic.value for topic in topics]
            return make_response(jsonify(response), 200)
        except Exception as e:
            logger.error(e)
            return make_response(jsonify({
                'message': 'Error filtering topics'
            }), 500)


question_blueprint.add_url_rule("/question/<question_id>",
                                view_func=Question.as_view('question_with_id'))
question_blueprint.add_url_rule("/question", view_func=QuestionList.as_view("question_list"))
question_blueprint.add_url_rule(
    "/question/search", view_func=QuestionSearch.as_view("question_search"))
question_blueprint.add_url_rule(
    "/question/filter/ki", view_func=QuestionKIFilter.as_view("question_filter_ki"))
question_blueprint.add_url_rule("/question/filter/topic/<string:subject>",
                                view_func=QuestionTopicFilter.as_view("question_filter_topic"))
question_blueprint.add_url_rule(
    "/question/fetch", view_func=QuestionFromKIsAndTopics.as_view('question_fetch'))
question_blueprint.add_url_rule(
    "/question/user_created", view_func=TeacherOwnedQuestions.as_view('teacher_owned_questions')
)
question_blueprint.add_url_rule(
    "/question/user_created/<int:question_id>",
    view_func=TeacherOwnedQuestion.as_view('teacher_owned_question')
)
