from time import sleep

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from server.tests.factories import (SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture(autouse=True)
def create_objects(client):
    students = StudentFactory.create_batch(5)
    teacher = TeacherFactory.create()
    classes_ = SchoolClassFactory.create_batch(5, teacher_id=teacher.id)
    [st.add_from_class_list(classes_) for st in students]


class TestAdminStudentUI:
    def test_student_ui_is_visible(self, live_server, selenium):
        selenium.get(live_server.url('/admin/admin.student'))
        el = selenium.find_element_by_xpath('//*[@id="brand"]')
        assert el.text == 'Student list'

    def test_student_delete_does_not_raise(self, live_server, selenium):
        selenium.get(live_server.url('/admin/admin.student'))
        delete_button = selenium.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div/div/div[5]/table/tbody/tr[1]/td[2]/form/button/span')

        delete_button.click()
        Alert(selenium).accept()
        sleep(1)

        with pytest.raises(NoSuchElementException):
            assert selenium.find_element_by_xpath('/html/body/div[1]/h1')

        assert '/admin/admin.student' in selenium.current_url

    def test_student_delete_flashes_message(self, live_server, selenium, mocker):
        selenium.get(live_server.url('/admin/admin.student'))
        delete_button = selenium.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div/div/div[5]/table/tbody/tr[1]/td[2]/form/button/span')

        delete_button.click()
        Alert(selenium).accept()
        sleep(1)

        mocker.patch('server.models.Student.remove_model',
                     side_effect=Exception("Cannot delete model"))

        el = selenium.find_element_by_xpath('//*[@id="content"]/div[1]')
        assert "Failed to delete record" in el.text

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
