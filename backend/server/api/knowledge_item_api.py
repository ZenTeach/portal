from flask import Blueprint, abort, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import current_user, jwt_required
from server.api import logger
from server.models import KnowledgeItemSchema, Subject, Topic
from server.models.knowledge_item import KnowledgeItem

knowledge_item_blueprint = Blueprint("knowledge_items", __name__)


class KnowledgeItemsView(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        all_knowledge_items = KnowledgeItem.query.all()
        dumper = KnowledgeItemSchema(many=True)
        return make_response(jsonify({
            'data': dumper.dump(all_knowledge_items)
        }), 200)

    @jwt_required(fresh=True)
    def post(self):
        ki_data = request.get_json()
        if not ki_data:
            abort(400)
        subject_ = Subject.query.filter_by(name=ki_data.pop('subject')).first()
        topic = Topic.query.filter_by(value=ki_data.pop('topic')).first()

        if not subject_:
            abort(404)

        if not topic:
            abort(404)

        ki_data.update({
            'teacher_id': current_user.id,
            'subject_id': subject_.id,
            'topic_id': topic.id
        })

        dumper = KnowledgeItemSchema()
        ki = KnowledgeItem(**ki_data)
        try:
            ki.save()
        except Exception as e:
            logger.error(e)
            abort(500)

        return make_response(jsonify({
            'data': dumper.dump(topic)
        }), 201)


class KnowledgeItemView(MethodView):
    @jwt_required(fresh=True)
    def get(self, knowledge_item_id: int):
        dumper = KnowledgeItemSchema()
        knowledge_item = KnowledgeItem.query.filter_by(id=knowledge_item_id).first()
        if not knowledge_item:
            return make_response(jsonify({
                'data': [],
                'message': "Knowledge Item not found."
            }), 404)
        return make_response(jsonify({
            'data': dumper.dump(knowledge_item)
        }), 200)

    @jwt_required(fresh=True)
    def put(self, knowledge_item_id: int):
        knowledge_item: KnowledgeItem = KnowledgeItem.query.filter_by(id=knowledge_item_id).first()
        if not knowledge_item:
            return make_response(jsonify({
                'data': [],
                'message': "Knowledge Item not found."
            }), 404)
        ki_data = request.get_json()
        if not ki_data:
            abort(400)
        dumper = KnowledgeItemSchema()
        try:
            knowledge_item.update_and_save(**ki_data)
            knowledge_item.save()
        except Exception as e:
            logger.error(e)
            abort(500)
        return make_response(jsonify({
            'data': dumper.dump(knowledge_item)
        }), 200)


class KnowledgeItemSearch(MethodView):
    @jwt_required(fresh=True)
    def post(self):
        search = request.get_json().get('search')
        subject_name = request.get_json().get('subject')
        topic_value = request.get_json().get('topic')
        subject = Subject.query.filter_by(name=subject_name).first()
        topic = Topic.query.filter_by(value=topic_value).first()

        if not search:
            abort(400)

        if not topic:
            abort(400)

        dumper = KnowledgeItemSchema(many=True)
        knowledge_items = KnowledgeItem.query.search(search)

        if subject:
            knowledge_items = knowledge_items.filter_by(subject_id=subject.id)

        if topic:
            knowledge_items = knowledge_items.filter_by(topic_id=topic.id)

        knowledge_items = knowledge_items.all()

        return make_response(jsonify({
            'data': dumper.dump(knowledge_items)
        }), 200)


knowledge_item_blueprint.add_url_rule(
    '/knowledge_items', view_func=KnowledgeItemsView.as_view('knowledge_items'))
knowledge_item_blueprint.add_url_rule(
    '/knowledge_item/<int:knowledge_item_id>',
    view_func=KnowledgeItemView.as_view('knowledge_item'))
knowledge_item_blueprint.add_url_rule(
    '/knowledge_item/search',
    view_func=KnowledgeItemSearch.as_view('knowledge_item_search'))
