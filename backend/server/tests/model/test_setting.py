from collections import OrderedDict
from secrets import token_urlsafe

from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import Setting


def test_setting_get_loaders(client: FlaskClient):
    setting = Setting()
    assert setting.get_loaders() == ['_load_examboard', '_load_exempt_list']


def test_setting_run_loaders(client: FlaskClient, mocker: MockFixture):
    setting = Setting()
    assert 'exam_board' in list(setting.configuration.keys())
    assert 'exempts' in list(setting.configuration.keys())


def test_setting_get_item(client: FlaskClient, mocker: MockFixture):
    token = token_urlsafe(16)

    def mock__load_exempt_list():
        return OrderedDict({'exempts': [token]})

    mocker.patch('server.config._load_exempt_list', autospec=mock__load_exempt_list,
                 side_effect=mock__load_exempt_list)

    setting = Setting()
    assert setting.configuration.get('exempts') == [token]
    assert setting.get('exempts') == [token]
