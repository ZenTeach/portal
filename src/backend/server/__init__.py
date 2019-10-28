import os
import logging

from flask import Flask, has_request_context, request
from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS


def configure_logging():
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.INFO)


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
    '[%(asctime)s] %(remote_addr)s requested %(url)s\n'
    '%(levelname)s in %(module)s: %(message)s'
)

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS(supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
ma = Marshmallow()


def create_app(script_info=None):
    app = Flask(__name__)

    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    ma.init_app(app)

    configure_logging()

    from . import models
    from flask_migrate import Migrate, MigrateCommand
    migration_directory = os.path.join('server', 'models', 'migrations')
    migrate = Migrate(app, db, directory=migration_directory)

    # Register bluprints
    from server.api.school_class_api import school_class_blueprint
    from server.api.class_quiz_api import class_quiz_blueprint
    from server.api.teacher_auth_api import teacher_auth_blueprint
    from server.api.student_auth_api import student_auth_blueprint
    from server.api.questions_api import question_blueprint
    from server.api.stats_api import statistics_view_blueprint
    from server.api import root_api

    app.register_blueprint(school_class_blueprint, url_prefix='/api/v1')
    app.register_blueprint(class_quiz_blueprint, url_prefix='/api/v1')
    app.register_blueprint(teacher_auth_blueprint, url_prefix='/api/v1')
    app.register_blueprint(student_auth_blueprint, url_prefix='/api/v1')
    app.register_blueprint(question_blueprint, url_prefix='/api/v1')
    app.register_blueprint(statistics_view_blueprint, url_prefix='/api/v1')
    app.register_blueprint(root_api)

    default_handler.setFormatter(formatter)

    # @app.errorhandler(500)
    # def internal_error(exception):
    #     app.logger.error(exception)

    @app.before_request
    def interceptor():
        print(request.cookies)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
