from pytest import fail
from server.lib.grader import Grader
from server.tasks.grader_tasks import grader_administered_quizzes


class TestQuizGraderTask:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_grader_administered_quizzes_runs(self, monkeypatch):
        def mock_from_quiz_session(x):
            return True
        monkeypatch.setattr(Grader, 'from_quiz_session', mock_from_quiz_session)
        try:
            grader_administered_quizzes('some_foo_id')
        except Exception as exception:
            raise fail("DID RAISE {0}".format(exception))
