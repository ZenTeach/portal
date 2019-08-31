import os
from secrets import token_urlsafe

class BaseConfig:
    SERVER_NAME='zenteach_be'
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my_precious'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False # Set this to True in production
    JWT_COOKIE_CSRF_PROTECT = True

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    JWT_SECRET_KEY = token_urlsafe()

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')
    JWT_SECRET_KEY = token_urlsafe()

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')