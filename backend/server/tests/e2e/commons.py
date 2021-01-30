from functools import lru_cache

from selenium.common.exceptions import NoSuchElementException


def open_page(driver, url):
    driver.get(url)


@lru_cache(16)
def get_els(driver, selector, selector_type):
    finder = None
    if selector_type == 'css':
        finder = driver.find_elements_by_css_selector
    else:
        finder = driver.find_elements_by_xpath

    return finder(selector)


@lru_cache(16)
def get_el(driver, selector, selector_type="xpath"):
    finder = None
    if selector_type == 'css':
        finder = driver.find_element_by_css_selector
    else:
        finder = driver.find_element_by_xpath

    return finder(selector)


def is_el_present(driver, selector, selector_type="xpath"):
    finder = None
    if selector_type == 'css':
        finder = driver.find_element_by_css_selector
    else:
        finder = driver.find_element_by_xpath

    try:
        finder(selector)
        return True
    except NoSuchElementException:
        return False


def click_checkbox(driver, selector, selector_type):
    get_el(driver, selector, selector_type).click()


def click_button(driver, selector, selector_type):
    get_el(driver, selector, selector_type).click()


def select_option(driver, selector, value, selector_type):
    found_option = False
    options = get_els(driver, selector, selector_type)
    for option in options:
        if option.get_attribute('value') == str(value):
            found_option = True
            option.click()
    if not found_option:
        raise Exception('Option %s not found. %s' % (value, " ".join(
            [option.get_attribute('value') for option in options])))


def enter_text_field(driver, selector, selector_type, text):
    text_field = get_el(driver, selector, selector_type)
    text_field.clear()
    text_field.send_keys(text)


def get_selected_option(driver, selector, selector_type):
    options = get_els(driver, selector, selector_type)
    for option in options:
        if option.is_selected():
            return option.get_attribute('value')


def is_option_selected(driver, selector, selector_type, value):
    options = get_els(driver, selector, selector_type)
    for option in options:
        if option.is_selected() != (value == option.get_attribute('value')):
            return False
    return True


def fill_content_editable_field(driver, selector, selector_type, value):
    div_editable = get_el(driver, selector, selector_type)
    is_editable = div_editable.get_attribute('contenteditable')
    if is_editable and div_editable:
        driver.execute_script(f"arguments[0].setAttribute('textContent', '{value}')", div_editable)
