import os
from datetime import timedelta
from functools import lru_cache
from io import BytesIO
from os import getcwd
from pathlib import Path
from secrets import token_urlsafe
from typing import NamedTuple, Optional, Union, get_type_hints

from dotenv import load_dotenv
from yaml import load
from yamlloader.ordereddict import CLoader

__all__ = ["BaseConfig", "DevelopmentConfig", "TestingConfig",
           "ProductionConfig", "_load_examboard", "_load_exempt_list"]

if os.getenv('RUNTIME') == 'development':
    load_dotenv()


@lru_cache(256)
def _load_examboard():
    data = None
    with open(f"{os.path.join(getcwd(), 'server/config', 'exam_board.yml')}") as fp:
        data = load(fp, Loader=CLoader)  # nosec

    return data


@lru_cache(256)
def _load_exempt_list():
    data = None
    with open(f"{os.path.join(getcwd(), 'server/config', 'exempt_list.yml')}") as fp:
        data = load(fp, Loader=CLoader)  # nosec

    return data


def _parse_bool(val: Union[str, bool]) -> bool:  # pylint: disable=E1136
    return val if type(val) == bool else val.lower() in ['true', 'yes', '1']


class Credentials:

    def __init__(self,
                 credential_file: Path,
                 encryption_key: str):
        self._credential_file = credential_file
        self.encryption_key = encryption_key

    @property
    def decrypted_text(self):
        pass

    @property
    def encrypted_text(self):
        pass

    def encrypt(self):
        pass

    def decrypt(self):
        pass

    def _encrypt_text(self):
        pass

    def _decrypt_text(self):
        pass


class ConfigFile:

    def __init__(self, text: BytesIO, encryption_file: Optional[Union[Path, str]] = None):
        self._text = text
        self._encryption_file = encryption_file

    @property
    def _editor():
        return os.getenv('EDITOR')

    """
        credentials:create
    """
    def create():
        pass

    def edit():
        pass


class AppConfig:
    DEBUG: bool = False
    ENV: str = 'development'
    API_KEY: str
    HOSTNAME: str
    PORT: int

    """
    Map environment variables to class fields according to these rules:
      - Field won't be parsed unless it has a type annotation
      - Field will be skipped if not in all caps
      - Class field and environment variable name are the same
    """

    def __init__(self, env):
        for field in self.__annotations__:
            if not field.isupper():
                continue

            # Raise AppConfigError if required field not supplied
            default_value = getattr(self, field, None)
            if default_value is None and env.get(field) is None:
                raise Exception('The {} field is required'.format(field))

            # Cast env var value to expected type and raise AppConfigError on failure
            try:
                var_type = get_type_hints(AppConfig)[field]
                if var_type == bool:
                    value = _parse_bool(env.get(field, default_value))
                else:
                    value = var_type(env.get(field, default_value))

                self.__setattr__(field, value)
            except ValueError:
                raise Exception('Unable to cast value of "{}" to type "{}" for "{}" field'.format(
                    env[field],
                    var_type,
                    field
                )
                )

    def __repr__(self):
        return str(self.__dict__)

    def _resolve_config_name(self) -> Path:
        return Path.resolve(os.path.join(os.getcwd(), f"config/{self.ENV}.yml.enc"))


class CeleryConfig(NamedTuple):

    """
        Celery configuration options for the application.
    """
    result_backend: str = os.environ.get("RESULT_BACKEND")
    worker_task_log_format: str = os.environ.get("CELERYD_TASK_LOG_FORMAT",
                                                 "[%(asctime)s: %(levelname)s/%(processName)s] - [%(task_name)s(%(task_id)s)] %(message)s")  # noqa
    broker_url: str = os.environ.get("BROKER_URL")
    broker_transport: str = os.environ.get('BROKER_TRANSPORT')

    broker_transport_options: dict = {
        'region': os.environ.get('AWS_REGION'),
        'polling_interval': 20,
        'visibility_timeout': 10800,
        'task_default_queue': os.environ.get('DEFAULT_QUEUE')
    }
    task_default_queue: str = os.environ.get('DEFAULT_QUEUE')
    worker_enable_remote_control: bool = False
    worker_send_task_events: bool = False
    task_track_started: bool = True

    # Configuration builder for celery-redbeat scheduler
    redbeat_key_prefix: str = os.environ.get('REDBEAT_KEY_PREFIX', None)
    redbeat_lock_timeout: int = os.environ.get('REDBEAT_LOCK_TIMEOUT', 300)
    redbeat_redis_url: str = os.environ.get('REDBEAT_REDIS_URL', 'redis://localhost:6379/1')
    redbeat_redis_use_ssl: bool = os.environ.get('REDBEAT_REDIS_USE_SSL', False)

    # TODO: Add task routing

    def __repr__(self) -> str:
        return str(self._asdict())


celery_configuration = CeleryConfig()._asdict()


class BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = token_urlsafe()
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ALGORITHM = "HS512"
    JWT_CSRF_IN_COOKIES = True
    JWT_IDENTITY_CLAIM = "sub"
    JWT_COOKIE_SAMESITE = "None"
    JWT_ACCESS_COOKIE_PATH = "/api/v1/"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_COOKIE_PATH = "/api/v1/teacher/token/refresh"
    JWT_ACCESS_CSRF_HEADER_NAME = "X-CSRF-ACCESS-TOKEN"
    JWT_REFRESH_CSRF_HEADER_NAME = "X-CSRF-REFRESH-TOKEN"
    REDIS_URL = os.environ.get("REDIS_URL")
    FLASK_ADMIN_SWATCH = "journal"

    CORS_VARY_HEADER = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    DEFAULT_MAIL_SENDER = os.environ.get("DEFAULT_MAIL_SENDER")
    ALLOWED_CORS_ORIGIN = os.environ.get('ALLOWED_CORS_ORIGIN')
    TMP_DIR = str(Path(os.environ.get('TMP_DIR', "")).resolve())
    LOG_ACTIVITY = False
    CLIENT_URL = os.environ.get('CLIENT_URL')
    IMAGE_ALLOWED_EXTENSIONS = ['png', 'jpeg', 'jpg']
    UPLOAD_FOLDER = '/tmp'  # nosec


class DevelopmentConfig(BaseConfig):
    JWT_SECRET_KEY = token_urlsafe(4)
    JWT_CSRF_IN_COOKIES = False
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = "Lax"
    LOG_ACTIVITY = True
    FLASK_DEBUG = 1
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_USE_TLS = True
    WTF_CSRF_TIME_LIMIT = 3600
    AUTH0_DOMAIN = "https://dev-iogpmb3i.eu.auth0.com/api/v2/"
    AUTH0_API_IDENTIFIER = "5d52c515b1fd1306b64a47a6"
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'server/static/uploaded')


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_SECRET_KEY = token_urlsafe()
    MAIL_DEFAULT_SENDER = os.environ.get('no-reply@tester.com')


class ProductionConfig(BaseConfig):
    prometheus_multiproc_dir = os.environ.get('PROMETHEUS_MULTIPROC_DIR', '/tmp')  # nosec
    JWT_IDENTITY_CLAIM = "sub"
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_DOMAIN = os.environ.get('JWT_COOKIE_DOMAIN', None)
    PROPAGATE_EXCEPTIONS = True
    SECRET_KEY = token_urlsafe()
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'server/static/uploaded')
    JWT_BLACKLIST_TOKEN_CHECKS = ('access', 'refresh')
