import logging
import os
import pathlib
from datetime import date, datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

from celery import Celery
from dotenv import load_dotenv
from flask import (Flask, has_request_context, jsonify, make_response,
                   request)
from flask.json import JSONEncoder
from flask.logging import default_handler
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, create_access_token, get_jwt,
                                get_jwt_identity, set_access_cookies)
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_redis import FlaskRedis
from healthcheck import HealthCheck
from sqlalchemy_searchable import make_searchable

from server.db import db
from server.security import bcrypt


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
health = HealthCheck()
celery = Celery("zenteach_tasks")
redis_store = FlaskRedis()
app = None


class AppJSONEncoder(JSONEncoder):
    """Custom JSON encoding function.

    This class will check if the object being serialized has a function called `to_json()`, and call it if available,  # noqa
    as well as adding a type-hint value to the output dict (`__type` key/value pair)  # noqa
    """
    @staticmethod
    def default(obj):
        """Default object encoder function

        Args:
            obj (:obj:`Any`): Object to be serialized

        Returns:
            JSON string
        """
        if isinstance(obj, datetime):
            return obj.isoformat()

        if issubclass(obj.__class__, Enum.__class__):
            return obj.value

        if isinstance(obj, UUID):
            return str(obj)

        if isinstance(obj, date):
            return obj.isoformat()

        if isinstance(obj, dict):
            return dict(obj)

        to_dict = getattr(obj, 'to_dict', None)
        if to_dict:
            out = obj.to_dict()
            return out

        return JSONEncoder.default(obj)


""" Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.
"""


def monkey_patch_json_encoder():
    from json import JSONEncoder

    def _default(self, obj):
        return AppJSONEncoder.default(obj)

    _default.default = JSONEncoder.default
    JSONEncoder.default = _default


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.json_provider_class = AppJSONEncoder
    if os.environ.get("RUNTIME") == "production":
        if os.path.exists("/var/www/zenteach_be/application.cfg"):
            app.config.from_pyfile("/var/www/zenteach_be/application.cfg")
        else:
            if pathlib.Path('../.env').resolve().exists():
                load_dotenv()
            app_settings = os.getenv("APP_SETTINGS")
            app.config.from_object(app_settings)
        from prometheus_flask_exporter.multiprocess import \
            GunicornInternalPrometheusMetrics
        metrics = GunicornInternalPrometheusMetrics.for_app_factory(path='/app_metrics')
        metrics.init_app(app)
    else:
        app_settings = os.getenv("APP_SETTINGS", "server.config.DevelopmentConfig")
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

    from server.config import celery_configuration
    celery.conf.update(celery_configuration)

    # Add database uri for db scheduler
    app.config.update(database_url=app.config.get('SQLALCHEMY_DATABASE_URI', ''))

    configure_logging()
    from flask_migrate import Migrate

    from . import models

    migration_directory = os.path.join("server", "models", "migrations")
    Migrate(app, db, directory=migration_directory)

    # import background tasks after initializing celery
    # import server.tasks

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(header, decrypted_token):
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

    # Registry healthcheck
    # TODO: Setup celery health check endpoint here
    app.add_url_rule("/healthcheck", "healthcheck", view_func=lambda: health.run())

    default_handler.setFormatter(formatter)

    if os.environ.get('RUNTIME') == 'development':
        # APISpec : auto api documenting
        from apispec import APISpec
        from apispec.ext.marshmallow import MarshmallowPlugin
        from flask_apispec.extension import FlaskApiSpec

        docs = FlaskApiSpec()
        app.config.update({
            'APISPEC_SPEC': APISpec(
                title='ZenTeach',
                version='v1',
                openapi_version='2.0',
                plugins=[MarshmallowPlugin()],
            ),
            'APISPEC_SWAGGER_URL': '/swagger/',
            'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'
        })
        docs.init_app(app)
        auto_document_apis(docs, app)

    if os.environ.get('RUNTIME') == 'production':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    monkey_patch_json_encoder()

    # TODO: move this to federated auth endpoint
    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
            return response
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response

    @app.errorhandler(422)
    def handle_validation_error(err):
        # The marshmallow.ValidationError is available on err.exc
        return jsonify({"message": err.exc.messages}), 422

    @app.shell_context_processor
    def ctx():
        import server.models as sm

        def ap(mappable):
            import pprint
            pprint(mappable.dict())
        return {
            "app": app,
            "db": db,
            "sm": sm,
            "ap": ap,
            "celery": celery
        }

    return app


def auto_document_apis(document_, app: Flask):
    for name, rule in app.view_functions.items():
        blueprint, endpoint = '', ''
        try:
            blueprint, endpoint = name.split('.')
        except:  # noqa
            blueprint = name

        if (blueprint.startswith('admin') or
           blueprint.startswith('flask') or
            blueprint.startswith('prometheus') or
                blueprint == 'static' or blueprint == 'healthcheck'):

            next
        else:
            document_.register(rule, endpoint=endpoint, blueprint=blueprint)
