import time

import pytest
from flask import url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class TestAdmin:
    _driver = None

    @classmethod
    def setup_class(cls):
        options = webdriver.ChromeOptions()
        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        chrome_driver_binary = "/usr/local/bin/chromedriver"
        cls.driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)

    @classmethod
    def teardown_class(cls):
        cls.driver.quit()

    @property
    def driver(self):
        return self._driver or None

    @driver.setter
    def driver(self, it):
        self._driver = it

    def test_admin_smoketest(self, live_server):
        assert live_server._process
        assert live_server._process.is_alive()

        assert live_server.app.config['SERVER_NAME'] == \
            'localhost:%d' % live_server.port

        self.driver.get(live_server.url('/admin'))
        assert url_for('admin.login_view') in self.driver.current_url

    def _login_admin(self, admin_email, admin_password, live_server):
        self.driver.get(live_server.url('/admin'))
        WebDriverWait(self.driver, 5).\
            until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "form input#email")
            )).send_keys(admin_email)
        self.driver.find_element_by_id("password").send_keys("Asdfgh12!")
        self.driver.find_element_by_class_name("fourth").click()

    def test_admin_login(self, live_server, admin_):
        self._login_admin(admin_.email, "Asdfgh12!", live_server)
        time.sleep(1)
        assert url_for('admin.index') in self.driver.current_url

    @pytest.mark.skip("FIX: admin fixture is recreated!")
    def test_question_index_view(self, live_server, admin_):
        self._login_admin(admin_.email, "Asdfgh12!", live_server)
        time.sleep()
        teacher_index_url = url_for("admin.teacher.index_view")
        self.driver.get(live_server.url(teacher_index_url))
        assert "Teacher" in self.driver.title
