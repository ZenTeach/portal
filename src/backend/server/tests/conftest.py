from server import create_app, db
import pytest
import pytest_mock
import mock
from pytest_factoryboy import register, LazyFixture
from server.tests.factories import StudentFactory, TeacherFactory, SchoolClassFactory, ClassQuizFactory, ClassQuizScoreFactory

register(StudentFactory, "student")
register(TeacherFactory, "teacher")
register(SchoolClassFactory, "school_class")
         #_postgen_dependencies=["teacher__id"])
register(ClassQuizFactory, "class_quiz")
         #_postgen_dependencies=["school_class__id"])
# register(ClassQuizScoreFactory)


@pytest.fixture(scope="function")
def client():
    app = create_app()
    app.config.from_object('server.config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()  # looks like db.session.close() would work as well
        db.drop_all()

@pytest.fixture(autouse=True)
def after_each_cleanup(mocker):
    # import pdb; pdb.set_trace()
    mocker.resetall()
