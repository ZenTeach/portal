import os
from secrets import token_urlsafe


class BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my_precious'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = True
    JWT_ACCESS_COOKIE_PATH = '/api/v1/'
    # JWT_REFRESH_COOKIE_PATH='/api/v1/teacher/token/refresh'
    JWT_ACCESS_CSRF_HEADER_NAME = 'X-CSRF-ACCESS-TOKEN'
    JWT_REFRESH_CSRF_HEADER_NAME = 'X-CSRF-REFRESH-TOKEN'


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_SECRET_KEY = token_urlsafe()
    JWT_CSRF_IN_COOKIES = False
    JWT_COOKIE_CSRF_PROTECT = False
    FLASK_DEBUG = 1


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')
    JWT_SECRET_KEY = token_urlsafe()


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_COOKIE_SECURE = True
