from flask import Blueprint, abort, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from server.api import logger
from server.models import Topic, TopicSchema

topic_blueprint = Blueprint("topics", __name__)


class TopicsView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        dumper = TopicSchema(many=True)
        all_topics = Topic.query.all()
        return make_response(jsonify({
            'data': dumper.dump(all_topics)
        }), 200)

    @jwt_required(fresh=True)
    def post(self):
        topic_data = request.get_json()
        if not topic_data:
            abort(400)
        dumper = TopicSchema()
        topic = Topic(**topic_data)
        try:
            topic.save()
        except Exception as e:
            logger.error(e)
            abort(500)

        return make_response(jsonify({
            'data': dumper.dump(topic)
        }), 201)


class TopicView(MethodView):
    @jwt_required(fresh=True)
    def get(self, topic_id: int):
        dumper = TopicSchema()
        topic = Topic.query.filter_by(id=topic_id).first()
        if not topic:
            return make_response(jsonify({
                'data': [],
                'message': "Topic not found."
            }), 404)
        return make_response(jsonify({
            'data': dumper.dump(topic)
        }), 200)

    @jwt_required(fresh=True)
    def put(self, topic_id):
        topic: Topic = Topic.query.filter_by(id=topic_id).first()
        if not topic:
            return make_response(jsonify({
                'data': [],
                'message': "Topic not found."
            }), 404)
        topic_data = request.get_json()
        if not topic_data:
            abort(400)
        dumper = TopicSchema()
        try:
            topic.update_from_dict(topic_data)
            topic.save()
        except Exception as e:
            logger.error(e)
            abort(500)
        return make_response(jsonify({
            'data': dumper.dump(topic)
        }), 200)


class TopicsSearch(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        search = request.get_json().get('search')
        if not search:
            abort(400)
        dumper = TopicSchema(many=True)
        topics = Topic.query.search(search).all()
        return make_response(jsonify({
            'data': dumper.dump(topics)
        }), 200)


topic_blueprint.add_url_rule('/topics', view_func=TopicsView.as_view('topics'))
topic_blueprint.add_url_rule('/topic/<int:topic_id>', view_func=TopicView.as_view('topic'))
topic_blueprint.add_url_rule('topics/search', view_func=TopicsSearch.as_view('topic_search'))
