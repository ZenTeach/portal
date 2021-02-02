from random import randint
from time import sleep
from typing import Dict

import pytest
from factory import build
from flask_testing import LiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from server.models import Admin, Questions, Teacher
from server.tests.e2e.commons import (click_button, click_checkbox,
                                      enter_text_field,
                                      fill_content_editable_field,
                                      select_option)
from server.tests.factories import (AdminFactory, QuestionChoiceFactory,
                                    QuestionsFactory, TeacherFactory)


@pytest.fixture
def admin_(client) -> Admin:
    return AdminFactory.create()


@pytest.fixture
def teacher_(client) -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def question_params() -> Dict:
    choices = [build(dict, FACTORY_CLASS=QuestionChoiceFactory,
                     weight=1, is_correct_choice=True) for _ in range(4)]
    question_payload = build(dict, FACTORY_CLASS=QuestionsFactory,
                             multiple_choice_question_type=True)

    question_payload['choices'] = choices

    return question_payload


class TestQuestionUI:
    @pytest.mark.e2e
    def test_questions_ui_is_visible(self, live_server: LiveServerTestCase, selenium):
        selenium.get(live_server.url('/admin/admin.question'))
        el = selenium.find_element_by_xpath('//*[@id="brand"]')
        assert el.text == 'Questions list'

    # @pytest.mark.skip
    @pytest.mark.e2e
    def test_questions_create_form_succeeds(self, live_server, selenium, question_params: Dict):
        selenium.get(live_server.url('/admin/admin.question'))
        sleep(1)
        click_button(selenium, '//*[@id="content"]/div[1]/a', 'xpath')

        # Fill topic
        enter_text_field(selenium, '//*[@id="topic"]', 'xpath', question_params['question'])

        # Fill knowledge item
        enter_text_field(selenium, '//*[@id="knowledge_item"]',
                         'xpath', question_params['knowledge_item'])

        # Fill tag
        enter_text_field(selenium, '//*[@id="tag"]', 'xpath', question_params['tag'])

        # Fill question type
        select_option(selenium, '//*[@id="question_type"]', 'multiple_choice', 'xpath')

        # Fill question
        enter_text_field(selenium, '//*[@id="question"]', 'xpath', question_params['question'])

        for idx, choice in enumerate(question_params['choices']):
            click_button(selenium, '//*[@id="choices-button"]', 'xpath')
            # Fill in choices
            sleep(1)

            # Fill in choice value
            enter_text_field(
                selenium, f"//*[@id=\"choices-{idx}-value\"]", 'xpath', choice['value'])

            # Fill in feedback. Check if it's possible to send key events to a contenteditable div
            fill_content_editable_field(
                selenium,
                f"//*[@id=\"choices-{idx}-feedback\"]/div[1]",
                'xpath',
                choice['feedback'])

        # select random correct choice
        rnd_choice = randint(0, len(question_params['choices']) - 1)

        click_checkbox(selenium, f"//*[@id=\"choices-{rnd_choice}-is_correct_choice\"]", 'xpath')

        enter_text_field(selenium, f"//*[@id=\"choices-{rnd_choice}-weight\"]", 'xpath', 1)

        # Submit
        click_button(selenium, '//*[@id="content"]/form/div[8]/input[1]', 'xpath')
        sleep(1)

        assert Questions.query.filter_by(question=question_params['question']).first() is not None

    @pytest.fixture(autouse=True)
    def _login_admin(self, admin_: Admin, live_server, selenium) -> None:
        selenium.get(live_server.url('/admin'))
        WebDriverWait(selenium, 5).\
            until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 "form input#email")
            )).send_keys(admin_.email)
        selenium.find_element_by_id("password").send_keys("Asdfgh12!")
        selenium.find_element_by_class_name("fourth").click()
