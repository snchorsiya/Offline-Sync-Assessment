import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait


def open_form():
    """
    Open the local dynamic survey form.
    """

    ch_option = Options()
    ch_option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=ch_option)
    # Implicit wait
    driver.implicitly_wait(20)
    
    file_path = os.path.abspath("dynamic_form.html")

    driver.get("file://" + file_path)
    driver.maximize_window()
    print("Browser opened...")
    time.sleep(5)

    return driver


def test_hobby_visible_when_yes():

    driver = open_form()

    try:

        # Locate hobby question
        hobby_question = Select(
            driver.find_element(
                By.ID,
                "hobby-question"
            )
        )

        # Locate dependent question
        hobby_field = driver.find_element(
            By.ID,
            "hobby-field"
        )

        # Verify initial state
        assert not hobby_field.is_displayed(), \
            "Hobby field should be hidden initially"

        # Select Yes
        hobby_question.select_by_visible_text("Yes")

        # Wait until dependent field becomes visible
        WebDriverWait(driver, 20).until(
            lambda d: d.find_element(
                By.ID,
                "hobby-field"
            ).is_displayed()
        )

        # Final verification
        assert hobby_field.is_displayed(), \
            "Hobby field should be visible when Yes is selected"

    finally:

        driver.quit()


def test_hobby_hidden_when_no():

    driver = open_form()

    try:

        # Locate hobby question
        hobby_question = Select(
            driver.find_element(
                By.ID,
                "hobby-question"
            )
        )

        # Select No
        hobby_question.select_by_visible_text("No")

        # Locate dependent question
        hobby_field = driver.find_element(
            By.ID,
            "hobby-field"
        )

        # Verify field remains hidden
        assert not hobby_field.is_displayed(), \
            "Hobby field should remain hidden when No is selected"

    finally:

        driver.quit()


def test_hobby_visibility_changes_correctly():

    driver = open_form()

    try:

        # Locate question
        hobby_question = Select(
            driver.find_element(
                By.ID,
                "hobby-question"
            )
        )

        # Locate dependent field
        hobby_field = driver.find_element(
            By.ID,
            "hobby-field"
        )

        # -------------------------
        # Step 1: Select Yes
        # -------------------------

        hobby_question.select_by_visible_text("Yes")

        WebDriverWait(driver, 10).until(
            lambda d: d.find_element(
                By.ID,
                "hobby-field"
            ).is_displayed()
        )

        assert hobby_field.is_displayed(), \
            "Hobby field should be visible after selecting Yes"


        # -------------------------
        # Step 2: Select No
        # -------------------------

        hobby_question.select_by_visible_text("No")

        WebDriverWait(driver, 10).until(
            lambda d: not d.find_element(
                By.ID,
                "hobby-field"
            ).is_displayed()
        )

        assert not hobby_field.is_displayed(), \
            "Hobby field should be hidden after selecting No"

    finally:

        driver.quit()