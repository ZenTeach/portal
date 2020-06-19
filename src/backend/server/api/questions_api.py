
from flask import Blueprint, abort, jsonify, make_response, request
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource, reqparse
from server import db
from server.api import api_logger
from server.decorators import with_required_roles
from server.models import Questions, QuestionsSchema, QuestionTypeEnum
from sqlalchemy import exc

question_blueprint = Blueprint("question", __name__)
api = Api(question_blueprint)
dumper = QuestionsSchema()

parser = reqparse.RequestParser()
parser.add_argument("subject", required=True,
                    help="Question subject not recognized")


class QuestionList(Resource):
    method_decorators = [jwt_required]

    @with_required_roles(["Teacher", "Admin"])
    def get(self):
        args = parser.parse_args()
        question_list = Questions.query.filter_by(
            subject=args["subject"]).all()
        return make_response(
            {"questions": [dumper.dump(question)
                           for question in question_list]}, 200
        )

    @with_required_roles(["Teacher", "Admin"])
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
        tag = data.get("tag")
        choices = data.get("choices")
        try:
            question_entry = Questions.query.filter_by(
                subject=subject, tag=tag, question=question
            ).first()
            if not question_entry:
                db.session.add(
                    Questions(
                        question=question,
                        question_type=question_type,
                        subject=subject,
                        topic=topic,
                        tag=tag,
                        choices=choices,
                    )
                )
                db.session.commit()
                response_object = jsonify(
                    {"status": "success", "message": "Question was added!"}
                )
                return make_response(response_object, 201)
            else:
                error_object["message"] = "Question already exists."
                return make_response(error_object, 400)
        except exc.IntegrityError:
            db.session.rollback()
            return make_response(error_object, 500)


class Question(Resource):
    method_decorators = [jwt_required]

    @with_required_roles(["Teacher", "Admin"])
    def get(self, question_id):
        question = Questions.query.filter_by(id=question_id).first()
        return make_response({"question": dumper.dump(question)}, 200)

    @with_required_roles(["Admin"])
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
                }), 200)
        except exc.IntegrityError:
            db.session.rollback()
            return make_response(
                jsonify({
                    "message": "Error while deleteing \
                        question id: {}".format(question_id)
                }),
                500)

    @with_required_roles(["Admin"])
    def put(self):
        pass


class QuestionPing(Resource):
    def get(self):
        return make_response(
            {"status": "success", "message": "Pinged Questions API"}, 200
        )


class QuestionSearch(Resource):
    @jwt_required
    def post(self):
        query_params = request.get_json()
        api_logger.debug(f"query_params: {query_params}")
        try:
            result_set = (
                Questions.query.search(query_params["query"])
                .filter_by(
                    subject=query_params["subject"],
                    topic=query_params["topic"])
                .filter(Questions
                        .knowledge_item
                        .in_(query_params["knowledge_item"]))
                .all()
            )

            api_logger.debug(f"Result set length: {len(result_set)}")
            if len(result_set) != 0:
                response = {"data": [dumper.dump(
                    result) for result in result_set]}
                return make_response(jsonify(response), 200)
            else:
                response = {"message": "No result found"}
                return make_response(jsonify(response), 200)
        except Exception as e:
            api_logger.debug(e)
            error_object = {"message": "Error processing request"}
            return make_response(jsonify(error_object), 500)


class QuestionKIFilter(Resource):
    @jwt_required
    def get(self, topic):
        if len(topic) == 0:
            abort(404, "Topic is not given.")
        kis = (
            Questions.query.with_entities(Questions.knowledge_item)
            .filter_by(topic=topic)
            .all()
        )
        response = [x[0] for x in kis]
        return make_response(jsonify(response), 200)


api.add_resource(QuestionPing, "/question/ping")
api.add_resource(Question, "/question/<question_id>")
api.add_resource(QuestionList, "/question")
api.add_resource(QuestionSearch, "/question/search")
api.add_resource(QuestionKIFilter, "/question/filter/ki/<string:topic>")
