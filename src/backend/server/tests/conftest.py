from server import create_app, db
import pytest
from pytest_factoryboy import register
from server.tests.factories import StudentFactory, TeacherFactory, SchoolClassFactory, ClassQuizFactory, ClassQuizScoreFactory

register(StudentFactory, "student")
register(TeacherFactory, "teacher")
register(SchoolClassFactory, "school_class",
         _postgen_dependencies=["teacher__id"])
register(ClassQuizFactory, "class_quiz",
         _postgen_dependencies=["school_class__id"])
# register(ClassQuizScoreFactory)


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object('server.config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()  # looks like db.session.close() would work as well
        db.drop_all()
