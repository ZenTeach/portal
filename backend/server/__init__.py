import logging
import os
from datetime import timedelta

from celery import Celery
from flask import (Flask, current_app, has_request_context, jsonify,
                   make_response, request)
from flask.logging import default_handler
from flask_admin import Admin
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.pool import Pool
from sqlalchemy_searchable import make_searchable
from werkzeug.local import LocalProxy


def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("werkzeug").setLevel(logging.INFO)


logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)


class RequestFormatter(logging.Formatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    "[%(asctime)s] %(remote_addr)s requested %(url)s\n"
    "%(levelname)s in %(module)s: %(message)s"
)

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS(supports_credentials=True,
            resources={
                r"/api/v1/*": {
                    "origins": os.environ.get('ALLOWED_CORS_ORIGIN', '*'),
                    "max_age": timedelta(hours=24)
                }
            })
ma = Marshmallow()
mail = Mail()
celery = Celery("zenteach_tasks")
redis_store = FlaskRedis()
app = None
globalConfig = LocalProxy(lambda: current_app.config)


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1;")
    except Exception as exc:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


def create_app():
    app = Flask(__name__, template_folder="templates")

    if os.environ.get("FLASK_ENV") == "production":
        if os.path.exists("/var/www/zenteach_be/application.cfg"):
            app.config.from_pyfile("/var/www/zenteach_be/application.cfg")
        else:
            app_settings = os.getenv("APP_SETTINGS")
            app.config.from_object(app_settings)
    else:
        app_settings = os.getenv("APP_SETTINGS")
        app.config.from_object(app_settings)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    redis_store.init_app(app)
    make_searchable(db.metadata, options={
        'regconfig': 'pg_catalog.simple'
    })

    login_manager.init_app(app)

    from server.models import Admin as AdminModel

    @login_manager.user_loader
    def load_user(admin_id):
        return db.session.query(AdminModel).get(admin_id)

    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    configure_logging()
    from . import models
    from flask_migrate import Migrate

    migration_directory = os.path.join("server", "models", "migrations")
    Migrate(app, db, directory=migration_directory)

    from server.admin import (
        QuestionView,
        SchoolClassView,
        StudentView,
        TeacherView,
        ClassQuizView,
        UserInvitationView,
        SubjectsView,
        ZenteachAdminIndexView,
    )

    admin = Admin(
        app,
        name="Zenteach Admin Portal",
        template_mode="bootstrap3",
        base_template="admin_layout.html",
        index_view=ZenteachAdminIndexView(),
    )
    admin.add_view(ClassQuizView(models.ClassQuiz,
                                 db.session, endpoint="admin.quiz"))
    admin.add_view(TeacherView(
        models.Teacher, db.session, endpoint="admin.teacher"))
    admin.add_view(StudentView(
        models.Student, db.session, endpoint="admin.student"))
    admin.add_view(
        SchoolClassView(models.SchoolClass, db.session, endpoint="admin.class")
    )
    admin.add_view(
        QuestionView(models.Questions, db.session, endpoint="admin.question")
    )
    admin.add_view(
        UserInvitationView(models.Invitations, db.session, endpoint="admin.user_invite")
    )
    admin.add_view(
        SubjectsView(models.Subject, db.session, endpoint="admin.subjects")
    )

    # import background tasks after initializing celery
    # import server.tasks
    @jwt.token_in_blacklist_loader
    def check_if_token_is_revoked(decrypted_token):
        jti = decrypted_token["jti"]
        entry = redis_store.get(jti)
        if entry is None:
            return True
        return entry == "true"

    @jwt.invalid_token_loader
    def respond_to_invalid_token(description):
        return make_response(
            jsonify({"status": "error", "message": "Session expired"}), 401
        )

    # Register bluprints
    from server.api.school_class_api import school_class_blueprint
    from server.api.class_quiz_api import class_quiz_blueprint
    from server.api.teacher_auth_api import teacher_auth_blueprint
    from server.api.student_auth_api import student_auth_blueprint
    from server.api.questions_api import question_blueprint
    from server.api.stats_api import statistics_view_blueprint
    from server.api.quiz_submit_api import quiz_submit_blueprint
    from server.api import root_api

    app.register_blueprint(school_class_blueprint, url_prefix="/api/v1")
    app.register_blueprint(class_quiz_blueprint, url_prefix="/api/v1")
    app.register_blueprint(teacher_auth_blueprint, url_prefix="/api/v1")
    app.register_blueprint(student_auth_blueprint, url_prefix="/api/v1")
    app.register_blueprint(question_blueprint, url_prefix="/api/v1")
    app.register_blueprint(statistics_view_blueprint, url_prefix="/api/v1")
    app.register_blueprint(quiz_submit_blueprint, url_prefix="/api/v1")
    if os.environ.get('FLASK_ENV') == 'development':
        app.register_blueprint(root_api)

    default_handler.setFormatter(formatter)

    if os.environ.get('FLASK_ENV') == 'production':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db, "globalConfig": globalConfig}

    return app
