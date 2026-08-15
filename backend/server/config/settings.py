"""FastAPI settings (pydantic-settings) for the Zenteach portal backend.

Reads the same environment variables the legacy Flask config classes use so
switching the entry point does not change deployment configuration. The
legacy ``server.config`` package remains in place for the Flask compat path
(models, tests, manage.py); this module is the canonical source of truth for
the FastAPI application.
"""

import os
from datetime import timedelta
from functools import cached_property, lru_cache
from secrets import token_urlsafe
from typing import Optional, Tuple

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- runtime ---------------------------------------------------------
    runtime: str = Field("development", validation_alias="RUNTIME")
    app_settings: str = Field(
        "server.config.DevelopmentConfig", validation_alias="APP_SETTINGS"
    )
    debug: bool = False
    server_name: Optional[str] = Field(None, validation_alias="SERVER_NAME")

    # --- database --------------------------------------------------------
    database_url: Optional[str] = Field(None, validation_alias="DATABASE_URL")
    database_test_url: Optional[str] = Field(None, validation_alias="DATABASE_TEST_URL")
    sqlalchemy_track_modifications: bool = False

    # --- redis -----------------------------------------------------------
    redis_url: str = Field("redis://localhost:6379/app", validation_alias="REDIS_URL")

    # --- jwt -----------------------------------------------------------
    jwt_secret_key: str = Field("", validation_alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS512", validation_alias="JWT_ALGORITHM")
    jwt_identity_claim: str = Field("sub", validation_alias="JWT_IDENTITY_CLAIM")
    jwt_access_token_expires: timedelta = timedelta(days=1)
    jwt_refresh_token_expires: timedelta = timedelta(days=30)
    jwt_cookie_secure: bool = Field(False, validation_alias="JWT_COOKIE_SECURE")
    jwt_cookie_csrf_protect: bool = Field(True, validation_alias="JWT_COOKIE_CSRF_PROTECT")
    jwt_csrf_in_cookies: bool = Field(True, validation_alias="JWT_CSRF_IN_COOKIES")
    jwt_cookie_samesite: str = Field("None", validation_alias="JWT_COOKIE_SAMESITE")
    jwt_cookie_domain: Optional[str] = Field(None, validation_alias="JWT_COOKIE_DOMAIN")
    jwt_access_cookie_path: str = Field("/api/v1/", validation_alias="JWT_ACCESS_COOKIE_PATH")
    jwt_refresh_cookie_path: str = Field(
        "/api/v1/", validation_alias="JWT_REFRESH_COOKIE_PATH"
    )
    jwt_access_csrf_header_name: str = Field(
        "X-CSRF-ACCESS-TOKEN", validation_alias="JWT_ACCESS_CSRF_HEADER_NAME"
    )
    jwt_refresh_csrf_header_name: str = Field(
        "X-CSRF-REFRESH-TOKEN", validation_alias="JWT_REFRESH_CSRF_HEADER_NAME"
    )
    jwt_blacklist_token_checks: Tuple[str, ...] = ("access", "refresh")

    # --- cors / client ---------------------------------------------------
    allowed_cors_origin: str = Field("*", validation_alias="ALLOWED_CORS_ORIGIN")
    client_url: Optional[str] = Field(None, validation_alias="CLIENT_URL")

    # --- misc ------------------------------------------------------------
    tmp_dir: str = Field("", validation_alias="TMP_DIR")
    log_activity: bool = Field(False, validation_alias="LOG_ACTIVITY")
    upload_folder: str = Field("/tmp", validation_alias="UPLOAD_FOLDER")
    image_allowed_extensions: Tuple[str, ...] = ("png", "jpeg", "jpg")
    default_mail_sender: Optional[str] = Field(
        None, validation_alias="DEFAULT_MAIL_SENDER"
    )
    secret_key: str = Field("", validation_alias="SECRET_KEY")
    prometheus_multiproc_dir: str = Field(
        "/tmp", validation_alias="PROMETHEUS_MULTIPROC_DIR"  # nosec
    )

    # --- mail ------------------------------------------------------------
    mail_server: Optional[str] = Field(None, validation_alias="MAIL_SERVER")
    mail_port: Optional[str] = Field(None, validation_alias="MAIL_PORT")
    mail_username: Optional[str] = Field(None, validation_alias="MAIL_USERNAME")
    mail_password: Optional[str] = Field(None, validation_alias="MAIL_PASSWORD")
    mail_use_tls: bool = True
    mail_default_sender: Optional[str] = Field(
        None, validation_alias="MAIL_DEFAULT_SENDER"
    )

    # --- celery ----------------------------------------------------------
    broker_url: Optional[str] = Field(None, validation_alias="BROKER_URL")
    result_backend: Optional[str] = Field(None, validation_alias="RESULT_BACKEND")
    broker_transport: Optional[str] = Field(None, validation_alias="BROKER_TRANSPORT")
    aws_region: Optional[str] = Field(None, validation_alias="AWS_REGION")
    default_queue: Optional[str] = Field(None, validation_alias="DEFAULT_QUEUE")
    worker_task_log_format: str = Field(
        "[%(asctime)s: %(levelname)s/%(processName)s] - [%(task_name)s(%(task_id)s)] %(message)s",  # noqa: E501
        validation_alias="CELERYD_TASK_LOG_FORMAT",
    )
    redbeat_key_prefix: Optional[str] = Field(None, validation_alias="REDBEAT_KEY_PREFIX")
    redbeat_lock_timeout: int = Field(300, validation_alias="REDBEAT_LOCK_TIMEOUT")
    redbeat_redis_url: str = Field(
        "redis://localhost:6379/1", validation_alias="REDBEAT_REDIS_URL"
    )
    redbeat_redis_use_ssl: bool = Field(False, validation_alias="REDBEAT_REDIS_USE_SSL")

    # --- sentry ----------------------------------------------------------
    sentry_dsn: Optional[str] = Field(None, validation_alias="SENTRY_DSN")

    @cached_property
    def effective_jwt_secret_key(self) -> str:
        # The random fallback must be generated once per process, otherwise
        # tokens signed on one request fail to verify on the next.
        return self.jwt_secret_key or self.secret_key or token_urlsafe(64)

    def celery_config(self) -> dict:
        """Celery configuration dict (drop-in for the legacy NamedTuple)."""
        return {
            "result_backend": self.result_backend,
            "worker_task_log_format": self.worker_task_log_format,
            "broker_url": self.broker_url,
            "broker_transport": self.broker_transport,
            "broker_transport_options": {
                "region": self.aws_region,
                "polling_interval": 20,
                "visibility_timeout": 10800,
                "task_default_queue": self.default_queue,
            },
            "task_default_queue": self.default_queue,
            "worker_enable_remote_control": False,
            "worker_send_task_events": False,
            "task_track_started": True,
            "redbeat_key_prefix": self.redbeat_key_prefix,
            "redbeat_lock_timeout": self.redbeat_lock_timeout,
            "redbeat_redis_url": self.redbeat_redis_url,
            "redbeat_redis_use_ssl": self.redbeat_redis_use_ssl,
        }

    def flask_config(self) -> dict:
        """Materialize this settings object as a Flask-style config dict.

        Used to populate the fake Flask compat app so legacy components that
        read ``current_app.config`` keep working unchanged.
        """
        return {
            "RUNTIME": self.runtime,
            "APP_SETTINGS": self.app_settings,
            "DEBUG": self.debug,
            "SERVER_NAME": self.server_name,
            "TESTING": self.runtime == "testing",
            "SQLALCHEMY_TRACK_MODIFICATIONS": self.sqlalchemy_track_modifications,
            "SQLALCHEMY_DATABASE_URI": self.database_url,
            "REDIS_URL": self.redis_url,
            "JWT_SECRET_KEY": self.effective_jwt_secret_key,
            "JWT_ALGORITHM": self.jwt_algorithm,
            "JWT_IDENTITY_CLAIM": self.jwt_identity_claim,
            "JWT_ACCESS_TOKEN_EXPIRES": self.jwt_access_token_expires,
            "JWT_REFRESH_TOKEN_EXPIRES": self.jwt_refresh_token_expires,
            "JWT_COOKIE_SECURE": self.jwt_cookie_secure,
            "JWT_COOKIE_CSRF_PROTECT": self.jwt_cookie_csrf_protect,
            "JWT_CSRF_IN_COOKIES": self.jwt_csrf_in_cookies,
            "JWT_COOKIE_SAMESITE": self.jwt_cookie_samesite,
            "JWT_COOKIE_DOMAIN": self.jwt_cookie_domain,
            "JWT_ACCESS_COOKIE_PATH": self.jwt_access_cookie_path,
            "JWT_REFRESH_COOKIE_PATH": self.jwt_refresh_cookie_path,
            "JWT_ACCESS_CSRF_HEADER_NAME": self.jwt_access_csrf_header_name,
            "JWT_REFRESH_CSRF_HEADER_NAME": self.jwt_refresh_csrf_header_name,
            "JWT_BLACKLIST_TOKEN_CHECKS": list(self.jwt_blacklist_token_checks),
            "ALLOWED_CORS_ORIGIN": self.allowed_cors_origin,
            "CLIENT_URL": self.client_url,
            "TMP_DIR": str(os.path.join(os.getcwd(), self.tmp_dir))
            if self.tmp_dir
            else "",
            "LOG_ACTIVITY": self.log_activity,
            "UPLOAD_FOLDER": self.upload_folder,
            "IMAGE_ALLOWED_EXTENSIONS": list(self.image_allowed_extensions),
            "DEFAULT_MAIL_SENDER": self.default_mail_sender,
            "SECRET_KEY": self.secret_key or self.effective_jwt_secret_key,
            "PROMETHEUS_MULTIPROC_DIR": self.prometheus_multiproc_dir,
            "MAIL_SERVER": self.mail_server,
            "MAIL_PORT": self.mail_port,
            "MAIL_USERNAME": self.mail_username,
            "MAIL_PASSWORD": self.mail_password,
            "MAIL_USE_TLS": self.mail_use_tls,
            "MAIL_DEFAULT_SENDER": self.mail_default_sender,
            "BROKER_URL": self.broker_url,
            "RESULT_BACKEND": self.result_backend,
            "BROKER_TRANSPORT": self.broker_transport,
            "AWS_REGION": self.aws_region,
            "DEFAULT_QUEUE": self.default_queue,
            "CELERYD_TASK_LOG_FORMAT": self.worker_task_log_format,
            "REDBEAT_KEY_PREFIX": self.redbeat_key_prefix,
            "REDBEAT_LOCK_TIMEOUT": self.redbeat_lock_timeout,
            "REDBEAT_REDIS_URL": self.redbeat_redis_url,
            "REDBEAT_REDIS_USE_SSL": self.redbeat_redis_use_ssl,
            "SENTRY_DSN": self.sentry_dsn,
        }


@lru_cache()
def get_settings() -> Settings:
    """Return the cached application settings singleton."""
    return Settings()
