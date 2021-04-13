from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from server import db
from server.api import logger, report_5xx_error
from server.decorators import with_required_roles
from server.models import Questions, QuestionsSchema, QuestionTypeEnum
from sqlalchemy import exc
from webargs import fields
from webargs.flaskparser import use_kwargs

question_blueprint = Blueprint("question", __name__)
dumper = QuestionsSchema()

question_args = {
    'subject': fields.Str(required=True)
}


class QuestionList(MethodView):
    @jwt_required
    @use_kwargs(question_args, location='query')
    def get(self, **kwargs):
        subject = kwargs.get('subject')

        question_list = None
        if subject == "":
            question_list = []
        else:
            question_list = Questions.query.filter(
                Questions.subject.op('~*')(subject)).all()

        return make_response(
            {"questions": [dumper.dump(question)
                           for question in question_list]}, 200
        )

    @jwt_required
    def post(self):
        data = request.get_json()
        error_object = jsonify(
            {"status": "fail", "message": "Invalid payload."})

        if not data:
            return make_response(error_object, 400)

        question = data.get("question")
        question_type = QuestionTypeEnum(data.get("question_type"))
        subject = data.get("subject")
        topic = data.get("topic")
        knowledge_item = data.get("knowledge_item")
        correct_choice_id = data.get("correct_choice_id")
        tag = data.get("tag")
        choices = data.get("choices")
        try:
            question_entry = Questions.query.filter_by(
                subject=subject, tag=tag, question=question
            ).first()
            if not question_entry:
                Questions(
                    question=question,
                    question_type=question_type,
                    subject=subject,
                    topic=topic,
                    tag=tag,
                    knowledge_item=knowledge_item,
                    correct_choice_id=correct_choice_id,
                    choices=choices,
                ).save()

                response_object = jsonify(
                    {"status": "success", "message": "Question was added!"}
                )
                return make_response(response_object, 201)
            else:
                return make_response(jsonify({
                    "status": "fail",
                    "message": "Question already exists."
                }), 400)
        except Exception as e:
            db.session.rollback()
            logger.error(e)
            report_5xx_error(e)
            return make_response(error_object, 500)


class Question(MethodView):
    method_decorators = [jwt_required]

    def get(self, question_id):
        question = Questions.query.filter_by(id=question_id).first()
        return make_response({"question": dumper.dump(question)}, 200)

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
            db.session.commit()
            return make_response(
                jsonify({
                    "message": "Deleted question {}".format(question.id)
                }), 204)
        except exc.IntegrityError as e:
            logger.error(e)
            db.session.rollback()
            report_5xx_error(e)
            return make_response(
                jsonify({
                    "message": "Error while deleteing \
                        question id: {}".format(question_id)
                }),
                500)

    @with_required_roles(["Admin"])
    def put(self):
        pass


class TeacherOwnedQuestion(MethodView):
    method_decorators = [jwt_required]

    def get(self):
        teacher = get_jwt_identity()["identity"]
        questions = Questions.query.filter_by(teacher_id=teacher["id"]).all()

        return make_response(
            jsonify({
                "questions": [dumper.dump(question) for question in questions]
            }), 200)


class QuestionSearch(MethodView):
    @jwt_required
    def post(self):
        query_params = request.get_json()
        try:
            result_set = Questions.query.search(query_params["query"]).filter(
                Questions.subject.op('~*')(query_params["subject"])
            ).filter(
                Questions.topic.in_(query_params["topic"])
            ).filter(
                Questions.knowledge_item.in_(query_params["knowledge_item"])
            ).all()

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
            report_5xx_error(e)
            error_object = {"message": "Error processing request"}
            return make_response(jsonify(error_object), 500)


class QuestionFromKIsAndTopics(MethodView):
    @jwt_required
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
            query = query.filter(Questions.topic.in_(topics))
        if len(kis) != 0:
            query = query.filter(Questions.knowledge_item.in_(kis))

        questions = query.all()

        response = {"data": [dumper.dump(
                    question) for question in questions]}

        return make_response(response, 200)


class QuestionKIFilter(MethodView):
    @jwt_required
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
            kis = (
                Questions.query.with_entities(Questions.topic, Questions.knowledge_item)
                .filter(Questions.topic.in_(topics_selected))
                .filter(Questions.knowledge_item.isnot(None))
                .filter(Questions.knowledge_item != '').all()
            )

            return make_response(jsonify(kis), 200)
        except Exception as e:
            logger.error(e)
            report_5xx_error(e)
            return make_response(jsonify({
                "message": "Error filtering Knowledge Items"
            }), 500)


class QuestionTopicFilter(MethodView):
    @jwt_required
    def get(self, subject: str):
        try:
            topics = Questions.query.with_entities(Questions.topic)\
                .filter(Questions.subject.op('~*')(subject))\
                .filter(Questions.topic.isnot(None))\
                .filter(Questions.topic != '').distinct(Questions.topic).all()
            response = [x for (x,) in topics]
            return make_response(jsonify(response), 200)
        except Exception as e:
            logger.error(e)
            report_5xx_error(e)
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
    "/question/user_created", view_func=TeacherOwnedQuestion.as_view('teacher_owned_question')
)
