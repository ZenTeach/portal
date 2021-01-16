from time import sleep

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from server.models import SchoolClass, Teacher
from server.tests.e2e.commons import (click_button, enter_text_field,
                                      select_option)
from server.tests.factories import AdminFactory, TeacherFactory


@pytest.fixture
def admin_(client):
    return AdminFactory.create()


@pytest.fixture
def teacher_(client):
    return TeacherFactory.create()


class TestSchoolClassUI:
    @pytest.mark.e2e
    def test_school_class_ui_is_visible(self, live_server, selenium):
        selenium.get(live_server.url('/admin/admin.class'))
        el = selenium.find_element_by_xpath('//*[@id="brand"]')
        assert el.text == 'School class list'

    @pytest.mark.e2e
    def test_school_class_create_form_succeeds(self, live_server, selenium, teacher_: Teacher):
        selenium.get(live_server.url('/admin/admin.class'))
        sleep(1)
        click_button(selenium, '//*[@id="content"]/div[1]/a', 'xpath')

        # Fill class name
        enter_text_field(selenium, '//*[@id="name"]', 'xpath', 'Example class')

        # Select subject
        select_option(selenium, '//*[@id="subject"]', 'chemistry', 'xpath')

        # select teacher
        click_button(selenium, '//*[@id="s2id_teacher"]/a', 'xpath')
        sleep(1)
        click_button(selenium, '//*[@id="select2-result-label-3"]', 'xpath')

        # Submit
        click_button(selenium, '//*[@id="content"]/form/div[6]/input[1]', 'xpath')

        assert SchoolClass.query.filter_by(name="Example class").first() is not None

    @pytest.fixture(autouse=True)
    def _login_admin(self, admin_, live_server, selenium):
        selenium.get(live_server.url('/admin'))
        WebDriverWait(selenium, 5).\
            until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "form input#email")
            )).send_keys(admin_.email)
        selenium.find_element_by_id("password").send_keys("Asdfgh12!")
        selenium.find_element_by_class_name("fourth").click()
