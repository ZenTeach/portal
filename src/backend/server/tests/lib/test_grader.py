import pytest
from server.lib import Grader
from server.models import QuizSession
from server.tests.factories import ClassQuizFactory


@pytest.fixture(scope='function')
def quiz_session(client, school_class, student):
    quiz = ClassQuizFactory.build(class_id=school_class.id)
    quiz.save()
    session = QuizSession(student=student,
                          class_quiz=quiz,
                          student_id=student.id,
                          class_quiz_id=quiz.id)
    session.save()
    return session


def quiz_submission():
    pass


class TestQuizGrader(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_from_quiz_session(self, client, quiz_session, school_class, mocker):
        def _mock_grader_init(school_class_id, class_quiz, batch):
            assert school_class_id is not None
            assert class_quiz is not None

        mocker.patch('server.lib.grader.Grader.__init__', _mock_grader_init)
        mocker.patch('server.lib.grader.Grader.start_grading')
        mocker.patch('server.lib.grader.Feedback')

        Grader.from_quiz_session(quiz_session.uuid)

    def test_quiz_grading(self, client, quiz_session, school_class, mocker):
        pass
