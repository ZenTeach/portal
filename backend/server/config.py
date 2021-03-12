import os
from datetime import timedelta
from pathlib import Path
from secrets import token_urlsafe


class BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = token_urlsafe()
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True
    JWT_ACCESS_COOKIE_PATH = "/api/v1/"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_COOKIE_PATH = "/api/v1/teacher/token/refresh"
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-ACCESS-TOKEN"
    JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-REFRESH-TOKEN"
    REDIS_URL = os.environ.get("REDIS_URL")
    FLASK_ADMIN_SWATCH = "journal"
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERYD_TASK_LOG_FORMAT = os.environ.get("CELERYD_TASK_LOG_FORMAT")
    CELERY_TRACK_STARTED = True
    CORS_RESOURCES = [r"/api/v1/*"]
    CORS_MAX_AGE = timedelta(hours=24)
    CORS_VARY_HEADER = True
    CORS_SUPPORTS_CREDENTIALS = True
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEFAULT_MAIL_SENDER = os.environ.get("DEFAULT_MAIL_SENDER")
    TMP_DIR = str(Path(os.environ.get('TMP_DIR')).resolve())
    CLIENT_URL = os.environ.get('CLIENT_URL')
    IMAGE_ALLOWED_EXTENSIONS = ['png', 'jpeg', 'jpg']
    UPLOAD_FOLDER = '/tmp'  # nosec


class DevelopmentConfig(BaseConfig):
    JWT_SECRET_KEY = token_urlsafe()
    JWT_CSRF_IN_COOKIES = False
    JWT_COOKIE_CSRF_PROTECT = False
    FLASK_DEBUG = 1
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = True
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ("access", "refresh")
    WTF_CSRF_TIME_LIMIT = 3600
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'server/static/uploaded')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
    JWT_SECRET_KEY = token_urlsafe()
    JWT_BLACKLIST_ENABLED = False
    MAIL_DEFAULT_SENDER = os.environ.get('no-reply@tester.com')


class ProductionConfig(BaseConfig):
    BROKER_TRANSPORT = os.environ.get('BROKER_TRANSPORT')
    BROKER_TRANSPORT_OPTIONS = {
        'region': os.environ.get('AWS_REGION'),
        'polling_interval': 20,
        'visibility_timeout': 10800,
        'task_default_queue': os.environ.get('CELERY_DEFAULT_QUEUE')
    }
    BROKER_USER = os.getenv('BROKER_USER')
    BROKER_PASSWORD = os.getenv('BROKER_PASSWORD')
    CELERY_DEFAULT_QUEUE = os.environ.get('CELERY_DEFAULT_QUEUE')
    CELERY_ENABLE_REMOTE_CONTROL = False
    CELERY_SEND_EVENTS = False
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ("access", "refresh")
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_DOMAIN = os.environ.get('JWT_COOKIE_DOMAIN', None)
    PROPAGATE_EXCEPTIONS = True
    SECRET_KEY = token_urlsafe()
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'server/static/uploaded')
    CORS_ORIGINS = ['portal.zenteach.co.uk', 'stage.portal.zenteach.co.uk']
