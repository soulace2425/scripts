#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
discord_profile.py
10 July 2022 13:03:05

Selenium script for updating Discord custom status.
"""

import argparse
import os
import sys
from datetime import date

from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

DRIVER_PATH = "C:/Users/soula/AppData/Local/Programs/Python/Python310/Scripts/MicrosoftWebDriver.exe"

WAIT_TIMEOUT = 5.0  # seconds
DISCORD_URL = "https://discord.com/login"
START_DATE = date(2022, 6, 11)
HSSEAS_TEMPLATE = "day {0} of waiting for HSSEAS to let me in"

# full xpaths

XPATH_LOGIN_BUTTON = "/html/body/div[1]/div/div/div[1]/div[1]/header[1]/nav/div/a"
XPATH_EMAIL_INPUT = "/html/body/div[1]/div[2]/div/div[1]/div/div/div/div/form/div/div/div[1]/div[2]/div[1]/div/div[2]/input"
XPATH_PASSWORD_INPUT = "/html/body/div[1]/div[2]/div/div[1]/div/div/div/div/form/div/div/div[1]/div[2]/div[2]/div/input"
XPATH_AVATAR_ICON = "/html/body/div[1]/div[2]/div/div[1]/div/div[2]/div/div[1]/div/div[2]/div[1]/section/div[2]/div[1]/div"
XPATH_CUSTOM_STATUS = "/html/body/div[1]/div[2]/div/div[3]/div/div/div/div/div[7]/div/div/span"
XPATH_STATUS_INPUT = "/html/body/div[1]/div[2]/div/div[3]/div[2]/div/div/div[2]/div[1]/div[2]/div/div[2]/input"


class Parser(argparse.ArgumentParser):
    def __init__(self) -> None:
        super().__init__(description="Update discord status through Selenium")
        self.add_argument("--headless", "-l", action="store_true",
                          help="run the driver headlessly (no window popup)")
        self.add_argument("status", nargs="*", default=None,
                          help="custom status if not using HSSEAS counter")


def login(driver: webdriver.Edge) -> None:
    load_dotenv()

    # enter credentials
    email_input = driver.find_element("xpath",
                                      XPATH_EMAIL_INPUT)
    password_input = driver.find_element("xpath",
                                         XPATH_PASSWORD_INPUT)
    email_input.clear()
    email_input.send_keys(os.environ["DISCORD_EMAIL"])
    password_input.clear()
    password_input.send_keys(os.environ["DISCORD_PASSWORD"] + "\n")
    print("successfully inputted credentials")


def update_status(driver: webdriver.Edge, status: str = None) -> None:
    avatar_icon = driver.find_element("xpath",
                                      XPATH_AVATAR_ICON)
    avatar_icon.click()

    custom_status = driver.find_element("xpath",
                                        XPATH_CUSTOM_STATUS)
    custom_status.click()

    status_input = driver.find_element("xpath",
                                       XPATH_STATUS_INPUT)

    # use HSSEAS counter as default status
    status = status or HSSEAS_TEMPLATE.format(day_number())
    status_input.clear()
    status_input.send_keys(status + "\n")
    print(f"inputted {status=}")


# copy-pasted from coding_mix/coding_mix.pyw
def day_number() -> int:
    """Return day number since start, with START_DATE as Day 1."""
    return (date.today() - START_DATE).days + 1  # +1 to start at Day 1


def main() -> None:
    """Main driver function."""
    ns = Parser().parse_args(sys.argv[1:])

    service = Service(DRIVER_PATH)
    options = Options()

    # run without browser popup
    if ns.headless:
        options.add_argument("headless")

    # remember to update Edge browser itself to match driver version
    # msedgedriver.exe needs to be in PATH but it keeps not detecting
    driver: webdriver.Edge = webdriver.Edge(service=service, options=options)
    driver.get(DISCORD_URL)

    # wait for page to load
    driver.implicitly_wait(WAIT_TIMEOUT)

    login(driver)
    update_status(driver, " ".join(ns.status))

    print("successfully executed process")
    driver.quit()
    print("successfully terminated script")


if __name__ == "__main__":
    main()
