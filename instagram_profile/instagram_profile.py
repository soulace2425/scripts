#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
instagram_profile.py
23 June 2022 22:19:21

Simple script using web-scraping to update my Instagram
account profile with the HSSEAS day count.
"""

import os
import time
from datetime import date

from dotenv import load_dotenv
from selenium import webdriver
# FOR WAITING
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

"""
# waiting boilerplate:
element = WebDriverWait(driver, 10).until(
	EC.presence_of_element_located((By.LINK_TEXT, "Beginner Python Tutorials"))
)
"""

WAIT_TIMEOUT = 5.0  # seconds
INSTAGRAM_URL = "https://www.instagram.com/direct/inbox/"
START_DATE = date(2022, 6, 11)
BIO_TEMPLATE = "day {0} of waiting for HSSEAS to let me in"


def login(driver: webdriver.Edge) -> None:
    load_dotenv()

    # find elements
    username_elem = driver.find_element_by_xpath(
        "//*[@id=\"loginForm\"]/div/div[1]/div/label/input")
    password_elem = driver.find_element_by_xpath(
        "//*[@id=\"loginForm\"]/div/div[2]/div/label/input")
    login_button = driver.find_element_by_xpath(
        "//*[@id=\"loginForm\"]/div/div[3]/button/div")

    username_elem.clear()
    username_elem.send_keys(os.environ["INSTAGRAM_USERNAME"])
    password_elem.clear()
    password_elem.send_keys(os.environ["INSTAGRAM_PASSWORD"])
    print("succesfully inputted credentials")

    login_button.click()
    print("logging in...")


def navigate_to_profile(driver: webdriver.Edge) -> None:
    avatar_elem = driver.find_element_by_xpath(
        "//*[@id=\"react-root\"]/section/nav/div[2]/div/div/div[3]/div/div[6]/div[1]/span/img")
    avatar_elem.click()

    # full xpath needed since xpath had a variable part
    profile_elem = driver.find_element_by_xpath(
        "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[6]/div[2]/div[2]/div[2]/a[1]/div/div[2]/div/div/div/div")
    profile_elem.click()

    # get rid of stupid popup blocking detection of edit button
    # popup_elem = driver.find_element_by_xpath(
    #     "/div/div/div/div[2]/div")
    # popup_elem.click()

    # full xpath needed since xpath had a variable part
    waiter = WebDriverWait(driver, 10)
    callback = expected_conditions.presence_of_element_located(
        (By.XPATH,
         "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/div/header/section/div[2]/div/a")
    )
    edit_button: WebElement = waiter.until(
        callback, "could not detect edit profile button")

    # edit_button = driver.find_element_by_xpath(
    #     "/html/body/div[1]/div/div[1]/div/div[1]/div/div/div[1]/div[1]/section/main/div/header/section/div[2]/div/a")
    edit_button.click()
    edit_button.click()
    print("navigating to the edit profile page")


# copy-pasted from coding_mix/coding_mix.pyw
def day_number() -> int:
    """Return day number since start, with START_DATE as Day 1."""
    return (date.today() - START_DATE).days + 1  # +1 to start at Day 1


def update_profile(driver: webdriver.Edge) -> None:
    new_bio = BIO_TEMPLATE.format(day_number())

    bio_box = driver.find_element_by_xpath(
        "//*[@id=\"pepBio\"]")
    bio_box.clear()
    bio_box.send_keys(new_bio)
    print(f"typed {new_bio=}")

    submit_button = driver.find_element_by_xpath(
        "//*[@id=\"react-root\"]/section/main/div/article/form/div[10]/div/div")
    submit_button.click()
    print("submitted profile change")


def main() -> None:
    """Main driver function."""
    # remember to update Edge browser itself to match driver version
    # MicrosoftEdgeDriver.exe in a PATH directory: Python/Python39/Scripts
    driver: webdriver.Edge = webdriver.Edge()
    # driver.get(INSTAGRAM_URL)

    driver.get("https://www.instagram.com/vinlin24/")

    # wait for page to load
    driver.implicitly_wait(WAIT_TIMEOUT)

    login(driver)
    navigate_to_profile(driver)
    update_profile(driver)

    print("successfully executed process")
    driver.quit()
    print("successfully terminated script")


if __name__ == "__main__":
    main()
