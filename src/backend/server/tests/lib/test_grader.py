import pytest
from server.lib.grader import Grader
from server.models import ClassQuizStatus

# @pytest.mark.parametrize("school_class__id", [1000])
def test_grader(school_class, class_quiz):
    grader_test_object = Grader(school_class.id)
    assert True
    assert class_quiz.status == ClassQuizStatus.administered
