import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS(supports_credentials=True, resources={r"/api/*": {"origins": "*"}})


def create_app(script_info=None):
    app = Flask(__name__)

    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

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
    from server.api import root_api

    app.register_blueprint(school_class_blueprint, url_prefix='/api/v1')
    app.register_blueprint(class_quiz_blueprint, url_prefix='/api/v1')
    app.register_blueprint(teacher_auth_blueprint, url_prefix='/api/v1')
    app.register_blueprint(student_auth_blueprint, url_prefix='/api/v1')
    app.register_blueprint(question_blueprint, url_prefix='/api/v1')
    app.register_blueprint(root_api)

    @app.shell_context_processor
    def ctx():
        return {'app': app, 'db': db}

    return app
