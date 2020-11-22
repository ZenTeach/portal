import re
import time

import pytest
from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from server.tests.factories import AdminFactory


@pytest.fixture
def admin_(client):
    return AdminFactory.create()


class TestAdmin:
    def test_admin_smoketest(self, live_server, selenium):
        assert live_server._process
        assert live_server._process.is_alive()

        assert live_server.app.config['SERVER_NAME'] == \
            'localhost:%d' % live_server.port

        selenium.get(live_server.url('/admin'))
        assert url_for('admin.login_view') in selenium.current_url

    def _login_admin(self, admin_email, admin_password, live_server, selenium):
        selenium.get(live_server.url('/admin'))
        WebDriverWait(selenium, 5).\
            until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "form input#email")
            )).send_keys(admin_email)
        selenium.find_element_by_id("password").send_keys(admin_password)
        selenium.find_element_by_class_name("fourth").click()

    @pytest.mark.parametrize("admin_pass,expectation",
                             [
                                 pytest.param("", False),
                                 pytest.param("Asdfgh12!", True)
                             ])
    def test_admin_login(self, live_server, admin_, selenium, admin_pass, expectation):
        self._login_admin(admin_.email, admin_pass, live_server, selenium)
        time.sleep(1)
        url_matcher = re.compile(r'^http\:\/\/localhost\:[0-9]*\/admin\/$')
        matches = re.fullmatch(url_matcher, selenium.current_url) is not None
        assert matches == expectation
