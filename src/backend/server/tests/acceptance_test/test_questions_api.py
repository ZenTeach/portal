import json
from uuid import uuid4

from server.models import Questions
from server.tests.factories import QuestionsFactory


class TestQuestionsAPI:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_knowledge_item_filter(self, client, mocker):
        mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
        for _ in range(10):
            uuid = uuid4()
            v = QuestionsFactory.build(topic="testKI", uuid=uuid,
                                       multiple_choice_question_type=True)
            v.save()
        response = client.get("/api/v1/question/filter/ki/testKI")
        data = json.loads(response.data)
        kis = Questions.query.with_entities(Questions.knowledge_item)\
            .filter_by(topic="testKI")\
            .all()
        kis = [value for (value,) in kis]

        assert response.status_code == 200
        assert data == kis

    def test_topic_filter(self, client, mocker):
        mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
        for _ in range(10):
            uuid = uuid4()
            v = QuestionsFactory.build(subject="Chemistry", uuid=uuid,
                                       multiple_choice_question_type=True)
            v.save()
        response = client.get("/api/v1/question/filter/topic/Chemistry")
        data = json.loads(response.data)
        topics = Questions.query.with_entities(Questions.topic)\
            .filter_by(subject="Chemistry")\
            .all()
        topics = [value for (value,) in topics]

        assert response.status_code == 200
        assert data == topics
