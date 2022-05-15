

# import celery
import pytest

# from server import celery

"""
@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://zenteach:zenteach_broker@localhost:5672/jobs',
        'result_backend': 'redis://localhost:6379'
    }


"""


@pytest.fixture(scope='session')
def celery_config():
    return {
        'worker_hijack_root_logger': False,
        'worker_log_color': False,
        'accept_content': {'json'},
        'enable_utc': True,
        'timezone': 'UTC',
        'broker_transport': 'amqp',
        'broker_url': 'amqp://zenteach:zenteach_broker@localhost:5672/jobs',
        'result_backend': 'redis://localhost:6379/',
        'broker_heartbeat': 0,
    }


@pytest.mark.skip
def test_celery_smoke_test(celery_app):
    pass
